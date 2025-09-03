# 🔌 Tuya Client (Python)

Cliente ligero en Python para interactuar con la **Tuya Cloud API**.  
Maneja automáticamente el `access_token`, firma las peticiones con **HMAC-SHA256** y expone una clase simple para integrarla en tus proyectos.

---

## 📂 Estructura del proyecto

```plaintext
Tuya_Implementation/
│
├── tuya_client/           # Cliente Tuya
│   ├── __init__.py
│   └── client.py          # Clase TuyaClient
│
├── examples/              # Ejemplos de uso
│   ├── demo.py
│   ├── demo_device_info.py
│   ├── demo_balance_switch.py
│   ├── demo_balance_energy.py
│   ├── demo_breaker_status.py
│   ├── demo_breaker_status_converted.py
│   └── demo_switch_interactive.py
│
├── requirements.txt       # Dependencias (requests, python-dotenv)
└── README.md
```

---

## ⚙️ Instalación

1. Clona el repositorio o copia la carpeta `tuya_client/` en tu proyecto:

```bash
git clone https://github.com/jmoreno08/Tuya_implementation.git
cd Tuya_implementation
```

2. Crea y activa un entorno virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / MacOS
source .venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuración de credenciales

Crea un archivo `.env` en la raíz con tus credenciales de la **Tuya IoT Platform**:

```env
TUYA_CLIENT_ID=your_client_id
TUYA_SECRET=your_secret
TUYA_BASE_URL=https://openapi.tuyaus.com
TUYA_DEVICE_ID=your_device_id
```

### Endpoints regionales
- **US** → `https://openapi.tuyaus.com`  

---

## ▶️ Uso de la clase `TuyaClient`

La clase principal para interactuar con la API es `TuyaClient`, ubicada en `tuya_client/client.py`.

### Ejemplo básico

```python
import os
from dotenv import load_dotenv
from tuya_client import TuyaClient

# Cargar variables de entorno
load_dotenv()

client = TuyaClient(
    os.getenv("TUYA_CLIENT_ID"),
    os.getenv("TUYA_SECRET"),
    os.getenv("TUYA_BASE_URL", "https://openapi.tuyaus.com")
)

# Obtener token de autenticación
client.get_token()

# Consultar estado de un dispositivo
device_id = os.getenv("TUYA_DEVICE_ID")
resp = client.request("GET", f"/v1.0/devices/{device_id}/status")

print(resp.json())
```

### Ejemplos avanzados

En la carpeta [`examples/`](examples/) encontrarás scripts para distintos escenarios:

- **demo.py**: Ejemplo básico de autenticación y consulta de estado.
- **demo_device_info.py**: Obtiene información detallada del dispositivo.
- **demo_balance_switch.py**: Consulta el estado de interruptores.
- **demo_balance_energy.py**: Obtiene datos de consumo energético.
- **demo_breaker_status.py** y **demo_breaker_status_converted.py**: Estado de breakers y conversión de datos.
- **demo_switch_interactive.py**: Control interactivo de interruptores.

Ejecuta cualquier ejemplo así:

```bash
python examples/demo_device_info.py
```

---

## 📚 Documentación rápida de la clase

- **Inicialización**  
  `TuyaClient(client_id, secret, base_url)`
- **Obtener token**  
  `client.get_token()`
- **Realizar petición**  
  `client.request(method, endpoint, params=None, body=None)`

Consulta el código fuente en [`tuya_client/client.py`](tuya_client/client.py) para más detalles.

---

## 🛠️ Soporte

¿Dudas o sugerencias? Abre un issue en el repositorio o contacta al autor.



