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
    raise RuntimeError("⚠️ Debes configurar TUYA_CLIENT_ID, TUYA_SECRET y TUYA_DEVICE_ID en el archivo .env")


def main():
    client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)

    print("🔑 Obteniendo token...")
    client.get_token()

    # --- Paso 1: Consultar saldo actual ---
    print("📡 Consultando balance_energy actual...")
    resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}/status")
    data = resp.json()

    balance_before = None
    for item in data.get("result", []):
        if item["code"] == "balance_energy":
            balance_before = item["value"]
            print(f"➡️ Saldo actual: {balance_before} (unidad cruda, típicamente Wh)")

    # --- Paso 2: Recargar ---
    recharge_value = 5000  # Ejemplo: 5000 Wh = 5 kWh
    print(f"⚡ Enviando recarga de {recharge_value} Wh...")
    payload = {
        "commands": [
            {"code": "charge_energy", "value": recharge_value}
        ]
    }

    resp = client.request(
        "POST",
        f"/v1.0/devices/{DEVICE_ID}/commands",
        body=payload,
        headers={"Content-Type": "application/json"},
    )
    print("✅ Respuesta de recarga:", resp.json())

    # --- Paso 3: Consultar saldo actualizado ---
    print("📡 Consultando balance_energy actualizado...")
    resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}/status")
    data = resp.json()

    balance_after = None
    for item in data.get("result", []):
        if item["code"] == "balance_energy":
            balance_after = item["value"]
            print(f"➡️ Nuevo saldo: {balance_after} (unidad cruda, típicamente Wh)")

    if balance_before is not None and balance_after is not None:
        diff = balance_after - balance_before
        print(f"📊 Diferencia: {diff} Wh ({diff/1000:.2f} kWh)")


if __name__ == "__main__":
    main()
