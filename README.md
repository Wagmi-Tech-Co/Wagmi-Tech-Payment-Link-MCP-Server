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
        "payment-mcp-server"
      ],
      "env": {
        "PROVIDER": "moka",
        "DEALER_CODE": "your_dealer_code",
        "USERNAME": "your_username",
        "PASSWORD": "your_password",
        "CUSTOMER_TYPE_ID": "your_customer_type_id"
      }
    }
  }
}
```

### 3. Test the Server (Optional)
```bash
# Test with environment variables
docker run -it \
  -e PROVIDER="moka" \
  -e DEALER_CODE="your_dealer_code" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  -e CUSTOMER_TYPE_ID="your_type_id" \
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

## Transport Mode

This server uses **stdio transport** for direct MCP client connections via stdin/stdout communication.

## Docker Usage

### Building the Image
```bash
docker build -t payment-mcp-server .
```

### Running the Server
```bash
# Run with environment variables
docker run -it \
  -e PROVIDER="moka" \
  -e DEALER_CODE="your_dealer_code" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  -e CUSTOMER_TYPE_ID="your_customer_id" \
  payment-mcp-server

# Or with .env file
docker run -it --env-file .env payment-mcp-server

# Run with different provider (currently only moka is supported)
docker run -it \
  -e PROVIDER="moka" \
  -e DEALER_CODE="your_dealer_code" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  payment-mcp-server

# The server communicates via stdin/stdout for direct MCP client connection
```

## Docker Compose Usage

```bash
# Create .env file with your credentials first
echo "PROVIDER=moka" > .env
echo "DEALER_CODE=your_dealer_code" >> .env
echo "USERNAME=your_username" >> .env  
echo "PASSWORD=your_password" >> .env
echo "CUSTOMER_TYPE_ID=your_type_id" >> .env

# Run the server
docker-compose up
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROVIDER` | Payment provider to use | moka |
| `DEALER_CODE` | Payment provider dealer code | Required |
| `USERNAME` | Payment provider username | Required |
| `PASSWORD` | Payment provider password | Required |
| `CUSTOMER_TYPE_ID` | Customer type ID | Required |

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--provider` | Payment provider to use (env: PROVIDER) | moka |
| `--dealer-code` | Payment provider dealer code | Required |
| `--username` | Payment provider username | Required |
| `--password` | Payment provider password | Required |
| `--customer-type-id` | Customer type ID | Required |
| `--host` | Server host | 0.0.0.0 |
| `--port` | Server port | 8050 |

## Logs

Logs are saved to `/app/logs/` inside the container. To persist logs, mount a volume:

```bash
docker run -v ./logs:/app/logs payment-mcp-server
```
---

## Support & Help

Need help setting up or using the Wagmi Tech Payment MCP Server? 

**Contact us:** hello@wagmitech.co

We're here to help you integrate payment capabilities into your AI workflows.

This Payment MCP Server is just the beginning of our vision to make payment processing more intelligent, accessible, and integrated into the AI ecosystem.

### [Wagmi Tech](https://www.wagmi.tech/)
*We're All Gonna Make It!* 

---

