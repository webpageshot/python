FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install geckodriver
RUN GECKODRIVER_VERSION=$(wget -qO- "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")') \
    && wget "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" \
    && tar -xzf "geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" -C /usr/local/bin \
    && rm "geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" \
    && chmod +x /usr/local/bin/geckodriver

# Set up working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p img

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DISPLAY=:99 \
    MOZ_HEADLESS=1

# Expose port for the web server
EXPOSE 8000

# Set default command
CMD ["python3", "server.py"]
