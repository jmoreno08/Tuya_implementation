import os
import sys
from dotenv import load_dotenv

# 👇 permitir importar tuya_client/ sin instalar como paquete
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tuya_client import TuyaClient

# Cargar credenciales
load_dotenv()
CLIENT_ID = os.getenv("TUYA_CLIENT_ID")
SECRET = os.getenv("TUYA_SECRET")
BASE_URL = os.getenv("TUYA_BASE_URL", "https://openapi.tuyaus.com")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")

if not CLIENT_ID or not SECRET or not DEVICE_ID:
    raise RuntimeError("⚠️ Debes configurar TUYA_CLIENT_ID, TUYA_SECRET y TUYA_DEVICE_ID en .env")


def set_prepayment(client: TuyaClient, enable: bool):
    """Habilita o deshabilita el modo prepago (balance_energy)."""
    payload = {
        "commands": [
            {"code": "switch_prepayment", "value": enable}
        ]
    }
    resp = client.request(
        "POST",
        f"/v1.0/devices/{DEVICE_ID}/commands",
        body=payload,
        headers={"Content-Type": "application/json"},
    )
    return resp.json()


def recharge_energy(client: TuyaClient, value_wh: int):
    """Recarga energía en Wh (ejemplo: 5000 = 5 kWh)."""
    payload = {
        "commands": [
            {"code": "charge_energy", "value": value_wh}
        ]
    }
    resp = client.request(
        "POST",
        f"/v1.0/devices/{DEVICE_ID}/commands",
        body=payload,
        headers={"Content-Type": "application/json"},
    )
    return resp.json()


def get_prepayment_status(client: TuyaClient):
    """Consulta el estado actual de switch_prepayment y balance_energy."""
    resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}/status")
    data = resp.json()
    prepay = None
    balance = None
    for item in data.get("result", []):
        if item["code"] == "switch_prepayment":
            prepay = item["value"]
        if item["code"] == "balance_energy":
            balance = item["value"]
    return prepay, balance


def main():
    client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)
    print("🔑 Obteniendo token...")
    client.get_token()

    while True:
        prepay, balance = get_prepayment_status(client)
        print("\n📊 Estado actual del breaker:")
        print(f"➡️ switch_prepayment: {prepay}")
        if balance is not None:
            print(f"➡️ balance_energy: {balance} Wh ({balance/1000:.2f} kWh)")

        print("\n===== MENÚ =====")
        print("1. Habilitar prepago (balance_energy)")
        print("2. Deshabilitar prepago (balance_energy)")
        print("3. Recargar energía")
        print("4. Salir")
        choice = input("Selecciona una opción: ")

        if choice == "1":
            print("⚡ Habilitando prepago...")
            print("Respuesta:", set_prepayment(client, True))
        elif choice == "2":
            print("⚡ Deshabilitando prepago...")
            print("Respuesta:", set_prepayment(client, False))
        elif choice == "3":
            try:
                kwh = float(input("Ingrese la cantidad de kWh a recargar: "))
                value_wh = int(kwh * 1000)  # convertir a Wh
                print(f"⚡ Recargando {value_wh} Wh ({kwh:.2f} kWh)...")
                print("Respuesta:", recharge_energy(client, value_wh))
            except ValueError:
                print("❌ Valor inválido, ingrese un número válido.")
        elif choice == "4":
            print("👋 Saliendo del programa.")
            break
        else:
            print("❌ Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    main()
