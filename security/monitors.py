# security/monitor.py
import os
import time
import inspect
import winreg
from gui.dialogs import CustomMessageBox
class SecurityMonitor:
    _instance = None
    _initialized = False

    def __init__(self):
        self.logger = None
        self.suspicious_activities = []
        self.start_time = time.time()

    @staticmethod
    def configure(logger):
        monitor = SecurityMonitor.getMonitor()
        if not SecurityMonitor._initialized:
            monitor.logger = logger
            SecurityMonitor._initialized = True
        return monitor

    @staticmethod
    def getMonitor():
        if SecurityMonitor._instance is None:
            SecurityMonitor._instance = SecurityMonitor()
        return SecurityMonitor._instance


    def check_code_injection(self):
        try:
            frames = inspect.stack()
            for frame in frames:
                if any(k in str(frame.code_context) for k in ['eval', 'exec', 'compile', '__import__']):
                    self.log_threat("Potential code injection", frame)
                    return True
        except:
            pass
        return False

    def check_api_sniffing(self):
        try:
            current = inspect.currentframe()
            for frame_info in inspect.getouterframes(current):
                for var_value in frame_info.frame.f_locals.values():
                    if "TELEGRAM_BOT_TOKEN" in str(var_value):
                        self.log_threat("Unauthorized token access", frame_info)
                        return True
        except:
            pass
        return False
    
    def check_proxy_usage(self):
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        for var in proxy_vars:
            if os.environ.get(var):
                self.log_threat(f"Proxy env var: {var}", None)
                return True

        if os.name == 'nt':
            try:
                key = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                                     r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
                if winreg.QueryValueEx(key, "ProxyEnable")[0]:
                    self.log_threat("Windows proxy enabled", None)
                    return True
            except:
                pass

        return False

    def log_threat(self, message, frame_info):
        if self.logger:
            self.logger.error(f"[SECURITY] {message}")
        os._exit(1)

    def continuous_monitoring(self):
        while True:
            if self.check_code_injection() or self.check_api_sniffing():
                break
            time.sleep(5)
    
    def show_proxy_warning_message(self):
        dialog = CustomMessageBox(
            "🚨 Security Violation",
            "Proxy usage detected!",
        )
        dialog.exec_()