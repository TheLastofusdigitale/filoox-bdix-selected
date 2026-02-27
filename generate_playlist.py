import os, json, random, string, requests
from datetime import datetime
import pytz

# --- CONFIGURAZIONE ---
# Recupera l'URL dell'API dalle variabili d'ambiente
BASE_API = os.getenv("XOTT_API_URL") 
PHP_PROXY = "http://v5on.site/token/stream.php"
HEADERS = {"User-Agent": "Dalvik/2.1.0 (Linux; Android 10)"}

# NUOVI ID CATEGORIE RICHIESTI
TARGET_CATEGORY_IDS = {
    "23", "541", "1633", "1589", "542", "2124", "2297", "640",
    "611", "1612", "536", "1730", "1359", "561", "1397", "2296", 
    "793", "537", "1326", "1360", "540", "1170"
}

def fetch_data(action):
    """Esegue la chiamata API al server v5on.site"""
    if not BASE_API:
        print("❌ ERRORE: La variabile d'ambiente XOTT_API_URL non è configurata!")
        return []
    
    url = f"{BASE_API}&action={action}"
    try:
        # Nascondiamo la password nei log per sicurezza
        safe_url = url.split('password=')[0] + "password=***"
        print(f"📡 Recupero dati da: {safe_url}")
        
        res = requests.get(url, headers=HEADERS, timeout=25)
        res.raise_for_status()
        data = res.json()
        
        # Gestione formati diversi (lista o dizionario)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return list(data.values())
        return []
    except Exception as e:
        print(f"❌ Errore durante la richiesta {action}: {e}")
        return []

def generate_playlist(channels, categories, token):
    """Crea il contenuto del file M3U filtrando per le categorie scelte"""
    # Imposta il fuso orario per il timestamp nel file
    bd_tz = pytz.timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    # Crea una mappa ID -> Nome Categoria per una ricerca veloce
    category_map = {str(cat.get("category_id")): cat.get("category_name") for cat in categories if "category_id" in cat}
    
    lines = [
        "#EXTM3U",
        f"# 📦 GENERATA IL: {bd_time}",
        f"# 🌐 SERVER: v5on.site",
        f"# 🎯 CATEGORIE FILTRATE: {len(TARGET_CATEGORY_IDS)}",
        '#EXTINF:-1 tvg-id="" tvg-name="📺 BENVENUTO" tvg-logo="https://filexo.vercel.app/image/sultanarabi161.jpg" group-title="INFO",📺 BENVENUTO',
        'https://filexo.vercel.app/video/credit_developed_by_sultanarabi161.mp4'
    ]

    count = 0
    # Verifica se almeno una delle categorie target esiste sul server
    has_matching_categories = any(cid in category_map for cid in TARGET_CATEGORY_IDS)

    for ch in channels:
        if not isinstance(ch, dict):
            continue
            
        cat_id = str(ch.get("category_id", ""))
        
        # Filtra: se la categoria è nei target OPPURE se il server ha cambiato tutti gli ID
        if cat_id in TARGET_CATEGORY_IDS or not has_matching_categories:
            name = ch.get("name")
            s_id = ch.get("stream_id")
            logo = ch.get("stream_icon", "")
            cat_name = category_map.get(cat_id, "Altri Canali")

            if name and s_id:
                # Costruisce l'URL usando il proxy e il token generato
                stream_url = f"{PHP_PROXY}?id={s_id}&token={token}"
                lines.append(f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="{logo}" group-title="{cat_name}",{name}')
                lines.append(stream_url)
                count += 1

    # Scrittura fisica del file
    try:
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return count
    except Exception as e:
        print(f"❌ Errore durante la scrittura del file: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 --- INIZIO AGGIORNAMENTO PLAYLIST ---")
    
    # 1. Generazione di un token casuale di 32 caratteri
    new_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    print(f"🔑 Token generato: {new_token[:5]}...")

    # 2. Download categorie e canali
    cats = fetch_data("get_live_categories")
    chans = fetch_data("get_live_streams")
