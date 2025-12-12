import os
import shutil
import logging
from utils.helpers import get_lib_path, run_subprocess_no_console

logger = logging.getLogger("bookra1n")

def block_ota(udid: str) -> bool:
    idevicebackup2 = get_lib_path('idevicebackup2.exe') 
    if not os.path.exists(idevicebackup2):
        logger.debug("ideviceinfo.exe not found")
        return False
    
    base_dir = os.path.dirname(idevicebackup2)
    backup_dir = os.path.join(base_dir, udid)           
    ota_original = os.path.join(base_dir, "ota") 

    try:
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

        shutil.copytree(ota_original, backup_dir)

        cmd = [idevicebackup2, "restore", "."]

        process = run_subprocess_no_console(cmd, cwd=base_dir, timeout=300)
        if process.returncode == 0:
            logger.info("OTA Block Successful")
            return True
        else:
            logger.error(f"idevicebackup2 failed: {process.returncode}")
            return False

    except Exception as e:
        logger.error(f"Error Blocking OTA: {e}")
        return False
    
    finally:
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

def enable_ota(udid: str) -> bool:
    idevicebackup2 = get_lib_path('idevicebackup2.exe') 
    if not os.path.exists(idevicebackup2):
        logger.debug("ideviceinfo.exe not found")
        return False
    
    base_dir = os.path.dirname(idevicebackup2)
    backup_dir = os.path.join(base_dir, udid)           
    ota_original = os.path.join(base_dir, "enable_ota") 

    try:
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

        shutil.copytree(ota_original, backup_dir)

        cmd = [idevicebackup2, "restore", "."]

        process = run_subprocess_no_console(cmd, cwd=base_dir, timeout=300)
        if process.returncode == 0:
            logger.info("OTA Enable Successful")
            return True
        else:
            logger.error(f"idevicebackup2 failed: {process.returncode}")
            return False

    except Exception as e:
        logger.error(f"Error Enabling OTA: {e}")
        return False
    
    finally:
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)