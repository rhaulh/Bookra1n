# main.py
import sys
import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSharedMemory
from core.detector import DeviceDetector
from utils.helpers import hide_console
from utils.logger import setup_logger
from security.monitors import SecurityMonitor
from gui.dialogs import ActivationResultDialog

class SingleInstanceApp:
    def __init__(self, key):
        self.shared_memory = QSharedMemory(key)
        
    def is_running(self):
        if self.shared_memory.attach():
            return True
        
        if self.shared_memory.create(1):
            return False
        
        return True
    
    def release(self):
        if self.shared_memory.isAttached():
            self.shared_memory.detach()

def main():
   
    if sys.platform == 'win32':
        try:
            myappid = 'com.bookra1n.a12.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            logger.warning(f"Could not set App ID: {e}")
    
    logger = setup_logger()     
    logger.debug("Application starting...")
    SecurityMonitor.configure(logger)

    hide_console()

    app = QApplication(sys.argv)
    app.setApplicationName("Bookra1n A12 Bypass")
    
    single_instance = SingleInstanceApp("Bookra1n_A12_SingleInstance_Key_2024")
    
    if single_instance.is_running():
        logger.warning("Application is already running!")
        dialog = ActivationResultDialog(
            "Already Running",
            "Bookra1n is already running.",
            is_success=True,
            parent=None
        )
        dialog.exec_()
    
    logger.debug("Creating main window...")
    
    try:
        window = DeviceDetector()
        window.show()
        
        logger.debug("Application window displayed")
        
        exit_code = app.exec_()
        
        logger.debug(f"Application closing with exit code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Fatal error in application: {e}", exc_info=True)
        return 1
    
    finally:
        single_instance.release()

if __name__ == "__main__":
    sys.exit(main())