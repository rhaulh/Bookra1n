import logging
from core.afc_service import AFCService

class GarbageCollector(AFCService):
    logger = logging.getLogger("bookra1n")
    def __init__(self):
        pass

    def cleanup_device_folders(self):
        try:
            self.logger.debug("Starting device folder cleanup...")
            
            downloads_success = self.clean_downloads_folder()
            books_success = self.clean_books_folder()
            itunes_success = self.clean_itunes_control_folder()
            metaatastore_success = self.clean_books_MetadataStore_folder()
           
            self.logger.info("Folder cleanup Completed.")
            return downloads_success and books_success and itunes_success and metaatastore_success
            
        except Exception as e:
            self.logger.error(f"Error during clean folder process: {e}")
            return False
       
    def clean_downloads_folder(self):
        return self.clean_folder("Downloads/", log_name="Downloads")
    
    def clean_books_folder(self):
        return self.clean_folder("Books/", log_name="Books")
        
    def clean_books_MetadataStore_folder(self):
        return self.clean_folder("Books/MetadataStore", log_name="MetadataStore")
   
    def clean_itunes_control_folder(self):
        return self.clean_folder("iTunes_Control/iTunes/", log_name="Itunes_Control")
    