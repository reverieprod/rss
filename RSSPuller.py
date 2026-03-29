import requests
from bs4 import BeautifulSoup
import urllib.parse
import sys
import re
import html

# --- CONFIGURATION ---
TARGET_URL = "https://www.amazon.com/gp/movers-and-shakers/videogames/"
AFFILIATE_TAG = "saintrem-20"
BRIDGE_BASE = "https://remyrev.github.io/remyrsspullerVGMS/redirect.html"
OUTPUT_FILE = "my_custom_feed.xml"

def generate_amazon_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        print(f"Connecting to Amazon...")
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Grab all product links
        all_links = soup.find_all('a', href=re.compile(r'/dp/[A-Z0-9]{10}'))

        found_asins = set()
        rss_items = ""
        count = 0

        for link in all_links:
            if count >= 15: break
            
            href = link.get('href', '')
            # Regex to find the ASIN
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
            
            if asin_match:
                asin = asin_match.group(1)
                if asin not in found_asins:
                    found_asins.add(asin)
                    
                    # --- THE REGEX HACK ---
                    # Isolate the name slug: looks for text between slashes right before /dp/
                    # Example: /The-Legend-of-Zelda-Tears-of-the-Kingdom/dp/B09VG68YPB
                    name_match = re.search(r'/([^/]+)/dp/', href)
                    
                    if name_match:
                        # Grab the slug and replace dashes with spaces
                        slug = name_match.group(1)
                        raw_title = slug.replace('-', ' ')
                    else:
                        raw_title = f"Gaming Deal {asin}"

                    print(f"Captured via Regex: {raw_title}")

                    # Mask Link
                    raw_affiliate_url = f"https://www.amazon.com/dp/{asin}/?tag={AFFILIATE_TAG}"
                    encoded_target = urllib.parse.quote(raw_affiliate_url, safe='')
                    masked_link = f"{BRIDGE_BASE}?target={encoded_target}"
                    safe_link = html.escape(masked_link)

                    rss_items += f"""
    <item>
      <title><![CDATA[Trending: {raw_title}]]></title>
      <link>{safe_link}</link>
      <description><![CDATA[Check out this trending game on Amazon.]]></description>
    </item>"""
                    count += 1

        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Amazon Gaming Deals</title>
    <link>{TARGET_URL}</link>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        print(f"Success. Generated {count} entries using URL parsing.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_amazon_feed()
