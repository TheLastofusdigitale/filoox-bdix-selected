import os, json, random, string, requests
from datetime import datetime
import pytz

# --- CONFIG ---
# Se non trova la variabile d'ambiente, inserisci qui l'URL per testare localmente
BASE_API = os.getenv("XOTT_API_URL") 
PHP_PROXY = "http://v5on.site/token/stream.php"
HEADERS = {"User-Agent": "Dalvik/2.1.0 (Linux; Android 10)"}

# ID CATEGORIE (Controlla se sono ancora queste nel pannello)
TARGET_CATEGORY_IDS = {"23", "541", "1633", "1589", "542", "2124", "2297", "640","611", "1612", "536", "1730", "1359", "561", "1397", "2296", "793", "537", "1326", "1360", "540", "1170"}

def fetch_data(action):
    if not BASE_API:
        print("❌ Errore: XOTT_API_URL non configurata!")
        return []
    
    url = f"{BASE_API}&action={action}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=20)
        res.raise_for_status()
        data = res.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"❌ Errore API ({action}): {e}")
        return []

def generate_playlist(channels, categories, token):
    bd_tz = pytz.timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    # Mappa le categorie
    category_map = {str(cat["category_id"]): cat["category_name"] for cat in categories}
    
    # Debug: stampa le categorie trovate se lo script non genera nulla
    if not any(cid in category_map for cid in TARGET_CATEGORY_IDS):
        print("⚠️ Attenzione: Nessuno degli ID in TARGET_CATEGORY_IDS è stato trovato sul sito!")
        print(f"ID disponibili sul sito: {list(category_map.keys())[:10]}...")

    lines = [
        "#EXTM3U",
        f"# 📦 Aggiornato: {bd_time}",
        f"# 🌐 Server: v5on.site",
        '#EXTINF:-1 tvg-logo="https://filexo.vercel.app/image/sultanarabi161.jpg" group-title="Intro",📺 Welcome',
        'https://filexo.vercel.app/video/credit_developed_by_sultanarabi161.mp4'
    ]

    count = 0
    for ch in channels:
        cat_id = str(ch.get("category_id", ""))
        if cat_id in TARGET_CATEGORY_IDS:
            name = ch.get("name")
            s_id = ch.get("stream_id")
            logo = ch.get("stream_icon", "")
            cat_name = category_map.get(cat_id, "Generale")

            if name and s_id:
                stream_url = f"{PHP_PROXY}?id={s_id}&token={token}"
                lines.append(f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="{logo}" group-title="{cat_name}",{name}')
                lines.append(stream_url)
                count += 1

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return count

if __name__ == "__main__":
    print("🔄 Avvio generazione...")
    # Genera token casuale (richiesto dal tuo script originale)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    cats = fetch_data("get_live_categories")
    chans = fetch_data("get_live_streams")

    if cats and chans:
        total = generate_playlist(chans, cats, token)
        print(f"✅ Completato! {total} canali aggiunti a playlist.m3u")
    else:
        print("❌ Impossibile procedere: dati mancanti dal server.")
