import os
import tempfile
import time
import traceback
from utils.helpers import run_subprocess_no_console, get_lib_path
from core.device_commands import DeviceCommands
import logging

class AFCService(DeviceCommands):
    logger = logging.getLogger("bookra1n")

    def __init__(self):
        pass    

    def afc_client_operation(self, operation, *args):
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
        try:
            success, output = self.afc_client_operation('put', local_file_path, device_path)
            return success
        except Exception as e:
            self.logger.error(f"Error transferring file: {e}")
            return False
    
    def clean_folder(self, folder, exclude=None, only_files=False, log_name=None):
        try:
            folder = folder.rstrip('/') + '/'

            if exclude is None:
                exclude = ['.', '..']

            name = log_name or folder.strip('/')

            success, output = self.afc_client_operation('ls', folder)
            if not success:
                self.logger.warning(f"Could not list {name}")
                return False

            items = [item.strip() for item in output.strip().split('\n') if item.strip()]
            
            if not items:
                return True

            deleted_files = 0
            deleted_dirs = 0
            failed = []

            for item in items:
                if not item or item in exclude:
                    continue

                full_path = f"{folder}{item}"

                s_ok, stat = self.afc_client_operation("stat", full_path)
                if not s_ok:
                    self.logger.warning(f"Could not stat {full_path}")
                    failed.append(full_path)
                    continue

                is_dir = "st_ifmt: S_IFDIR" in stat

                if is_dir:
                    if only_files:
                        continue
                    
                    self.logger.debug(f"📁 Processing directory: {item}")
                    
                    clean_success = self.clean_folder(
                        full_path, 
                        exclude=exclude, 
                        only_files=False, 
                        log_name=item
                    )
                    
                    if not clean_success:
                        self.logger.warning(f"Failed to clean directory: {full_path}")
                        failed.append(full_path)
                        continue
                    
                    self.logger.debug(f"🗑️ Removing empty directory: {item}")
                    rm_success, rm_output = self.afc_client_operation("rmdir", full_path.rstrip('/'))
                    
                    if rm_success:
                        deleted_dirs += 1
                    else:
                        self.logger.warning(f"Could not remove directory {item}: {rm_output}")
                        failed.append(full_path)
                else:
                    rm_success, rm_output = self.afc_client_operation("rm", full_path)
                    
                    if rm_success:
                        deleted_files += 1
                    else:
                        self.logger.warning(f"Could not remove file {item}: {rm_output}")
                        failed.append(full_path)
            
            if failed:
                self.logger.warning(f"Failed to delete {len(failed)} items:")
                for f in failed[:5]:
                    self.logger.debug(f"  - {f}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error cleaning {name}: {e}")
            traceback.print_exc()
            return False

    def copy_file_from_device_to_device(self, source_path, dest_path):
        try:
 
            filename = os.path.basename(source_path)
            dest_path = dest_path + "/" + filename

            temp_dir = tempfile.mkdtemp()       
            tmp_local_path = os.path.join(temp_dir, filename)

            success, output = self.afc_client_operation("get", source_path, tmp_local_path)
            if not success:
                if os.path.exists(tmp_local_path):
                    os.remove(tmp_local_path)
                return False, f"Failed transferring file: {output}"

            success, output = self.afc_client_operation("put", tmp_local_path, dest_path)
            if not success:
                if os.path.exists(tmp_local_path):
                    os.remove(tmp_local_path)
                return False, f"Failed transferring file: {output}"

            if os.path.exists(tmp_local_path):
                os.remove(tmp_local_path)

            return True, "Transfer success"

        except Exception as e:
            self.logger.error(f"Error transferring file: {e}")

            return False, str(e)
        
    def check_if_file_injection_completed(self, payload, minimun_size):
        try:
            success, output = self.afc_client_operation('info', payload)
            if not success:
                return False
            
            size = None

            for line in output.splitlines():
                if line.startswith("st_size:"):
                    size = int(line.split(":")[1].strip())
                    break
                
            if size is not None and size > minimun_size:
                return True
            
            return False

        except Exception as e:
            self.logger.error(f"Error checking injection init: {e}")
            return False
    
    def transfer_local_file_to_device(self, folder, local_file_path):
        try:
            connected, strout = self.have_device_full_connection()
            if not connected:
                raise Exception("Device disconnected during transfer")
            
            filename = os.path.basename(local_file_path)
            device_path = f"{folder}/{filename}"
            
            if not self.transfer_file_to_device(local_file_path, device_path):
                raise Exception("Failed to transfer file to device")
            
            time.sleep(5)
            return True
                
        except Exception as e:
            raise Exception(f"Transfer error: {str(e)}")  
