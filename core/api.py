# core/api.py
import requests
from security.monitor import security_monitor
from config import (
    CHECK_MODEL_URL, CHECK_AUTH_URL,
    GUID_OPERATIONS_URL, ACTIVATION_COMPLETED_URL
)
from utils.device_models import device_models, get_model_from_product_type
from utils.helpers import get_random_hacking_text

class API:
    _session = requests.Session()
    _session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    })

    @classmethod
    def _get(cls, url, timeout=15):
        """Petición segura centralizada"""
        if security_monitor.check_proxy_usage():
            raise Exception("Proxy detected - operation blocked")
        return cls._session.get(url, timeout=timeout, verify=True)

    # === URLs ===
    @classmethod
    def get_api_url(cls, model):
        return f"{CHECK_MODEL_URL}{model}"

    @classmethod
    def get_authorization_url(cls, model, serial):
        return f"{CHECK_AUTH_URL}{model}&serial={serial}"

    @classmethod
    def get_guid_api_url(cls, serial):
        return f"{GUID_OPERATIONS_URL}{serial}&action=get_guid"

    @classmethod
    def get_stored_guid_url(cls, serial, guid):
        return f"{GUID_OPERATIONS_URL}{serial}&guid={guid}&action=store_guid"

    @classmethod
    def get_completed_api_url(cls, serial):
        return f"{ACTIVATION_COMPLETED_URL}{serial}"

    @classmethod
    def fetch_device_model(cls, product_type):
        try:
            if not product_type or product_type == "N/A":
                return "N/A"

            # Cache en memoria
            if product_type in device_models:
                return device_models[product_type]

            # Utils local
            success, model = get_model_from_product_type(product_type)
            if success:
                device_models[product_type] = model
                return model

            # API
            url = cls.get_api_url(product_type)
            response = cls._get(url)

            model_name = "Unknown Model"
            if response.status_code == 200:
                data = response.json()
                model_name = data.get("model_name", "").strip()
            elif response.status_code == 404:
                model_name = response.text.strip()

            if model_name and model_name not in ("Unknown", "Unknown Model", ""):
                device_models[product_type] = model_name
                return model_name

            return "Unknown Model"

        except Exception as e:
            print(f"API.fetch_device_model error: {e}")
            return "API Error"

    @classmethod
    def check_authorization(cls, model, serial):
        try:
            if not model or not serial or model in ("N/A", "API Error", "Unknown Model"):
                return "error", None

            url = cls.get_authorization_url(model, serial)
            response = cls._get(url)
            data = response.json() if "json" in response.headers.get("content-type", "") else {}

            if response.status_code == 200:
                return "authorized", data.get("stored_guid")
            elif response.status_code == 401:
                return "not_authorized", data.get("stored_guid")
            else:
                return "error", None

        except Exception:
            return "error", None

    @classmethod
    def fetch_guid(cls, serial):
        try:
            if not serial:
                return False, None

            url = cls.get_guid_api_url(serial)
            response = cls._get(url)

            if response.status_code == 200:
                data = response.json()
                guid = data.get("message")
                if guid and len(guid) == 36:
                    print(f"GUID found in server: {guid}")
                    return True, guid
            return False, None

        except Exception as e:
            print(f"Error fetch_guid_from_api: {e}")
            return False, None

    @classmethod
    def send_guid(cls, serial, guid):
        try:
            if not serial or not guid:
                return False

            url = cls.get_stored_guid_url(serial, guid)
            response = cls._get(url)

            if response.status_code == 200:
                print(f"GUID cached in server: {guid}")
                return True
            else:
                print(f"Error caching GUID: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error send_guid_to_api: {e}")
            return False

    @classmethod
    def send_complete_status(cls, serial):
        try:
            if not serial:
                return False
            url = cls.get_completed_api_url(serial)
            response = cls._get(url)
            return response.status_code == 200
        except:
            return False
        
    # TODO: connect signals
    def download_file_with_progress(self, url, local_path, progress_signal):
        try:
            # Security check for proxy usage
            if security_monitor.check_proxy_usage():
                raise Exception("Proxy usage detected - Operation not allowed")
                
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            progress_signal.emit(progress, get_random_hacking_text())
            
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False