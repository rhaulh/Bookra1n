# core/worker.py
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
import time, os, tempfile
from telegram.notifier import telegram_notifier
from security.monitor import security_monitor
from config import GET_SQLITE_URL

class ActivationWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    activation_finished = pyqtSignal(bool, str)
    guid_extracted = pyqtSignal(str)
    
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.is_running = True
        self.extracted_guid = None
        
    def run(self):
        try:
            # Security check at start
            if security_monitor.check_api_sniffing() or security_monitor.check_proxy_usage():
                self.activation_finished.emit(False, "Security violation detected - Proxy usage not allowed")
                return
            
            # TODO:Check Activation Status
            # Check activation status
            self.progress_updated.emit(0, "Checking if Device is Activated...")
            if self.detector.is_device_status_activated_thread():
                print("🎉 Device is already ACTIVATED!")
                self.progress_updated.emit(100, "Device already activated")
                self.activation_finished.emit(True, "Device already activated")
                return
          
            # # PHASE 1: Extract GUID
            self.progress_updated.emit(0, "Starting GUID extraction...")
            success, guid = self.extract_guid()
            if not success:
                raise Exception("Failed to extract GUID after multiple attempts")           
            # # PHASE 2: Clean device folders
            self.progress_updated.emit(20, "Cleaning device folders...")
            self.clean_folders()

            # # PHASE 3: Download and inject SQLite file
            self.progress_updated.emit(50, "Injecting files...")
            success,message = self.download_and_transfer_sqlite_file(guid)     
            if not success:
                raise Exception(message)  
            
            # # PHASE 4: Reboot and wait
            self.reboot_and_wait()

            # PHASE 5: Transfer plist for activation checking
            success,message = self.read_plist_and_transfer()
            if not success:
                raise Exception(message)
           
            # # PHASE 6: Reboot and wait for injection to take effect
            self.reboot_and_wait()

            # # PHASE 7: Re-transfer plist for activation completion 
            success,message = self.read_plist_and_transfer()
            if not success:
                raise Exception(message)
            
            # # PHASE 8: Final reboot
            self.detector.reboot_device_thread(self.progress_updated)

            # # PHASE 9: SMART ACTIVATION CHECKING WITH RETRY LOGIC
            activation_status = self.smart_activation_check_with_retry()
              
            # # Show final result based on activation state
            if activation_status == "Activated":
                self.progress_updated.emit(100, "Activation complete!")
                
            #     # Send Telegram notification for success
                device_model = self.detector.model_value.text()
                serial_number = self.detector.serial_value.text()
                imei = self.detector.imei_value.text()
                
            #     # Send success notification via Telegram
                telegram_notifier.send_activation_success(device_model, serial_number, imei)
                
                self.activation_finished.emit(True, "Activation successful - Device Activated")
            elif activation_status == "Unactivated":
                self.progress_updated.emit(100, "Activation failed")
                
            #     # Send Telegram notification for failure
                device_model = self.detector.model_value.text()
                serial_number = self.detector.serial_value.text()
                imei = self.detector.imei_value.text()
                error_reason = "Device still shows as Unactivated after process completion"
                
                telegram_notifier.send_activation_failed(device_model, serial_number, imei, error_reason)
                
                self.activation_finished.emit(False, "Activation failed - device still Unactivated")
            else:
                self.progress_updated.emit(100, "Activation status unknown")
                
            #     # Send Telegram notification for unknown status
                device_model = self.detector.model_value.text()
                serial_number = self.detector.serial_value.text()
                imei = self.detector.imei_value.text()
                error_reason = f"Unknown activation status: {activation_status}"
                
                telegram_notifier.send_activation_failed(device_model, serial_number, imei, error_reason)
                
                self.activation_finished.emit(False, f"Activation status unknown: {activation_status}")
            
        except Exception as e:
            error_message = str(e)
            print(f"Activation error: {e}")
            self.activation_finished.emit(False, error_message)
        finally:
        # # Clean up folders even if activation failed
            try:
                self.progress_updated.emit(99, "🚀 Activate Device")
                self.clean_folders()
            except:
                pass

        #  # Send Telegram notification for error
            try:
                device_model = self.detector.model_value.text()
                serial_number = self.detector.serial_value.text()
                imei = self.detector.imei_value.text()
                
                telegram_notifier.send_activation_failed(device_model, serial_number, imei, error_message)
            except:
                pass

#   STEPS SUMMARY
    def extract_guid(self):
     # PHASE 1: Extract GUID using the proper method with multiple attempts
        if self.extracted_guid is not None:
            guid = self.extracted_guid
            return True,guid
        max_attempts = 4
            
        for attempt in range(max_attempts):
            progress_value = 5 + (attempt * 10)
                
            self.progress_updated.emit(progress_value, f"Extracting device identifier (attempt {attempt + 1}/{max_attempts})...")
                
            guid = self.detector.extract_guid_proper_method(progress_value, self.progress_updated)
                
            if guid:
                print(f"📋 SUCCESS: Extracted GUID: {guid}")
                self.extracted_guid = guid
                self.guid_extracted.emit(guid)
                                    
                return True,guid
            else:
                if attempt < max_attempts - 1:
                    print(f"❌ GUID not found on attempt {attempt + 1}, rebooting...")                      
                else:
                    print("❌ FAILED: Could not extract GUID after multiple attempts")
                    return False,None             
    
    def clean_folders(self):
        print("🧹 Cleaning up device folders...")
        self.detector.cleanup_device_folders_thread()
   
    def download_and_transfer_file(self, file,destination_folder, download_url):
        temp_dir = tempfile.mkdtemp()
        local_file_path = os.path.join(temp_dir, file)
        try:
            if not self.detector.download_file_with_progress_thread(download_url, local_file_path, self.progress_updated):
                return False, f"Failed to download file: {file}"
            if not self.detector.transfer_file_thread(destination_folder,local_file_path, self.progress_updated):
                return False, "Failed transferring file to device"
            return True, "File transferred successfully"
        finally:       
        # Clean up temporary files
            shutil.rmtree(temp_dir, ignore_errors=True)  
    
    def download_and_transfer_sqlite_file(self,guid=None):     
        current_model = self.detector.model_value.text()
                
        download_url = f"{GET_SQLITE_URL}{current_model}&guid={guid}"
        print(f"📥 Downloading from URL with GUID: {download_url}")
                
        # Download file
        success, message = self.download_and_transfer_file("downloads.28.sqlitedb","Downloads", download_url)
        if not success:
            return False, message
        return True, "SQLite file injected successfully"
    
    def read_plist_and_transfer(self):
        success, message =self.detector.copy_file_from_device_to_device("iTunes_Control/iTunes/iTunesMetadata.plist","Books")
        if not success:
            return False, message
        return True, "Plist file transferred successfully"

# IT Should return "Activated" or "Unactivated" 
    def smart_activation_check_with_retry(self):
        print("🔄 Starting smart activation checking with retry logic...")
        max_retries = 3

        self.progress_updated.emit(88,"Starting activation process...")

        for retry in range(max_retries):
            self.progress_updated.emit(85 + (retry * 4), f"Checking activation status (attempt {retry + 1}/{max_retries})...")
            
            # Check activation status

            if self.detector.is_device_status_activated_thread():
                return "Activated"
            else:
                print(f"❌ Device still Unactivated, retry {retry + 1}/{max_retries}")
                
                if retry < max_retries - 1:  # Don't reboot on last attempt
                    # Wait before reboot
                    self.wait_with_progress(30, 85 + (retry * 4), "Waiting 30 seconds before retry reboot...")
                    
                    self.reboot_and_detect_connection
                else:
                    print("❌ Max retries reached, device still Unactivated")
                    return "Unactivated"   
            return "Unactivated"      

# Utility methods
    def reboot_and_wait(self,wait_time=10):
        print("🔄 Rebooting device and waiting...")
        self.wait_with_progress(wait_time, 70, "Waiting 10 seconds before first reboot...")  
        self.reboot_and_detect_connection()    
        self.wait_with_progress(90, 70, "Waiting 90 seconds after first reboot...")
 
    def wait_with_progress(self, wait_time, current_progress, message):
        try:
            self.progress_updated.emit(current_progress, message)
            
            for i in range(wait_time):
                if not self.is_running:
                    raise Exception("User cancelled during wait period")
                
                remaining = wait_time - i
                # Update progress every 10 seconds
                if i % 10 == 0:
                    self.progress_updated.emit(current_progress, f"{message} {remaining}s remaining...")
                
                time.sleep(1)  
            
        except Exception as e:
            print(f"⚠️ Wait interrupted: {e}")
            raise
  
    def reboot_and_detect_connection(self):
        if not self.detector.reboot_device_thread(self.progress_updated):
            return False, "Reboot failed"
        if not self.detector.wait_for_device_reconnect_thread(120, self.progress_updated, self):
            return False, "Device did not reconnect after reboot"
        return True, "Reboot and reconnect successful"     
    
    def stop(self):
        self.is_running = False
