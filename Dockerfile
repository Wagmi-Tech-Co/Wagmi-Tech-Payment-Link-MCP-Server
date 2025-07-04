# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install project dependencies using uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the application code
COPY server.py .
COPY constant.py .
COPY config/ ./config/
COPY core/ ./core/
COPY errors/ ./errors/
COPY providers/ ./providers/
COPY utils/ ./utils/

# Create logs directory
RUN mkdir -p logs

# Set default environment variables (can be overridden at runtime)
ENV PROVIDER="moka"
ENV DEALER_CODE=""
ENV USERNAME=""
ENV PASSWORD=""
ENV CUSTOMER_TYPE_ID=""
ENV TRANSPORT="sse"
ENV HOST="0.0.0.0"
ENV PORT="8050"

# Expose port for both SSE and stdio transports
EXPOSE 8050

# Health check for SSE transport
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8050/health || exit 1

# Create a startup script that handles different transport types
COPY <<EOF /app/start.sh
#!/bin/bash
set -e

if [ "\$TRANSPORT" = "sse" ]; then
    echo "Starting SSE transport server..."
    python server.py --provider="\$PROVIDER" --transport="\$TRANSPORT" --host="\$HOST" --port="\$PORT"
else
    echo "Starting stdio transport server..."
    if [ -z "\$DEALER_CODE" ] || [ -z "\$USERNAME" ] || [ -z "\$PASSWORD" ] || [ -z "\$CUSTOMER_TYPE_ID" ]; then
        echo "Error: For stdio transport, DEALER_CODE, USERNAME, PASSWORD, and CUSTOMER_TYPE_ID must be set"
        exit 1
    fi
    python server.py --provider="\$PROVIDER" --dealer-code="\$DEALER_CODE" --username="\$USERNAME" --password="\$PASSWORD" --customer-type-id="\$CUSTOMER_TYPE_ID" --transport="\$TRANSPORT" --host="\$HOST" --port="\$PORT"
fi
EOF

RUN chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]