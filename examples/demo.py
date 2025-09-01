import os
import sys
from dotenv import load_dotenv

# 👇 asegurar que podamos importar tuya_client/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tuya_client import TuyaClient

# Cargar credenciales desde .env
load_dotenv()

CLIENT_ID = os.getenv("TUYA_CLIENT_ID")
SECRET = os.getenv("TUYA_SECRET")
BASE_URL = os.getenv("TUYA_BASE_URL", "https://openapi.tuyaus.com")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")

client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)

print("🔑 Obteniendo token...")
client.get_token()

print(f"📡 Consultando estado del dispositivo {DEVICE_ID}...")
resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}/status")
print(resp.json())
