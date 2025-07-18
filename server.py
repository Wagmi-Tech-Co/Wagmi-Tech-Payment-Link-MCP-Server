"""
Clean MCP Payment Server with provider-based architecture.
"""
import os
import asyncio
import click
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair

from config.settings import config_manager
from providers.factory import ProviderFactory
from utils.logging import setup_logger
from errors.exceptions import PaymentError, ConfigurationError


class PaymentMCPServer:
    """Main MCP server class with clean architecture."""
    
    def __init__(self, provider_name: str = "moka", host: str = "0.0.0.0", port: int = 8060, transport: str = "stdio", auth_token: Optional[str] = None):
        self.logger = setup_logger(__name__)
        self.provider_name = provider_name
        self.provider = None
        self.mcp = None
        self.host = host
        self.port = port
        self.transport = transport
        self.auth_token = auth_token
    
    async def initialize(self) -> FastMCP:
        """Initialize the MCP server and provider."""
        try:
            # Validate configuration
            config_manager.validate_config()
            
            # Create payment provider
            self.provider = ProviderFactory.create_provider(self.provider_name)
            self.logger.info(f"Initialized {self.provider.get_provider_name()} provider")

            # Setup authentication if needed
            self.logger.info(f"Transport: {self.transport}")
            self.logger.info(f"Auth token: {self.auth_token}")
            auth_provider = None
            issuer_url = None
            if self.transport == 'sse' and self.auth_token:
                self.logger.info("SSE transport with auth token, setting up Bearer authentication.")
                
                # We generate a key on the fly. The token will be valid for this server session.
                key_pair = RSAKeyPair.generate()
                
                issuer_url = "https://wagmi.tech/auth"
                
                auth_provider = BearerAuthProvider(
                    public_key=key_pair.public_key,
                    issuer=issuer_url,
                    audience="wagmi-tech-payment-link-mcp-server"
                )
                
                # The provided auth_token is used as the subject of the JWT
                token = key_pair.create_token(
                    subject=self.auth_token,
                    issuer=issuer_url,
                    audience="wagmi-tech-payment-link-mcp-server",
                    expires_in_seconds=31536000,
                )
                self.logger.info(f"--- Your Bearer Token for this session ---")
                self.logger.info(f"Use this token in the 'Authorization' header: Bearer <token>")
                self.logger.info(f"{token}")
                self.logger.info(f"------------------------------------------")

            # Create MCP server
            server_config = config_manager.get_server_config()

            auth_config = None
            if auth_provider:
                resource_server_url = f"http://{self.host}:{self.port}"
                auth_config = {
                    "issuer_url": issuer_url,
                    "resource_server_url": resource_server_url,
                }

            self.mcp = FastMCP(
                name=server_config.name,
                host=self.host,
                port=self.port,
                token_verifier=auth_provider,
                auth=auth_config,
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
            commission_by_dealer: str = "12",
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
            - is_three_d: Indicates if 3D secure is mandatory. 0: not mandatory, 1: mandatory. (default is 1)
            - redirect_url: URL to redirect after payment
            - description: Description of the payment
            - customer_code: Customer code
            - first_name: First name of the customer
            - last_name: Last name of the customer
            - birth_date: Birth date of the customer
            - customer_gsm_number: GSM number of the customer
            - customer_email: Email address of the customer
            - address: Address of the customer
            - set_installment_by: Determines who sets the number of installments. 0: Customer, 1: Dealer. If 1, `installment_number` must be provided. (default is 1)
            - commission_by_dealer: Determines who pays the commission. 0: Customer pays all. 1: Dealer pays for single payment, customer for installments. 2-11: Dealer pays for single payment and up to that many installments. 12: Dealer pays for all. (default is "12")
            - is_commission_diff_by_dealer: If dealer pays for N installments, this decides commission for >N. 0: Customer pays full commission. 1: Customer pays the difference. (default is 0)
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
@click.option('--port', default=8060, help='Server port (default: 8060)')
@click.option('--transport', envvar='TRANSPORT', default='stdio', help='Transport type (default: stdio)')
@click.option('--auth-token', envvar='AUTH_TOKEN', default=None, help='A string to identify the client, used to generate a bearer token for SSE transport.')
def main(provider, dealer_code, username, password, customer_type_id, host, port, transport, auth_token):
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
        valid_transports = ['stdio', 'sse']
        if transport not in valid_transports:
            raise ConfigurationError(
                f"Unsupported transport '{transport}'. Available: {', '.join(valid_transports)}"
            )
        
        logger.info(f"Starting Payment MCP server with provider: {provider}")
        logger.info(f"Transport: {transport}")
        logger.info(f"Starting Payment MCP server with provider: {provider}")
        logger.info(f"Server will run on {host}:{port}")
        
        async def _run():
            server = PaymentMCPServer(provider_name=provider, host=host, port=port, transport=transport, auth_token=auth_token)
            mcp = await server.initialize()
            logger.info("Payment MCP server started successfully")
            return mcp
        
        # Run the server
        mcp = asyncio.run(_run())
        mcp.run(transport=transport)
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    main()
