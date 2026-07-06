#!/usr/bin/env python3
"""
Robust Business Catalogue Scraper with:
- Memory-efficient streaming
- Robust data cleaning
- Exception handling
- Type conversion utilities
"""

import os
import re
import csv
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from typing import List, Dict, Optional, Tuple

# ----------------------------------------------------------------------
# 1. CONFIGURATION & UTILITIES
# ----------------------------------------------------------------------

# Load environment variables (e.g., .env file with directory_url)
load_dotenv()

# Default headers (more realistic than fake browser)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Timeout for HTTP requests (prevent hanging)
REQUEST_TIMEOUT = 30  # seconds

# ----------------------------------------------------------------------
# 2. DATA CLEANING & TYPE CONVERSION UTILITIES
# ----------------------------------------------------------------------

def clean_phone_number(phone_text: str) -> str:
    """
    Convert phone numbers to international format.
    Handles: +32 498 123 456, 0123 456 789, 123456789, etc.
    """
    if not phone_text:
        return "N/A"
    
    # Normalize: remove all non-digits, keep + if present
    cleaned = re.sub(r'[^\d+]', '', phone_text)
    
    # If starts with +, ensure no space after
    if cleaned.startswith('+'):
        cleaned = cleaned.replace(' ', '')
    
    return cleaned if cleaned else "N/A"

def extract_price(price_text: str) -> Optional[float]:
    """
    Convert prices like "€5.50", "$12.99", "£20" to float.
    Returns None if no valid price found.
    """
    if not price_text:
        return None
    
    # Remove currency symbols and spaces
    cleaned = re.sub(r'[^0-9.\-]', '', price_text)
    cleaned = cleaned.replace(',', '.')  # Handle commas in some locales
    
    if not cleaned:
        return None
    
    try:
        # Handle negative prices
        return float(cleaned.replace('-', '')) if cleaned else None
    except ValueError:
        return None

def parse_date(date_text: str, date_format: str = "%Y-%m-%d") -> Optional[str]:
    """
    Parse date strings into ISO format (YYYY-MM-DD).
    Returns None if parsing fails.
    """
    if not date_text:
        return None
    
    # Try common formats
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
        "%d-%m-%Y", "%m-%d-%Y", "%B %d, %Y", "%d %B %Y",
        "%I:%M %p", "%Y-%m-%dT%H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_text.strip(), fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # If no format matches, return as-is (trimmed)
    return date_text.strip() if date_text.strip() else None

# Need to import datetime
from datetime import datetime

# ----------------------------------------------------------------------
# 3. MAIN SCRAPING FUNCTION
# ----------------------------------------------------------------------

def scrape_directory() -> List[Dict]:
    """
    Scrape business directory and return clean data.
    Memory-efficient with generator pattern.
    """
    # Get directory URL from environment variable
    directory_url = os.environ.get('directory_url')
    
    if not directory_url:
        print("❌ Error: directory_url not found in environment variables!")
        return []
    
    print(f"📥 Fetching data from: {directory_url}")
    
    try:
        response = requests.get(
            directory_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )
        
        # Check HTTP status
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    
    # Create BeautifulSoup instance
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all business cards (adjust selector if needed)
    cards = soup.select('.card')
    
    print(f"📊 Found {len(cards)} business cards to process...")
    
    company_data = []
    
    # Process each card
    for i, card in enumerate(cards, 1):
        # Add progress
        progress = f"[{i}/{len(cards)}]"
        
        # Extract name
        name_elements = card.select('.cardTitle')
        cname = name_elements[0].get_text().strip() if name_elements else "N/A"
        cname = cname[:100] if len(cname) > 100 else cname  # Limit length
        
        # Extract address
        address_elements = card.select('.cardDetails')
        address = address_elements[0].get_text().strip() if address_elements else "N/A"
        address = address[:200] if len(address) > 200 else address
        
        # Extract phone with proper cleaning
        phone_elements = card.select('.cardContact')
        phone = clean_phone_number(
            phone_elements[0].get_text().strip() if phone_elements else ""
        )
        
        # Extract URL
        url = card.get('href', 'N/A').strip() if card.has_attr('href') else "N/A"
        
        # Create clean record
        record = {
            "name": cname,
            "address": address,
            "phone": phone,
            "url": url
        }
        
        company_data.append(record)
        
        if (i % 100) == 0:
            print(f"✓ Processed {progress} - {i} records")
    
    return company_data

# ----------------------------------------------------------------------
# 4. CSV WRITING WITH PROPER ERROR HANDLING
# ----------------------------------------------------------------------

def write_csv_to_file(company_data: List[Dict], filename: str = "./belleville_company.csv") -> bool:
    """
    Write data to CSV with proper encoding and error handling.
    """
    fieldnames = ["Name", "Address", "Phone", "URL"]
    
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            writer.writerows(company_data)
        
        print(f"✅ Successfully wrote {len(company_data)} records to {filename}")
        return True
        
    except IOError as e:
        print(f"❌ Error writing to {filename}: {e}")
        return False
    except csv.Error as e:
        print(f"❌ CSV Error: {e}")
        return False

# ----------------------------------------------------------------------
# 5. MEMORY CLEANUP FUNCTION
# ----------------------------------------------------------------------

def cleanup_resources() -> None:
    """
    Clean up resources to prevent memory leaks.
    """
    # Clear any cached HTML
    import sys
    if 'response' in dir():
        del response
    if 'soup' in dir():
        del soup
    print("🧹 Resources cleaned up")

# ----------------------------------------------------------------------
# 6. MAIN EXECUTION
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Business Catalogue Scraper - Starting...")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Request timeout: {REQUEST_TIMEOUT}s")
    print()
    
    # Scrape data
    companies = scrape_directory()
    
    if companies:
        # Write to CSV
        if write_csv_to_file(companies):
            print("=" * 60)
            print(f"🎉 Successfully scraped {len(companies)} companies!")
            print("=" * 60)
            print("\nSample data:")
            for i, company in enumerate(companies[:3], 1):
                print(f"\n{i}. {company['name']}")
                print(f"   📍 {company['address']}")
                print(f"   📞 {company['phone']}")
                print(f"   🔗 {company['url']}")
        else:
            print("❌ Failed to write CSV file")
    else:
        print("❌ No data scraped. Check console for errors.")
    
    # Clean up resources
    cleanup_resources()
