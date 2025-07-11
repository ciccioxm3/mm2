#LOAD THE CONFIG
import json
import os

# Open the configuration file
with open('config.json') as f:
    # Load JSON data from file
    config = json.load(f)

# Accessing SC_DOMAIN
SITE = config["Siti"]
FT_DOMAIN = SITE["Filmpertutti"]['url']
SC_DOMAIN = SITE["StreamingCommunity"]['url']
TF_DOMAIN = SITE["Tantifilm"]['url']
LC_DOMAIN = SITE["LordChannel"]['url']
SW_DOMAIN = SITE["StreamingWatch"]['url']
AW_DOMAIN = SITE['AnimeWorld']['url']
SKY_DOMAIN = SITE['SkyStreaming']['url']
CB_DOMAIN = SITE['CB01']['url']
DDL_DOMAIN = SITE['DDLStream']['url']
DLHD_DOMAIN = SITE['DaddyLiveHD']['url']
GS_DOMAIN = SITE['Guardaserie']['url']
GHD_DOMAIN = SITE['GuardaHD']['url']
OST_DOMAIN = SITE['Onlineserietv']['domain']
SC = SITE['StreamingCommunity']['enabled']
FT = SITE['Filmpertutti']['enabled']
TF = SITE['Tantifilm']['enabled']
LC = SITE['LordChannel']['enabled']
SW = SITE['StreamingWatch']['enabled']
AW = SITE['AnimeWorld']['enabled']
SKY = SITE['SkyStreaming']['enabled']
CB = SITE['CB01']['enabled']
DDL = SITE['DDLStream']['enabled']
MYSTERIUS = SITE['Mysterius']['enabled']
GS = SITE['Guardaserie']['enabled']
GHD = SITE['GuardaHD']['enabled']
OST = SITE['Onlineserietv']['enabled']
DLHD = SITE['DaddyLiveHD']['enabled']
TF_ForwardProxy = SITE['Tantifilm']["TF_ForwardProxy"]
SC_ForwardProxy = SITE['StreamingCommunity']["SC_ForwardProxy"]
GS_ForwardProxy = SITE['Guardaserie']["GS_ForwardProxy"]
GH_ForwardProxy = SITE['GuardaHD']["GH_ForwardProxy"]
VX_ForwardProxy = SITE['StreamingCommunity']["VX_ForwardProxy"]
AW_ForwardProxy = SITE['AnimeWorld']["AW_ForwardProxy"]
MX_ForwardProxy = SITE['CB01']["MX_ForwardProxy"]
CB_ForwardProxy = SITE['CB01']["CB_ForwardProxy"]
OST_ForwardProxy = SITE['Onlineserietv']["OST_ForwardProxy"]
GS_PROXY = SITE['Guardaserie']["GS_PROXY"]
GH_PROXY = SITE['GuardaHD']["GH_PROXY"]
TF_PROXY = SITE['Tantifilm']["TF_PROXY"]
CB_PROXY = SITE['CB01']["CB_PROXY"]
SC_PROXY = SITE['StreamingCommunity']["SC_PROXY"]
VX_PROXY = SITE['StreamingCommunity']["VX_PROXY"]
AW_PROXY = SITE['AnimeWorld']["AW_PROXY"]
MX_PROXY = SITE['CB01']["MX_PROXY"]
OST_PROXY = SITE['Onlineserietv']["OST_PROXY"]
ips4_device_key = SITE['DDLStream']['cookies']["ips4_device_key"]
ips4_IPSSessionFront = SITE['DDLStream']['cookies']["ips4_IPSSessionFront"]
ips4_member_id = SITE['DDLStream']['cookies']["ips4_member_id"]
ips4_login_key = SITE['DDLStream']['cookies']["ips4_login_key"]
#General
GENERAL = config['General']
dotenv = GENERAL["load_env"]
HOST = GENERAL["HOST"]
PORT = GENERAL["PORT"]
Icon = GENERAL["Icon"]
Name = GENERAL["Name"]
Public_Instance = GENERAL["Public_Instance"]
Remote_Instance = GENERAL["Remote_Instance"]
Global_Proxy =  GENERAL["Global_Proxy"]

# Configurazioni LIVETV strutturate
LIVETV_CONFIG = json.loads(os.getenv('LiveTV', '{}'))
DADDYLIVE_BASE_URL = LIVETV_CONFIG.get('daddylive_url', 'https://daddylive.dad')
VAVOO_BASE_URL = LIVETV_CONFIG.get('vavoo_url', 'https://vavoo.to')
CALCIOX_BASE_URL = LIVETV_CONFIG.get('calciox_url', 'https://calcionew.newkso.ru/calcio/')
LIVETV = LIVETV_CONFIG.get('enabled', '1')
