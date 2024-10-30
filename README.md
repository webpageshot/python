# Domain Screenshot System

A system for generating and managing domain screenshots with a web interface, supporting both www and non-www variants of domains.

## Quick Start

1. Install Docker and Docker Compose
2. Run the system:
   ```bash
   ./run_all.sh start
   ```
3. Access the web interface at http://localhost:8000

## System Requirements

- Docker
- Docker Compose
- Python 3.x (for non-Docker setup)
- Modern web browser

## Installation

### Docker Setup (Recommended)

1. Install Docker and Docker Compose:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose

   # Fedora
   sudo dnf install docker docker-compose

   # macOS
   brew install docker docker-compose
   ```

2. Clone the repository and navigate to the project directory

3. Run the system:
   ```bash
   ./run_all.sh start
   ```

### Manual Setup (Alternative)

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   python3 server.py
   ```

## Usage

### Command Line Interface

The `run_all.sh` script provides several commands:

```bash
./run_all.sh [OPTION]

Options:
  start    - Build (if needed) and start the containers
  stop     - Stop the containers
  restart  - Restart the containers
  rebuild  - Force rebuild and start the containers
  clean    - Stop containers and remove images
  logs     - Show container logs
  help     - Show this help message
```

### Web Interface Features

1. Domain Management:
   - Add individual domain names
   - Add base names for domain generation
   - Edit domain lists through text editor
   - Generate www and non-www variants

2. Screenshot Management:
   - Capture screenshots in parallel
   - View real-time progress
   - Regenerate screenshots
   - Remove all screenshots

3. File Management:
   - Edit source.txt (base names)
   - Edit extensions.txt (TLD list)
   - View and manage generated domains

## Configuration

### Environment Variables (.env)

```bash
# Server configuration
SERVER_HOST=localhost
SERVER_PORT=8000

# File paths
SOURCE_FILE=source.txt
TARGET_FILE=target.txt
EXTENSIONS_FILE=extensions.txt
IMAGE_DIR=img

# Screenshot settings
SCREENSHOT_WIDTH=1920
SCREENSHOT_HEIGHT=1080
SCREENSHOT_RESIZE_WIDTH=500
PAGE_LOAD_WAIT=3

# Threading configuration
MAX_WORKERS=4
MAX_RETRIES=3
RETRY_DELAY=2

# Browser settings
HEADLESS=true

# Docker configuration
COMPOSE_PROJECT_NAME=domain-screenshot
DOCKER_BUILDKIT=1
```

### File Structure

- `source.txt`: List of base domain names
- `extensions.txt`: List of domain extensions (TLDs)
- `target.txt`: Generated domain combinations
- `img/`: Directory containing screenshots

## Docker Volumes

The following directories are persisted:
- `./img`: Screenshot images
- `./source.txt`: Source domain names
- `./target.txt`: Generated domain list
- `./extensions.txt`: Domain extensions
- `./.env`: Environment configuration

## Features

- Multi-threaded screenshot capture
- Real-time progress monitoring
- Live gallery viewer
- File editing capabilities
- Screenshot regeneration
- Bulk operations management
- WWW and non-WWW domain variants
- Docker support for easy deployment
- Configurable screenshot dimensions
- Automatic image resizing
- Error handling and retries
- Clean web interface

## Troubleshooting

1. If containers fail to start:
   ```bash
   ./run_all.sh logs
   ```

2. To rebuild the containers:
   ```bash
   ./run_all.sh rebuild
   ```

3. To completely reset:
   ```bash
   ./run_all.sh clean
   ./run_all.sh start
   ```

## Security Notes

- The system is designed for internal use
- No authentication is implemented
- Use behind a firewall or VPN
- Don't expose to public internet

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use and modify as needed.
