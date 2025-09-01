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
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")

if not CLIENT_ID or not SECRET or not DEVICE_ID:
    raise RuntimeError("⚠️ Debes configurar TUYA_CLIENT_ID, TUYA_SECRET y TUYA_DEVICE_ID en .env")


def send_switch_command(client: TuyaClient, device_id: str, state: bool):
    """Enciende o apaga el switch"""
    body = {
        "commands": [
            {"code": "switch", "value": state}
        ]
    }
    resp = client.request(
        "POST",
        f"/v1.0/devices/{device_id}/commands",
        body=body,
        headers={"Content-Type": "application/json"},
    )
    return resp.json()


def main():
    client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)

    print("🔑 Obteniendo token...")
    client.get_token()

    print("\n💡 Control interactivo del switch")
    print("Escribe 'on' para encender, 'off' para apagar, 'exit' para salir.\n")

    while True:
        cmd = input("👉 Comando [on/off/exit]: ").strip().lower()

        if cmd == "exit":
            print("👋 Saliendo...")
            break
        elif cmd == "on":
            print("💡 Encendiendo switch...")
            result = send_switch_command(client, DEVICE_ID, True)
            print("Respuesta:", result)
        elif cmd == "off":
            print("💤 Apagando switch...")
            result = send_switch_command(client, DEVICE_ID, False)
            print("Respuesta:", result)
        else:
            print("⚠️ Comando no válido. Usa 'on', 'off' o 'exit'.")


if __name__ == "__main__":
    main()
