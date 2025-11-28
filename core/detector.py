# core/detector.py
import os
import time
import random
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
import threading, time, os, requests, re, webbrowser, tempfile, shutil
from core.worker import ActivationWorker
from gui.dialogs import CustomMessageBox, ActivationResultDialog
from security.monitor import security_monitor
from utils.helpers import run_subprocess_no_console, get_lib_path, get_random_hacking_text
from config import CONTACT_URL
from gui.mainUI import Ui_MainWindow
from core.api import API
from core.afc_service import AFCService

class DeviceDetector(QMainWindow,Ui_MainWindow):
    device_connected = pyqtSignal(bool)
    model_received = pyqtSignal(str)
    show_auth_dialog = pyqtSignal(str, str)
    enable_activate_btn = pyqtSignal(bool)
    update_status_label = pyqtSignal(str, str)
    update_progress = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.style_sheet_path = "gui\styles.qss"

        # Ruta segura compatible con PyInstaller
        self.style_sheet_path = self.resource_path("gui/styles.qss")

        # Cargar estilos si existen
        if os.path.exists(self.style_sheet_path):
            with open(self.style_sheet_path, "r", encoding="utf-8") as f:
                self.button_styles = f.read()
                self.ui.activate_btn.setStyleSheet(self.button_styles)
        else:
            self.button_styles = ""

        self.device_info = {}
        self.current_serial = None
        self.current_product_type = None
        self.current_ios = None
        
        self.authorization_checked = False
        self.device_authorized = False
        self.activation_in_progress = False
        self.zrac_guid_data = None
        self.extracted_guid = None
        self.activation_worker = None
        
        # Start security monitoring in background
        self.start_security_monitoring()
        self.afc = AFCService()
        
        # Connect signals
        self.device_connected.connect(self.on_device_connected)
        self.model_received.connect(self.on_model_received)
        self.show_auth_dialog.connect(self.on_show_auth_dialog)
        self.update_status_label.connect(self.on_update_status_label)
        self.update_progress.connect(self.on_update_progress)
        self.enable_activate_btn.connect(self.set_activate_button_state)
        self.ui.activate_btn.clicked.connect(self.activate_device)
        self.setup_device_monitor()
    
    def resource_path(self,relative_path):
        import sys, os

        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            # Carpeta base cuando NO es .exe
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        return os.path.join(base_path, relative_path)
    
    def start_security_monitoring(self):
        def monitor():
            security_monitor.continuous_monitoring()
        
        security_thread = threading.Thread(target=monitor, daemon=True)
        security_thread.start()

        self.ui.activate_btn.setProperty("state", "waiting")
        self.ui.activate_btn.setCursor(Qt.ArrowCursor)

    def set_activate_button_state(self, enabled: bool):
        self.ui.activate_btn.setEnabled(enabled)

        if enabled:
            self.ui.activate_btn.setProperty("state", "ready")
            self.ui.activate_btn.setText("🚀 Activate Device")
            self.ui.activate_btn.setCursor(Qt.PointingHandCursor)
        else:
            self.ui.activate_btn.setProperty("state", "waiting")
            self.ui.activate_btn.setText("⏳ Waiting for Authorization...")
            self.ui.activate_btn.setCursor(Qt.ArrowCursor)

        self.ui.activate_btn.style().unpolish(self.ui.activate_btn)
        self.ui.activate_btn.style().polish(self.ui.activate_btn)
        self.ui.activate_btn.update()

   # ========== CONNECTION METHODS ==========

    def is_device_connected(self):
        """Check if device is still connected"""
        try:
            ideviceinfo_path = get_lib_path('ideviceinfo.exe')
            if os.path.exists(ideviceinfo_path):
                result = run_subprocess_no_console([ideviceinfo_path], timeout=5)
                return result and result.returncode == 0 and result.stdout.strip()
            return False
        except:
            return False

    def reboot_device_sync(self):
        try:
            ios_path = get_lib_path('ios.exe')
            if not os.path.exists(ios_path):
                print("❌ ios.exe not found in libs folder")
                return False
            
            cmd = [ios_path, 'reboot']
            result = run_subprocess_no_console(cmd, timeout=30)
            
            if result and result.returncode == 0:
                print("✅ Device reboot command sent successfully")
                return True
            else:
                print(f"⚠️ Reboot command failed")
                return True  # Return True anyway to continue
                
        except Exception as e:
            print(f"⚠️ Reboot error: {e}")
            return True  # Return True anyway to continue

    def wait_for_device_reconnect_sync(self, timeout):
        """Wait for device to reconnect (synchronous version)"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.is_device_connected():
                    print("✅ Device reconnected after reboot")
                    return True
                time.sleep(5)  # Check every 5 seconds
            
            print("⚠️ Device did not reconnect within timeout period")
            return False
        except Exception as e:
            print(f"⚠️ Wait for reconnect error: {e}")
            return False

    # ========== THREAD-SAFE METHODS ==========

    def transfer_file_thread(self,folder, local_file_path, progress_signal):
        """Transfer file to device - thread safe"""
        try:
            # First check if device is still connected
            if not self.is_device_connected():
                raise Exception("Device disconnected during transfer")
            
            
            # Get the filename from the local path
            filename = os.path.basename(local_file_path)
            
            # Transfer file to Downloads folder
            progress_signal.emit(20, "Transferring activation file...")
            device_path = f"{folder}/{filename}"
            
            if not self.afc.transfer_file_to_device(local_file_path, device_path):
                raise Exception("Failed to transfer file to device")
            
            print(f"✅ File transferred to {device_path}")
            
            # Wait a bit for processing to potentially start
            progress_signal.emit(30, "Initializing file processing...")
            time.sleep(5)
            
            return True
                
        except Exception as e:
            raise Exception(f"Transfer error: {str(e)}")  
   
    def reboot_device_thread(self, progress_signal):
        try:
            # Check if ios.exe exists in libs folder
            ios_path = get_lib_path('ios.exe')
            
            if not os.path.exists(ios_path):
                raise Exception("ios.exe not found in libs folder")
            
            progress_signal.emit(95, get_random_hacking_text())
            
            # Execute reboot command
            cmd = [ios_path, 'reboot']
            result = run_subprocess_no_console(cmd, timeout=30)
            
            if result and result.returncode == 0:
                return True
            else:
                print(f"Reboot error")
                return True
                
        except Exception as e:
            print(f"Reboot error: {e}")
            return True

    def wait_for_device_reconnect_thread(self, timeout, progress_signal, worker):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not worker.is_running:
                return False  # User cancelled
            
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            
            if self.is_device_connected():
                print("Device reconnected after reboot")
                return True
            
            time.sleep(5)  # Check every 5 seconds
        
        print("Device did not reconnect within timeout period")
        return False

    def check_activation_status_thread(self):
        """Check device activation status - thread safe"""
        try:
            print("🔍 Checking device activation status...")
            
            ideviceinfo_path = get_lib_path('ideviceinfo.exe')
            
            if not os.path.exists(ideviceinfo_path):
                print("❌ ideviceinfo.exe not found")
                return False
            
            # Get activation state from device
            result = run_subprocess_no_console([ideviceinfo_path, '-k', 'ActivationState'], timeout=15)
            
            if result and result.returncode == 0:
                activation_state = result.stdout.strip()
                
                if activation_state == "Activated":
                    return True
                elif activation_state == "Unactivated":
                    return False
                else:
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error checking activation status: {e}")
            return False

    # ========== ACTIVATION PROCESS ==========
    
    def activate_device(self):
        # """UPDATED ACTIVATION PROCESS with proper threading"""
        if not self.device_authorized:
            QMessageBox.warning(self, "Not Authorized", "Device is not authorized for activation.")
            return
        
        # # Security check before activation - including proxy detection
        if security_monitor.check_api_sniffing() or security_monitor.check_proxy_usage():
            QMessageBox.critical(self, "Security Violation", "Proxy usage detected! Application cannot run with proxy settings.")
            return
        
        # Show custom instruction dialog
        instruction_dialog = QDialog(self)
        instruction_dialog.setWindowTitle("Setup Instructions")
        instruction_dialog.setFixedSize(500, 350)
        instruction_dialog.setModal(True)
        instruction_dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Important: Setup Required")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #e8f4fd;
            border-radius: 5px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Instructions
        instructions_text = QLabel(
            "Before starting the activation process, please ensure your device is properly set up:\n\n"
            "🔹 <b>Step 1:</b> Connect your device to <b>WIFI</b>\n\n"
            "🔹 <b>Step 2:</b> Proceed to the <b>Activation Lock</b> section on your device\n\n"
            "🔹 <b>Step 3:</b> Make sure the device is showing the activation lock screen\n\n"
            "If you've completed these steps, click 'Continue' to begin the activation process."
        )
        instructions_text.setStyleSheet("""
            font-size: 14px;
            color: #34495e;
            line-height: 1.5;
            padding: 15px;
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
        """)
        instructions_text.setWordWrap(True)
        instructions_text.setTextFormat(Qt.RichText)
        layout.addWidget(instructions_text)
        
        # Warning note
        warning_label = QLabel("⚠️ Activation will not work if these steps are not completed!")
        warning_label.setStyleSheet("""
            font-size: 12px;
            color: #e74c3c;
            font-weight: bold;
            font-style: italic;
            margin: 10px 0;
            padding: 8px;
            background-color: #fdf2f2;
            border: 1px solid #e74c3c;
            border-radius: 3px;
        """)
        warning_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(instruction_dialog.reject)
        
        continue_btn = QPushButton("Continue")
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        continue_btn.clicked.connect(instruction_dialog.accept)
        continue_btn.setDefault(True)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(continue_btn)
        layout.addLayout(button_layout)
        
        instruction_dialog.setLayout(layout)
        
        # Show dialog and check response
        result = instruction_dialog.exec_()
        
        if result == QDialog.Rejected:
            print("User cancelled activation after reading instructions")
            return
        
        # Show progress bar and reset
        self.ui.progress_bar.setVisible(True)
        self.ui.progress_bar.setValue(0)
        self.ui.activate_btn.setText("Starting activation process...")
        self.enable_activate_btn.emit(False)
        self.activation_in_progress = True

        # Create and start worker thread
        self.activation_worker = ActivationWorker(self)
        self.activation_worker.progress_updated.connect(self.on_update_progress)
        self.activation_worker.activation_finished.connect(self.on_activation_finished)
        self.activation_worker.guid_extracted.connect(self.on_guid_extracted)
        self.activation_worker.start()

    def on_guid_extracted(self, guid):
        print(f"📋 SUCCESS GUID extracted in main thread: {guid}")

    def on_activation_finished(self, success, message):
        if success:
            self.show_custom_activation_success()
        else:
            self.show_custom_activation_error(message)
 
    def show_custom_activation_success(self):
        """Show custom activation success message box"""
        self.ui.progress_bar.setVisible(False)
        self.activation_in_progress = False
        
        dialog = ActivationResultDialog(
            "🎉 Activation Successful!",
            "Your device has been successfully activated!\n\nThe activation process completed successfully. Your device is now ready to use.",
            is_success=True,
            parent=self
        )
        dialog.exec_()
        
        # Update status
        self.ui.status_value.setText("Activation Complete")
        self.ui.status_value.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")

    def show_custom_activation_error(self, error_message):
        """Show custom activation error message box"""
        self.ui.progress_bar.setVisible(False)
        self.enable_activate_btn.emit(True)
        self.activation_in_progress = False
        
        dialog = ActivationResultDialog(
            "🚨 Activation Error",
            f"An error occurred during activation.\n\nError: {error_message}\n\nPlease try again.",
            is_success=False,
            parent=self
        )
        dialog.exec_()
        
        # Update status
        self.ui.status_value.setText("Activation Error")
        self.ui.status_value.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")

    def on_model_received(self, model_name):
        self.ui.model_value.setText(model_name)
    
    def on_show_auth_dialog(self, model_name, serial):
        """Show authorization dialog from main thread"""
        print(f"Showing authorization dialog for {model_name} - {serial}")
        message = f"Congratulations! Your device {model_name} with serial number {serial} is supported for activation."
        
        dialog = CustomMessageBox(
            "Device Supported",
            message,
            serial,
            self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            print("User clicked Proceed to Order")
            # Open strawhat.com in browser
            webbrowser.open(CONTACT_URL)
            # Keep activate button disabled until device is authorized
            self.enable_activate_btn.emit(False)
        else:
            print("User canceled the authorization process")
            # Keep activate button disabled
            self.enable_activate_btn.emit(False)
    
    def on_update_status_label(self, status_text, color):
        """Update status label from main thread"""
        self.ui.status_value.setText(status_text)
        self.ui.status_value.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
    
    def on_update_progress(self, value, text):
        """Update progress bar and label from main thread"""
        self.ui.progress_bar.setValue(value)
        self.ui.activate_btn.setText(text)

    def copy_to_clipboard(self, text, label):
        print(f"Copying to clipboard: {text}")
        """Copy text to clipboard and show temporary feedback"""
        if text != "N/A" and text != "Unknown" and text != "Unknown Model" and not text.startswith("API Error"):
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            original_text = label.text()
            original_style = label.styleSheet()
            
            label.setText("Copied!")
            label.setStyleSheet("""
                color: #27ae60; 
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                border: 1px solid #27ae60;
                border-radius: 3px;
                background-color: #d5f4e6;
            """)
            
            QTimer.singleShot(2000, lambda: self.restore_text(label, original_text, original_style))
    
    def restore_text(self, label, original_text, original_style):
        """Restore the original label text and style"""
        label.setText(original_text)
        label.setStyleSheet(original_style)
        
    def setup_device_monitor(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_device_status)
        self.timer.start(2000)
        
    def check_device_status(self):
        if self.activation_in_progress:
            return

        # === FUNCIÓN INTERNA BIEN DEFINIDA ===
        def device_check_thread():
            try:
                ideviceinfo_path = get_lib_path('ideviceinfo.exe')
                idevice_id_path = get_lib_path('idevice_id.exe')

                # Primero intenta con ideviceinfo (da toda la info)
                if os.path.exists(ideviceinfo_path):
                    result = run_subprocess_no_console([ideviceinfo_path], timeout=10)
                    if result and result.returncode == 0 and result.stdout.strip():
                        self.parse_device_info(result.stdout)
                        self.device_connected.emit(True)
                        return

                # Si no, al menos detecta conexión básica con idevice_id
                if os.path.exists(idevice_id_path):
                    result = run_subprocess_no_console([idevice_id_path, '-l'], timeout=8)
                    if result and result.returncode == 0 and result.stdout.strip():
                        print("¡Dispositivo detectado! (solo conexión básica)")
                        self.device_connected.emit(True)
                        QTimer.singleShot(0, self.update_basic_connection)
                        return

                # Si llega aquí → no hay dispositivo
                self.device_connected.emit(False)

            except Exception as e:
                print(f"Error en detección: {e}")
                self.device_connected.emit(False)

        # === LANZAR EN HILO ===
        threading.Thread(target=device_check_thread, daemon=True).start()   
    
    def parse_device_info(self, output):
        self.device_info = {}
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                self.device_info[key] = value
        
        QTimer.singleShot(0, self.update_device_info)
    
    def update_device_info(self):
        try:
            # --- Obtener datos básicos ---
            serial = self.device_info.get('SerialNumber', 'N/A')
            ios_version = self.device_info.get('ProductVersion', 'N/A')
            imei = self.device_info.get('InternationalMobileEquipmentIdentity', 'N/A')
            product_type = self.device_info.get('ProductType', 'N/A')
            udid = self.device_info.get('UniqueDeviceID', 'N/A')

            if serial == 'N/A' and udid != 'N/A':
                serial = udid[-8:] if len(udid) >= 8 else udid

            device_changed = (
                serial != self.current_serial or
                product_type != self.current_product_type or
                ios_version != self.current_ios
            )

            if not device_changed:
                return

            print(f"New device → Serial: {serial} | Type: {product_type} | iOS: {ios_version}")

            self.current_serial = serial
            self.current_product_type = product_type
            self.current_ios = ios_version
            self.authorization_checked = False
            self.device_authorized = False
            self.zrac_guid_data = None

            self.ui.serial_value.setText(serial)
            self.ui.ios_value.setText(ios_version)
            self.ui.imei_value.setText(imei or "N/A")
            self.ui.status_value.setText("Connected")
            self.ui.status_value.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")
            self.enable_activate_btn.emit(False)

            if not product_type or product_type == 'N/A':
                self.ui.model_value.setText("Unknown Device")
                return

            self.ui.model_value.setText("Loading...")

            def background_check():
                try:
                    model_name = API.fetch_device_model(product_type)
                    self.model_received.emit(model_name if model_name else "Unknown Model")

                    if not model_name or model_name in ("N/A", "Unknown Model") or model_name.startswith("API Error"):
                        return

                    auth_status, stored_guid = API.check_authorization(model_name, serial)

                    if auth_status == "authorized":
                        print(f"Device AUTHORIZED: {serial}")
                        self.device_authorized = True
                        self.update_status_label.emit("Bypass Authorized", "#27ae60")
                        self.enable_activate_btn.emit(True)

                    elif auth_status == "not_authorized":
                        print(f"Device NOT authorized → mostrando diálogo de compra")
                        self.show_auth_dialog.emit(model_name, serial)

                    elif auth_status == "proxy_detected":
                        self.show_proxy_warning_message()
                        self.update_status_label.emit("Security Violation", "#e74c3c")
                        self.enable_activate_btn.emit(False)

                    else:
                        self.update_status_label.emit("Connected", "#27ae60")
                        self.enable_activate_btn.emit(False)

                    self.authorization_checked = True

                except Exception as e:
                    print(f"Error en background_check(): {e}")
                    traceback.print_exc()
                    self.model_received.emit("API Error")

            # Lanzar correctamente el hilo
            threading.Thread(target=background_check, daemon=True).start()

        except Exception as e:
            print(f"Error crítico en update_device_info(): {e}")
            traceback.print_exc()
    
    def check_device_authorization(self, model_name, serial):
        if not self.authorization_checked:
            print(f"Checking authorization for device: {model_name} - {serial}")
            
            def check_auth():
                auth_status, guid = self.check_authorization(model_name, serial)
                
                if auth_status == "authorized":
                    print(f"✅ Device {serial} is AUTHORIZED!")
                    self.device_authorized = True
                    # Update status to "Bypass Authorized" and enable activate button
                    self.update_status_label.emit("Bypass Authorized", "#27ae60")
                    self.enable_activate_btn.emit(True)
                    return guid
                elif auth_status == "not_authorized":
                    print(f"Device {serial} is NOT authorized! Showing order dialog.")
                    # Show dialog when NOT authorized
                    self.show_auth_dialog.emit(model_name, serial)
                    # Keep status as "Connected" and button disabled
                    self.update_status_label.emit("Connected", "#27ae60")
                    self.enable_activate_btn.emit(False)
                    
                elif auth_status == "proxy_detected":
                    print(f"Proxy detected for device {serial}! Blocking access.")
                    # Show proxy warning and block access
                    self.show_proxy_warning_message()
                    # Keep status as "Connected" and button disabled
                    self.update_status_label.emit("Security Violation", "#e74c3c")
                    self.enable_activate_btn.emit(False)
                    
                elif auth_status == "folder_not_found":
                    print(f"Device folder for {model_name} not found on server.")
                    # Show custom message for folder not found
                    self.show_folder_not_found_message(model_name, serial)
                    # Keep status as "Connected" and button disabled
                    self.update_status_label.emit("Connected", "#27ae60")
                    self.enable_activate_btn.emit(False)
                    
                else:
                    print(f"Device {serial} authorization status unknown or error.")
                    # Keep status as "Connected" and button disabled for unknown/error cases
                    self.update_status_label.emit("Connected", "#27ae60")
                    self.enable_activate_btn.emit(False)

                self.authorization_checked = True
                return None
            threading.Thread(target=check_auth, daemon=True).start()
    
    def show_proxy_warning_message(self):
        """Show proxy warning message"""
        def show_dialog():
            msg = QMessageBox(self)
            msg.setWindowTitle("Security Violation")
            msg.setText("Proxy usage detected!\n\nThis application cannot run with proxy settings for security reasons.\n\nPlease disable any proxy settings and try again.")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        
        QTimer.singleShot(0, show_dialog)
    
    def show_folder_not_found_message(self, model_name, serial):
        """Show custom message when device folder is not found"""
        def show_dialog():
            msg = QMessageBox(self)
            msg.setWindowTitle("Device Not Ready")
            msg.setText(f"Your {model_name} device will be ready in a bit.\n\nPlease check back later.")
            msg.setInformativeText(f"Serial: {serial}")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        
        QTimer.singleShot(0, show_dialog)

    def update_basic_connection(self):
        """Update UI when device is connected but we can't get detailed info"""
        # Only update if this is a new basic connection
        if self.current_serial != "basic_connection":
            self.current_serial = "basic_connection"
            self.current_product_type = "Unknown"
            self.current_ios = "Unknown"
            self.device_authorized = False
            
            self.ui.serial_value.setText("Connected")
            self.ui.ios_value.setText("Unknown")
            self.ui.imei_value.setText("Unknown")
            self.ui.model_value.setText("Unknown")
            self.ui.status_value.setText("Connected (Limited Info)")
            self.ui.status_value.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 14px;")
            self.enable_activate_btn.emit(False)
            print("Basic connection detected - limited info available")
        
    def clear_device_info(self):
        """Clear device info when disconnected"""
        if self.current_serial is not None:
            self.current_serial = None
            self.current_product_type = None
            self.authorization_checked = False
            self.device_authorized = False
            
            self.ui.serial_value.setText("N/A")
            self.ui.ios_value.setText("N/A")
            self.ui.imei_value.setText("N/A")
            self.ui.model_value.setText("N/A")
            self.ui.status_value.setText("Disconnected")
            self.ui.status_value.setStyleSheet("color: #e74c3c; font-size: 14px;")
            self.enable_activate_btn.emit(False)
            print("Device disconnected - cleared UI")

    def on_device_connected(self, connected):
        if not connected:
            QTimer.singleShot(0, self.clear_device_info)
