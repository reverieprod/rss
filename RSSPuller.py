import requests
from bs4 import BeautifulSoup
import urllib.parse
import sys
import re
import html
import random  # <-- Added the random module

# --- CONFIGURATION ---
TARGET_URL = "https://www.amazon.com/gp/movers-and-shakers/videogames/"
AFFILIATE_TAG = "saintrem-20"
BRIDGE_BASE = "https://reverieprod.github.io/rss/redirect.html"
OUTPUT_FILE = "my_custom_feed.xml"

# --- THE HYPE VAULT ---
# The script will randomly pick one of these for each item
HYPE_PHRASES = [
    "Climbing the charts in Video Games today! Check out this trending deal now",
    "Now Rising on the Trending Charts",
    "Current standout in the gaming category. Catch it quick!",
    "Level up your collection today!",
    "This one is flying up the ranks today. Don't miss out on the hype!",
    "Don't miss the top trending items!",
    "A major trend alert in the gaming section today. Check it out!"
]

def generate_amazon_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        items = soup.find_all('div', id=lambda x: x and x.startswith('p13n-asin-index-'))
        if not items:
            items = soup.find_all('li', class_='zg-item-immersion')

        found_asins = set()
        rss_items = ""
        count = 0

        for item in items:
            if count >= 15: break
            
            link_elem = item.find('a', href=re.compile(r'/dp/[A-Z0-9]{10}'))
            if not link_elem: continue
            href = link_elem.get('href', '')
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
            
            if asin_match:
                asin = asin_match.group(1)
                if asin not in found_asins:
                    found_asins.add(asin)
                    
                    name_match = re.search(r'/([^/]+)/dp/', href)
                    raw_title = name_match.group(1).replace('-', ' ') if name_match else f"Gaming Deal {asin}"

                    item_text = item.get_text()
                    price_match = re.search(r'\$[0-9]+\.[0-9]{2}', item_text)
                    price = price_match.group(0) if price_match else ""
                    
                    title_with_price = f"{raw_title} - {price}" if price else raw_title

                    # --- THE RANDOMIZER ---
                    # Rolls the dice and picks a phrase from the vault
                    item_desc = random.choice(HYPE_PHRASES)

                    raw_affiliate_url = f"https://www.amazon.com/dp/{asin}/?tag={AFFILIATE_TAG}"
                    encoded_target = urllib.parse.quote(raw_affiliate_url, safe='')
                    masked_link = f"{BRIDGE_BASE}?target={encoded_target}"
                    
                    rss_items += f"""
    <item>
      <title><![CDATA[{title_with_price}]]></title>
      <link>{html.escape(masked_link)}</link>
      <description><![CDATA[{item_desc}]]></description>
    </item>"""
                    count += 1

        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>Amazon Gaming</title><link>{TARGET_URL}</link>{rss_items}</channel></rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"Success: {count} items generated with randomized descriptions.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_amazon_feed()
