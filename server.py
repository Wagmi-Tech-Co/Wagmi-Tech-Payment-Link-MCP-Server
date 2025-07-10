"""
Clean MCP Payment Server with provider-based architecture.
"""
import os
import asyncio
import click
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from config.settings import config_manager
from providers.factory import ProviderFactory
from core.interfaces import ProviderCredentials
from utils.logging import setup_logger
from errors.exceptions import PaymentError, ConfigurationError


class PaymentMCPServer:
    """Main MCP server class with clean architecture."""
    
    def __init__(self, provider_name: str = "moka", host: str = "0.0.0.0", port: int = 8050, transport: str = "stdio"):
        self.logger = setup_logger(__name__)
        self.provider_name = provider_name
        self.provider = None
        self.mcp = None
        self.host = host
        self.port = port
        self.transport = transport
        self._current_headers = {}
        self.sse_transport = None
        self.app = None
    
    async def initialize(self) -> FastMCP:
        """Initialize the MCP server and provider."""
        try:
            # Create payment provider
            self.provider = ProviderFactory.create_provider(self.provider_name)
            self.logger.info(f"Initialized {self.provider.get_provider_name()} provider")
            
            # Create MCP server
            server_config = config_manager.get_server_config()
            self.mcp = FastMCP(
                name=server_config.name
            )
            
            # Register tools
            self._register_tools()
            
            # Set up transport based on type
            if self.transport == "sse":
                self._setup_sse_server()
            
            self.logger.info("Payment MCP server initialized successfully")
            return self.mcp
            
        except Exception as e:
            self.logger.error(f"Failed to initialize server: {str(e)}")
            raise
    
    def _setup_sse_server(self):
        """Set up SSE server with header authentication."""
        self.logger.info("Setting up SSE server with header authentication")
        
        # Create SSE transport
        self.sse_transport = SseServerTransport("/messages/")
        
        # Create the SSE handler that can access request headers
        async def handle_sse(request: Request):
            # Extract headers for authentication
            self._current_headers = dict(request.headers)
            self.logger.info(f"SSE connection with {len(self._current_headers)} headers")
            self.logger.debug(f"Available headers: {list(self._current_headers.keys())}")
            
            # Check for authentication headers
            credentials = self._get_credentials_from_headers()
            if not credentials:
                self.logger.warning("SSE connection rejected: missing authentication headers")
                raise HTTPException(
                    status_code=401, 
                    detail="Missing authentication headers: X-Dealer-Code, X-Username, X-Password, X-Customer-Type-ID required"
                )
            
            self.logger.info(f"SSE connection authenticated for dealer: {credentials.dealer_code}")
            
            # Connect to SSE transport
            async with self.sse_transport.connect_sse(
                request.scope,
                request.receive,
                request._send
            ) as (in_stream, out_stream):
                # Run the MCP server
                await self.mcp._mcp_server.run(
                    in_stream,
                    out_stream,
                    self.mcp._mcp_server.create_initialization_options()
                )
        
        # Create Starlette app for SSE endpoints
        sse_app = Starlette(
            routes=[
                Route("/sse", handle_sse, methods=["GET"]),
                Mount("/messages/", app=self.sse_transport.handle_post_message)
            ]
        )
        
        # Create FastAPI app and mount SSE app
        self.app = FastAPI(title="Payment MCP Server")
        self.app.mount("/", sse_app)
        
        # Add health check endpoint
        @self.app.get("/health")
        def health_check():
            return {"message": "Payment MCP Server is running", "transport": "sse"}
    
    def _get_credentials_from_headers(self, request_headers: Dict[str, str] = None) -> Optional[ProviderCredentials]:
        """Extract credentials from request headers for SSE transport."""
        try:
            # Use provided headers or captured headers
            headers = request_headers or self._current_headers
            
            # Debug logging
            self.logger.debug(f"Attempting to extract credentials from {len(headers)} headers")
            self.logger.debug(f"Available header keys: {list(headers.keys())}")
            
            # Try different header formats (case-insensitive)
            header_keys = {k.lower(): k for k in headers.keys()}
            
            dealer_code = (
                headers.get(header_keys.get('x-dealer-code', ''), '') or
                headers.get(header_keys.get('dealer-code', ''), '') or
                headers.get(header_keys.get('dealercode', ''), '') or ''
            )
            
            username = (
                headers.get(header_keys.get('x-username', ''), '') or
                headers.get(header_keys.get('username', ''), '') or ''
            )
            
            password = (
                headers.get(header_keys.get('x-password', ''), '') or
                headers.get(header_keys.get('password', ''), '') or ''
            )
            
            customer_type_id_str = (
                headers.get(header_keys.get('x-customer-type-id', ''), '') or
                headers.get(header_keys.get('customer-type-id', ''), '') or
                headers.get(header_keys.get('customertypeid', ''), '') or ''
            )
            
            try:
                customer_type_id = int(customer_type_id_str) if customer_type_id_str else 0
            except ValueError:
                customer_type_id = 0
            
            # Debug the extracted values (without showing password)
            self.logger.debug(f"Extracted - dealer_code: '{dealer_code}', username: '{username}', password: {'*' * len(password) if password else ''}, customer_type_id: {customer_type_id}")
            
            if not all([dealer_code, username, password]) or customer_type_id == 0:
                self.logger.warning(f"Missing required authentication headers. Found: dealer_code={bool(dealer_code)}, username={bool(username)}, password={bool(password)}, customer_type_id={customer_type_id}")
                return None
                
            return ProviderCredentials(
                dealer_code=dealer_code,
                username=username,
                password=password,
                customer_type_id=customer_type_id
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting credentials from headers: {str(e)}")
            return None
    
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
            
            Authentication:
            - For SSE transport: Provide credentials via headers (X-Dealer-Code, X-Username, X-Password, X-Customer-Type-ID)
            - For stdio transport: Credentials are read from environment variables
            
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
                # Get credentials based on transport type
                credentials = None
                if self.transport == "sse":
                    # Get credentials from headers (required for SSE transport)
                    credentials = self._get_credentials_from_headers()
                    
                    if credentials:
                        self.logger.info(f"Using header credentials for dealer: {credentials.dealer_code}")
                    else:
                        # No credentials available
                        available_headers = list(self._current_headers.keys())
                        self.logger.warning(f"No valid credentials found in headers. Available headers: {available_headers}")
                        return {
                            "error": "For SSE transport, credentials must be provided via headers: X-Dealer-Code, X-Username, X-Password, X-Customer-Type-ID", 
                            "error_code": "MISSING_AUTH_HEADERS",
                            "debug": {
                                "available_headers": available_headers,
                                "transport": self.transport
                            }
                        }
                                                
                else:
                    # For stdio transport, validate environment variables
                    try:
                        config_manager.validate_config()
                    except ConfigurationError as e:
                        return {"error": str(e), "error_code": "CONFIG_ERROR"}
                
                return await self.provider.create_payment_link(
                    amount=amount,
                    credentials=credentials,
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
    
    def run_sse_server(self):
        """Run the SSE server using uvicorn."""
        import uvicorn
        self.logger.info(f"Starting SSE server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)


@click.command()
@click.option('--provider', envvar='PROVIDER', default='moka', help='Payment provider to use (default: moka)')
@click.option('--dealer-code', envvar='DEALER_CODE', help='Dealer code (required for stdio transport)')
@click.option('--username', envvar='USERNAME', help='Username (required for stdio transport)')
@click.option('--password', envvar='PASSWORD', help='Password (required for stdio transport)')
@click.option('--customer-type-id', envvar='CUSTOMER_TYPE_ID', help='Customer type ID (default: 2)')
@click.option('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
@click.option('--port', default=8050, help='Server port (default: 8050)')
@click.option('--transport', envvar='TRANSPORT', default='sse', help='Transport type (default: sse)')
def main(provider, dealer_code, username, password, customer_type_id, host, port, transport):
    """Start the Payment MCP server with clean architecture."""
    
    # Load environment variables
    load_dotenv()
    
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
        logger.info(f"Server will run on {host}:{port}")
        
        if transport == 'sse':
            # SSE transport - headers required at connection time
            logger.info("SSE transport: credentials expected via headers (X-Dealer-Code, X-Username, X-Password)")
            
            async def _run_sse():
                server = PaymentMCPServer(provider_name=provider, host=host, port=port, transport=transport)
                await server.initialize()
                return server
            
            # Initialize and run SSE server
            server = asyncio.run(_run_sse())
            server.run_sse_server()
            
        else:
            # STDIO transport - validate credentials are provided
            if not all([dealer_code, username, password, customer_type_id]):
                missing = []
                if not dealer_code:
                    missing.append('--dealer-code')
                if not username:
                    missing.append('--username')
                if not password:
                    missing.append('--password')
                if not customer_type_id:
                    missing.append('--customer-type-id')
                raise ConfigurationError(
                    f"For stdio transport, the following options are required: {', '.join(missing)}"
                )
            
            # Set configuration from CLI options for stdio transport
            config_manager.set_config_from_env({
                'DEALER_CODE': dealer_code,
                'USERNAME': username,
                'PASSWORD': password,
                'CUSTOMER_TYPE_ID': customer_type_id,
            })
            
            logger.info(f"STDIO transport: using configured credentials for dealer: {dealer_code}")
            
            async def _run_stdio():
                server = PaymentMCPServer(provider_name=provider, host=host, port=port, transport=transport)
                mcp = await server.initialize()
                logger.info("Payment MCP server started successfully")
                return mcp
        
            # Run the stdio server
            mcp = asyncio.run(_run_stdio())
            mcp.run(transport=transport)
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    main()
