# core/detector.py
import sys
import os
import subprocess
import time
import random
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
import threading, time, os, requests, re, webbrowser, tempfile, shutil
from core.worker import ActivationWorker
from gui.dialogs import CustomMessageBox, ActivationResultDialog
from security.monitor import security_monitor
from utils.helpers import run_subprocess_no_console, get_lib_path
from PyQt5 import uic
from core.api import Api

class DeviceDetector(QMainWindow):
    device_connected = pyqtSignal(bool)
    model_received = pyqtSignal(str)
    show_auth_dialog = pyqtSignal(str, str)
    enable_activate_btn = pyqtSignal(bool)
    update_status_label = pyqtSignal(str, str)
    update_progress = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "gui/mainUI.ui"
        )
        uic.loadUi(ui_path, self)

        # ==================== External StyleSheet ====================
        self.style_sheet_path = "gui/styles.qss"

        if os.path.exists(self.style_sheet_path):
            with open(self.style_sheet_path, "r", encoding="utf-8") as f:
                self.button_styles = f.read()
                self.activate_btn.setStyleSheet(self.button_styles)
        else:
            self.button_styles = ""

        self.device_info = {}
        self.current_serial = None
        self.current_product_type = None
        self.cached_models = self.cached_models = {
            # --- iPhone 16 Series (2024) ---
            "iPhone17,3": "iPhone 16 Pro Max",
            "iPhone17,2": "iPhone 16 Pro",
            "iPhone17,1": "iPhone 16 Plus",
            "iPhone16,4": "iPhone 16",

            # --- iPhone 15 Series (2023) ---
            "iPhone16,2": "iPhone 15 Pro Max",
            "iPhone16,1": "iPhone 15 Pro",
            "iPhone15,7": "iPhone 15 Plus",
            "iPhone15,6": "iPhone 15",

            # --- iPhone 14 Series / 13 Refresh (2022) ---
            "iPhone14,8": "iPhone 14 Plus",
            "iPhone14,7": "iPhone 14",
            "iPhone14,6": "iPhone SE (3rd generation)",

            # --- iPhone 13 Series (2021) ---
            "iPhone14,5": "iPhone 13",
            "iPhone14,4": "iPhone 13 mini",
            "iPhone14,3": "iPhone 13 Pro Max",
            "iPhone14,2": "iPhone 13 Pro",

            # --- iPhone 12 Series (2020) ---
            "iPhone13,4": "iPhone 12 Pro Max",
            "iPhone13,3": "iPhone 12 Pro",
            "iPhone13,2": "iPhone 12",
            "iPhone13,1": "iPhone 12 mini",

            # --- iPhone 11 Series (2019) ---
            "iPhone12,5": "iPhone 11 Pro Max",
            "iPhone12,3": "iPhone 11 Pro",
            "iPhone12,1": "iPhone 11",
            "iPhone11,8": "iPhone XR",
            "iPhone11,6": "iPhone XS Max",
            "iPhone11,4": "iPhone XS Max (China)",
            "iPhone11,2": "iPhone XS",

            # --- iPhone X / 8 Series (2017) ---
            "iPhone10,6": "iPhone X",
            "iPhone10,3": "iPhone X",
            "iPhone10,5": "iPhone 8 Plus",
            "iPhone10,2": "iPhone 8 Plus",
            "iPhone10,4": "iPhone 8",
            "iPhone10,1": "iPhone 8",

            # --- iPhone 7 Series (2016) ---
            "iPhone9,4": "iPhone 7 Plus",
            "iPhone9,2": "iPhone 7 Plus",
            "iPhone9,3": "iPhone 7",
            "iPhone9,1": "iPhone 7",

            # --- iPhone SE 1 & 2 ---
            "iPhone12,8": "iPhone SE (2nd generation)",
            "iPhone8,4": "iPhone SE (1st generation)",

            # --- iPhone 6S / 6 Series ---
            "iPhone8,2": "iPhone 6s Plus",
            "iPhone8,1": "iPhone 6s",
            "iPhone7,2": "iPhone 6",
            "iPhone7,1": "iPhone 6 Plus",

            # --- iPhone 5 / 5S / 5C ---
            "iPhone6,2": "iPhone 5s",
            "iPhone6,1": "iPhone 5s",
            "iPhone5,4": "iPhone 5c",
            "iPhone5,3": "iPhone 5c",
            "iPhone5,2": "iPhone 5",
            "iPhone5,1": "iPhone 5",

            # --- iPhone 4 / 4S ---
            "iPhone4,1": "iPhone 4s",
            "iPhone3,3": "iPhone 4",
            "iPhone3,2": "iPhone 4 (GSM Rev A)",
            "iPhone3,1": "iPhone 4",

            # --- iPhone 3GS / 3G ---
            "iPhone2,1": "iPhone 3GS",
            "iPhone1,2": "iPhone 3G",

            # --- iPhone Original ---
            "iPhone1,1": "iPhone",

            # --- iPad Pro 13" / 11" (M4, 2024) ---
            "iPad16,6": "iPad Pro 13-inch (M4)",
            "iPad16,4": "iPad Pro 11-inch (M4)",
            "iPad16,5": "iPad Pro 13-inch (M4, Wi-Fi+Cellular)",
            "iPad16,3": "iPad Pro 11-inch (M4, Wi-Fi+Cellular)",

            # --- iPad Pro (M2, 2022) ---
            "iPad14,5": "iPad Pro 12.9-inch (6th generation, M2)",
            "iPad14,6": "iPad Pro 12.9-inch (6th generation, M2, Wi-Fi+Cellular)",
            "iPad14,3": "iPad Pro 11-inch (4th generation, M2)",
            "iPad14,4": "iPad Pro 11-inch (4th generation, M2, Wi-Fi+Cellular)",

            # --- iPad Pro (M1, 2021) ---
            "iPad13,8": "iPad Pro 12.9-inch (5th generation, M1)",
            "iPad13,9": "iPad Pro 12.9-inch (5th generation, M1, Wi-Fi+Cellular)",
            "iPad13,6": "iPad Pro 11-inch (3rd generation, M1)",
            "iPad13,7": "iPad Pro 11-inch (3rd generation, M1, Wi-Fi+Cellular)",

            # --- iPad Pro (2020) ---
            "iPad8,12": "iPad Pro 12.9-inch (4th generation)",
            "iPad8,11": "iPad Pro 12.9-inch (4th generation, Wi-Fi+Cellular)",
            "iPad8,10": "iPad Pro 11-inch (2nd generation)",
            "iPad8,9": "iPad Pro 11-inch (2nd generation, Wi-Fi+Cellular)",

            # --- iPad Pro (2018) ---
            "iPad8,8": "iPad Pro 12.9-inch (3rd generation)",
            "iPad8,7": "iPad Pro 12.9-inch (3rd generation, Wi-Fi+Cellular)",
            "iPad8,6": "iPad Pro 11-inch (1st generation)",
            "iPad8,5": "iPad Pro 11-inch (1st generation, Wi-Fi+Cellular)",

            # --- iPad Pro (2017) ---
            "iPad7,4": "iPad Pro 10.5-inch",
            "iPad7,3": "iPad Pro 10.5-inch (Wi-Fi+Cellular)",
            "iPad7,2": "iPad Pro 12.9-inch (2nd generation)",
            "iPad7,1": "iPad Pro 12.9-inch (2nd generation, Wi-Fi+Cellular)",

            # --- iPad Pro (2015) ---
            "iPad6,8": "iPad Pro 12.9-inch (1st generation)",
            "iPad6,7": "iPad Pro 12.9-inch (1st generation, Wi-Fi+Cellular)",
            "iPad6,4": "iPad Pro 9.7-inch",
            "iPad6,3": "iPad Pro 9.7-inch (Wi-Fi+Cellular)",

            # --- iPad Air 5 (2022) ---
            "iPad13,1": "iPad Air (5th generation)",
            "iPad13,2": "iPad Air (5th generation, Wi-Fi+Cellular)",

            # --- iPad Air 4 (2020) ---
            "iPad13,16": "iPad Air (4th generation)",
            "iPad13,17": "iPad Air (4th generation, Wi-Fi+Cellular)",

            # --- iPad Air 3 (2019) ---
            "iPad11,4": "iPad Air (3rd generation, Wi-Fi+Cellular)",
            "iPad11,3": "iPad Air (3rd generation)",

            # --- iPad Air 2 (2014) ---
            "iPad5,4": "iPad Air 2",
            "iPad5,3": "iPad Air 2",

            # --- iPad Air (2013) ---
            "iPad4,2": "iPad Air",
            "iPad4,3": "iPad Air",
            "iPad4,1": "iPad Air",

            # --- iPad 10 (2022) ---
            "iPad13,18": "iPad (10th generation)",
            "iPad13,19": "iPad (10th generation, Wi-Fi+Cellular)",

            # --- iPad 9 (2021) ---
            "iPad12,1": "iPad (9th generation)",
            "iPad12,2": "iPad (9th generation, Wi-Fi+Cellular)",

            # --- iPad 8 (2020) ---
            "iPad11,6": "iPad (8th generation)",
            "iPad11,7": "iPad (8th generation, Wi-Fi+Cellular)",

            # --- iPad 7 (2019) ---
            "iPad7,12": "iPad (7th generation)",
            "iPad7,11": "iPad (7th generation, Wi-Fi+Cellular)",

            # --- iPad 6 (2018) ---
            "iPad7,6": "iPad (6th generation)",
            "iPad7,5": "iPad (6th generation, Wi-Fi+Cellular)",

            # --- iPad 5 (2017) ---
            "iPad6,12": "iPad (5th generation)",
            "iPad6,11": "iPad (5th generation, Wi-Fi+Cellular)",

            # --- iPad 4 (2012) ---
            "iPad3,6": "iPad (4th generation)",
            "iPad3,5": "iPad (4th generation, Wi-Fi+Cellular)",
            "iPad3,4": "iPad (4th generation)",

            # --- iPad 3 (2012) ---
            "iPad3,3": "iPad (3rd generation)",
            "iPad3,2": "iPad (3rd generation, Wi-Fi+Cellular)",
            "iPad3,1": "iPad (3rd generation)",

            # --- iPad 2 ---
            "iPad2,4": "iPad 2 (Rev A)",
            "iPad2,3": "iPad 2 (Wi-Fi+Cellular)",
            "iPad2,2": "iPad 2 (GSM)",
            "iPad2,1": "iPad 2",

            # --- iPad 1 ---
            "iPad1,1": "iPad"

        }

        self.authorization_checked = False
        self.device_authorized = False
        self.activation_in_progress = False
        self.zrac_guid_data = None
        self.extracted_guid = None
        self.activation_worker = None
        
        # Start security monitoring in background
        self.start_security_monitoring()
        
        # Connect signals
        self.device_connected.connect(self.on_device_connected)
        self.model_received.connect(self.on_model_received)
        self.show_auth_dialog.connect(self.on_show_auth_dialog)
        self.update_status_label.connect(self.on_update_status_label)
        self.update_progress.connect(self.on_update_progress)
        self.enable_activate_btn.connect(self.set_activate_button_state)
        self.activate_btn.clicked.connect(self.activate_device)
        self.setup_device_monitor()
    
    def start_security_monitoring(self):
        def monitor():
            security_monitor.continuous_monitoring()
        
        security_thread = threading.Thread(target=monitor, daemon=True)
        security_thread.start()

        self.activate_btn.setProperty("state", "waiting")
        self.activate_btn.setCursor(Qt.ArrowCursor)

    def set_activate_button_state(self, enabled: bool):
        self.activate_btn.setEnabled(enabled)

        if enabled:
            self.activate_btn.setProperty("state", "ready")
            self.activate_btn.setText("🚀 Activate Device")
            self.activate_btn.setCursor(Qt.PointingHandCursor)
        else:
            self.activate_btn.setProperty("state", "waiting")
            self.activate_btn.setText("⏳ Waiting for Authorization...")
            self.activate_btn.setCursor(Qt.ArrowCursor)

        self.activate_btn.style().unpolish(self.activate_btn)
        self.activate_btn.style().polish(self.activate_btn)
        self.activate_btn.update()

#  ========== AFC CLIENT OPERATIONS ==========

    def afc_client_operation(self, operation, *args):
        """Execute AFC client operations"""
        try:
            afcclient_path = get_lib_path('afcclient.exe')
            
            if not os.path.exists(afcclient_path):
                raise Exception("afcclient.exe not found in libs folder")
            
            cmd = [afcclient_path, operation] + list(args)
            result = run_subprocess_no_console(cmd, timeout=30)
            
            if result and result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr if result else "Unknown error"
                
        except Exception as e:
            return False, str(e)

    def transfer_file_to_device(self, local_file_path, device_path):
        """Transfer file to device using AFC client"""
        try:
            success, output = self.afc_client_operation('put', local_file_path, device_path)
            return success
        except Exception as e:
            print(f"Error transferring file: {e}")
            return False
    
    def clean_folder(self, folder, exclude=None, only_files=False, log_name=None):
        try:
            # Normalizar la ruta
            folder = folder.rstrip('/') + '/'

            if exclude is None:
                exclude = ['.', '..']

            name = log_name or folder.strip('/')

            # Listar contenido
            success, output = self.afc_client_operation('ls', folder)
            if not success:
                print(f"❌ Could not list {name}")
                return False

            items = [item.strip() for item in output.strip().split('\n') if item.strip()]
            
            if not items:
                print(f"✓ {name} is already empty")
                return True

            deleted_files = 0
            deleted_dirs = 0
            failed = []

            # Primero procesar todos los items
            for item in items:
                if not item or item in exclude:
                    continue

                full_path = f"{folder}{item}"

                # Obtener información del item
                s_ok, stat = self.afc_client_operation("stat", full_path)
                if not s_ok:
                    print(f"⚠️ Could not stat {full_path}")
                    failed.append(full_path)
                    continue

                is_dir = "st_ifmt: S_IFDIR" in stat

                if is_dir:
                    if only_files:
                        continue
                    
                    print(f"📁 Processing directory: {item}")
                    
                    # Limpiar recursivamente el contenido del directorio
                    clean_success = self.clean_folder(
                        full_path, 
                        exclude=exclude, 
                        only_files=False,  # Cambiar a False para limpiar todo
                        log_name=item
                    )
                    
                    if not clean_success:
                        print(f"⚠️ Failed to clean directory: {full_path}")
                        failed.append(full_path)
                        continue
                    
                    # Intentar borrar el directorio vacío
                    print(f"🗑️ Removing empty directory: {item}")
                    rm_success, rm_output = self.afc_client_operation("rmdir", full_path.rstrip('/'))
                    
                    if rm_success:
                        deleted_dirs += 1
                    else:
                        print(f"❌ Could not remove directory {item}: {rm_output}")
                        failed.append(full_path)
                else:
                    # Es un archivo
                    rm_success, rm_output = self.afc_client_operation("rm", full_path)
                    
                    if rm_success:
                        deleted_files += 1
                    else:
                        print(f"❌ Could not remove file {item}: {rm_output}")
                        failed.append(full_path)

            # Resumen
            
            if failed:
                print(f"⚠️ Failed to delete {len(failed)} items:")
                for f in failed[:5]:  # Mostrar solo los primeros 5
                    print(f"  - {f}")
                return False

            return True

        except Exception as e:
            print(f"❌ Error cleaning {name}: {e}")
            traceback.print_exc()
            return False

    def copy_file_from_device_to_device(self, source_path, dest_path):
        try:
            print(f"📥 Leyendo archivo desde iPhone: {source_path}")

            temp_dir = tempfile.mkdtemp()
            filename = os.path.basename(source_path)
            tmp_local_path = os.path.join(temp_dir, filename)

            success, output = self.afc_client_operation("get", source_path, tmp_local_path)
            if not success:
                os.remove(tmp_local_path)
                return False, f"No se pudo leer el archivo: {output}"
            
            dest_path = dest_path + "/" + filename

            success, output = self.afc_client_operation("put", tmp_local_path, dest_path)

            if not success:
                os.remove(tmp_local_path)
                return False, f"No se pudo transferir al destino: {output}"

            os.remove(tmp_local_path)

            print("✅ Copia realizada correctamente")
            return True, "Copia realizada correctamente"

        except Exception as e:
            print(f"❌ Error copiando archivo: {e}")
            return False, str(e)

    # ========== CLEANUP METHODS ==========
    
    def cleanup_device_folders_thread(self):
        """Clean up Downloads, Books, and iTunes_Control folders - thread safe"""
        try:
            print("🧹 Starting device folder cleanup...")
            
            # 1. Clean Downloads folder
            print("🗑️ Cleaning Downloads folder...")
            downloads_success = self.clean_downloads_folder()
            
            # 2. Clean Books folder
            print("📚 Cleaning Books folder...")
            books_success = self.clean_books_folder()
            
            # 3. Clean iTunes_control folder
            print("🎵 Cleaning iTunes_Control folder...")
            itunes_success = self.clean_itunes_control_folder()

            # 4. Clean iTunes_control folder
            print("🎵 Cleaning MetadataStore folder...")
            self.clean_books_MetadataStore_folder()
            
            print("✅ Device folder cleanup completed")
            return downloads_success and books_success and itunes_success
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
   
    def clean_downloads_folder(self):
        return self.clean_folder("Downloads/", log_name="Downloads")
    
    def clean_books_folder(self):
        return self.clean_folder("Books/", log_name="Books")
        
    def clean_books_MetadataStore_folder(self):
        return self.clean_folder("Books/MetadataStore", log_name="MetadataStore")
    
    def clean_itunes_control_folder(self):
        return self.clean_folder("iTunes_Control/iTunes/", log_name="Itunes_Control")
    
  
   # ========== GUID EXTRACTION METHODS ==========
    
    def extract_guid_proper_method(self, progress_value, progress_signal):
        try:
            print("🔄 Starting GUID extraction process...")         
            # Step 1: Reboot device
            progress_signal.emit(progress_value + 2, "Rebooting device...")
            print("🔁 Step 1: Rebooting device...")
            if not self.reboot_device_sync():
                print("⚠️ Reboot failed, continuing anyway...")
            
            # Wait for device to reconnect
            progress_signal.emit(progress_value + 4, "Waiting for device to reconnect...")
            if not self.wait_for_device_reconnect_sync(120):
                print("⚠️ Device did not reconnect properly")
            
            # Step 2: Clean folders using AFC client
            progress_signal.emit(progress_value + 6, "Cleaning folders...")
            print("🗑️ Step 2: Cleaning folders...")
            if not self.cleanup_device_folders_thread():
                print("⚠️ Could not clean folders")
            
            # Step 3: Get device UDID
            progress_signal.emit(progress_value + 8, "Getting device UDID...")
            print("📱 Step 3: Getting device UDID...")
            udid = self.get_device_udid()
            if not udid:
                print("❌ Cannot get device UDID")
                return None
            
            print(f"📋 Device UDID: {udid}")
            
            # Step 4: Collect logs using pymobiledevice3
            progress_signal.emit(progress_value + 10, "Collecting system logs...")
            log_archive_path = self.collect_syslog_with_pymobiledevice(udid)
            if not log_archive_path:
                print("❌ Failed to collect syslog")
                return None
            
            # Step 5: Search for BLDatabaseManager/BLDatabase in logs
            progress_signal.emit(progress_value + 12, "Searching for GUID in logs...")
            guid = self.search_bl_database_in_log_archive(log_archive_path)
            
            # Clean up temporary files
            try:
                if os.path.exists(log_archive_path):
                    shutil.rmtree(os.path.dirname(log_archive_path), ignore_errors=True)
            except:
                pass
            
            if guid:
                return guid
            else:
                return None
                
        except Exception as e:
            print(f"❌ GUID extraction error: {e}")
            return None
        
    def collect_syslog_with_pymobiledevice(self, udid, timeout=300):
        
        try:
            # ✅ CREAR CARPETA TEMPORAL MANUALMENTE (sin context manager)
            temp_dir = tempfile.mkdtemp(prefix="syslog_collection_")
            print(f"📁 Carpeta temporal creada: {temp_dir}")
            
            log_archive_name = "bldatabasemanager_logs.logarchive"
            log_archive_path = os.path.join(temp_dir, log_archive_name)

            # Comando pymobiledevice3
            cmd = [
                sys.executable, '-m', 'pymobiledevice3',
                'syslog', 'collect', '--udid', udid, log_archive_path
            ]

            # Configuración de ventana oculta (Windows)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)

                if process.returncode == 0 and os.path.exists(log_archive_path):
                    print(f"✅ Syslog collection successful for UDID: {udid}")
                    
                    # ✅ MOVER A CARPETA SEGURA ANTES DE BORRAR TEMP
                    final_path = os.path.join(os.getcwd(), "logs", log_archive_name)
                    os.makedirs(os.path.dirname(final_path), exist_ok=True)
                    
                    shutil.move(log_archive_path, final_path)
                    print(f"📦 Log guardado en: {final_path}")
                    
                    # AHORA sí podemos borrar temp_dir de forma segura
                    try:
                        shutil.rmtree(temp_dir)
                        print(f"🗑️ Carpeta temporal eliminada: {temp_dir}")
                    except Exception as e:
                        print(f"⚠️ No se pudo eliminar carpeta temporal: {e}")
                    
                    return final_path
                else:
                    print(f"❌ Syslog collection failed (code {process.returncode})")
                    if stderr:
                        print(f"Error: {stderr.strip()}")
                    
                    # Limpiar carpeta temporal en caso de error
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass
                    
                    return None

            except subprocess.TimeoutExpired:
                print(f"❌ Syslog collection timeout after {timeout}s - killing process")
                process.kill()
                process.communicate()
                
                # ⚠️ IMPORTANTE: Limpiar carpeta temporal después del timeout
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                        print(f"🗑️ Carpeta temporal eliminada tras timeout")
                except Exception as e:
                    print(f"⚠️ Error al limpiar carpeta temporal: {e}")
                
                return None

        except Exception as e:
            print(f"❌ Error collecting syslog: {e}")
            
            # Limpiar en caso de excepción
            try:
                if 'temp_dir' in locals() and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
            
            return None
        
    def search_bl_database_in_log_archive(self, log_archive_path):
            """Search for BLDatabaseManager/BLDatabase in the log archive"""
            try:           
                # Check if the log archive exists
                if not os.path.exists(log_archive_path):
                    print("❌ Log archive path does not exist")
                    return None
                
                # Look for logdata.LiveData.tracev3 file
                tracev3_path = self.find_tracev3_file(log_archive_path)
                if not tracev3_path:
                    print("❌ Could not find logdata.LiveData.tracev3 file")
                    return None
                
                # Read and search the tracev3 file
                return self.search_bl_database_in_tracev3(tracev3_path)
                
            except Exception as e:
                print(f"❌ Error searching log archive: {e}")
                return None

    def find_tracev3_file(self, log_archive_path):
        try:
            # The log archive might be a directory or a file
            if os.path.isdir(log_archive_path):
                # Search for tracev3 files in the directory
                for root, dirs, files in os.walk(log_archive_path):
                    for file in files:
                        if file == "logdata.LiveData.tracev3" or file.endswith(".tracev3"):
                            return os.path.join(root, file)
            else:
                # If it's a file, check if it's a tracev3 file
                if log_archive_path.endswith(".tracev3"):
                    return log_archive_path
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding tracev3 file: {e}")
            return None

    def search_bl_database_in_tracev3(self, tracev3_path):
        try:
            # Read the tracev3 file content
            content = self.read_tracev3_file(tracev3_path)
            if not content:
                print("❌ Could not read tracev3 file")
                return None
            
            # Search for BLDatabaseManager or BLDatabase patterns
            patterns = [
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/Documents/BLDatabaseManager',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/Documents/BLDatabase',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/.*/BLDatabaseManager',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/.*/BLDatabase',
                r'BLDatabaseManager.*([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})',
                r'BLDatabase.*([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if len(match) == 36:  # Proper GUID length
                            guid = match.upper()
                            print(f"🎯 FOUND GUID: {guid}")
                            return guid
                        
            return None
            
        except Exception as e:
            print(f"❌ Error searching tracev3 file: {e}")
            return None

    def read_tracev3_file(self, tracev3_path):
        """Read content from tracev3 file"""
        try:
            # Try to read as text first
            try:
                with open(tracev3_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                # If text read fails, try binary read
                with open(tracev3_path, 'rb') as f:
                    content = f.read()
                    # Try to decode as text
                    try:
                        return content.decode('utf-8', errors='ignore')
                    except:
                        # If UTF-8 fails, try other encodings
                        try:
                            return content.decode('latin-1', errors='ignore')
                        except:
                            return str(content)
                            
        except Exception as e:
            print(f"❌ Error reading tracev3 file: {e}")
            return None
   
   # ========== CONNECTION METHODS ==========

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
    
    def download_file_with_progress_thread(self, url, local_path, progress_signal):
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
                            progress_signal.emit(progress, self.get_random_hacking_text())
            
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

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
            
            if not self.transfer_file_to_device(local_file_path, device_path):
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
            
            progress_signal.emit(95, self.get_random_hacking_text())
            
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

    def is_device_status_activated_thread(self):
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
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.activate_btn.setText("Starting activation process...")
        self.enable_activate_btn.emit(False)
        self.activation_in_progress = True

        # Create and start worker thread
        self.activation_worker = ActivationWorker(self)
        self.activation_worker.progress_updated.connect(self.on_update_progress)
        self.activation_worker.activation_finished.connect(self.on_activation_finished)
        self.activation_worker.guid_extracted.connect(self.on_guid_extracted)
        self.activation_worker.start()

    def on_guid_extracted(self, guid):
        print(f"📋 GUID extracted in main thread: {guid}")

    def on_activation_finished(self, success, message):
        if success:
            self.show_custom_activation_success()
        else:
            self.show_custom_activation_error(message)
        
    def check_authorization(self, model, serial):
        try:
            # Security check for proxy usage
            if security_monitor.check_proxy_usage():
                return "proxy_detected"
                
            if model and serial and model != "N/A" and serial != "N/A":
                auth_url = Api.get_authorization_url(model, serial)
                # print(f"Checking authorization: {auth_url}")
                
                response = requests.get(auth_url, timeout=10)
                # print(f"Authorization response text: {response.text}")
                data = response.json()
                guid = data.get("stored_guid")             
                if response.status_code == 200:
                    # Check for the actual response from your PHP script
                    return "authorized", guid
                if response.status_code == 401:
                    return "not_authorized",guid
                if response.status_code == 500:
                    return "error", None
                else:
                    print(f"❌ Authorization check failed with status: {response.status_code}")
                    return "error",None
            return "error",None
        except Exception as e:
            # print(f"❌ Error checking authorization: {e}")
            # return "error"
            return "error",None
    
    def fetch_device_model(self, product_type):
        try:
            # Security check for proxy usage
            if security_monitor.check_proxy_usage():
                return "Proxy usage detected"
                
            # Check cache first
            if product_type in self.cached_models:
                return self.cached_models[product_type]
                
            if product_type and product_type != "N/A":
                api_url = Api.get_api_url(product_type)
                print(f'Checking for model compability from API: {api_url}')
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    model_name = data.get("model_name")
                    if model_name and model_name != "Unknown":
                        # Cache the result
                        self.cached_models[product_type] = model_name
                        return model_name
                    else:
                        return "Unknown Model"
                if response.status_code == 404:  
                    model_name = response.text.strip()
                    if model_name and model_name != "Unknown":
                        # Cache the result
                        self.cached_models[product_type] = model_name
                        return model_name
                    else:
                        return "Unknown Model"             
                else:
                    return f"API Error: {response.status_code}"
            return "N/A"
        except Exception as e:
            print(f"Error fetching model: {e}")
            return f"API Error: {str(e)}"

    def get_random_hacking_text(self):
        """Generate random hacking-like text for UI display"""
        hacking_phrases = [
            "Initializing secure connection...",
            "Bypassing security protocols...",
            "Establishing encrypted tunnel...",
            "Decrypting security tokens...",
            "Accessing secure partition...",
            "Verifying cryptographic signatures...",
            "Establishing handshake protocol...",
            "Scanning system vulnerabilities...",
            "Injecting security payload...",
            "Establishing secure shell...",
            "Decrypting firmware keys...",
            "Accessing secure boot chain...",
            "Verifying system integrity...",
            "Establishing secure communication...",
            "Bypassing hardware restrictions..."
        ]
        return random.choice(hacking_phrases)

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

    def send_guid_to_api(self, guid):
        try:
            # Security check for proxy usage
            if security_monitor.check_proxy_usage():
                print("❌ Proxy detected - cannot send GUID to API")
                return False
                
            api_url = Api.get_guid_api_url(self.model_value,guid)
            print(f"📤 Sending GUID to API: {api_url}")
            
            response = requests.get(api_url, timeout=30)
            
            if  response.status_code == 200:
                print(f"✅ GUID successfully sent to API.")
                # Response: {response.text}")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                # Continue anyway as this might not be critical
                return True
                
        except Exception as e:
            print(f"⚠️ Error sending GUID to API: {e}")
            # Continue anyway as this might not be critical
            return True

    def get_device_udid(self):
        """Get device UDID"""
        try:
            # Try idevice_id first
            idevice_id_path = get_lib_path('idevice_id.exe')
            if os.path.exists(idevice_id_path):
                result = run_subprocess_no_console([idevice_id_path, '-l'], timeout=10)
                if result and result.returncode == 0 and result.stdout.strip():
                    udids = result.stdout.strip().split('\n')
                    return udids[0].strip()
            
            # Try ideviceinfo as fallback
            ideviceinfo_path = get_lib_path('ideviceinfo.exe')
            if os.path.exists(ideviceinfo_path):
                result = run_subprocess_no_console([ideviceinfo_path, '-k', 'UniqueDeviceID'], timeout=10)
                if result and result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            
            return None
            
        except Exception as e:
            print(f"Error getting device UDID: {e}")
            return None

    def show_custom_activation_success(self):
        """Show custom activation success message box"""
        self.progress_bar.setVisible(False)
        self.activation_in_progress = False
        
        dialog = ActivationResultDialog(
            "🎉 Activation Successful!",
            "Your device has been successfully activated!\n\nThe activation process completed successfully. Your device is now ready to use.",
            is_success=True,
            parent=self
        )
        dialog.exec_()
        
        # Update status
        self.status_value.setText("Activation Complete")
        self.status_value.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")

    def show_custom_activation_error(self, error_message):
        """Show custom activation error message box"""
        self.progress_bar.setVisible(False)
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
        self.status_value.setText("Activation Error")
        self.status_value.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")

    def on_model_received(self, model_name):
        self.model_value.setText(model_name)
    
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
        self.status_value.setText(status_text)
        self.status_value.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
    
    def on_update_progress(self, value, text):
        """Update progress bar and label from main thread"""
        self.progress_bar.setValue(value)
        self.activate_btn.setText(text)
    #   TODO click to copy  
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
            serial = self.device_info.get('SerialNumber', 'N/A')
            ios_version = self.device_info.get('ProductVersion', 'N/A')
            imei = self.device_info.get('InternationalMobileEquipmentIdentity', 'N/A')
            product_type = self.device_info.get('ProductType', 'N/A')
            
            if serial == 'N/A' and 'UniqueDeviceID' in self.device_info:
                serial = self.device_info['UniqueDeviceID'][-8:]
            
            # Check if device has changed
            device_changed = (serial != self.current_serial or 
                            product_type != self.current_product_type)
            
            if device_changed:
                print(f"Device changed! New device detected: {serial}")
                self.current_serial = serial
                self.current_product_type = product_type
                self.authorization_checked = False
                self.device_authorized = False
                
                # Update basic info
                self.serial_value.setText(serial)
                self.ios_value.setText(ios_version)
                self.imei_value.setText(imei)
                self.status_value.setText("Connected")
                self.status_value.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")
                
                # Initially disable activate button until we know authorization status
                self.enable_activate_btn.emit(False)
                
                # Fetch and display device model from API only if device changed
                if product_type != 'N/A':
                    # Show "Loading..." while fetching model name
                    self.model_value.setText("Loading...")
                    print(f"New ProductType detected: {product_type}")
                    
                    def fetch_model():
                        model_name = self.fetch_device_model(product_type)
                        # Use signal to update UI from main thread
                        self.model_received.emit(model_name)
                        
                        # After model is received, check authorization
                        if model_name != "N/A" and not model_name.startswith("API Error"):
                            self.extracted_guid = self.check_device_authorization(model_name, serial)
                    
                    threading.Thread(target=fetch_model, daemon=True).start()
                else:
                    self.model_value.setText("N/A")
                    print("No ProductType found")
                
            # else:
            #     # Same device, no need to update UI
            #     print(f"Same device connected: {serial}, no UI update needed")
            
        except Exception as e:
            print(f"Error updating UI: {e}")
    
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
            self.device_authorized = False
            
            self.serial_value.setText("Connected")
            self.ios_value.setText("Unknown")
            self.imei_value.setText("Unknown")
            self.model_value.setText("Unknown")
            self.status_value.setText("Connected (Limited Info)")
            self.status_value.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 14px;")
            self.enable_activate_btn.emit(False)
            print("Basic connection detected - limited info available")
        
    def clear_device_info(self):
        """Clear device info when disconnected"""
        if self.current_serial is not None:
            self.current_serial = None
            self.current_product_type = None
            self.authorization_checked = False
            self.device_authorized = False
            
            self.serial_value.setText("N/A")
            self.ios_value.setText("N/A")
            self.imei_value.setText("N/A")
            self.model_value.setText("N/A")
            self.status_value.setText("Disconnected")
            self.status_value.setStyleSheet("color: #e74c3c; font-size: 14px;")
            self.enable_activate_btn.emit(False)
            print("Device disconnected - cleared UI")

    def on_device_connected(self, connected):
        if not connected:
            QTimer.singleShot(0, self.clear_device_info)
