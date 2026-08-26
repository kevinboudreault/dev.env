import os, re, csv, logging, requests
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# --------------------------------------------------------------------- # 
# 0. CONSTANTS                                                          #
# --------------------------------------------------------------------- # 

DEFAULT_URL = "https://business.bellevillechamber.ca/list/search?q=&c=&sa=False&gr=310.6855&gn="
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)

# --------------------------------------------------------------------- # 
# 1. CLEAN-UP & NORMALIZE HELPERS                                       # 
# --------------------------------------------------------------------- # 

def clean_phone(phone_text: str) -> Optional[str]:
    """Strip all non-digit characters from the phone number."""
    if not phone_text:
        return None
    cleaned = re.sub(r'[^\d]', '', phone_text)
    return cleaned if cleaned else None

def clean_text(text: str) -> Optional[str]:
    """Collapse internal whitespace and strip strings."""
    if not text:
        return None
    out = re.sub(r'\s+', ' ', text.strip())
    return out if out else None

# --------------------------------------------------------------------- # 
# 2. HTTP WITH RETRY                                                    # 
# --------------------------------------------------------------------- # 

_http_session_adapter_retry = Retry(total=3, backoff_factor=0.35, status_forcelist=[500, 502, 503, 504])
_http_adapter = HTTPAdapter(max_retries=_http_session_adapter_retry)

def get_response_text(url: str) -> str:
    """Returns HTML text or empty string on failure."""
    session = requests.Session()
    session.mount('https://', _http_adapter)
    
    try:
        r = session.get(url, timeout=15, headers=HEADERS)
        if r.status_code == 200:
            LOGGER.info(f"HTTP {r.status_code} => successfully fetched text from {url}")
            return r.text
        else:
            LOGGER.warning(f"HTTP {r.status_code} error received for {url}")
    except Exception as e:
        LOGGER.warning(f"Request error occurred: {e} — continuing anyway")
    return ""

# --------------------------------------------------------------------- # 
# 3. EXTRACT SINGLE BUSINESS CARD DATA                                   # 
# --------------------------------------------------------------------- # 

def extract_card_data(card_soup: BeautifulSoup) -> Optional[Dict]:
    """Extracts name, phone, and address from a single business card block."""
    result = {"name": None, "phone": None, "address": None, "website": None }

    # Find the title element (usually an h5 with gz-card-title)
    title_tag = card_soup.find("h5", class_="gz-card-title") or card_soup.find("h5")
    if not title_tag:
        return None
        
    result["name"] = clean_text(title_tag.get_text())

    # Chamber directory blocks typically format details in list items or text blocks
    # Let's extract phone numbers using 'tel:' href patterns or text regex matching
    tel_link = card_soup.find("a", href=lambda href: href and href.startswith("tel:"))
    if tel_link:
        result["phone"] = clean_phone(tel_link.get_text())
    else:
        # Fallback regex search for standard North American phone formatting
        phone_match = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', card_soup.get_text())
        if phone_match:
            result["phone"] = clean_phone(phone_match.group(1))

    # --- Precise Microdata Address Extraction ---
    # Try locating the structured microdata street elements inside the card
    street_span = card_soup.find(attrs={"itemprop": "streetAddress"})
    city_zip_div = card_soup.find(attrs={"itemprop": "citystatezip"})

    if street_span and city_zip_div:
        # Extract and scrub individual pieces
        street = clean_text(street_span.get_text())
        
        # Collapse internal spacing for items inside citystatezip (City, Province, Postal)
        city_zip_text = clean_text(city_zip_div.get_text())
        
        if street and city_zip_text:
            result["address"] = f"{street}, {city_zip_text}"
            
    # Fallback to older text line tracking mechanism if microdata wrappers missing
    if not result["address"]:
        text_content = card_soup.get_text(separator="\n")
        lines = [line.strip() for line in text_content.split("\n") if line.strip()]
        for line in lines:
            if " ON " in line or " Ontario " in line or re.search(r'[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d', line):
                result["address"] = clean_text(line)
                break

    # --- Precise Website Extraction ---
    # Target the layout wrapper element directly
    website_container = card_soup.find(class_="gz-card-website")
    if website_container:
        web_link = website_container.find("a")
        if web_link and web_link.get("href"):
            result["website"] = web_link.get("href").strip()

    # Fallback: Look across all anchor cards using GrowthZone script onclick event metrics
    if not result["website"]:
        all_links = card_soup.find_all("a", href=True)
        for link in all_links:
            onclick_attr = link.get("onclick", "")
            if "MemberWebsite" in onclick_attr:
                result["website"] = link.get("href").strip()
                break

    return result

# --------------------------------------------------------------------- # 
# 4. DIRECTORY-SHAPE SCRAPE                                             # 
# --------------------------------------------------------------------- # 

def scrape_directory(url: str) -> List[Dict]:
    """Return a list of result dicts collected from the full directory page."""  
    html = get_response_text(url)
    if not html:
        return []
    
    out: List[Dict] = []
    soup = BeautifulSoup(html, "html.parser")

    # Locate individual card elements using GrowthZone structure selectors
    card_divs = soup.select("div.gz-results-card") or soup.select("div.card") or soup.select(".gz-list-card-wrapper")
    
    # Fallback to scanning custom structure blocks if precise container classes miss
    if not card_divs:
         card_divs = soup.find_all("div", class_=lambda x: x and "card" in x)

    for card in card_divs:
        card_data = extract_card_data(card)
        if card_data and card_data["name"]:
            out.append(card_data)
            
    return out

# --------------------------------------------------------------------- # 
# 5. MAIN ENTRY & EXPORT TO CSV                                         # 
# --------------------------------------------------------------------- # 

def main() -> None:
    target_url = os.getenv("BELLEVILLE_URL", DEFAULT_URL)
    LOGGER.info(f"Starting directory scrape process on: {target_url}")
    
    businesses = scrape_directory(target_url)
    LOGGER.info(f"Extraction complete. Total records uncovered: {len(businesses)}")
    
    # Save the pulled contents securely to a CSV file
    csv_file = "belleville_businesses.csv"
    if businesses:
        keys = businesses[0].keys()
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(businesses)
        LOGGER.info(f"Data successfully successfully written to file: {csv_file}")
    else:
        LOGGER.warning("No complete directory elements matched the layout selectors pattern.")

if __name__ == "__main__":
    main()
