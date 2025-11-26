# 🍓 A12Bypass – iOS A12+ Activation Lock WiFi Bypass Tool

**Open-source bypass tool for iOS devices with A12 and newer chips**
Based on the original exploit by strawhatdev01 and the sandbox escape of `itunesstored` & `bookassetd` ([POC: downloads.28.sqlitedb sandbox escape](https://hanakim3945.github.io/posts/download28_sbx_escape/)).

> FORKED FROM: [https://github.com/strawhatdev01/A12Bypass](https://github.com/strawhatdev01/A12Bypass)

## 🚀 Main Features

- Full support for A12+ devices (iPhone XR and newer)
- Activation Lock bypass via WiFi (Hello screen)
- Telegram integration for real-time notifications
- Stealth mode operation (hidden window)
- Advanced anti-analysis and anti-debugging protection
- Automatic GUID/ECID extraction
- Multi-phase activation process with automatic retries
- Basic Server Side Implementation

## 🛡️ Integrated Security Measures

- Anti-debugging / anti-ptrace
- Proxy and VPN detection
- Code injection prevention
- API sniffing protection
- Runtime integrity verification

## 📋 Requirements

| Requirement                  | Details                                       |
| ---------------------------- | --------------------------------------------- |
| Operating System             | Windows 10/11                                 |
| Python                       | 3.11 (recommended)                            |
| Python Dependencies          | `PyQt5`, `pymobiledevice3`, `requests`        |
| Additional Libraries         | `libimobiledevice` (optional but recommended) |
| Device                       | iPhone/iPad with A12 or newer chip            |
| Device State                 | Activation Lock screen (Hello screen)         |
| Connection                   | USB + WiFi enabled on the device              |
| Additional Files (mandatory) | See **Required Files** section                |

## 🔧 Installation

```bash
git clone https://github.com/rhaulh/A12Bypass.git
cd A12Bypass
pip install -r requirements.txt
```

⚙️ **Required Additional Files (MANDATORY)**
The bypass requires the following files modified with the exact GUID/ECID of the target device:

- downloads.28.sqlitedb → modified database
- BLDatabaseManager → modified binary
- asset.epub → contains modified com.apple.MobileGestalt.plist
- Empty minimal plist file

All these files must be hosted on a server that customizes them and properly signed/edited for the specific device. NOTE. Added a Basic Implementation

- NEW MobileGestalt Files are needed to complete activation. Server Side has only a few for some iOS Builds
- SMALL UTILITY FOR REGISTERING SERIALS: [https://github.com/rhaulh/A12BypassAdminSerials](https://github.com/rhaulh/A12BypassAdminSerials)
  🎯 **Usage**

1. Connect the iOS device via USB
2. Make sure it is on the Activation screen (Hello screen) and connected to WiFi
3. Edit config.py with your data (see below)
4. Run:

```
python main.py
```

5. Follow the on-screen instructions
6. Receive real-time notifications through Telegram

⚙️ **Configuration (config.py)**

```
# Telegram (required for notifications)
TELEGRAM_BOT_TOKEN = "your_token_here"
TELEGRAM_CHAT_ID   = "your_chat_id_here"

# Server URLs (change if using your own backend)
BASE_API_URL      = "https://yourserver.com/api"
CHECK_MODEL_URL   = "/check_model"
CHECK_AUTH_URL    = "/check_auth"
CONTACT_URL       = "/contact"
```

📱 **Supported Devices**

- iPhone XR, XS, XS Max
- iPhone 11 / 11 Pro / 11 Pro Max
- iPhone 12 / 12 mini / 12 Pro / 12 Pro Max
- iPhone 13 / 13 mini / 13 Pro / 13 Pro Max
- iPhone 14 / 14 Plus / 14 Pro / 14 Pro Max
- iPhone 15 / 15 Plus / 15 Pro / 15 Pro Max
- iPhone 16 series
- iPads with A12, A12X, A12Z and later chips

⚠️ **Important Notes**

- The device must stay connected to WiFi during the entire process
- Multiple attempts and reboots may be necessary
- An internet connection is required (server communication)
- This method does not permanently remove iCloud; it only allows bypassing the activation screen

🔒 **Legal Disclaimer**

This project is strictly for:

- Educational purposes
- Security research
- Legitimate recovery of owned devices
- Authorized testing

Unauthorized use violates the laws of most countries (including the CFAA in the U.S. and equivalent EU laws).
The author is not responsible for misuse of this tool.

📞 **Support & Contact**

- Facebook: fb.com/rhaulh
- Telegram Channel (updates): coming soon

🏴‍☠️ **Credits**

- Original developer: strawhatdev01
- Sandbox escape exploit: hanakim3945
- Fork maintenance: rhaulh

**Tags:** iOS bypass, A12+ bypass, iCloud bypass, checkm8, Activation Lock, Hello bypass, pymobiledevice3

---

ESPAÑOL:

# 🍓 A12Bypass – Herramienta de bypass WiFi para Activation Lock en iOS A12+

**Herramienta open-source para saltar la pantalla de activación (Hello Screen) en dispositivos iOS con chip A12 y superiores**  
Basada en el desarrollo original de strawhatdev01 y la explotación de sandbox escape en `itunesstored` & `bookassetd`  
→ POC original: [downloads.28.sqlitedb sandbox escape](https://hanakim3945.github.io/posts/download28_sbx_escape/)

> FORKED FROM: https://github.com/strawhatdev01/A12Bypass

## 🚀 Características principales

- Soporte completo para dispositivos A12+ (iPhone XR en adelante)
- Bypass de Activation Lock manteniendo conexión WiFi activa
- Notificaciones en tiempo real vía Telegram
- Ejecución en modo sigilo (sin ventana visible)
- Protecciones avanzadas anti-análisis y anti-debug
- Extracción automática de GUID/ECID del dispositivo
- Proceso de activación en múltiples etapas con reintentos automáticos

## 🛡️ Medidas de seguridad integradas

- Anti-debugging y anti-ptrace
- Detección de proxies y VPNs
- Prevención de inyección de código
- Protección contra interceptación de APIs
- Verificación de integridad en tiempo de ejecución

## 📋 Requisitos del sistema

| Requisito              | Detalle                                       |
| ---------------------- | --------------------------------------------- |
| Sistema operativo      | Windows 10 / 11                               |
| Python                 | Versión 3.11 (recomendado)                    |
| Dependencias Python    | `PyQt5`, `pymobiledevice3`, `requests`        |
| Librerías adicionales  | `libimobiledevice` (recomendado)              |
| Dispositivo iOS        | Chip A12 o superior (iPhone XR y posteriores) |
| Estado del dispositivo | En pantalla de Activation Lock (Hello Screen) |
| Conexión               | USB al PC + WiFi activo en el dispositivo     |
| Archivos adicionales   | Obligatorios (ver sección más abajo)          |

## 🔧 Instalación

```bash
git clone https://github.com/rhaulh/A12Bypass.git
cd A12Bypass
pip install -r requirements.txt
⚙️ Archivos adicionales requeridos (OBLIGATORIOS)
El bypass solo funciona si tienes estos archivos personalizados con el ECID/GUID exacto del dispositivo:
	•	downloads.28.sqlitedb → base de datos modificada
	•	BLDatabaseManager → binario parcheado
	•	asset3.epub → contiene com.apple.MobileGestalt.plist modificado
	•	Archivo .plist mínimo vacío
Estos archivos deben estar en la carpeta raíz del proyecto y generados específicamente para cada dispositivo.
🎯 Instrucciones de uso
	1	Conecta el iPhone/iPad por USB
	2	Asegúrate de que esté en la pantalla de activación y conectado a WiFi
	3	Edita el archivo config.py con tus credenciales (ver abajo)
	4	Ejecuta el programa:
python main.py
	5	Sigue las instrucciones en pantalla
	6	Recibe actualizaciones en tiempo real por Telegram
⚙️ Configuración (config.py)
# Telegram — obligatorio para notificaciones
TELEGRAM_BOT_TOKEN = "tu_token_del_bot"
TELEGRAM_CHAT_ID   = "tu_chat_id"

# URLs del servidor backend (cambiar si usas uno propio)
BASE_API_URL      = "https://tuservidor.com/api"
CHECK_MODEL_URL   = "/check_model"
CHECK_AUTH_URL    = "/check_auth"
CONTACT_URL       = "/contact"
📱 Dispositivos compatibles
	•	iPhone XR, XS, XS Max
	•	iPhone 11 / 11 Pro / 11 Pro Max
	•	iPhone 12 / 12 mini / 12 Pro / 12 Pro Max
	•	iPhone 13 / 13 mini / 13 Pro / 13 Pro Max
	•	iPhone 14 / 14 Plus / 14 Pro / 14 Pro Max
	•	iPhone 15 / 15 Plus / 15 Pro / 15 Pro Max
	•	iPhone 16 / 16 Pro / 16 Pro Max
	•	Todos los iPad con chip A12, A12X, A12Z y superiores
⚠️ Notas importantes
	•	El dispositivo debe permanecer conectado a WiFi todo el tiempo
	•	Pueden necesitarse varios intentos y reinicios
	•	Requiere conexión a internet para comunicarse con el servidor
	•	Este es un bypass temporal: no elimina iCloud de forma permanente
🔒 Descargo de responsabilidad legal
Esta herramienta se publica exclusivamente con fines:
	•	Educativos
	•	Investigación de seguridad
	•	Recuperación legítima de dispositivos propios
	•	Pruebas autorizadas en entornos controlados
El uso no autorizado constituye un delito en la mayoría de países (incluyendo violación de la CFAA en EE.UU. y leyes equivalentes en Europa y Latinoamérica).El autor y colaboradores no se responsabilizan por el mal uso.
📞 Soporte y contacto
	•	Facebook: fb.com/rhaulh
	•	Telegram: próximamente canal oficial de actualizaciones
🏴‍☠️ Créditos
	•	Autor original: strawhatdev01
	•	Exploit sandbox escape: hanakim3945
	•	Mantenimiento y mejoras del fork: rhaulh
Tags: iOS bypass, A12+ bypass, iCloud bypass, Activation Lock, Hello Screen bypass, checkm8, pymobiledevice3
```
