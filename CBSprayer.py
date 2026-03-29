import requests
import sys
import html  # This is the "Soap" that cleans the text

# Official API Configuration
API_URL = "https://chaturbate.com/api/public/affiliates/onlinerooms/?wm=uVv1N&client_ip=request_ip&format=json&limit=15&gender=f"
AFFILIATE_TEMPLATE = "https://chaturbate.com/in/?tour=YrCr&campaign=uVv1N&track=rss&room={username}"
OUTPUT_FILE = "cb_trending_feed.xml"

def generate_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"Connecting to Chaturbate API...")
        response = requests.get(API_URL, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"API Error: Status {response.status_code}")
            sys.exit(1)

        data = response.json()
        rooms = data.get('results', [])

        if not rooms:
            print("API returned 0 results.")
            sys.exit(1)

        rss_items = ""
        for room in rooms:
            # We "escape" the username and subject to fix the XML error
            name = html.escape(room.get('username', ''))
            subject = html.escape(room.get('room_subject', 'Live Now'))
            
            # Affiliate links often have & symbols too, so we clean the whole URL
            raw_url = AFFILIATE_TEMPLATE.format(username=name)
            affiliate_url = html.escape(raw_url)
            
            rss_items += f"""
    <item>
      <title>{name} - {subject}</title>
      <link>{affiliate_url}</link>
      <description>{name} is live on Chaturbate.</description>
    </item>"""

        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Trending CB Rooms</title>
    <link>https://chaturbate.com/</link>
    <description>Top 15 Trending rooms</description>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
            
        print(f"Success! {OUTPUT_FILE} created and sanitized.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_rss()
