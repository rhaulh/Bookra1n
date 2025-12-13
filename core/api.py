# core/api.py
import os
import requests
import logging
from config import (
    CHECK_MODEL_URL, CHECK_AUTH_URL,
    ACTIVATION_COMPLETED_URL
)
from utils.helpers import get_random_hacking_text
from security.monitors import SecurityMonitor

logger = logging.getLogger("bookra1n")
security_monitor = SecurityMonitor.getMonitor()

class API:
    _session = requests.Session()
    _session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    })

    @classmethod
    def _get(cls, url, timeout=15,**kwargs):
        if security_monitor.check_proxy_usage():
            raise RuntimeError("Proxy detected")
        try:
            return cls._session.get(
                url,
                timeout=timeout,
                verify=True,
                **kwargs
            )
        except requests.RequestException as e:
            logger.error(f"HTTP GET request failed: {e}")
            raise

    @classmethod
    def get_check_supported_devices_url(cls, model,ios):
        return f"{CHECK_MODEL_URL}{model}&ios={ios}"

    @classmethod
    def get_authorization_url(cls,serial):
        return f"{CHECK_AUTH_URL}{serial}"

    @classmethod
    def get_completed_api_url(cls, serial,ios,model):
        return f"{ACTIVATION_COMPLETED_URL}{serial}&model={model}&ios={ios}"

    @classmethod
    def check_supported_model(cls, product_type,ios):
        try:
            url = cls.get_check_supported_devices_url(product_type,ios)
            response = cls._get(url)
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            return False

        except Exception as e:
            logger.debug(f"API.check_supported_model error: {e}")
            return False

    @classmethod
    def check_authorization(cls, serial):
        try:   
            url = cls.get_authorization_url(serial)
            response = cls._get(url)
            data = response.json() if "json" in response.headers.get("content-type", "") else {}

            if response.status_code == 200:
                return True,"authorized"
            elif response.status_code == 401:
                return False,"not_authorized"
            else:
                return False,""

        except Exception:
            return False,""

    @classmethod
    def send_complete_status(cls, serial,ios,model):
        try:
            if not serial:
                return False
            url = cls.get_completed_api_url(serial,ios,model)
            response = cls._get(url)
            return response.status_code == 200
        except:
            return False
    
    @classmethod       
    def download_file_with_progress(
        cls,
        url,
        local_path,
        progress_value=0,
        progress_signal=None
    ):
        response = None
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            response = cls._get(
                url,
                stream=True,
                timeout=(5, 30)
            )

            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(local_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue

                    file.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        progress = int((downloaded_size / total_size) * 10)

                        if progress_signal:
                            try:
                                progress_signal.emit(
                                    progress_value + progress,
                                    get_random_hacking_text()
                                )
                            except Exception:
                                pass

            if total_size > 0 and downloaded_size < total_size:
                logger.debug("Warning: partial download detected")
                return False

            return True

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False

        finally:
            if response is not None:
                response.close()
