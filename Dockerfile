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
ENV CUSTOMER_TYPE_ID="2"
ENV TRANSPORT="stdio"
ENV HOST="0.0.0.0"
ENV PORT="8060"
ENV AUTH_TOKEN=""

# Expose port for SSE transport (only used when TRANSPORT=sse)
EXPOSE 8060

# Run the server with configurable transport
CMD ["sh", "-c", "uv run python server.py --provider=$PROVIDER --dealer-code=$DEALER_CODE --username=$USERNAME --password=$PASSWORD --customer-type-id=$CUSTOMER_TYPE_ID --transport=$TRANSPORT --host=$HOST --port=$PORT --auth-token=$AUTH_TOKEN"]