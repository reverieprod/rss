import requests
import sys
import html
import urllib.parse

# --- CONFIGURATION ---
# Using your hardcoded offset of 5
API_URL = "https://chaturbate.com/api/public/affiliates/onlinerooms/?wm=uVv1N&client_ip=request_ip&format=json&limit=4&gender=f&hd=true&offset=4"
# Your specific preconfigured URL template
AFFILIATE_TEMPLATE = "https://chaturbate.com/in/?tour=YrCr&campaign=uVv1N&track=rss&room={username}"
# Your Bridge Page
BRIDGE_BASE = "https://remyrev.github.io/remyrsspullerVGMS/redirect.html"
OUTPUT_FILE = "cb_trending_feed.xml"

def generate_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(API_URL, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        rooms = data.get('results', [])

        if not rooms:
            sys.exit(1)

        rss_items = ""
        for room in rooms:
            # 1. Get the Username
            name = room.get('username', '')
            clean_name = html.escape(name)
            subject = html.escape(room.get('room_subject', 'Live Now'))
            
            # 2. CONSTRUCT THE CUSTOM LINK (Reverted Method)
            custom_url = AFFILIATE_TEMPLATE.format(username=name)
            
            # 3. MASK THE LINK (Bridge Method)
            encoded_target = urllib.parse.quote(custom_url)
            masked_link = f"{BRIDGE_BASE}?target={encoded_target}"
            
            # 4. High-res image hack
            raw_img = room.get('image_url', '')
            high_res_img = raw_img.replace('_360x270', '').replace('_450x338', '') 
            safe_thumb = html.escape(high_res_img)
            
            rss_items += f"""
    <item>
      <title><![CDATA[{clean_name} - {subject}]]></title>
      <link>{masked_link}</link>
      <description><![CDATA[{clean_name} is live now.]]></description>
      <media:content url="{safe_thumb}" medium="image" />
    </item>"""

        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Trending CB Rooms (Custom Template)</title>
    <link>https://chaturbate.com/</link>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"Success! {OUTPUT_FILE} updated with custom template & masked links.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_rss()
