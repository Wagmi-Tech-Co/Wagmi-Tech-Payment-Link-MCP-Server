# Payment MCP Server

**Turkey's First Payment MCP Server**

The Wagmi Tech Payment MCP Server is a Model Context Protocol (MCP) server that provides seamless integration with payment service providers, allowing developers and AI agents to create and manage payment links effortlessly.

## Use Cases

Transform how payments work with our Payment MCP Server:

- **AI Customer Service**: Let AI assistants create payment links during customer interactions
- **Automated Billing**: Generate payment requests through conversational AI
- **E-commerce Innovation**: Integrate payment creation into AI-powered sales processes
- **Business Automation**: Streamline invoicing and payment collection workflows
- **Dealership Management**: Enable dealerships and retail businesses to collect payments, deposits, and installments through AI-driven systems

## Supported Providers 

- **Moka United** - One of Turkey's leading payment service providers ✅
- **More providers coming soon**... 🔄

*As Turkey's first Payment MCP Server, we're committed to expanding support for all major payment service providers.*

## Available Tools

### create_payment_link
Creates a payment request 

**Required Parameters:**
- `amount` (float): Payment amount

**Optional Parameters:**
- `other_trx_code` (string): Transaction code for reconciliation
- `full_name` (string): Customer full name
- `email` (string): Customer email
- `currency` (string): Payment currency (default: "TL")
- `installment_number` (int): Number of installments
- And many more...

## Usage with MCP Client (e.g., Claude Desktop, Cursor)

### 1. Build the Docker Image
```bash
docker build -t payment-mcp-server .
```

### 2. Configure MCP Client
Add the server configuration to your MCP client (e.g., Claude Desktop, Cursor):

**For stdio transport :**
```json
{
  "mcpServers": {
    "payment-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "PROVIDER",
        "-e", "DEALER_CODE",
        "-e", "USERNAME",
        "-e", "PASSWORD",
        "-e", "CUSTOMER_TYPE_ID",
        "-e", "TRANSPORT",
        "payment-mcp-server"
      ],
      "env": {
        "PROVIDER": "moka",
        "DEALER_CODE": "your_dealer_code",
        "USERNAME": "your_username",
        "PASSWORD": "your_password",
        "CUSTOMER_TYPE_ID": "your_customer_type_id",
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

**For SSE transport (default):**

First, run the server:
```bash
docker run -p 8050:8050 payment-mcp-server
```

Then configure your MCP client to connect via HTTP:
```json
{
  "mcpServers": {
    "payment-mcp-server": {
      "url": "http://localhost:8050/sse",
      "headers": {
        "X-Dealer-Code": "your_dealer_code",
        "X-Username": "your_username",
        "X-Password": "your_password",
        "X-Customer-Type-ID": "your_customer_type_id"
      }
    }
  }
}
```

### 3. Test the Server (Optional)
```bash
# Test with SSE transport (default)
docker run -p 8050:8050 payment-mcp-server
# Then access via http://localhost:8050/health

# Test with stdio transport 
docker run -it \
  -e PROVIDER="moka" \
  -e DEALER_CODE="your_dealer_code" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  -e CUSTOMER_TYPE_ID="your_type_id" \
  -e TRANSPORT="stdio" \
  payment-mcp-server

```

### 4. Ready to Use in MCP Client
Once configured, you can use the `create_payment_link` tool in your MCP client to create  payment requests.

---

## Architecture

This server follows clean architecture principles with clear separation of concerns:

- **`core/`** - Core business logic and interfaces
- **`providers/`** - Payment provider implementations (Moka United, extensible for others)
- **`utils/`** - Utility functions (logging, authentication, validation)
- **`errors/`** - Custom error handling classes
- **`config/`** - Configuration management

## Transport Modes

This server supports two transport modes:

### 1. **stdio transport** 
For direct MCP client connections via stdin/stdout communication.

### 2. **SSE transport** (Server-Sent Events) - Default
For multi-tenant support with per-connection authentication. This allows:
- **Multiple concurrent connections** with different credentials
- **Per-connection authentication** via headers
- **Real-time payment link creation** across multiple sessions
- **Multi-tenant architecture** for businesses with multiple accounts
- **Scalable architecture** for businesses with multiple touchpoints

**Connection method**: Set `TRANSPORT=sse` and connect via HTTP (e.g., `http://localhost:8050/sse`)

Perfect for:

- **Multi-tenant applications** where each user has different credentials
- **Call centers** with multiple agents using different merchant accounts
- **SaaS platforms** serving multiple customers
- **Team environments** with different payment provider accounts

#### SSE Transport Features

**Authentication**: Per-connection via headers
- `X-Dealer-Code`: Your dealer code
- `X-Username`: Your username
- `X-Password`: Your password
- `X-Customer-Type-ID`: Customer type ID (required)

**Supported Header Formats** (case-insensitive):
- `X-Dealer-Code`, `Dealer-Code`, `dealercode`
- `X-Username`, `Username`, `username`
- `X-Password`, `Password`, `password`
- `X-Customer-Type-ID`, `Customer-Type-ID`, `customertypeid`

**Health Check**: `GET /health` endpoint for monitoring


## Docker Usage

### Building the Image
```bash
docker build -t payment-mcp-server .
```

### Running the Server

**SSE Transport (Default - Recommended)**
```bash
# Run SSE server (credentials via headers at connection time)
docker run -p 8050:8050 payment-mcp-server

# With specific transport and port
docker run -p 8050:8050 -e TRANSPORT="sse" payment-mcp-server

# SSE transport with LibreChat integration
# No environment variables needed - credentials via headers
docker run -p 8050:8050 -e TRANSPORT="sse" payment-mcp-server
```

**stdio Transport**
```bash
# Run with environment variables (required for stdio)
docker run -it \
  -e DEALER_CODE="your_dealer_code" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  -e CUSTOMER_TYPE_ID="your_customer_type_id" \
  -e TRANSPORT="stdio" \
  payment-mcp-server

# Or with .env file
docker run -it --env-file .env -e TRANSPORT="stdio" payment-mcp-server
```

**Health Check**
```bash
# Check if SSE server is running
curl http://localhost:8050/health
```

## Docker Compose Usage

**For SSE Transport (Default)**
```bash
# Run SSE server (no credentials needed in .env)
docker-compose --profile sse up

# Or simply (default profile)
docker-compose up

# Server runs at http://localhost:8050
# Health check at http://localhost:8050/health
```

**For stdio Transport**
```bash
# Create .env file with your credentials first (required for stdio)
echo "PROVIDER=moka" > .env
echo "DEALER_CODE=your_dealer_code" >> .env
echo "USERNAME=your_username" >> .env  
echo "PASSWORD=your_password" >> .env
echo "CUSTOMER_TYPE_ID=your_type_id" >> .env

# Run with stdio transport
docker-compose --profile stdio up
```

## Environment Variables

| Variable | Description | Default | Required For |
|----------|-------------|---------|-------------|
| `PROVIDER` | Payment provider to use | moka | Both |
| `DEALER_CODE` | Payment provider dealer code | - | stdio transport only |
| `USERNAME` | Payment provider username | - | stdio transport only |
| `PASSWORD` | Payment provider password | - | stdio transport only |
| `CUSTOMER_TYPE_ID` | Customer type ID | - | stdio transport only |
| `TRANSPORT` | Transport mode (stdio/sse) | sse | Both |

**Note**: For SSE transport, credentials are provided via headers at connection time, not environment variables.

## CLI Options

| Option | Description | Default | Required For |
|--------|-------------|---------|-------------|
| `--provider` | Payment provider to use (env: PROVIDER) | moka | Both |
| `--dealer-code` | Payment provider dealer code | - | stdio transport only |
| `--username` | Payment provider username | - | stdio transport only |
| `--password` | Payment provider password | - | stdio transport only |
| `--customer-type-id` | Customer type ID | - | stdio transport only |
| `--host` | Server host | 0.0.0.0 | sse transport only |
| `--port` | Server port | 8050 | sse transport only |
| `--transport` | Transport mode (stdio/sse) (env: TRANSPORT) | sse | Both |

**Note**: For SSE transport, credentials are provided via headers at connection time, not CLI options.

## Logs

Logs are saved to `/app/logs/` inside the container. To persist logs, mount a volume:

```bash
docker run -v ./logs:/app/logs payment-mcp-server
```

## Development


### Adding New Providers

1. Create a new provider directory under `providers/`
2. Implement the `PaymentProvider` interface
3. Add provider to the factory in `providers/factory.py`
4. Update documentation

### Security

- Credentials are never logged in production
- SSE transport allows per-connection authentication
- Input validation prevents injection attacks
- HTTPS recommended for production deployments

---

## Support & Help

Need help setting up or using the Wagmi Tech Payment MCP Server? 

**Contact us:** hello@wagmitech.co

We're here to help you integrate payment capabilities into your AI workflows.

This Payment MCP Server is just the beginning of our vision to make payment processing more intelligent, accessible, and integrated into the AI ecosystem.

### [Wagmi Tech](https://www.wagmi.tech/)
*We're All Gonna Make It!* 

---