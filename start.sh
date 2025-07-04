#!/bin/bash
set -e

if [ "$TRANSPORT" = "sse" ]; then
    echo "Starting SSE transport server..."
    python server.py --provider="$PROVIDER" --transport="$TRANSPORT" --host="$HOST" --port="$PORT"
else
    echo "Starting stdio transport server..."
    if [ -z "$DEALER_CODE" ] || [ -z "$USERNAME" ] || [ -z "$PASSWORD" ] || [ -z "$CUSTOMER_TYPE_ID" ]; then
        echo "Error: For stdio transport, DEALER_CODE, USERNAME, PASSWORD, and CUSTOMER_TYPE_ID must be set"
        exit 1
    fi
    python server.py --provider="$PROVIDER" --dealer-code="$DEALER_CODE" --username="$USERNAME" --password="$PASSWORD" --customer-type-id="$CUSTOMER_TYPE_ID" --transport="$TRANSPORT" --host="$HOST" --port="$PORT"
fi
