import urllib.request
import urllib.parse
import re
import xml.etree.ElementTree as ET

url = "https://www.amazon.com/gp/movers-and-shakers/videogames/ref=zg_bsms_nav_videogames_0"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Fetching data and extracting titles...")

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html_data = response.read().decode('utf-8')
        
        # --- THE UPGRADED REMIX MAGIC ---
        
        # We now capture TWO groups: Group 1 is the Title Slug, Group 2 is the ID
        regex_pattern = r'href="/([^/]+)/dp/([A-Z0-9]{10})'
        
        # This creates a list of pairs, e.g., [('Super-Mario', 'B0123...'), ('Zelda', 'B0987...')]
        raw_matches = re.findall(regex_pattern, html_data)
        
        # Remove duplicates while keeping the pairs intact
        unique_matches = list(set(raw_matches))
        
        # --- UPDATED AFFILIATE TAG ---
        affiliate_tag = "saintrem-20"
        
        print(f"Found {len(unique_matches)} unique games. Building the RSS XML file...")

        # --- BUILDING THE RSS FEED ---
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        
        ET.SubElement(channel, "title").text = "My Custom Amazon Video Games Feed"
        ET.SubElement(channel, "link").text = "https://www.amazon.com"
        ET.SubElement(channel, "description").text = "Trending video games with my custom affiliate tags."
        
        # We unpack our pairs into two variables: title_slug and asin
        for title_slug, asin in unique_matches:
            item = ET.SubElement(channel, "item")
            
            # 1. Clean up the title: Decode any URL characters (like %20) and swap dashes for spaces
            decoded_title = urllib.parse.unquote(title_slug)
            clean_title = decoded_title.replace('-', ' ')
            
            # 2. Add the real title to the feed
            ET.SubElement(item, "title").text = clean_title
            
            # 3. Add the clean, remixed affiliate link
            clean_url = f"https://www.amazon.com/dp/{asin}?tag={affiliate_tag}"
            ET.SubElement(item, "link").text = clean_url
            
        # Format and save the file
        ET.indent(rss, space="  ", level=0) 
        tree = ET.ElementTree(rss)
        
        filename = "my_custom_feed.xml"
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        
        print(f"\nSuccess! Check '{filename}' for your real titles.")

except Exception as e:
    print(f"\nUh oh, something went wrong: {e}")