import cloudscraper
from bs4 import BeautifulSoup
import re
import sys

# Your Configuration
TARGET_URL = "https://chaturbate.com/teen-cams/female/"
AFFILIATE_TEMPLATE = "https://chaturbate.com/in/?tour=YrCr&campaign=uVv1N&track=rss&room={username}"
OUTPUT_FILE = "cb_trending_feed.xml"
LIMIT = 15

def generate_rss():
    # We use cloudscraper instead of requests to bypass 403/Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    try:
        print(f"Attempting to scrape {TARGET_URL}...")
        response = scraper.get(TARGET_URL, timeout=15)
        
        # Check if we got through
        if response.status_code == 403:
            print("CRITICAL ERROR: Still getting 403. The site is blocking GitHub's IP range.")
            sys.exit(1)
            
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Logic to find room links
        links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9_-]+/$'))
        
        blacklist = {'/female-cams/', '/male-cams/', '/trans-cams/', '/couple-cams/', '/tags/', '/auth/', '/terms/', '/privacy/', '/help/'}
        
        usernames = []
        for link in links:
            href = link.get('href')
            if href not in blacklist:
                name = href.strip('/')
                if name not in usernames:
                    usernames.append(name)
            
            if len(usernames) >= LIMIT:
                break

        if not usernames:
            print("ERROR: Found 0 usernames. The site layout might have changed.")
            sys.exit(1)

        # Build RSS
        rss_items = ""
        for name in usernames:
            affiliate_url = AFFILIATE_TEMPLATE.format(username=name)
            rss_items += f"""
    <item>
      <title>{name} is Live</title>
      <link>{affiliate_url}</link>
      <description>Check out {name} on the trending list.</description>
    </item>"""

        rss_content = f"""<?xml version='1.0' encoding='utf-8'?>
<rss version="2.0">
  <channel>
    <title>Trending CB Female Cams</title>
    <link>{TARGET_URL}</link>
    <description>Top 15 trending rooms with affiliate tracking.</description>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"Successfully generated {OUTPUT_FILE} with {len(usernames)} items.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_rss()
