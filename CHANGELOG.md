# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-01-30

### Added
- Docker support with Dockerfile and docker-compose.yml
- Command-line interface through run_all.sh
- Docker volume persistence for data
- Health checking for containers
- Resource limits configuration
- Automatic browser opening
- Container log viewing

### Changed
- Updated documentation with Docker instructions
- Improved environment variable handling
- Enhanced error handling in scripts
- Better resource management

## [1.1.0] - 2024-01-30

### Added
- WWW prefix support in domain generation
- Both www and non-www versions of domains
- Alphabetical sorting of generated domains

### Changed
- Updated domain generator to use environment variables
- Improved error handling in domain generation
- Better file organization

## [1.0.0] - 2024-01-30

### Added
- Initial release of the domain screenshot system
- Domain name generator (domaingen.py)
  - Reads names from source file
  - Combines with popular TLDs
  - Saves to target file
- Screenshot capture system (screenshot.py)
  - Multi-threaded processing
  - Configurable retry mechanism
  - Progress monitoring
  - Image resizing
- Real-time viewer server (server.py)
  - Auto-refreshing gallery
  - Progress statistics
  - Responsive design
- Environment configuration
  - Centralized .env configuration
  - Customizable settings
- Automation script (run_all.sh)
  - Sequential process execution
  - Background server management
  - Browser auto-launch

### Features
- Multi-threaded screenshot capture
- Real-time progress monitoring
- Automatic image resizing
- Configurable retry mechanism
- Live gallery viewer
- Environment-based configuration

## [0.2.0] - 2024-01-30

### Added
- Real-time web viewer
- Progress monitoring
- Multi-threading support
- Error handling and retries

### Changed
- Switched from Chrome to Firefox WebDriver
- Improved error handling
- Enhanced logging system

## [0.1.0] - 2024-01-30

### Added
- Basic domain name generator
- Simple screenshot capture
- Initial project structure
- Basic configuration support

### Changed
- Moved from synchronous to asynchronous processing
- Improved file organization
- Enhanced error handling
