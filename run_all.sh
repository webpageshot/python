#!/bin/bash

# Load environment variables
source .env

# Function to display usage
show_help() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  start    - Build (if needed) and start the containers"
    echo "  stop     - Stop the containers"
    echo "  restart  - Restart the containers"
    echo "  rebuild  - Force rebuild and start the containers"
    echo "  clean    - Stop containers and remove images"
    echo "  logs     - Show container logs"
    echo "  help     - Show this help message"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Error: Docker is not running or you don't have permission to use it"
        exit 1
    fi
}

# Function to start containers
start_containers() {
    echo "Starting containers..."
    if [ ! -d "img" ]; then
        mkdir img
    fi
    docker-compose up -d
    echo "Waiting for server to start..."
    sleep 3
    echo "Opening browser..."
    python3 -m webbrowser "http://${SERVER_HOST}:${SERVER_PORT}/"
    echo "System is running! Press Ctrl+C to stop viewing logs"
    docker-compose logs -f
}

# Function to stop containers
stop_containers() {
    echo "Stopping containers..."
    docker-compose down
}

# Function to rebuild containers
rebuild_containers() {
    echo "Rebuilding containers..."
    docker-compose build --no-cache
    start_containers
}

# Function to clean up
cleanup() {
    echo "Cleaning up..."
    docker-compose down --rmi all --volumes --remove-orphans
}

# Check if Docker is running
check_docker

# Process command line arguments
case "$1" in
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    restart)
        stop_containers
        start_containers
        ;;
    rebuild)
        rebuild_containers
        ;;
    clean)
        cleanup
        ;;
    logs)
        docker-compose logs -f
        ;;
    help)
        show_help
        ;;
    *)
        echo "No option specified, starting containers..."
        start_containers
        ;;
esac
