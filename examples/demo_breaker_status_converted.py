import os
import sys
import base64
import struct
from dotenv import load_dotenv

# 👇 permitir importar tuya_client/ sin instalar como paquete
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tuya_client import TuyaClient

# Cargar variables de entorno
load_dotenv()

CLIENT_ID = os.getenv("TUYA_CLIENT_ID")
SECRET = os.getenv("TUYA_SECRET")
BASE_URL = os.getenv("TUYA_BASE_URL", "https://openapi.tuyaus.com")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")  # ID del breaker

if not CLIENT_ID or not SECRET or not DEVICE_ID:
    raise RuntimeError("⚠️ Debes configurar TUYA_CLIENT_ID, TUYA_SECRET y TUYA_DEVICE_ID en el archivo .env")


def convert_phase(raw_b64: str, phase_name: str):
    """Convierte valores de fase (base64) a voltajes reales."""
    decoded = base64.b64decode(raw_b64)

    val_0 = struct.unpack("<H", decoded[:2])[0] / 10 if len(decoded) >= 2 else 0
    val_2 = struct.unpack("<H", decoded[2:4])[0] / 10 if len(decoded) >= 4 else 0

    if 1 <= val_0 <= 300:
        return f"{val_0:.1f} V (offset0)"
    if 1 <= val_2 <= 300:
        return f"{val_2:.1f} V (offset2)"
    return f"{val_0:.1f} V (offset0) / {val_2:.1f} V (offset2, crudo)"


def convert_status(code: str, value):
    """Convierte cualquier estado crudo en unidades humanas."""
    # --- Valores numéricos clásicos ---
    if code == "cur_current":   # mA → A
        return f"{value / 1000:.2f} A"
    elif code == "cur_voltage":  # décimas de V → V
        return f"{value / 10:.1f} V"
    elif code == "cur_power":   # décimas de W → W
        return f"{value / 10:.1f} W"
    elif code in ("switch", "switch_1"):
        return "Encendido" if value else "Apagado"
    elif code == "fault":
        return "Sin fallos" if value == 0 else f"Fallo ({value})"

    # --- Energía ---
    if code in ("balance_energy", "charge_energy", "total_forward_energy"):
        # Suelen venir en Wh → convertimos a kWh
        return f"{value / 1000:.2f} kWh"

    # --- Fases ---
    if code in ("phase_a", "phase_b", "phase_c"):
        return convert_phase(value, code)

    # --- Alarmas ---
    if code.startswith("alarm_set"):
        try:
            decoded = base64.b64decode(value)
            raw_int = int.from_bytes(decoded, "little")
            return f"Alarm bits: {bin(raw_int)}"
        except Exception:
            return value

    # Otros valores se devuelven tal cual
    return value


def main():
    client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)

    print("🔑 Obteniendo token...")
    client.get_token()

    print(f"📡 Consultando estado del breaker {DEVICE_ID}...")
    resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}/status")
    data = resp.json()

    print("✅ Respuesta cruda:")
    print(data)

    if "result" in data:
        print("\n📊 Valores convertidos:")
        for item in data["result"]:
            readable = convert_status(item["code"], item["value"])
            print(f" - {item['code']}: {readable}")


if __name__ == "__main__":
    main()
