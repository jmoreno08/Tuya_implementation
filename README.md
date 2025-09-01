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
│   └── demo.py
│
├── requirements.txt       # Dependencias (requests, python-dotenv)
└── README.md
```

---

## ⚙️ Instalación

1. Clona el repositorio o copia la carpeta `tuya_client/` en tu proyecto:

```bash
git clone https://github.com/tu_usuario/mi_proyecto.git
cd mi_proyecto
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

## ▶️ Uso

Ejecutar el demo:

```bash
python examples/demo.py
```

### Ejemplo de integración

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

# Obtener token
client.get_token()

# Consultar estado de un dispositivo
device_id = os.getenv("TUYA_DEVICE_ID")
resp = client.request("GET", f"/v1.0/devices/{device_id}/status")

print(resp.json())
```



