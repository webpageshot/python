import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get file paths from environment variables
SOURCE_FILE = os.getenv('SOURCE_FILE', 'source.txt')
TARGET_FILE = os.getenv('TARGET_FILE', 'target.txt')
EXTENSIONS_FILE = os.getenv('EXTENSIONS_FILE', 'extensions.txt')

def generate_domains():
    # Read base names
    try:
        with open(SOURCE_FILE, 'r') as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {SOURCE_FILE} not found")
        return
    
    # Read extensions
    try:
        with open(EXTENSIONS_FILE, 'r') as f:
            extensions = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {EXTENSIONS_FILE} not found")
        return
    
    # Generate domain combinations
    domains = []
    for name in names:
        for ext in extensions:
            # Add both www and non-www versions
            domains.append(f"{name}{ext}")
            domains.append(f"www.{name}{ext}")
    
    # Sort domains alphabetically
    domains.sort()
    
    # Write to target file
    try:
        with open(TARGET_FILE, 'w') as f:
            for domain in domains:
                f.write(f"{domain}\n")
        print(f"Generated {len(domains)} domains")
    except Exception as e:
        print(f"Error writing to {TARGET_FILE}: {str(e)}")

if __name__ == "__main__":
    generate_domains()
