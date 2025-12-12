import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent, QTimer,QObject
from utils.helpers import resource_path
from data.models import DeviceInfo

class Ui_MainWindow(QObject):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 550)
        MainWindow.setMinimumSize(QtCore.QSize(900, 550))
        MainWindow.setMaximumSize(QtCore.QSize(900, 550))
        MainWindow.setWindowTitle('Icon')
        MainWindow.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icon.ico').replace('\\', '/')))
        
        # Icon
        icon_path = resource_path("gui/logo.ico")
        if os.path.exists(icon_path):
            MainWindow.setWindowIcon(QtGui.QIcon(icon_path))
        
        self.style_sheet_path = resource_path("gui/styles.qss")
            
        # Increase all UI text size by 20%
        app = QtWidgets.QApplication.instance()
        if app is not None:
            try:
                f = app.font()
                # fallback if pointSizeF returns 0
                current = f.pointSizeF() if f.pointSizeF() > 0 else f.pointSize() or 10
                f.setPointSizeF(current * 1.0) # Reset to normal scaling for this design
                app.setFont(f)
            except Exception:
                pass

        # Frameless Window Setup
        MainWindow.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window
        )
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Apply background image with rounded corners
        bg_path = os.path.join(os.path.dirname(__file__), 'wall.jpeg').replace('\\', '/')
        if os.path.exists(bg_path):
            # We need to set the style on a frame inside centralwidget or centralwidget itself
            # To get rounded corners on the window, the central widget needs to have them and clip
            self.centralwidget.setStyleSheet(f"""
                QWidget#centralwidget {{
                    border-image: url('{bg_path}') 0 0 0 0 stretch stretch;
                    border-radius: 30px;
                }}
            """)
        else:
            self.centralwidget.setStyleSheet("""
                QWidget#centralwidget {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2b32b2, stop:1 #1488cc);
                    border-radius: 30px;
                }
            """)


        # Main Horizontal Layout
        self.horizontalLayout_main = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_main.setSpacing(0)
        self.horizontalLayout_main.setObjectName("horizontalLayout_main")

        # Left Panel (iPhone Image)
        self.left_panel = QtWidgets.QWidget(self.centralwidget)
        self.left_panel.setMinimumSize(QtCore.QSize(350, 0))
        self.left_panel.setStyleSheet("background: transparent;")
        self.left_panel.setObjectName("left_panel")
        
        # Use Stacked Layout for overlay
        self.stacked_layout = QtWidgets.QStackedLayout(self.left_panel)
        self.stacked_layout.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        self.stacked_layout.setContentsMargins(0, 50, 0, 0) # Push image down a bit
        
        # Layer 1: iPhone/Hmm Image
        self.iphone_label = QtWidgets.QLabel(self.left_panel)
        self.iphone_label.setAlignment(QtCore.Qt.AlignCenter)
        self.stacked_layout.addWidget(self.iphone_label)
        
        # Layer 2: Rocket Animation
        self.rocket_label = QtWidgets.QLabel(self.left_panel)
        self.rocket_label.setAlignment(QtCore.Qt.AlignCenter)
        self.rocket_label.setStyleSheet("background: transparent;")
        self.stacked_layout.addWidget(self.rocket_label)
        
        # Default to disconnected.png (disconnected state)
        self.set_device_connection_image(False)
        
        self.horizontalLayout_main.addWidget(self.left_panel)

        # Right Panel (Content)
        self.right_panel = QtWidgets.QWidget(self.centralwidget)
        self.right_panel.setStyleSheet("background: rgba(0, 0, 0, 100); border-top-left-radius: 30px; border-top-right-radius: 30px; border-bottom-right-radius: 30px;") # Semi-transparent dark overlay
        self.right_panel.setObjectName("right_panel")
        self.verticalLayout_right = QtWidgets.QVBoxLayout(self.right_panel)
        self.verticalLayout_right.setContentsMargins(40, 40, 40, 40)
        self.verticalLayout_right.setSpacing(10)
        self.verticalLayout_right.setObjectName("verticalLayout_right")

        # Header Section
        self.header_frame = QtWidgets.QFrame(self.right_panel)
        self.header_frame.setStyleSheet("background: transparent; border: none;")
        self.header_frame.setObjectName("header_frame")
        self.horizontalLayout_header = QtWidgets.QHBoxLayout(self.header_frame)
        self.horizontalLayout_header.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_header.setSpacing(15)
        
        # Logo
        self.logo_label = QtWidgets.QLabel(self.header_frame)
        self.logo_label.setFixedSize(60, 60)
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png').replace('\\', '/')
        if os.path.exists(logo_path):
            self.logo_label.setPixmap(QtGui.QPixmap(logo_path).scaled(60, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logo_label.setObjectName("logo_label")
        self.horizontalLayout_header.addWidget(self.logo_label)

        # Title Container
        self.title_container = QtWidgets.QWidget(self.header_frame)
        self.verticalLayout_title = QtWidgets.QVBoxLayout(self.title_container)
        self.verticalLayout_title.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_title.setSpacing(0)

        self.app_title = QtWidgets.QLabel(self.title_container)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(36)
        self.app_title.setFont(font)
        self.app_title.setStyleSheet("color: #ff6b6b;") # Reddish/Pink color from screenshot
        self.app_title.setObjectName("app_title")
        self.verticalLayout_title.addWidget(self.app_title)

        self.app_subtitle = QtWidgets.QLabel(self.title_container)
        font_sub = QtGui.QFont()
        font_sub.setFamily("Segoe UI")
        font_sub.setPointSize(12)
        self.app_subtitle.setFont(font_sub)
        self.app_subtitle.setStyleSheet("color: rgba(255, 255, 255, 150);")
        self.app_subtitle.setObjectName("app_subtitle")
        self.verticalLayout_title.addWidget(self.app_subtitle)
        
        self.horizontalLayout_header.addWidget(self.title_container)
        self.horizontalLayout_header.addStretch()
        
        # Close Button
        self.close_btn = QtWidgets.QPushButton(self.header_frame)
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.close_btn.setText("⨉")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 30);
                color: white;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 48, 200); /* Red hover */
                border-color: rgba(255, 59, 48, 255);
                color:white;
            }
        """)
        self.close_btn.clicked.connect(MainWindow.close)
        self.horizontalLayout_header.addWidget(self.close_btn)
        
        self.verticalLayout_right.addWidget(self.header_frame)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_right.addItem(spacerItem)

        # Info Section
        self.info_frame = QtWidgets.QFrame(self.right_panel)
        self.info_frame.setStyleSheet("background: transparent; border: none;")
        self.info_frame.setObjectName("info_frame")
        self.formLayout = QtWidgets.QFormLayout(self.info_frame)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setHorizontalSpacing(20)
        self.formLayout.setVerticalSpacing(10)

        def create_info_row(title_text, obj_name_prefix):
            title = QtWidgets.QLabel(self.info_frame)
            title.setText(title_text)
            title.setStyleSheet("color: rgba(255, 255, 255, 180); font-weight: bold; font-family: 'Segoe UI'; font-size: 10pt;")

            value = QtWidgets.QLabel(self.info_frame)
            value.setText("N/A")
            value.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 10pt;")
            value.setObjectName(f"{obj_name_prefix}_value")

            if obj_name_prefix == "serial":
                value.setCursor(Qt.PointingHandCursor)
                value.installEventFilter(self)
                self.serial_value_label = value

            # Store title ref if needed, though usually static
            setattr(self, f"{obj_name_prefix}_title", title)
            setattr(self, f"{obj_name_prefix}_value", value)
            
            return title, value
        
        self.formLayout.addRow(*create_info_row("DEVICE:", "name"))
        self.formLayout.addRow(*create_info_row("MODEL:", "model"))
        self.formLayout.addRow(*create_info_row("SN:", "serial"))
        self.formLayout.addRow(*create_info_row("iOS:", "ios"))
        self.formLayout.addRow(*create_info_row("IMEI:", "imei"))
        self.formLayout.addRow(*create_info_row("STATUS:", "status"))
        
        
        self.verticalLayout_right.addWidget(self.info_frame)

        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_right.addItem(spacerItem2)

        # Progress Bar
        self.progress_bar = QtWidgets.QProgressBar(self.right_panel)
        self.progress_bar.setVisible(False)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 30);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: #ff6b6b;
                border-radius: 2px;
            }
        """)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout_right.addWidget(self.progress_bar)

        # Activate Button
        self.activate_btn = QtWidgets.QPushButton(self.right_panel)
        if os.path.exists(self.style_sheet_path):
            with open(self.style_sheet_path, "r", encoding="utf-8") as f:
                self.button_styles = f.read()
                self.activate_btn.setStyleSheet(self.button_styles)
        else:
            self.button_styles = ""
        self.activate_btn.setEnabled(False)
        self.activate_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.activate_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.activate_btn.setObjectName("activate_btn")
        self.verticalLayout_right.addWidget(self.activate_btn)

        # Buttons OTA Layout
        self.hbox_ota = QtWidgets.QHBoxLayout()
        self.hbox_ota.setSpacing(10)  # opcional

        # Block OTA Button
        self.block_ota_btn = QtWidgets.QPushButton(self.right_panel)
        self.block_ota_btn.setStyleSheet(self.button_styles)
        self.block_ota_btn.setEnabled(False)
        self.block_ota_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.block_ota_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.block_ota_btn.setObjectName("block_ota_btn")

        # Enable OTA Button
        self.enable_ota_btn = QtWidgets.QPushButton(self.right_panel)
        self.enable_ota_btn.setStyleSheet(self.button_styles)
        self.enable_ota_btn.setEnabled(False)
        self.enable_ota_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.enable_ota_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.enable_ota_btn.setObjectName("enable_ota_btn")


        self.hbox_ota.addWidget(self.block_ota_btn)
        self.hbox_ota.addWidget(self.enable_ota_btn)


        self.verticalLayout_right.addLayout(self.hbox_ota)


        self.horizontalLayout_main.addWidget(self.right_panel)
        
        self.horizontalLayout_main.setStretch(0, 4) # Left
        self.horizontalLayout_main.setStretch(1, 6) # Right

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Bookra1n A12"))
        self.app_title.setText(_translate("MainWindow", "Bookra1n."))
        self.app_subtitle.setText(_translate("MainWindow", "A tool for everyone."))
        
        self.model_title.setText(_translate("MainWindow", "MODEL:"))
        self.serial_title.setText(_translate("MainWindow", "SN:"))
        self.ios_title.setText(_translate("MainWindow", "iOS:"))
        self.imei_title.setText(_translate("MainWindow", "IMEI:"))
        self.status_title.setText(_translate("MainWindow", "STATUS:"))
        
        self.status_value.setText(_translate("MainWindow", "Disconnected"))
        self.set_device_connection_status("Disconnected")
        self.activate_btn.setText(_translate("MainWindow", "Start Bypass"))
        self.block_ota_btn.setText(_translate("MainWindow", "Block OTA Updates"))
        self.enable_ota_btn.setText(_translate("MainWindow", "Enable OTA Updates"))

    # UPDATE UI WITH DEVICE INFO
    def update_ui(self,device:DeviceInfo):
        self.name_value.setText(device.name)
        self.model_value.setText(device.model)
        self.serial_value.setText(device.serial)
        self.ios_value.setText(device.ios)
        self.imei_value.setText(device.imei)

        if not device.authorized:
            self.set_device_connection_status(device.pair)
        else:
            self.update_status_label("Device Authorized", True) 
              
        self.on_set_activate_button_state(device.authorized)
        self.on_set_block_ota_button_state(device.activated)
        self.on_set_enable_ota_button_state(device.activated)

    # LABEL UPDATES
    def set_device_connection_status(self, status):
        status_text=None
        connected = True
        match status:
            case "Limited":
                status_text = "Connected (Limited info)"
            case "Full":
                status_text = "Connected"
            case "Disconnected":
                status_text = "Disconnected"
                connected = False
        self.update_connection_status_label(status_text,status)
        self.set_device_connection_image(connected) 

    def update_connection_status_label(self, status_text, status):
        color="#27ae60"
        match status:
            case "Limited":
                color = "#BA4415"
            case "Disconnected":
                color="#d22b18"
            case "Full":
                color = "#27ae60"
        self.status_value.setText(status_text)
        self.status_value.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")

    def update_status_label(self, status_text, success):
        color="#27ae60" if success else "#d22b18"
        self.status_value.setText(status_text)
        self.status_value.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")

    # BUTTON STATE UPDATES
    def on_set_activate_button_state(self, enabled):
        if enabled:
            self.set_btn_state(self.activate_btn, "ready", "Activate Device", True)
        else:
            self.set_btn_state(self.activate_btn, "waiting", "Waiting for Authorization...", False)
        self.refresh_btn_style(self.activate_btn)
    
    def on_set_block_ota_button_state(self, enabled):
        if enabled:
            self.set_btn_state(self.block_ota_btn, "ready", "Block OTA Updates", True)
        else:
            self.set_btn_state(self.block_ota_btn, "waiting", "Block OTA Updates", False)
        self.refresh_btn_style(self.block_ota_btn)
    
    def on_set_enable_ota_button_state(self, enabled):
        if enabled:
            self.set_btn_state(self.enable_ota_btn, "ready", "Enable OTA Updates", True)
        else:
            self.set_btn_state(self.enable_ota_btn, "waiting", "Enable OTA Updates", False)
        self.refresh_btn_style(self.enable_ota_btn)
    

    def set_btn_state(self, btn, state: str, text: str = None, enabled: bool = False):
        btn.setProperty("state", state)
        if text is not None:
            btn.setText(text)

        btn.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        btn.setEnabled(enabled)

    def refresh_btn_style(self, btn):
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        btn.update()
    
    def on_activation_started(self,activated):
        self.progress_bar.setVisible(activated)
        self.progress_bar.setValue(0 if activated else 100)
        self.activate_btn.setText("Starting Activation..." if activated else "Activate Device")
        self.update_status_label("Activation in Progress..." if activated else "Device Authorized", activated)
        self.on_set_activate_button_state(not activated)
        self.set_processing_image(activated if activated else False)
    
    # PROGRESS BAR UPDATES 
    def on_update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.activate_btn.setText(text)

    # GUI Images

    def set_device_connection_image(self, connected):
        img_name = 'connected.png' if connected else 'disconnected.png'
        img_path = os.path.join(os.path.dirname(__file__), img_name).replace('\\', '/')
        
        if os.path.exists(img_path):
            pixmap = QtGui.QPixmap(img_path)
            self.iphone_label.setPixmap(pixmap.scaled(300, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.iphone_label.setText(f"{img_name} missing")
            self.iphone_label.setStyleSheet("color: white; border: 1px solid white;")
    
    def set_processing_image(self, is_processing):
        self.is_animating = is_processing
        
        if is_processing:
            gif_path = os.path.join(os.path.dirname(__file__), 'rocket.gif').replace('\\', '/')
            if os.path.exists(gif_path):
                if not hasattr(self, 'movie'):
                    self.movie = QtGui.QMovie(gif_path)
                    self.movie.setScaledSize(QtCore.QSize(200, 200))
                    
                self.rocket_label.setMovie(self.movie)
                self.movie.start()
                self.rocket_label.setVisible(True)
                self.rocket_label.raise_()
            else:
                self.logger.debug("Rocket GIF not found")
        else:
            if hasattr(self, 'movie'):
                self.movie.stop()
            self.rocket_label.clear()
            self.rocket_label.setVisible(False)
    
    def set_device_activated_image(self):
        img_name = 'activated.png'
        img_path = os.path.join(os.path.dirname(__file__), img_name).replace('\\', '/')
        
        if os.path.exists(img_path):
            pixmap = QtGui.QPixmap(img_path)
            self.iphone_label.setPixmap(pixmap.scaled(300, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.iphone_label.setText(f"{img_name} missing")
            self.iphone_label.setStyleSheet("color: white; border: 1px solid white;")

    # Reset controls after activation process
    def reset_controls(self,completed):
        status = "Activation Complete"  if completed else "Activation Error"   
        self.progress_bar.setVisible(False)
        if completed:
            self.set_device_activated_image()
        self.update_status_label(status,completed)

    # UTILS
    def eventFilter(self, obj, event):
        if obj == self.serial_value_label and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.copy_to_clipboard()
                return True
        return super().eventFilter(obj, event)
    
    def copy_to_clipboard(self):
        current = self.serial_value_label.text().strip()
        if not current in ("N/A", "Disconnected", ""):
            QApplication.clipboard().setText(current)
            old_text = current
            self.serial_value_label.setText("Serial Copied!")
            self.serial_value_label.setStyleSheet("color: #90ee90; font-weight: bold;")
            
            QTimer.singleShot(1200, lambda: (
                self.serial_value_label.setText(old_text),
                self.serial_value_label.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 10pt;")
            ))