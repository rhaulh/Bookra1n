# dialogs.py
from PyQt5.QtWidgets import QDialog
from gui.custom_message_box import Ui_CustomMessageBoxUI
from gui.activation_result_dialog import Ui_ActivationResultDialogUI
from gui.instrutions_dialog import Ui_InstructionDialogUI
from gui.auth_message_box import Ui_AuthMessageBoxUI   
from gui.custom_alert_box import Ui_CustomAlertBoxUI
from gui.draggable import Draggable

class AuthMessageBox(QDialog,Draggable):
    def __init__(self, title="Activation Required", message=None, serial_number="Unknown", parent=None):
        super().__init__(parent)
        self.ui = Ui_AuthMessageBoxUI()
        self.ui.setupUi(self)

        self.ui.labelTitle.setText(title)
        self.ui.labelMessage.setText(message or "Your device needs to be activated with a valid serial number.")
        self.ui.labelSerial.setText(f"Serial: {serial_number}")

        self.ui.btnCancel.clicked.connect(self.reject)
        self.ui.close_btn.clicked.connect(self.reject)
        self.ui.btnProceed.clicked.connect(self.accept)

class CustomAlertBox(QDialog,Draggable):
    def __init__(self, title=None, message=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_CustomAlertBoxUI()
        self.ui.setupUi(self)

        self.ui.labelTitle.setText(title)
        self.ui.labelInfo.setText(message)

        self.ui.close_btn.clicked.connect(self.reject)
        self.ui.btnProceed.clicked.connect(self.accept)

class CustomMessageBox(QDialog,Draggable):
    def __init__(self, title=None, message=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_CustomMessageBoxUI()
        self.ui.setupUi(self)

        self.ui.labelTitle.setText(title)
        self.ui.labelInfo.setText(message)

        self.ui.btnCancel.clicked.connect(self.reject)
        self.ui.close_btn.clicked.connect(self.reject)
        self.ui.btnProceed.clicked.connect(self.accept)

class ActivationResultDialog(QDialog,Draggable):
    def __init__(self, title="", message=None, is_success=True, parent=None):
        super().__init__(parent)
        self.ui = Ui_ActivationResultDialogUI()
        self.ui.setupUi(self)

        self.ui.labelTitle.setText(title)
        self.ui.labelMessage.setText(message or ("Your device has been activated successfully!" if is_success else "Activation failed"))

        if is_success:
            self.ui.labelTitle.setStyleSheet("color: #50fa7b;")
            self.ui.labelInfo.setVisible(False)
            if hasattr(self.ui, "set_success"):
                self.ui.set_success()
        else:
            self.ui.labelTitle.setStyleSheet("color: #ff5555;")
            self.ui.labelInfo.setVisible(False)
            if hasattr(self.ui, "set_failed"):
                self.ui.set_failed(message)

        self.ui.btnOk.clicked.connect(self.accept)
        self.ui.close_btn.clicked.connect(self.reject)

class InstructionDialog(QDialog,Draggable):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_InstructionDialogUI()
        self.ui.setupUi(self)
        
        # Conectar botones
        self.ui.btnCancel.clicked.connect(self.reject)
        self.ui.btnContinue.clicked.connect(self.accept)
        self.ui.close_btn.clicked.connect(self.reject)
    
    @staticmethod
    def show_instructions(parent=None):
        dialog = InstructionDialog(parent)
        return dialog.exec_() 