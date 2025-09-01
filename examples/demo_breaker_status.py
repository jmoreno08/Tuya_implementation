import os
import sys
from dotenv import load_dotenv

# 👇 permitir importar tuya_client/ sin instalar como paquete
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tuya_client import TuyaClient

# Cargar variables de entorno
load_dotenv()

CLIENT_ID = os.getenv("TUYA_CLIENT_ID")
SECRET = os.getenv("TUYA_SECRET")
BASE_URL = os.getenv("TUYA_BASE_URL", "https://openapi.tuyaus.com")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")  # debe ser el ID del breaker en Tuya IoT

if not CLIENT_ID or not SECRET or not DEVICE_ID:
    raise RuntimeError("⚠️ Debes configurar TUYA_CLIENT_ID, TUYA_SECRET y TUYA_DEVICE_ID en el archivo .env")


def main():
    client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)

    print("🔑 Obteniendo token...")
    client.get_token()

    print(f"📡 Descargando información del breaker {DEVICE_ID}...")
    resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}/status")
    data = resp.json()

    print("✅ Respuesta completa:")
    print(data)

    if "result" in data:
        print("\n📊 Estados reportados:")
        for item in data["result"]:
            print(f" - {item['code']}: {item['value']}")


if __name__ == "__main__":
    main()
