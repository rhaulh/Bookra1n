# core/detector.py
import traceback
import logging
from PyQt5.QtWidgets import QMainWindow,QDialog
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
import threading, time, webbrowser
from core.worker import ActivationWorker
from gui.dialogs import CustomMessageBox, ActivationResultDialog, InstructionDialog, AuthMessageBox,CustomAlertBox
from utils.device_models import get_model_from_product_type
from config import CONTACT_URL
from gui.mainUI import Ui_MainWindow
from core.api import API
from gui.draggable import Draggable
from data.models import DeviceInfo,DeviceCleanInfo,DeviceBasicConnectionInfo
from security.monitors import SecurityMonitor
from core.device_commands import DeviceCommands
from utils.ota import block_ota,enable_ota
class DeviceDetector(QMainWindow,Draggable,DeviceCommands):

    logger = logging.getLogger("bookra1n")
    security_monitor = SecurityMonitor.getMonitor()
    activation_worker = None
 
    # Monitor Signals
    device_connected = pyqtSignal(bool, str, str)
    is_device_connected = False
    show_auth_dialog = pyqtSignal(str, str)
    activation_started = pyqtSignal(bool)  
    activation_finished = pyqtSignal(bool, str)

    waiting_new_device = pyqtSignal(bool)    
    waiting_for_reboot =  pyqtSignal(bool)
    
    # UI Signals
    enable_activate_btn = pyqtSignal(bool)
    block_ota_btn = pyqtSignal(bool)
    enable_ota_btn = pyqtSignal(bool)
    update_status_label = pyqtSignal(str, bool)
    update_connection_status_label = pyqtSignal(str, str)
    update_progress = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_device = DeviceInfo()
        self.new_device = DeviceInfo()  

        # Flags
        self.activation_in_progress = False
        self.wait_for_reboot = False
        self.repair_attempted = False
        self.skipping_authorization_check = False
        self.skipping_model_check = False

        # Connect signals
        self.device_connected.connect(self.on_device_connected)
        self.show_auth_dialog.connect(self.on_show_auth_dialog)
        self.waiting_for_reboot.connect(self.on_waiting_for_reboot)
        self.activation_finished.connect(self.on_activation_finished)
        self.ui.activate_btn.clicked.connect(self.activate_device)
        self.update_progress.connect(self.ui.on_update_progress)
        self.activation_started.connect(self.on_activation_started)
        self.enable_activate_btn.connect(self.ui.on_set_activate_button_state)
        self.update_status_label.connect(self.ui.update_status_label)
        self.update_connection_status_label.connect(self.ui.update_connection_status_label)
        self.ui.block_ota_btn.clicked.connect(self.on_block_ota)
        self.ui.enable_ota_btn.clicked.connect(self.on_enable_ota)
        # Reset
        self.reset_activation_status()
        
        # Start monitoring in background: Security and Device Connection
        self.start_security_monitoring()
        self.setup_device_monitor()

    def reset_activation_status(self):
        self.authorization_checked = False
        self.waiting_authorization = False
        self.auth_thread_running = False
        self.wait_for_reboot = False
        self.activation_in_progress = False
        self.skipping_authorization_check = False
        self.skipping_model_check = False

    #  Monitors
    def start_security_monitoring(self):
        def monitor():
            self.security_monitor.continuous_monitoring()
        
        security_thread = threading.Thread(target=monitor, daemon=True)
        security_thread.start()
     
    def setup_device_monitor(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_device_connection_status)
        self.timer.start(2000)

    def setup_auth_monitor(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_authorization)
        self.timer.start(2000)

    def check_device_connection_status(self):
        def device_check_thread():
            try:
                connected, info = self.have_device_full_connection()
                if connected:
                    self.device_connected.emit(True,"Full",info)
                    return

                if self.retry_pairing(self.repair_attempted):
                    self.device_connected.emit(True,"Full",info)
                    return

                connected, info = self.have_device_limited_connection()
                if connected:
                    self.device_connected.emit(True,"Limited",info)
                    return

                self.device_connected.emit(False,"Disconnected",None)

            except Exception as e:
                self.logger.error(f"Detection Error: {e}")
                self.device_connected.emit(False,"Error",None)

        threading.Thread(target=device_check_thread, daemon=True).start()
   
    # DEVICE INFO PARSING & UPDATES
    def on_device_connected(self, connected, connection_type, info):
        if self.activation_in_progress:
            if not connected:
                if not self.wait_for_reboot:
                    self.logger.debug("Device disconnected during activation")
                    self.activation_worker.stop()
        else:
            if not connected:
                if self.is_device_connected:
                    self.logger.debug("Device disconnected")
                    self.clear_device_info()
            else:
                if not self.is_device_connected:
                    if connection_type == "Full":
                        self.parse_device_info(info)
                        self.setup_auth_monitor()
                    if connection_type == "Limited":
                        self.handle_basic_connection(info.strip())
                        
        self.is_device_connected = connected 

    def parse_device_info(self, output):
        KEY_MAP = {
            "ProductType": "model",
            "ProductVersion": "ios",
            "SerialNumber": "serial",
            "UniqueDeviceID": "udid",
            "InternationalMobileEquipmentIdentity":"imei",
            "RegionInfo":"region"
        }
        
        lines = output.split("\n")

        for line in lines:
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key in KEY_MAP:
                    attr_name = KEY_MAP[key]
                    setattr(self.new_device, attr_name, value)
        
        self.update_device_info()
    
    def update_device_info(self):
        try:
            serial = self.new_device.serial   
            model = self.new_device.model
            ios = self.new_device.ios
            
            if self.is_same_device(self.new_device):
                self.ui.update_ui(self.current_device)         
            else:
                self.logger.info(f"New device detected → Serial: {serial} | Type: {model} | iOS: {ios}")
                self.current_device = DeviceInfo()
                self.current_device = self.new_device
                self.current_device.name = get_model_from_product_type(self.new_device.model)
                self.current_device.pair = "Full"

                # UI
                self.ui.update_ui(self.current_device)

            # Reset Flags
            self.reset_activation_status()
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
            traceback.print_exc()
        finally:
            self.new_device = DeviceInfo()

    def is_same_device(self, new_device:DeviceInfo):
        if not hasattr(self.current_device, 'serial') or not self.current_device.serial:
            return False     
        if new_device.serial == self.current_device.serial:
            return True     
        return False

    def handle_basic_connection(self, udid):       
        self.logger.debug("Basic connection detected - limited info available")
        self.current_device.pair = "Limited"
        
        device_basic_info = DeviceBasicConnectionInfo()
        device_basic_info.udid = udid
        
        self.ui.update_ui(device_basic_info)

    def check_authorization(self):
        if not self.current_device.serial or not self.current_device.model or not self.current_device.ios:
            self.logger.warning("Incomplete device info - skipping authorization check")
            self.update_status_label.emit("Collecting device info...", False)
            self.enable_activate_btn.emit(False)
            return

        serial = self.current_device.serial
        model = self.current_device.model
        ios = self.current_device.ios
        region = self.current_device.region or ""

        if self.activation_in_progress and not self.skipping_authorization_check:
            self.logger.debug("Activation in progress - skipping authorization check")
            self.skipping_authorization_check = True
            return

        if not self.skipping_model_check:
            supported = API.check_supported_model(model, ios)

            if not supported or region == "CH/A":
                self.show_not_supported_message(model, serial, region)
                self.skipping_model_check = True
                self.enable_activate_btn.emit(False)
                return

            self.skipping_model_check = True

        if self.current_device.authorized:
            auth_status = API.check_authorization(serial)

            if auth_status == "not_authorized":
                self.current_device.authorized = False
                self.authorization_checked = False
                self.waiting_authorization = False
                self.update_status_label.emit("Not Authorized", False)
                self.enable_activate_btn.emit(False)
            else:
                return
            
        if self.authorization_checked:
            return

        try:
            auth_status = API.check_authorization(serial)

            if auth_status == "authorized":
                self.logger.info(f"Device AUTHORIZED: {serial}")
                self.current_device.authorized = True
                self.authorization_checked = True

                if self.check_activation_status():
                    self.update_status_label.emit("Device already Activated", True)
                    self.ui.on_set_block_ota_button_state(True)
                    self.ui.on_set_enable_ota_button_state(True)
                else:
                    self.enable_activate_btn.emit(True)
                    self.update_status_label.emit("Device Authorized", True)

                return

            elif auth_status == "not_authorized":
                if not self.waiting_authorization:
                    self.logger.debug("Device NOT authorized → showing dialog")
                    self.waiting_authorization = True
                    self.show_auth_dialog.emit(
                        self.current_device.model,
                        self.current_device.serial
                    )
                self.update_status_label.emit("Not Authorized", False)
                self.enable_activate_btn.emit(False)
                return

            elif auth_status == "proxy_detected":
                self.show_proxy_warning_message()
                self.update_status_label.emit("Security Violation", False)
                self.enable_activate_btn.emit(False)
                return

            else:
                self.update_status_label.emit("Connected", True)
                self.enable_activate_btn.emit(False)

        except Exception as e:
            self.logger.error(f"Error en check_authorization(): {e}")
            self.enable_activate_btn.emit(False)

    # ACTIVATION PROCESS  
    def activate_device(self):
        if self.activation_in_progress:
            self.logger.warning("Activation already in progress or stuck - resetting flag")
            return

        if not self.current_device.authorized:
            self.show_not_authorized_message()
            return
        
        if self.security_monitor.check_api_sniffing() or self.security_monitor.check_proxy_usage():
            self.show_proxy_warning_message()
            return

        if not InstructionDialog.show_instructions(self):                               
            return

        self.activation_started.emit(True)
    
    def enable_ota_thread(self):
        self.logger.debug("Enabling OTA updates...")
        if enable_ota(self.current_device.udid):
            dialog = CustomAlertBox(
            "🎉 OTA Enabled!",
             f"OTA Updates Enabled",
            parent=self
        )
        dialog.exec_()
        
    def on_enable_ota(self):
        self.logger.debug(f"Enabling OTA Dialog")     
                
        dialog = CustomMessageBox(
            "OTA Enabling Warning",
            f"OTA and Fake restore will be enabled\n\nProceed with Enabling OTA updates?",
            self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.logger.debug("User clicked Proceed to Enabling OTA")
            QTimer.singleShot(0, self.enable_ota_thread)
            
        else:
            self.logger.debug("User canceled the OTA Enabling process")
    
    def block_ota_thread(self):
        self.logger.debug("Blocking OTA updates...")
        if block_ota(self.current_device.udid):
            dialog = CustomAlertBox(
            "🎉 OTA Blocked!",
             f"OTA Updates Blocked",
            parent=self
        )
        dialog.exec_()

    def on_block_ota(self):
        self.logger.debug(f"Block OTA Advice Warning Dialog")     
                
        dialog = CustomMessageBox(
            "OTA Blocking Warning",
            f"Block OTA and Fake restore will be disabled\nProceed with blocking OTA updates?",
            self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.logger.debug("User clicked Proceed to Block OTA")
            QTimer.singleShot(0, self.block_ota_thread)
            
        else:
            self.logger.debug("User canceled the OTA blocking process")
        
    def on_activation_started(self, started):
        self.activation_in_progress = started
        if started:
            self.activation_worker = ActivationWorker(self)
            self.activation_worker.start()
        self.ui.on_activation_started(started)
    
    def on_activation_finished(self, success, message):
        self.logger.debug(message)
        self.on_activation_started(False)

        if success:
            self.ui.on_set_block_ota_button_state(True)
            self.show_custom_activation_success(message)
        else:
            self.ui.on_set_block_ota_button_state(False)
            self.show_custom_activation_error(message) 

    def on_waiting_for_reboot(self, waiting):
        self.wait_for_reboot = waiting
    
    # Messages and Dialogs
    def show_custom_activation_success(self, message):     
        dialog = ActivationResultDialog(
            "🎉 Your Device is Activated!",
            message,
            is_success=True,
            parent=self
        )
        dialog.exec_()
        
        self.ui.progress_bar.setVisible(False)
        self.ui.update_status_label("Activation Complete",True)
        self.enable_activate_btn.emit(False)

    def show_custom_activation_error(self, error_message):
        dialog = ActivationResultDialog(
            "🚨 Activation Error",
            error_message,
            is_success=False,
            parent=self
        )
        dialog.exec_()

        self.ui.progress_bar.setVisible(False)
        self.ui.update_status_label("Activation Error",False)
        self.enable_activate_btn.emit(True)

    def on_show_auth_dialog(self, model_name, serial):
        self.logger.debug(f"Showing authorization dialog for {model_name} - {serial}")     
        
        dialog = AuthMessageBox(
            "Device Supported",
            f"Congratulations! Your device {model_name} with serial number {serial} is supported for activation.",
            serial,
            self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.logger.debug("User clicked Proceed to Order")
            webbrowser.open(CONTACT_URL)
        else:
            self.logger.debug("User canceled the authorization process")

    def show_not_authorized_message(self):
        dialog = ActivationResultDialog(
            "Not Authorized",
            "Device not authorized for activation",
            is_success=False,
            parent=self
        )
        dialog.exec_()
    
    def show_proxy_warning_message(self):
        dialog = ActivationResultDialog(
            "🚨 Security Violation",
            "Proxy usage detected!",
            is_success=False,
            parent=self
        )
        dialog.exec_()
    
    def show_not_supported_message(self, model_name, serial,region=None):
        dialog = ActivationResultDialog(
            "Device Not Supported",
            f"Device NOT SUPPORTED.",
            is_success=False,
            parent=self
        )
        dialog.exec_()

# RESETS

    def clear_device_info(self):
        self.logger.debug("UI Cleanup ...")
        reset_device = DeviceCleanInfo()
        self.ui.update_ui(reset_device)
