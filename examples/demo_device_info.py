import os
import sys
from dotenv import load_dotenv

# 👇 agrega la raíz del proyecto al path para importar tuya_client/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tuya_client import TuyaClient

# Cargar variables de entorno (.env)
load_dotenv()

CLIENT_ID = os.getenv("TUYA_CLIENT_ID")
SECRET = os.getenv("TUYA_SECRET")
BASE_URL = os.getenv("TUYA_BASE_URL", "https://openapi.tuyaus.com")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")

if not CLIENT_ID or not SECRET or not DEVICE_ID:
    raise RuntimeError("⚠️ Debes configurar TUYA_CLIENT_ID, TUYA_SECRET y TUYA_DEVICE_ID en el archivo .env")

def main():
    client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)

    print("🔑 Obteniendo token...")
    token_info = client.get_token()
    print(token_info)

    if not client.access_token:
        raise RuntimeError("❌ No se pudo obtener access_token")

    print(f"📡 Consultando información del dispositivo {DEVICE_ID}...")
    resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}")
    data = resp.json()
    print("✅ Respuesta completa:")
    print(data)

    # Mostrar si está online
    if "result" in data:
        online = data["result"].get("online")
        name = data["result"].get("name", "Dispositivo")
        print(f"🔍 {name} está {'🟢 ONLINE' if online else '🔴 OFFLINE'}")

if __name__ == "__main__":
    main()
