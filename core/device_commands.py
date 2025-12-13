import os
import time
import logging
from utils.helpers import run_subprocess_no_console, get_lib_path,get_random_hacking_text

logger = logging.getLogger("bookra1n")
class DeviceCommands:
    def __init__(self):
        pass

    def have_device_full_connection(self):
        try:
            ideviceinfo_path = get_lib_path('ideviceinfo.exe')
            if os.path.exists(ideviceinfo_path):
                result = run_subprocess_no_console([ideviceinfo_path], timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    return True, result.stdout
            return False, None
        except:
            return False, None
   
    def have_device_limited_connection(self):
        try:
            idevice_id_path = get_lib_path('idevice_id.exe')
    
            if os.path.exists(idevice_id_path):
                result = run_subprocess_no_console([idevice_id_path, "-l"], timeout=8)
                if result and result.returncode == 0 and result.stdout.strip():
                    return True,result.stdout
            return False,None
        except:
            return False, None
        
    def wait_device_reconnect_sync(self, timeout=120):
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                connected, stdrout = self.have_device_full_connection()
                if connected:
                    logger.info("Device reconnect successful")
                    return True
                time.sleep(5)
            
            logger.error("Device did not reconnect within timeout period")
            return False
        except Exception as e:
            logger.critical(f"Wait for reconnect error: {e}")
            return False
    
    def reboot_device_sync(self):
        try:
            ios_path = get_lib_path('ios.exe')
            if not os.path.exists(ios_path):
                logger.debug("ios.exe not found in libs folder")
                return False
            
            cmd = [ios_path, 'reboot']
            result = run_subprocess_no_console(cmd, timeout=30)
            
            if result and result.returncode == 0:
                logger.info("Device reboot command sent successfully")
                return True
            else:
                logger.critical(f"Reboot command failed")
                return True
                
        except Exception as e:
            logger.error(f"Reboot error: {e}")
            return True

    def reboot_and_detect_connection(self, fallback=None):
        if fallback:
            fallback.emit(True)
        if self.reboot_device_sync() and self.wait_device_reconnect_sync(120):
            if fallback:
                fallback.emit(False)
            return True
        if fallback:
                fallback.emit(False)
        return False    
    
    def check_activation_status(self):
        try:
            logger.debug("Checking device activation status...")
            
            ideviceinfo_path = get_lib_path('ideviceinfo.exe')
            
            if not os.path.exists(ideviceinfo_path):
                logger.debug("ideviceinfo.exe not found")
                return False
            
            result = run_subprocess_no_console([ideviceinfo_path, '-k', 'ActivationState'], timeout=15)
            
            if result and result.returncode == 0:
                activation_state = result.stdout.strip()
                return activation_state == "Activated"
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking activation status: {e}")
            return False
