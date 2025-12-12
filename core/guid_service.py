import os
import subprocess
import tempfile
import re
import shutil
import logging
import time
from utils.helpers import run_subprocess_no_console, get_lib_path
from core.garbage_colector import GarbageCollector

class GuidService(GarbageCollector):
    logger = logging.getLogger("bookra1n")
    udid = None
    patterns = [
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/Documents/BLDatabaseManager',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/Documents/BLDatabase',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/.*/BLDatabaseManager',
                r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})/.*/BLDatabase',
                r'BLDatabaseManager.*([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})',
                r'BLDatabase.*([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})'
            ]
    
    def __init__(self):
        pass

    def extract_guid_proper_method(self, udid, progress_value, progress_signal):
        try:

            self.udid = udid
            
            progress_signal.emit(progress_value + 2, "Cleaning downloads folders...")
            if not self.clean_downloads_folder():
                self.logger.debug("Could not clean downloads folders")   
            
            self.logger.info(f"Collecting system logs for UDID: {self.udid}")

            log_archive_path = self.collect_syslog_with_pymobiledevice()
            if not log_archive_path:
                self.logger.critical("Failed to collect syslog")
                return None
            
            progress_signal.emit(progress_value + 2, "Searching for GUID in logs...")
            guid = self.search_bl_database_in_log_archive(log_archive_path) 
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
            self.logger.debug(f"GUID extraction error: {e}")
            return None
        
    def collect_syslog_with_pymobiledevice(self):
        try:
            temp_dir = tempfile.mkdtemp()
            log_archive_name = "bldatabasemanager_logs.logarchive"
            log_archive_path = os.path.join(temp_dir, log_archive_name)

            pymobiledevice3_path = get_lib_path("pymobiledevice3.exe")
            if not os.path.exists(pymobiledevice3_path):
                raise Exception("pymobiledevice3.exe not found in libs folder")

            cmd = [
                pymobiledevice3_path,
                "syslog",
                "collect",
                "--udid", self.udid,
                log_archive_path,
            ]
     
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
            
            process = subprocess.Popen(
                cmd,
                startupinfo=startupinfo,
                creationflags=creationflags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True
            )
            
            try:
                # Wait for process with timeout
                stdout, stderr = process.communicate(timeout=120)
                
                if process.returncode == 0:
                    self.logger.info("Syslog collection successful")
                    if os.path.exists(log_archive_path):
                        self.logger.info(f"Log archive created: {log_archive_path}")
                        return log_archive_path
                    else:
                        self.logger.error("Log archive file not found after successful collection")
                        return None
                else:
                    self.logger.error(f"Syslog collection failed with return code: {process.returncode}")
                    if stderr:
                        print(f"Error: {stderr.strip()}")
                    return None
                    
            except subprocess.TimeoutExpired:
                self.logger.error("Syslog collection timeout - killing process")
                process.kill()
                stdout, stderr = process.communicate()
                return None
                
        except Exception as e:
            self.logger.info(f"Error collecting syslog: {e}")
            return None
  
    def search_bl_database_in_log_archive(self, log_archive_path):
        self.logger.info("Looking for saved logs")
        try:           
            if not os.path.exists(log_archive_path):
                self.logger.debug("Log archive path does not exist")
                return None
            
            tracev3_path = self.find_tracev3_file(log_archive_path)
            if not tracev3_path:
                self.logger.debug("Could not find logdata.LiveData.tracev3 file")
                return None
            
            return self.search_bl_database_in_tracev3(tracev3_path)
            
        except Exception as e:
            self.logger.error(f"Error searching log archive: {e}")
            return None
    
    def find_tracev3_file(self, log_archive_path):
        try:
            self.logger.debug("Looking for specific log in folder")
            if os.path.isdir(log_archive_path):
                for root, dirs, files in os.walk(log_archive_path):
                    for file in files:
                        if file == "logdata.LiveData.tracev3" or file.endswith(".tracev3"):
                            return os.path.join(root, file)
            else:
                self.logger.debug("Looking for specific file")
                if log_archive_path.endswith(".tracev3"):
                    return log_archive_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding tracev3 file: {e}")
            return None

    def search_bl_database_in_tracev3(self, tracev3_path):
        try:
            self.logger.info("Searching for Target file")
            content = self.read_tracev3_file(tracev3_path)
            if not content:
                self.logger.error("Could not read tracev3 file")
                return None
            
            for pattern in self.patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if len(match) == 36:
                            guid = match.upper()
                            return guid                  
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching tracev3 file: {e}")
            return None

    def read_tracev3_file(self, tracev3_path):
        try:
            self.logger.info("Scrapping for GUID")
            try:
                with open(tracev3_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                with open(tracev3_path, 'rb') as f:
                    content = f.read()
                    try:
                        return content.decode('utf-8', errors='ignore')
                    except:
                        try:
                            return content.decode('latin-1', errors='ignore')
                        except:
                            return str(content)
                            
        except Exception as e:
            self.logger.error(f"Error reading tracev3 file: {e}")
            return None