import os
import sys
import time
import csv
import logging
import datetime
import re
import urllib.parse
import requests
import ssl
from typing import Dict, List, Optional, Generator
from bs4 import BeautifulSoup
from collections import deque
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ----------------------------------------------------------------------
# 0. CONFIGURATION & CONSTANTS
# ----------------------------------------------------------------------

# Define timeout and headers globally
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Default URL if environment variable is not set
DEFAULT_SCRAPE_URL = "https://example.com"  # Replace with your real target URL

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# ----------------------------------------------------------------------
# 1. DATA CLEANING UTILITIES
# ----------------------------------------------------------------------

def clean_phone_number(phone_text: str) -> str:
    """Clean and normalize phone numbers."""
    if not phone_text:
        return "N/A"
    
    # Replace common separators with nothing
    normalized = re.sub(r'[^\d+]', '', phone_text)
    
    # Remove '+' sign for consistent output, but keep it if user prefers
    return normalized if normalized else "N/A"

def clean_address(address_text: str) -> str:
    """Clean street addresses."""
    if not address_text:
        return "N/A"
    # Remove excessive whitespace and trailing punctuation
    return " ".join(address_text.strip().split())

def clean_url(url: str) -> str:
    """Clean URLs."""
    if not url:
        return "N/A"
    # Encode special characters safely
    try:
        return urllib.parse.quote(url, safe="/%:@?=&-_.~!*'()")
    except NameError:
        return url

# ----------------------------------------------------------------------
# 2. DATA EXTRACTION (Parsing)
# ----------------------------------------------------------------------

def extract_business_data(html_content: str, page_url: str) -> Optional[Dict]:
    """
    Extract business data from HTML content.
    Returns a dictionary if successful, None otherwise.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # --- Business Name Extraction ---
    name = None
    name_patterns = [
        soup.select_one('h1'),  # H1 tag
        soup.select_one('div.head-title h2'),  # Title div
        soup.select_one('.company_name'),  # Company class
        soup.select_one('.name'),  # Generic name
        soup.title.string,  # Page title
    ]
    
    for element in name_patterns:
        if element and element.get_text(strip=True):
            name = clean_address(element.get_text(strip=True))
            break

    if not name:
        return None

    # --- Phone Number Extraction ---
    phone = None
    phone_patterns = [
        soup.select_one('.company_phone'),
        soup.select_one('.phone'),
        soup.select_one('.contact_number'),
        soup.find('div', class_='phone'),
    ]
    
    for element in phone_patterns:
        if element:
            phone_text = element.get_text(strip=True)
            phone = clean_phone_number(phone_text)
            break
    
    # Fallback: Look for patterns in HTML text if not found
    if not phone:
        html_text = soup.get_text()
        # Regex to find standard US/International phone patterns
        phone_matches = re.findall(r'\+?1?\s*(?:\(|\d{3}\s*)\d{3}\s*\d{4}', html_text)
        if phone_matches:
            phone = phone_matches[0].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    # --- Website Extraction ---
    website = None
    if soup.find('meta', attrs={'property': 'og:url'}):
        website = soup.find('meta', attrs={'property': 'og:url'}).get('content')
    elif soup.find('meta', attrs={'property': 'twitter:url'}):
        website = soup.find('meta', attrs={'property': 'twitter:url'}).get('content')
    elif soup.find('a', href=True):
        website = soup.find('a', href=True).get('href')
    
    website = clean_url(website)

    # --- Email Extraction ---
    email = None
    email_patterns = [
        soup.select_one('.company_email'),
        soup.select_one('.email'),
        soup.select_one('.contact_email'),
        soup.find('meta', attrs={'property': 'og:email'}),
        soup.find('meta', attrs={'property': 'twitter:email'}),
    ]
    
    for element in email_patterns:
        if element and element.get_text(strip=True):
            email = element.get_text(strip=True).lower()
            break
    
    if not email:
        email_matches = re.findall(r'[\w\.-]+@[\w\.-]+(\.[\w\.-]+)*/?$', str(soup))
        if email_matches:
            email = email_matches[0]

    # --- Location/Address Extraction ---
    address = None
    address_patterns = [
        soup.select_one('.location'),
        soup.select_one('.address'),
        soup.select_one('.city'),
        soup.find('meta', attrs={'property': 'og:address'}),
    ]
    
    for element in address_patterns:
        if element and element.get_text(strip=True):
            address = clean_address(element.get_text(strip=True))
            break
            
    # Fallback: Look for patterns in HTML text if not found
    if not address:
        html_text = soup.get_text()
        # Regex to find patterns like "City, State Zip"
        location_matches = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+\d{5}', html_text)
        if location_matches:
            address = location_matches[0]

    return {
        "name": name,
        "phone": phone,
        "email": email,
        "website": website,
        "address": address,
    }

# ----------------------------------------------------------------------
# 3. SCRAPING LOGIC
# ----------------------------------------------------------------------

def make_request(url, params=None):
    """Makes HTTP request with retry logic and SSL handling."""
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10
    )

    session = requests.Session()
    session.verify = False
    session.mount('https://', adapter)

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        return response
    except Exception as e:
        LOGGER.error(f"✗ Request Error: {e}")
        raise

def scrape_business_cards(urls: List[str]) -> Generator[Dict, None, None]:
    """
    Generator function that yields business card data for each URL.
    Implements basic pagination logic.
    """
    for url in urls:
        # Add a small delay to be polite
        time.sleep(1) 
        
        try:
            print(f"Fetching: {url}")
            response = make_request(url)

            if response.status_code == 200:
                # Yield data from the current page
                business_data = extract_business_data(response.text, url)
                if business_data:
                    business_data['url'] = url
                    yield business_data
                    print(f"  ✓ Extracted: {business_data['name']}")
                else:
                    print(f"  ⚠ No data found on {url}")
            else:
                print(f"  ✗ Failed: Status {response.status_code}")
        except requests.RequestException as e:
            print(f"  ✗ Request Error: {e}")
        except Exception as e:
            print(f"  ✗ Unexpected Error: {e}")

def scrape_pagination(urls: List[str]) -> Generator[Dict, None, None]:
    """
    Generator function that handles pagination for scraping.
    """
    for url in urls:
        # Add a small delay to be polite
        time.sleep(1) 
        
        try:
            print(f"Fetching: {url}")
            response = make_request(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Example Pagination Logic: Look for 'next' button or links
                next_page = soup.select_one('a.next') or soup.select_one('a.next-page')
                
                if next_page:
                    # Determine pagination URL
                    # This is a generic pattern; adjust based on specific site structure
                    # Example: appending ?page=2
                    page_url = urllib.parse.urljoin(url, next_page.get('href'))
                    
                    print(f"  ⚠ Found next page: {page_url}")
                    
                    # Simple recursion for pagination example
                    for page_url in [url, page_url]:
                        business_data = extract_business_data(response.text, url)
                        if business_data:
                            business_data['url'] = url
                            yield business_data
                            print(f"  ✓ Extracted: {business_data['name']}")
            else:
                print(f"  ✗ Failed: Status {response.status_code}")
        except requests.RequestException as e:
            print(f"  ✗ Request Error: {e}")
        except Exception as e:
            print(f"  ✗ Unexpected Error: {e}")

# ----------------------------------------------------------------------
# 4. MAIN EXECUTION
# ----------------------------------------------------------------------

def get_environment_vars() -> Dict:
    """Read environment variables for scraping configuration."""
    return {
        "SCRAPE_URL": os.getenv('SCRAPE_URL', DEFAULT_SCRAPE_URL),
        "HEADERS": HEADERS,
        "REQUEST_TIMEOUT": REQUEST_TIMEOUT,
    }

def save_to_csv(data, filename='company_contacts.csv'):
    """
    Save scraped data to CSV file.
    """
    if not data:
        LOGGER.warning("No data to save")
        return

    field_names = set()
    for item in data:
        field_names.update(item.keys())
    field_names = sorted(field_names)

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data)

    LOGGER.info(f"✅ Saved {len(data)} records to {filename}")


def main():
    env_vars = get_environment_vars()
    scrape_url = env_vars.get("SCRAPE_URL")
    headers = env_vars.get("HEADERS")
    request_timeout = env_vars.get("REQUEST_TIMEOUT")

    print(f"📁 Starting scrape. Log: {sys.argv[0]}")
    print(f"🔗 Target URL: {scrape_url}")

    # Placeholder for your actual URLs. 
    # In a real scenario, this would be populated from env vars or a config file.
    urls = [scrape_url] 

    all_cards = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"scrape_output_{timestamp}.csv"

    print(f"📝 Scraping URLs...")
    
    # Use pagination logic if available
    # For this example, we use the simple scrape function
    for card in scrape_business_cards(urls):
        all_cards.append(card)

    # Output the data
    if all_cards:
        save_to_csv(all_cards, output_file)
        print(f"✅ Successfully saved {len(all_cards)} records to {output_file}")
    else:
        print("❌ No data collected.")

if __name__ == "__main__":
    main()
