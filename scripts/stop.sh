#!/bin/bash

echo "Stopping Korea History Quiz services..."

# Kill backend (port 8000) and frontend (port 8003)
for PORT in 8000 8003; do
    if lsof -ti:$PORT >/dev/null 2>&1; then
        fuser -k ${PORT}/tcp 2>/dev/null && echo "  Stopped service on :$PORT"
    else
        echo "  Nothing running on :$PORT"
    fi
done

# Stop OpenSearch containers
for NAME in es01 opensearch-dashboards; do
    if docker ps --format "{{.Names}}" | grep -q "^${NAME}$"; then
        docker stop "$NAME" && echo "  Stopped container: $NAME"
    fi
done

echo "Done."
