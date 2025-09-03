import os
import sys
import base64
import struct
from dotenv import load_dotenv

# 👇 permitir importar tuya_client/ sin instalar como paquete
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tuya_client import TuyaClient

# Cargar credenciales
load_dotenv()
CLIENT_ID = os.getenv("TUYA_CLIENT_ID")
SECRET = os.getenv("TUYA_SECRET")
BASE_URL = os.getenv("TUYA_BASE_URL", "https://openapi.tuyaus.com")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")  # ID del breaker en Tuya IoT

if not CLIENT_ID or not SECRET or not DEVICE_ID:
    raise RuntimeError("⚠️ Debes configurar TUYA_CLIENT_ID, TUYA_SECRET y TUYA_DEVICE_ID en el archivo .env")

# --- Configuración de modo de fases ---
# "auto"  -> detecta automáticamente (100–300 V)
# "120v"  -> prioriza rango 100–160 V
# "220v"  -> prioriza rango 200–260 V
PHASE_MODE = os.getenv("PHASE_MODE", "auto").lower()


def decode_phase_voltage(raw_b64: str, phase: str):
    """Decodifica base64 de voltaje probando divisores y selecciona según PHASE_MODE."""
    try:
        decoded = base64.b64decode(raw_b64)
        if len(decoded) < 2:
            return None

        raw_val = struct.unpack("<H", decoded[:2])[0]

        # Divisores típicos observados en breakers Tuya
        scales = [10, 100, 256, 1000, 114.3, 2560]
        candidates = [(raw_val / s, s) for s in scales]

        # --- Selección según PHASE_MODE ---
        if PHASE_MODE == "120v":
            # Forzar que sólo se acepten valores entre 100 y 160 V
            in_range = [(v, s) for (v, s) in candidates if 100 <= v <= 160]
            if in_range:
                chosen = min(in_range, key=lambda t: abs(120 - t[0]))
                return round(chosen[0], 1)
            # Si no hay valor válido, devolver ruido (fase desconectada)
            return round(raw_val / 2560, 1)

        if PHASE_MODE == "220v":
            in_range = [(v, s) for (v, s) in candidates if 200 <= v <= 260]
            if in_range:
                chosen = min(in_range, key=lambda t: abs(220 - t[0]))
                return round(chosen[0], 1)
            return round(raw_val / 2560, 1)

        # AUTO o fallback → valores entre 100–300 V
        in_range = [(v, s) for (v, s) in candidates if 100 <= v <= 300]
        if in_range:
            chosen = min(in_range, key=lambda t: abs(200 - t[0]))
            return round(chosen[0], 1)

        # Si nada cuadra → ruido (fase desconectada)
        v_min, _ = min(candidates, key=lambda t: t[0])
        return round(v_min, 1)

    except Exception:
        return None


def convert_status(code: str, value):
    """Convierte algunos códigos conocidos en unidades humanas."""
    if code in ("phase_a", "phase_b", "phase_c") and isinstance(value, str):
        return decode_phase_voltage(value, code)

    if code == "cur_voltage":
        return f"{value/10:.1f} V"
    if code == "cur_current":
        return f"{value/1000:.2f} A"
    if code == "cur_power":
        return f"{value/10:.1f} W"
    if code in ("balance_energy", "charge_energy", "total_forward_energy"):
        return f"{value/1000:.2f} kWh"
    if code in ("switch", "switch_1"):
        return "Encendido" if value else "Apagado"
    if code == "fault":
        return "Sin fallos" if value == 0 else f"Fallo ({value})"
    if code == "temp_current":
        return f"{value/10:.1f} °C"  # suele estar en décimas de °C

    return value


def main():
    client = TuyaClient(CLIENT_ID, SECRET, BASE_URL)

    print("🔑 Obteniendo token...")
    client.get_token()

    print(f"📡 Descargando información del breaker {DEVICE_ID}...")
    resp = client.request("GET", f"/v1.0/devices/{DEVICE_ID}/status")
    data = resp.json()

    print("✅ Respuesta completa:")
    print(data)

    phases = {}

    if "result" in data:
        print("\n📊 Estados convertidos:")
        for item in data["result"]:
            readable = convert_status(item["code"], item["value"])
            print(f" - {item['code']}: {readable}")

            if item["code"] in ("phase_a", "phase_b", "phase_c"):
                phases[item["code"]] = readable

    # --- Resumen de tensiones ---
    if phases:
        print("\n⚡ Resumen de tensiones:")
        for phase, v in phases.items():
            if isinstance(v, (int, float)) and v < 20:
                print(f"  {phase.upper()} = {v} V (fase desconectada)")
            else:
                print(f"  {phase.upper()} = {v} V")


if __name__ == "__main__":
    main()