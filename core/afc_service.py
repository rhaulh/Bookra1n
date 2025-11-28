import os
import tempfile
import traceback
from utils.helpers import run_subprocess_no_console, get_lib_path
from core.device_commands import DeviceCommands

class AFCService(DeviceCommands):
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
            print(f"📥 Transfering file: {source_path}")

            temp_dir = tempfile.mkdtemp()
            filename = os.path.basename(source_path)
            tmp_local_path = os.path.join(temp_dir, filename)

            success, output = self.afc_client_operation("get", source_path, tmp_local_path)
            if not success:
                os.remove(tmp_local_path)
                return False, f"Failed transfering file to: {output}"
            
            dest_path = dest_path + "/" + filename

            success, output = self.afc_client_operation("put", tmp_local_path, dest_path)

            if not success:
                os.remove(tmp_local_path)
                return False, f"Failed transfering file to: {output}"

            os.remove(tmp_local_path)

            return True, "Transfer success"

        except Exception as e:
            print(f"❌ Error transfering file: {e}")
            return False, str(e)
