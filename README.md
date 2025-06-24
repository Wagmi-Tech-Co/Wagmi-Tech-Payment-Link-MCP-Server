# MCP Payment Server

A Model Context Protocol (MCP) server for payment processing using stdio transport.

## Architecture

This server follows clean architecture principles with clear separation of concerns:

- **`core/`** - Core business logic and interfaces
- **`providers/`** - Payment provider implementations (Moka United, extensible for others)
- **`utils/`** - Utility functions (logging, authentication, validation)
- **`errors/`** - Custom error handling classes
- **`config/`** - Configuration management

## Supported Providers 

- **Moka United** - Turkish payment gateway

- **More is coming**.... 

## Transport Mode

This server uses **stdio transport** for direct MCP client connections via stdin/stdout communication.

## Docker Usage

### Building the Image
```bash
docker build -t mcp-payment-server .
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
  mcp-payment-server

# Or with .env file
docker run -it --env-file .env mcp-payment-server

# Run with different provider (currently only moka is supported)
docker run -it \
  -e PROVIDER="moka" \
  -e DEALER_CODE="your_dealer_code" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  mcp-payment-server

# The server communicates via stdin/stdout for direct MCP client connection
```

## Docker Compose Usage

```bash
# Create .env file with your credentials first
echo "PROVIDER=moka" > .env
echo "DEALER_CODE=your_dealer_code" >> .env
echo "USERNAME=your_username" >> .env  
echo "PASSWORD=your_password" >> .env
echo "CUSTOMER_TYPE_ID=2" >> .env

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
| `CUSTOMER_TYPE_ID` | Customer type ID | 2 |

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--provider` | Payment provider to use (env: PROVIDER) | moka |
| `--dealer-code` | Payment provider dealer code | Required |
| `--username` | Payment provider username | Required |
| `--password` | Payment provider password | Required |
| `--customer-type-id` | Customer type ID | 2 |
| `--host` | Server host | 0.0.0.0 |
| `--port` | Server port | 8050 |


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

## Logs

Logs are saved to `/app/logs/` inside the container. To persist logs, mount a volume:

```bash
docker run -v ./logs:/app/logs mcp-payment-server
```

## Usage Example

### 1. Build the Docker Image
```bash
docker build -t mcp-payment-server .
```

### 2. Configure MCP Client
Add the server configuration to your MCP client (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "mcp-server-payment": {
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
        "mcp-payment-server"
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
  -e CUSTOMER_TYPE_ID="2" \
  mcp-payment-server

```

### 4. Use in MCP Client
Once configured, you can use the `create_payment_link` tool in your MCP client to create  payment requests.

