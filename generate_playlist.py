import os, json, random, string, requests
from datetime import datetime, timezone
import pytz

# --- CONFIG ---
BASE_API = os.getenv("XOTT_API_URL")
PHP_PROXY = "http://v5on.site/token/stream.php"
HEADERS = {"User-Agent": "Dalvik/2.1.0 (Linux; Android 10)"}

# SELECTED CATEGORIES ONLY
TARGET_CATEGORY_IDS = {
    "23", "541", "1633", "1589", "542", "2124", "2297", "640","611", "1612", "536", "1730", "1359", "561", "1397", "2296", "793", "537", "1326", "1360", "540", "1170"
}
# --- 1️⃣ Generate new 32-char token ---
def generate_token():
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    timestamp = int(datetime.now().timestamp())
    with open("token.json", "w") as f:
        json.dump({"token": token, "generated_at": timestamp}, f, indent=2)
    return token

# --- 2️⃣ Fetch all categories ---
def fetch_categories():
    url = f"{BASE_API}&action=get_live_categories"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ Error fetching categories:", e)
        return []

# --- 3️⃣ Fetch all channels ---
def fetch_channels():
    url = f"{BASE_API}&action=get_live_streams"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ Error fetching channels:", e)
        return []

# --- 4️⃣ Generate organized playlist with categories ---
def generate_playlist(channels, categories, token):
    # BD Timezone
    bd_tz = pytz.timezone('Europe/Rome')
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    # Create category mapping
    category_map = {str(cat["category_id"]): cat["category_name"] for cat in categories}
    
    # Group channels by category (only target categories)
    channels_by_category = {}
    target_channels_count = 0
    
    for ch in channels:
        cat_id = str(ch.get("category_id"))
        # Only include channels from target categories
        if cat_id in TARGET_CATEGORY_IDS and cat_id in category_map:
            category_name = category_map[cat_id]
            if category_name not in channels_by_category:
                channels_by_category[category_name] = []
            channels_by_category[category_name].append(ch)
            target_channels_count += 1
    
    print(f"🎯 Filtered {target_channels_count} channels from {len(channels_by_category)} target categories")
    
    # Start building playlist
    lines = [
        "#EXTM3U",
        "# 📦 filoox-bdix Auto Playlist (Token base)",
        f"# ⏰ BD Updated time: {bd_time}",
        f"# 🔄 Updated hourly from xtreme — Total fetched: {target_channels_count}",
        "# 🔁 Rewritten to v5on format",
        "# 🔁 Each stream link uses token validation",
        "# 🌐 @ Credit: @nasodisquiddi",
        "# 🎯 Selected categories only"
    ]
    
    # Add demo channel first
    lines.extend([
        '#EXTINF:-1 tvg-id="" tvg-name="Intro - Channel" tvg-logo="https://filexo.vercel.app/image/sultanarabi161.jpg" group-title="Intro",📺 Welcome',
        'https://filexo.vercel.app/video/credit_developed_by_sultanarabi161.mp4'
    ])
    
    # Add channels organized by category
    for category_name, category_channels in sorted(channels_by_category.items()):
        # Add category header
        lines.append(f"# 🔰 {category_name}")
        
        for ch in category_channels:
            name = ch.get("name", "Unknown").strip()
            logo = ch.get("stream_icon", "").strip()
            stream_id = ch.get("stream_id")
            
            if not name or not stream_id:
                continue
                
            # Use token in URL
            stream_url = f"{PHP_PROXY}?id={stream_id}&token={token}"
            
            # EXTINF line with proper formatting
            extinf_line = f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="{logo}" group-title="{category_name}",{name}'
            lines.append(extinf_line)
            lines.append(stream_url)
    
    # Write to file
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return target_channels_count

# --- MAIN ---
if __name__ == "__main__":
    print("🔄 Starting playlist generation...")
    print(f"🎯 Target categories: {TARGET_CATEGORY_IDS}")
    
    # Generate token
    new_token = generate_token()
    print("✅ Token generated")
    
    # Fetch data
    categories = fetch_categories()
    channels = fetch_channels()
    
    print(f"📊 Fetched {len(categories)} categories and {len(channels)} total channels")
    
    # Generate playlist
    total_channels = generate_playlist(channels, categories, new_token)
    
    print(f"✅ Playlist generated with {total_channels} channels from target categories")
    print("🎯 Token & playlist updated successfully")
