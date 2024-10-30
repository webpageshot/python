from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import os
import time
import concurrent.futures
import logging
import threading
from queue import Queue
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment
IMAGE_DIR = os.getenv('IMAGE_DIR', 'img')
TARGET_FILE = os.getenv('TARGET_FILE', 'target.txt')
SCREENSHOT_WIDTH = int(os.getenv('SCREENSHOT_WIDTH', 1920))
SCREENSHOT_HEIGHT = int(os.getenv('SCREENSHOT_HEIGHT', 1080))
SCREENSHOT_RESIZE_WIDTH = int(os.getenv('SCREENSHOT_RESIZE_WIDTH', 500))
PAGE_LOAD_WAIT = int(os.getenv('PAGE_LOAD_WAIT', 3))
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 2))
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Thread-%(thread)d] - %(levelname)s - %(message)s'
)

# Thread-local storage for WebDriver instances
thread_local = threading.local()

# Shared queue for progress tracking
progress_queue = Queue()

def get_thread_driver():
    """Get or create thread-local WebDriver instance"""
    if not hasattr(thread_local, "driver"):
        chrome_options = Options()
        if HEADLESS:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--window-size={SCREENSHOT_WIDTH},{SCREENSHOT_HEIGHT}')
        chrome_options.add_argument('--disable-gpu')
        
        try:
            # Use webdriver-manager to get the correct chromedriver version
            service = Service(ChromeDriverManager().install())
            thread_local.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logging.error(f"Error setting up Chrome WebDriver: {str(e)}")
            raise
    return thread_local.driver

def cleanup_thread_driver():
    """Cleanup thread-local WebDriver instance"""
    if hasattr(thread_local, "driver"):
        try:
            thread_local.driver.quit()
        except Exception:
            pass
        delattr(thread_local, "driver")

def process_single_domain(domain):
    """Process a single domain with retries"""
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            driver = get_thread_driver()
            output_path = os.path.join(IMAGE_DIR, f"{domain.replace('.', '_')}.png")
            
            url = f"https://{domain}" if not domain.startswith(('http://', 'https://')) else domain
            logging.info(f"Processing: {url}")
            
            driver.get(url)
            time.sleep(PAGE_LOAD_WAIT)
            
            driver.set_window_size(SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT)
            driver.save_screenshot(output_path)
            
            with Image.open(output_path) as img:
                width_percent = (SCREENSHOT_RESIZE_WIDTH / float(img.size[0]))
                new_height = int((float(img.size[1]) * float(width_percent)))
                resized_img = img.resize((SCREENSHOT_RESIZE_WIDTH, new_height), Image.Resampling.LANCZOS)
                resized_img.save(output_path)
            
            logging.info(f"Screenshot saved: {output_path}")
            progress_queue.put(('success', domain))
            return True
            
        except Exception as e:
            retry_count += 1
            logging.error(f"Error processing {domain} (attempt {retry_count}/{MAX_RETRIES}): {str(e)}")
            
            cleanup_thread_driver()
            
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                progress_queue.put(('error', domain))
                return False

def progress_monitor():
    """Monitor and display progress information"""
    success_count = 0
    error_count = 0
    total_count = 0
    
    while True:
        try:
            status, domain = progress_queue.get()
            if status == 'success':
                success_count += 1
            elif status == 'error':
                error_count += 1
            elif status == 'total':
                total_count = domain
                logging.info(f"Starting processing of {total_count} domains")
                continue
            
            processed = success_count + error_count
            if total_count > 0:
                percentage = (processed / total_count) * 100
                logging.info(f"Progress: {processed}/{total_count} ({percentage:.1f}%) - "
                           f"Success: {success_count}, Errors: {error_count}")
            
            if processed == total_count:
                break
            
        except Exception as e:
            logging.error(f"Error in progress monitor: {str(e)}")
            break

def process_domains_parallel(domains):
    """Process domains in parallel using ThreadPoolExecutor"""
    monitor_thread = threading.Thread(target=progress_monitor)
    monitor_thread.start()
    
    progress_queue.put(('total', len(domains)))
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_single_domain, domain) for domain in domains]
            concurrent.futures.wait(futures)
    
    finally:
        cleanup_thread_driver()
    
    monitor_thread.join()

def main():
    try:
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
            
        with open(TARGET_FILE, 'r') as file:
            domains = [line.strip() for line in file]
        
        logging.info(f"Starting screenshot generation with {len(domains)} domains")
        process_domains_parallel(domains)
        logging.info("Processing completed!")
    
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
    
    finally:
        cleanup_thread_driver()

if __name__ == "__main__":
    main()
