# core/worker.py
import shutil
import logging
from PyQt5.QtCore import QThread
import time, os, tempfile
from telegram.notifier import telegram_notifier
from core.api import API
from core.guid_service import GuidService
from config import GET_SQLITE_URL,PAYLOAD,PAYLOAD2,PAYLOAD3
from core.garbage_colector import GarbageCollector
from core.device_commands import DeviceCommands
from core.afc_service import AFCService
from security.monitors import SecurityMonitor

class ActivationWorker(QThread, DeviceCommands):
    logger = logging.getLogger("bookra1n")
    security_monitor = SecurityMonitor.getMonitor()

    garbage_collector = GarbageCollector()
    guid_service = GuidService()
    afc = AFCService()

    progress_value = 0
    error_message = None

    def __init__(self, detector):
        super().__init__()
        self.activation_in_progress = detector.activation_in_progress
        self.device = detector.current_device
        self.progress_updated = detector.update_progress
        self.waiting_for_reboot = detector.waiting_for_reboot
        self.activation_finished = detector.activation_finished

    def run(self):
        try:

            if self.security_monitor.check_api_sniffing() or self.security_monitor.check_proxy_usage():
                self._finish(False, "Security violation detected - Proxy usage not allowed")
                return

            self._update_progress(0, "Checking if Device is Activated...")

            self._ensure_activation_not_stopped()

            activation_success = self.smart_activation_check_with_retry()

            if activation_success:
                self._update_progress(100, "Activation complete!")
                try:
                    telegram_notifier.send_activation_success(
                        self.device.model,
                        self.device.serial,
                        self.device.imei
                    )
                except Exception as e:
                    self.logger.warning(f"Telegram success notify failed: {e}")

                try:
                    API.send_complete_status(
                        self.device.serial,
                        self.device.ios,
                        self.device.model
                    )
                except Exception as e:
                    self.logger.warning(f"API send_complete_status failed: {e}")

                self._finish(True, "Device Successfully Activated")
            else:
                self._fail("Activation failed")

        except Exception as e:
            self.error_message = str(e)
            self.logger.error(f"Activation error: {e}")
            self._finish(False, self.error_message)

        finally:
            try:
                self._update_progress(99, "Cleaning up...")
                self.garbage_collector.cleanup_device_folders()
            except Exception as e:
                self.logger.warning(f"Cleanup failed: {e}")

            if self.error_message:
                try:
                    telegram_notifier.send_activation_failed(
                        self.device.model,
                        self.device.serial,
                        self.device.imei,
                        self.error_message
                    )
                except Exception as e:
                    self.logger.error(f"Failed to send Telegram notification: {e}")


    def _finish(self, success: bool, message: str):
        self.activation_finished.emit(success, message)

    def _fail(self, reason: str):
        self._update_progress(100, reason)
        try:
            telegram_notifier.send_activation_failed(
                self.device.model,
                self.device.serial,
                self.device.imei,
                reason
            )
        except Exception as e:
            self.logger.warning(f"Telegram failure notify failed: {e}")
        self._finish(False, reason)

    def _ensure_activation_not_stopped(self):

        if not self.activation_in_progress:
            self.logger.info("Process stopped by user or Disconnected device")
            self._fail("Activation failed")

    def _update_progress(self, value: int, message: str = "") -> int:
        # Clamp entre 0 y 100 para seguridad
        if value < 0:
            value = 0
        if value > 100:
            value = 100
        self.progress_value = int(value)
        try:
            self.progress_updated.emit(self.progress_value, message)
        except Exception:
            # Proteger contra callbacks inválidos
            self.logger.debug("Progress emit failed (callback issue)")
        return self.progress_value

    def add_progress(self, value: int, message: str = None) -> int:
        self.progress_value = int(self.progress_value + value)
        if self.progress_value > 100:
            self.progress_value = 100
        if message:
            try:
                self.progress_updated.emit(self.progress_value, message)
            except Exception:
                self.logger.debug("Progress emit failed (callback issue)")
        return self.progress_value

    def set_progress_value(self, value: int) -> int:
        """Setea y retorna el progreso (compatibilidad con llamadas previas)."""
        return self._update_progress(int(value), "")


    def smart_activation_check_with_retry(self) -> bool:
        self.logger.info("Starting Smart Activation with retry")

        if not self.device.guid:
            ok, guid = self.extract_guid()
            if not ok:
                return False
            self.device.guid = guid

        ok, msg = self.injection_stage()
        if not ok:
            if msg == "wifi":
                self.logger.debug("Device is not connected to Wifi")
            else:
                self.logger.error(f"Injection has failed: {msg}")
            return False

        self.logger.info("Injection completed successfully")

        self._update_progress(80, "Verifying activation status...")
  
        return self.check_activation_status()
    

    def extract_guid(self):
        max_attempts = 6
        self.add_progress(10, "Starting GUID extraction...")

        for attempt in range(max_attempts):
            self._ensure_activation_not_stopped()
            self.logger.info(f"Extracting device identifier (attempt {attempt + 1}/{max_attempts})...")

            self.logger.debug("Starting GUID extraction process...")         
        
            if not self.reboot_and_detect_connection(self.waiting_for_reboot):
                return False, None

            extracted_guid = self.guid_service.extract_guid_proper_method(
                self.device.udid,
                self.progress_value,
                self.progress_updated
            )

            if extracted_guid:
                self.logger.debug(f"🎯 FOUND GUID: {extracted_guid}")
                return True, extracted_guid
                
            self.logger.warning(f"GUID not found on attempt {attempt + 1}")
            time.sleep(1)

        self.logger.error("FAILED: Could not extract GUID after multiple attempts")
        return False, None


    def injection_stage(self):
        try:
            self.logger.info("Preparing file injection...")
            self._ensure_activation_not_stopped()

            self.add_progress(10, "Cleaning device folders...")
            self.garbage_collector.cleanup_device_folders()

            self.add_progress(10, "Injecting files...")
            success, message = self.download_and_transfer_file("Downloads")
            if not success:
                return False, message

            if not self.reboot_and_detect_connection(self.waiting_for_reboot):
                return False, "Reboot Failed"
            
            success, status = self.check_file_injection(PAYLOAD2, 200)
            if not success:
                return False, "wifi"

            success, message = self.read_plist_and_transfer()
            if not success:
                return False, message
            
            self.wait_with_progress(30)

            if not self.reboot_and_detect_connection(self.waiting_for_reboot):
                return False, "Reboot Failed"

            self.add_progress(10, "Closing exploit...")
            self.logger.debug("Patching activation files")

            success, status = self.check_file_injection(PAYLOAD3, 3000)
            if not success:
                return False, status

            if not self.reboot_and_detect_connection(self.waiting_for_reboot):
                return False, "Reboot Failed"

            return True, "Injection stage completed"

        except Exception as e:
            self.logger.debug(f"Injection Stage error: {e}")
            return False, str(e)


    def download_and_transfer_file(self, destination_folder):
        self.logger.debug("Starting download and transfer process")
        self._ensure_activation_not_stopped()

        # Construir URL
        download_url = f"{GET_SQLITE_URL}{self.device.model}&ios={self.device.ios}&guid={self.device.guid}"
        temp_dir = None

        try:
            self.logger.debug(f"Downloading and injecting file")
            temp_dir = tempfile.mkdtemp()
            local_file_path = os.path.join(temp_dir, PAYLOAD)

            ok = API.download_file_with_progress(
                download_url,
                local_file_path,
                self.progress_value,
                self.progress_updated
            )

            if not ok:
                error_msg = "Failed to download file"
                self.logger.error(error_msg)
                return False, error_msg

            self._ensure_activation_not_stopped()

            self.logger.debug("Transferring file to device via AFC")
            if not self.afc.transfer_local_file_to_device(destination_folder, local_file_path):
                error_msg = "Failed transferring file to device"
                self.logger.error(error_msg)
                return False, error_msg

            self.logger.debug("File downloaded and transferred successfully")
            return True, "File injected successfully"

        except Exception as e:
            error_msg = f"Error during download and transfer: {e}"
            self.logger.error(error_msg)
            return False, error_msg

        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    self.logger.warning(f"Failed to clean up temp directory: {e}")

    def read_plist_and_transfer(self):
        self._ensure_activation_not_stopped()
        try:
            self.logger.debug("Reading plist and transferring to device...")
            success, message = self.afc.copy_file_from_device_to_device(PAYLOAD2, "Books")
            if not success:
                return False, message
            
            return True, "Payload injected successfully"
        except Exception as e:
            self.logger.error(f"read_plist_and_transfer error: {e}")
            return False, str(e)

    def check_file_injection(self, file, minimum_size, timeout=120):
        self.logger.debug("Waiting for injection to start...")
        try:
            for elapsed in range(timeout):
                self._ensure_activation_not_stopped()

                if self.afc.check_if_file_injection_completed(file, minimum_size):
                    self.logger.debug(f"Injection started after {elapsed} seconds. Waiting for completion...")
                    return True, "Injection Init"

                time.sleep(1)

            self.logger.error(f"Injection failed to start within {timeout} seconds")
            return False, f"Injection never started within {timeout} seconds"

        except Exception as e:
            self.logger.error(f"Error injecting file: {file} - {e}")
            return False, f"Error injecting file: {file} ({e})"

    def wait_with_progress(self, wait_time, message=""):
        try:
            self.add_progress(5, message)
            for i in range(wait_time):
                self._ensure_activation_not_stopped()
                remaining = wait_time - i
                if i % 10 == 0:
                    self.progress_updated.emit(self.progress_value, f"{message} {remaining}s remaining...")
                time.sleep(1)
        except Exception as e:
            self.logger.debug(f"Wait interrupted: {e}")
            raise


    def stop(self):
        self.activation_in_progress = False
