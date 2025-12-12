# Bookra1n iOS A12+ Activation Lock WiFi Bypass Tool

**Open-source bypass tool for iOS devices with A12 and newer chips**

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

## Requirements

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
git clone https://github.com/rhaulh/Bookra1n.git
cd Bookra1n
pip install -r requirements.txt
```

⚙️ **Required Additional Files (MANDATORY)**
The bypass requires the following files modified with the exact GUID/ECID of the target device:

- downloads.28.sqlitedb → modified database
- BLDatabaseManager → modified binary
- asset.epub → contains modified com.apple.MobileGestalt.plist
- Empty minimal plist file

All these files must be hosted on a server that customizes them and properly signed/edited for the specific device.

🎯 **Usage**

1. Connect the iOS device via USB
2. Make sure it is on the Activation screen (Hello screen) and connected to WiFi
3. Create a config.py with your data (see below)
4. Run:

```
python main.py
```

5. Follow the on-screen instructions
6. Receive real-time notifications through Telegram

⚙️ **Configuration (create and put config.py in root folder)**

```
# config.py
TELEGRAM_BOT_TOKEN = "BotToken"
TELEGRAM_CHAT_ID = "ChatID"

# Base URL
BASE_API_URL = "https://your-server.com/a12/"

# Enpoints
MODEL_URL = "endoint-models-check.php?model="
AUTH_URL = "endpoint-auth.php?serial="
SQL_URL = "endpoint-stage1.php?model="
COMPLETED_URL = "sendpoint-success-fallback.php?action=complete&serial="
# Endpoints with parameters

CHECK_MODEL_URL = f"{BASE_API_URL}{MODEL_URL}"
CHECK_AUTH_URL = f"{BASE_API_URL}{AUTH_URL}"
GET_SQLITE_URL = f"{BASE_API_URL}{SQL_URL}"
ACTIVATION_COMPLETED_URL = f"{BASE_API_URL}{COMPLETED_URL}"

CONTACT_URL = "https://t.me/telegram-user"

PAYLOAD = "downloads.28.sqlitedb"
PAYLOAD2 = "iTunes_Control/iTunes/iTunesMetadata.plist"
PAYLOAD2_1 = "Books/iTunesMetadata.plist"
PAYLOAD3 = "Books/asset.epub"
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
- Telegram Channel (updates): [https://t.me/Bookra1n](https://t.me/Bookra1n)

🏴‍☠️ **Credits**

- Original developer: strawhatdev01
- Sandbox escape exploit: hanakim3945
- Repo Owner: rhaulh
- GUI: ColorBlueTelegram
- Official Telegram @Bookra1n

> BASED In Repo: [https://github.com/strawhatdev01/A12Bypass](https://github.com/strawhatdev01/A12Bypass)
> Based on the original exploit by strawhatdev01 and the sandbox escape of `itunesstored` & `bookassetd` ([POC: downloads.28.sqlitedb sandbox escape](https://hanakim3945.github.io/posts/download28_sbx_escape/)).

**Tags:** iOS bypass, Bookra1n, A12+ bypass, iCloud bypass, checkm8, Activation Lock, Hello bypass, pymobiledevice3
