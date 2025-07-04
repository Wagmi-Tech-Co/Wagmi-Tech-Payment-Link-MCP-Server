"""
Clean MCP Payment Server with provider-based architecture.
"""
import os
import asyncio
import click
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from config.settings import config_manager
from providers.factory import ProviderFactory
from utils.logging import setup_logger
from errors.exceptions import PaymentError, ConfigurationError


class PaymentMCPServer:
    """Main MCP server class with clean architecture."""
    
    def __init__(self, provider_name: str = "moka"):
        self.logger = setup_logger(__name__)
        self.provider_name = provider_name
        self.provider = None
        self.mcp = None
    
    async def initialize(self) -> FastMCP:
        """Initialize the MCP server and provider."""
        try:
            # Validate configuration
            config_manager.validate_config()
            
            # Create payment provider
            self.provider = ProviderFactory.create_provider(self.provider_name)
            self.logger.info(f"Initialized {self.provider.get_provider_name()} provider")
            
            # Create MCP server
            server_config = config_manager.get_server_config()
            self.mcp = FastMCP(
                name=server_config.name,
                host=server_config.host,
                port=server_config.port,
            )
            
            # Register tools
            self._register_tools()
            
            self.logger.info("Payment MCP server initialized successfully")
            return self.mcp
            
        except Exception as e:
            self.logger.error(f"Failed to initialize server: {str(e)}")
            raise
    
    def _register_tools(self):
        """Register MCP tools."""
        
        @self.mcp.tool()
        async def create_payment_link(
            amount: float,
            # Optional parameters
            other_trx_code: str = "1",
            full_name: str = "",
            gsm_number: str = "",
            email: str = "",
            currency: str = "TL",
            installment_number: int = 0,
            is_pool_payment: int = 0,
            is_pre_auth: int = 0,
            is_tokenized: int = 0,
            is_three_d: int = 1,
            redirect_url: str = "",
            description: str = "",
            customer_code: str = "",
            first_name: str = "",
            last_name: str = "",
            birth_date: str = "",
            customer_gsm_number: str = "",
            customer_email: str = "",
            address: str = "",
            set_installment_by: int = 1,
            commission_by_dealer: str = "0",
            is_commission_diff_by_dealer: int = 0,
            buyer_full_name: str = "",
            buyer_email: str = "",
            buyer_gsm_number: str = "",
            buyer_address: str = ""
        ) -> Dict[str, Any]:
            """Create a payment request using the configured payment provider.
            
            Required parameters:
            - amount: Payment amount
            
            Optional parameters:
            - other_trx_code: Your unique transaction code for reconciliation (default is "1")
            - full_name: Full name of the customer
            - gsm_number: GSM number of the customer
            - email: Email address of the customer
            - currency: Currency for the payment (default is "TL")
            - installment_number: Number of installments (default is 0)
            - is_pool_payment: Indicates if it's a pool payment (default is 0)
            - is_pre_auth: Indicates if it's a pre-authorization (default is 0)
            - is_tokenized: Indicates if the payment is tokenized (default is 0)
            - is_three_d: Indicates if 3D secure is enabled (default is 1)
            - redirect_url: URL to redirect after payment
            - description: Description of the payment
            - customer_code: Customer code
            - first_name: First name of the customer
            - last_name: Last name of the customer
            - birth_date: Birth date of the customer
            - customer_gsm_number: GSM number of the customer
            - customer_email: Email address of the customer
            - address: Address of the customer
            - set_installment_by: Method to set installment (default is 1)
            - commission_by_dealer: Commission by dealer (default is "0")
            - is_commission_diff_by_dealer: Indicates if commission differs by dealer (default is 0)
            - buyer_full_name: Full name of the buyer
            - buyer_email: Email address of the buyer
            - buyer_gsm_number: GSM number of the buyer
            - buyer_address: Address of the buyer
            
            Returns:
            - A dictionary containing the response from the payment provider API.
            - URL: The URL for the payment request.
            - If the request fails:"Request failed" try again one time more.
            - if the request fails, it will raise a PaymentError with an appropriate message.
            
            Note:
            - it is okay to use turkish characters in names and addresses.
            """
            try:
                return await self.provider.create_payment_link(
                    amount=amount,
                    other_trx_code=other_trx_code,
                    full_name=full_name,
                    gsm_number=gsm_number,
                    email=email,
                    currency=currency,
                    installment_number=installment_number,
                    is_pool_payment=is_pool_payment,
                    is_pre_auth=is_pre_auth,
                    is_tokenized=is_tokenized,
                    is_three_d=is_three_d,
                    redirect_url=redirect_url,
                    description=description,
                    customer_code=customer_code,
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=birth_date,
                    customer_gsm_number=customer_gsm_number,
                    customer_email=customer_email,
                    address=address,
                    set_installment_by=set_installment_by,
                    commission_by_dealer=commission_by_dealer,
                    is_commission_diff_by_dealer=is_commission_diff_by_dealer,
                    buyer_full_name=buyer_full_name,
                    buyer_email=buyer_email,
                    buyer_gsm_number=buyer_gsm_number,
                    buyer_address=buyer_address
                )
            except PaymentError as e:
                self.logger.error(f"Payment creation failed: {str(e)}")
                return {"error": str(e), "error_code": getattr(e, 'error_code', None)}
            except Exception as e:
                self.logger.error(f"Unexpected error in create_payment_link: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}


@click.command()
@click.option('--provider', envvar='PROVIDER', default='moka', help='Payment provider to use (default: moka)')
@click.option('--dealer-code', envvar='DEALER_CODE', required=True, help='Dealer code')
@click.option('--username', envvar='USERNAME', required=True, help='Username')
@click.option('--password', envvar='PASSWORD', required=True, help='Password')
@click.option('--customer-type-id', envvar='CUSTOMER_TYPE_ID', default='2', help='Customer type ID (default: 2)')
@click.option('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
@click.option('--port', default=8050, help='Server port (default: 8050)')
def main(provider, dealer_code, username, password, customer_type_id, host, port):
    """Start the Payment MCP server with clean architecture."""
    
    # Load environment variables
    load_dotenv()
    
    # Set configuration from CLI options
    config_manager.set_config_from_env({
        'DEALER_CODE': dealer_code,
        'USERNAME': username,
        'PASSWORD': password,
        'CUSTOMER_TYPE_ID': customer_type_id,
    })
    
    logger = setup_logger(__name__)
    
    try:
        # Validate provider
        available_providers = ProviderFactory.get_available_providers()
        if provider not in available_providers:
            raise ConfigurationError(
                f"Unsupported provider '{provider}'. Available: {', '.join(available_providers)}"
            )
        
        logger.info(f"Starting Payment MCP server with provider: {provider}")
        logger.info(f"Server will run on {host}:{port}")
        
        async def _run():
            server = PaymentMCPServer(provider_name=provider)
            mcp = await server.initialize()
            logger.info("Payment MCP server started successfully")
            return mcp
        
        # Run the server
        mcp = asyncio.run(_run())
        mcp.run()
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    main()
