from bs4 import BeautifulSoup
import re
import urllib.parse
import asyncio
from Src.Utilities.dictionaries import (
    STATIC_CHANNELS_DATA, DADDYLIVE_CHANNEL_NAME_MAP, 
    CHANNELS_RAW_CALCIO, VAVOO_CHANNEL_NAME_MAP, CHANNEL_LOGOS_VAVOO,
    DADDYLIVECHANNELSURL_247ITA, BASE_URL_CALCIO, BASE_URL_VAVOO
)

import Src.Utilities.config as config

# --- Costanti e Helper da 247ita.py ---
HEADERS_REQUESTS_247ITA = {
    "Accept": "*/*",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,ru;q=0.5",
    "Priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "Sec-Ch-UA-Mobile": "?0",
    "Sec-Ch-UA-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Storage-Access": "active",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
}

def get_247ita_channel_numeric_id(channel_name_query, html_content):
    """
    Cerca l'ID numerico di un canale specifico nell'HTML fornito.
    Restituisce l'ID numerico come stringa, o None se non trovato.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)

    # Gestione speciale per DAZN 1
    if "dazn 1" in channel_name_query.lower():
        return "877"

    for link in links:
        link_text_normalized = link.text.strip().lower().replace("italy", "").replace("hd+", "").replace("(251)", "").replace("(252)", "").replace("(253)", "").replace("(254)", "").replace("(255)", "").replace("(256)", "").replace("(257)", "").strip()
        # Potrebbe essere necessario un matching più flessibile qui
        if channel_name_query.lower() in link_text_normalized:
            href = link['href']
            stream_number = href.split('-')[-1].replace('.php', '')
            return stream_number
    return None

async def fetch_247ita_channel_list_html(client):
    """Scarica l'HTML della lista dei canali 247ita."""
    try:
        # Usa il client AsyncSession di MammaMia per coerenza
        response = await client.get(DADDYLIVECHANNELSURL_247ITA, headers=HEADERS_REQUESTS_247ITA, impersonate="chrome120")
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Errore durante il fetch dell'HTML da 247ita: {e}")
        return None

async def get_247ita_streams(client, mfp_url=None, mfp_password=None):
    """
    Recupera tutti gli stream da 247ita.
    """
    html_content = await fetch_247ita_channel_list_html(client)
    if not html_content:
        return []

    streams = []
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)

    # Aggiungi DAZN 1 manualmente se non già presente o per assicurare l'ID corretto
    processed_dazn1 = False

    for link in links:
        if "Italy".lower() in link.text.lower(): # Filtra per canali italiani
            channel_name_original_from_link = link.text.strip() # Es. "Sky Calcio 1 Italy HD+"
            # print(f"DEBUG: DaddyLive Original Name: {channel_name_original_from_link}") # LOG

            # Nome da usare per il lookup nella mappa DADDYLIVE_CHANNEL_NAME_MAP.
            # Rimuoviamo "Italy", "HD+", numeri tra parentesi e convertiamo in lowercase per un matching più flessibile.
            name_for_map_lookup = channel_name_original_from_link.replace("Italy", "") \
                                                                .replace("HD+", "") \
                                                                .replace("(251)", "").replace("(252)", "").replace("(253)", "") \
                                                                .replace("(254)", "").replace("(255)", "").replace("(256)", "") \
                                                                .replace("(257)", "") \
                                                                .strip().lower()
            # print(f"DEBUG: DaddyLive Name for Map Lookup: {name_for_map_lookup}") # LOG

            mapped_name = DADDYLIVE_CHANNEL_NAME_MAP.get(name_for_map_lookup)

            if mapped_name:
                # Se abbiamo una mappatura (es. "sky calcio 1" -> "Sky Sport 251"), usiamo quella.
                channel_name_final_display = mapped_name
            else:
                # Altrimenti, applichiamo la pulizia più generale.
                channel_name_final_display = channel_name_original_from_link.replace("Italy", "") \
                                                                        .replace("8", "") \
                                                                        .replace("(251)", "").replace("(252)", "").replace("(253)", "") \
                                                                        .replace("(254)", "").replace("(255)", "").replace("(256)", "") \
                                                                        .replace("(257)", "") \
                                                                        .replace("HD+", "").strip()

            href = link['href']
            stream_number = href.split('-')[-1].replace('.php', '')

            if "dazn 1" in channel_name_final_display.lower(): # Usa il nome finale per il check
                stream_number = "877" # ID corretto per DAZN 1
                processed_dazn1 = True

            # Usa la configurazione per costruire l'URL dinamico del stream
            stream_url_dynamic = f"{config.DADDYLIVE_BASE_URL}/stream/stream-{stream_number}.php"
            final_url = stream_url_dynamic
            if mfp_url and mfp_password:
                final_url = f"{mfp_url}/extractor/video?host=DLHD&redirect_stream=true&api_password={mfp_password}&d={urllib.parse.quote(stream_url_dynamic)}"
            
            streams.append({
                'id': f"{channel_name_final_display.lower().replace(' ', '-')}", # Rimosso "omgtv-247ita-"
                'title': f"{channel_name_final_display} (D)",
                'url': final_url,
                'logo': STATIC_LOGOS_247ITA.get(channel_name_final_display.lower(), "https://raw.githubusercontent.com/cribbiox/eventi/refs/heads/main/ddlive.png"),
                'group': "247ita" # Per raggruppamento in MammaMia
            })

    if not processed_dazn1: # Aggiungi DAZN 1 se non trovato nel loop (improbabile ma per sicurezza)
        stream_number_dazn = "877"
        stream_url_dynamic_dazn = f"https://daddylive.dad/stream/stream-{stream_number_dazn}.php"
        final_url_dazn = stream_url_dynamic_dazn
        if mfp_url and mfp_password:
            final_url_dazn = f"{mfp_url}/extractor/video?host=DLHD&redirect_stream=true&api_password={mfp_password}&d={urllib.parse.quote(stream_url_dynamic_dazn)}"
        streams.append({
            'id': "dazn-1", # Rimosso "omgtv-247ita-"
            'title': "DAZN 1 (D)",
            'url': final_url_dazn,
            'logo': STATIC_LOGOS_247ITA.get("dazn 1"),
            'group': "247ita"
        })
    return streams

# --- Logica Canali Statici Interni ---
async def get_livetv_stream_for_channel_and_source(channel_id: str, source: str, client, mfp_url=None, mfp_password=None):
    """
    Ottiene uno stream per un canale specifico da una fonte specifica LIVETV.
    Esempio: channel_id="sky-uno", source="247ita"
    """
    if source == "247ita":
        all_247ita_streams = await get_247ita_streams(client, mfp_url, mfp_password)
        
        for stream in all_247ita_streams:
            if stream['id'] == channel_id: # Confronto diretto con ID unificato
                return stream
                
    elif source == "static":
        all_static_streams = await get_static_channel_streams(client, mfp_url, mfp_password)
        
        for stream in all_static_streams:
            if stream['id'] == channel_id: # Confronto diretto con ID unificato
                return stream
                
    elif source == "calcio":
        all_calcio_streams = await get_calcio_streams(client, mfp_url, mfp_password)
        
        for stream in all_calcio_streams:
            if stream['id'] == channel_id: # Confronto diretto con ID unificato
                return stream
                
    elif source == "vavoo":
        all_vavoo_streams = await get_vavoo_streams(client, mfp_url, mfp_password)
        
        for stream in all_vavoo_streams:
            if stream['id'] == channel_id: # Confronto diretto con ID unificato
                return stream
    
    return None

async def get_static_channel_streams(client, mfp_url=None, mfp_password=None):
    """
    Recupera i canali statici definiti localmente in STATIC_CHANNELS_DATA
    e applica la logica MFP se fornita.
    """
    streams = []
    for channel_data in STATIC_CHANNELS_DATA:
        original_channel_id = channel_data.get('id')
        original_channel_title = channel_data.get('title')
        original_channel_url = channel_data.get('url')
        original_channel_logo = channel_data.get('logo')
        group_name = channel_data.get('group', "Statici")

        # Salta i canali se mancano informazioni essenziali, specialmente l'URL
        # Modificato per non richiedere 'original_channel_logo'
        if not all([original_channel_id, original_channel_title, original_channel_url]):
            # print(f"DEBUG LIVETV (static): Canale statico saltato per dati mancanti (ID, Titolo o URL): {channel_data}")
            continue
        # print(f"DEBUG LIVETV (static): Processando canale statico: {original_channel_title}")

        final_url = original_channel_url # Default to original URL

        if mfp_url and mfp_password:
            # print(f"DEBUG LIVETV (static): MFP abilitato per {original_channel_title}. URL originale: {original_channel_url}")
            is_mpd_processed_for_mfp = False
            mpd_marker = ".mpd"
            try:
                # Cerca ".mpd" nell'URL originale
                mpd_index = original_channel_url.lower().index(mpd_marker)
                
                # Estrai l'URL base fino a ".mpd" incluso
                base_mpd_url = original_channel_url[:mpd_index + len(mpd_marker)]
                
                # Estrai la parte della query string che segue ".mpd"
                query_string_part = ""
                if len(original_channel_url) > mpd_index + len(mpd_marker):
                    potential_query_part = original_channel_url[mpd_index + len(mpd_marker):]
                    if potential_query_part.startswith("&"): # Assumiamo che i parametri inizino con &
                        query_string_part = potential_query_part[1:] # Rimuovi il primo &
                
                if query_string_part: # Se ci sono parametri come key_id e key
                    final_url = f"{mfp_url}/proxy/mpd/manifest.m3u8?api_password={mfp_password}&d={urllib.parse.quote(base_mpd_url)}&{query_string_part}"
                else: # MPD senza parametri di chiave esterni
                    final_url = f"{mfp_url}/proxy/mpd/manifest.m3u8?api_password={mfp_password}&d={urllib.parse.quote(base_mpd_url)}"
                is_mpd_processed_for_mfp = True
                # print(f"DEBUG LIVETV (static): {original_channel_title} è MPD. Applicando proxy MFP MPD. URL finale: {final_url}")

            except ValueError: # ".mpd" non trovato nell'URL
                pass # Verrà gestito come HLS sotto

            if not is_mpd_processed_for_mfp: # Se non è stato processato come MPD (es. è HLS)
                final_url = f"{mfp_url}/proxy/hls/manifest.m3u8?api_password={mfp_password}&d={urllib.parse.quote(original_channel_url)}"
                # print(f"DEBUG LIVETV (static): {original_channel_title} non è MPD (o marker non trovato). Applicando proxy MFP HLS. URL finale: {final_url}")

        streams.append({
            'id': f"{original_channel_id}", # Rimosso "livetv-static-" (usa ID originale)
            'title': f"{original_channel_title} (MPD)",
            'url': final_url,
            'group': group_name
        })
        # Aggiungi il logo solo se esiste
        if original_channel_logo:
            streams[-1]['logo'] = original_channel_logo
        # print(f"DEBUG LIVETV (static): Aggiunto stream: {streams[-1]}")
    return streams

async def get_calcio_streams(client, mfp_url=None, mfp_password=None):
    # print("DEBUG: Entrando in get_calcio_streams") # LOG
    streams = []
    raw_channel_list = CHANNELS_RAW_CALCIO + [item[1].split('/mono.m3u8')[0] + '/' for item in EXTRA_CHANNELS_CALCIO]

    if not raw_channel_list:
        # print("DEBUG: raw_channel_list è vuota in get_calcio_streams") # LOG
        return []

    # print(f"DEBUG: raw_channel_list ha {len(raw_channel_list)} elementi.") # LOG

    for raw_path_part in raw_channel_list:
        try:
            channel_display_name, server_tag_suffix = _format_channel_name_calcio(raw_path_part)
            # Usa la configurazione dal config
            original_stream_url = f"{BASE_URL_CALCIO}{raw_path_part}mono.m3u8"
            
            final_url = original_stream_url
            if mfp_url and mfp_password:
                final_url = f"{mfp_url}/proxy/hls/manifest.m3u8?api_password={mfp_password}&d={urllib.parse.quote(original_stream_url)}"
            final_url += HEADER_CALCIO_PARAMS
            
            unique_id_suffix = raw_path_part.rstrip('/').replace("calcio", "").lower()

            # Converti unique_id_suffix in formato standard (es: "x1skynature" -> "sky-nature")
            clean_id = unique_id_suffix.replace("x1", "").replace("x2", "").replace("x", "")
            clean_id = clean_id.replace("sky", "sky-").replace("sport", "-sport").replace("cinema", "-cinema")
            
            stream_data = {
                'id': f"{clean_id}", # Rimosso "omgtv-calcio-"
                'title': f"{channel_display_name}{server_tag_suffix}", 
                'url': final_url,
                'logo': LOGO_URL_CALCIO,
                'group': "Calcio"
            }
            streams.append(stream_data)
            # print(f"DEBUG: Aggiunto stream calcio: {stream_data['id']} - {stream_data['title']}") # LOG
        except Exception as e:
            # print(f"DEBUG: Errore durante il processamento di {raw_path_part} in get_calcio_streams: {e}") # LOG
            continue # Continua con il prossimo canale
            
    # print(f"DEBUG: Uscendo da get_calcio_streams, {len(streams)} streams generati.") # LOG
    return streams


# --- Logica Vavoo ---
async def get_vavoo_streams(client, mfp_url=None, mfp_password=None):
    streams = []
    try:
        # Usa la configurazione dal config
        response = await client.get(f"{BASE_URL_VAVOO}/channels", timeout=10, impersonate="chrome120")
        response.raise_for_status()
        channels_list = response.json()
    except Exception as e:
        print(f"Error fetching Vavoo channel list: {e}")

        return []

    for ch_data in channels_list:
        if ch_data.get("country") == "Italy":
            raw_name_from_vavoo = ch_data["name"].strip()

            # Applica la mappatura specifica di Vavoo se il nome grezzo (lowercase) è nel map
            # Il nome per il display e per la logica interna sarà quello mappato (es. "Sky Sport 251")
            # o quello originale se non c'è mappatura.
            effective_channel_name = VAVOO_CHANNEL_NAME_MAP.get(raw_name_from_vavoo.lower(), raw_name_from_vavoo)

            # Pulisci ulteriormente l'effective_channel_name e preparalo per il display
            cleaned_effective_name = _clean_channel_name_vavoo(effective_channel_name)

            # Usa la configurazione dal config
            original_stream_url = f"{BASE_URL_VAVOO}/play/{ch_data['id']}/index.m3u8"
            
            final_url = original_stream_url
            if mfp_url and mfp_password:
                final_url = f"{mfp_url}/proxy/hls/manifest.m3u8?api_password={mfp_password}&d={urllib.parse.quote(original_stream_url)}"
            final_url += HEADER_VAVOO_PARAMS

            channel_id_safe = cleaned_effective_name.lower().replace(' ', '-').replace('+', '')
            logo_key_for_dict = cleaned_effective_name.lower()

            streams.append({
                'id': f"{channel_id_safe}", # Rimosso "omgtv-vavoo-"
                'title': f"{cleaned_effective_name} (V)",
                'url': final_url,
                'logo': CHANNEL_LOGOS_VAVOO.get(logo_key_for_dict, "https://www.vavoo.tv/software/images/logo.png"), # Fallback logo Vavoo
                'group': "Vavoo"
            })
    return streams
