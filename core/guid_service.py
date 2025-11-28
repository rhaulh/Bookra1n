import os
import tempfile
import re
import subprocess
import sys
import shutil
from utils.helpers import run_subprocess_no_console, get_lib_path
from core.api import API
from core.garbage_colector import GarbageCollector

class GuidService(GarbageCollector):
    guid = None
    max_attempts = 4
    patterns = [
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/Documents/BLDatabaseManager',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/Documents/BLDatabase',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/.*/BLDatabaseManager',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/.*/BLDatabase',
                r'BLDatabaseManager.*([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})',
                r'BLDatabase.*([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})'
            ]
    
    def __init__(self,progress_updated,guid_extracted):
        self.progress_updated = progress_updated
        self.guid_extracted = guid_extracted
       
    def get_device_udid(self):
        try:
            # Try idevice_id first
            idevice_id_path = get_lib_path('idevice_id.exe')
            if os.path.exists(idevice_id_path):
                result = run_subprocess_no_console([idevice_id_path, '-l'], timeout=10)
                if result and result.returncode == 0 and result.stdout.strip():
                    udids = result.stdout.strip().split('\n')
                    return True, udids[0].strip()
            
            # Try ideviceinfo as fallback
            ideviceinfo_path = get_lib_path('ideviceinfo.exe')
            if os.path.exists(ideviceinfo_path):
                result = run_subprocess_no_console([ideviceinfo_path, '-k', 'UniqueDeviceID'], timeout=10)
                if result and result.returncode == 0 and result.stdout.strip():
                    return True, result.stdout.strip()
            
            return False,None
            
        except Exception as e:
            print(f"Error getting device UDID: {e}")
            return False,None

    def try_to_get_cached_guid(self,serial):
        success,guid = API.fetch_guid(serial)
        if success:
            print(f"Found GUID in Cache: {guid}")
            return True,guid
        return False,None
    
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
            success,udid = self.get_device_udid()
            if not success:
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
            temp_dir = tempfile.mkdtemp(prefix="syslog_collection_")
            print(f"📁 Carpeta temporal creada: {temp_dir}")
            
            log_archive_name = "bldatabasemanager_logs.logarchive"
            log_archive_path = os.path.join(temp_dir, log_archive_name)

            cmd = [
                sys.executable, '-m', 'pymobiledevice3',
                'syslog', 'collect', '--udid', udid, log_archive_path
            ]

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
                    
                    final_path = os.path.join(os.getcwd(), "logs", log_archive_name)
                    os.makedirs(os.path.dirname(final_path), exist_ok=True)
                    
                    shutil.move(log_archive_path, final_path)
                    print(f"📦 Log saved in: {final_path}")
                    
                    try:
                        shutil.rmtree(temp_dir)
                        print(f"🗑️ Temp folder deleted: {temp_dir}")
                    except Exception as e:
                        print(f"⚠️ No temp folder found: {e}")
                    
                    return final_path
                else:
                    print(f"❌ Syslog collection failed (code {process.returncode})")
                    if stderr:
                        print(f"Error: {stderr.strip()}")
                    
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass
                    
                    return None

            except subprocess.TimeoutExpired:
                print(f"❌ Syslog collection timeout after {timeout}s - killing process")
                process.kill()
                process.communicate()
                
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                        print(f"🗑️ Temp folder deleted after timeout")
                except Exception as e:
                    print(f"⚠️ Failed to delete temp folder: {e}")
                
                return None

        except Exception as e:
            print(f"❌ Error collecting syslog: {e}")
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
            
            for pattern in self.patterns:
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