from core.afc_service import AFCService

class GarbageCollector(AFCService):
    def __init__(self):
        pass

    def cleanup_device_folders_thread(self):
        try:
            print("🧹 Starting device folder cleanup...")
            
            downloads_success = self.clean_downloads_folder()
            books_success = self.clean_books_folder()
            itunes_success = self.clean_itunes_control_folder()
            metaatastore_success = self.clean_books_MetadataStore_folder()
            
            return downloads_success and books_success and itunes_success and metaatastore_success
            
        except Exception as e:
            return False
       
    def clean_downloads_folder(self):
        return self.clean_folder("Downloads/", log_name="Downloads")
    
    def clean_books_folder(self):
        return self.clean_folder("Books/", log_name="Books")
        
    def clean_books_MetadataStore_folder(self):
        return self.clean_folder("Books/MetadataStore", log_name="MetadataStore")
   
    def clean_itunes_control_folder(self):
        return self.clean_folder("iTunes_Control/iTunes/", log_name="Itunes_Control")
    