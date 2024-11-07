#!/bin/bash
# dev.sh

function rebuild() {
    echo "Stopping existing container..."
    docker stop whisper-dev 2>/dev/null
    docker rm whisper-dev 2>/dev/null
    
    echo "Building new image..."
    docker build -t whisper-fastapi-dev .
    
    echo "Starting new container..."
    docker run -d \
        -p 8000:8000 \
        -v "$(pwd):/app" \
        --name whisper-dev \
        whisper-fastapi-dev
    
    echo "Container started! Viewing logs..."
    docker logs -f whisper-dev
}

function logs() {
    docker logs -f whisper-dev
}

function shell() {
    docker exec -it whisper-dev bash
}

function restart() {
    docker restart whisper-dev
    docker logs -f whisper-dev
}

case "$1" in
    "rebuild")
        rebuild
        ;;
    "logs")
        logs
        ;;
    "shell")
        shell
        ;;
    "restart")
        restart
        ;;
    *)
        echo "Usage: ./dev.sh [rebuild|logs|shell|restart]"
        ;;
esac