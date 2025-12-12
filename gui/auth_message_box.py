from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AuthMessageBoxUI(object):
    def setupUi(self, AuthMessageBoxUI):
        AuthMessageBoxUI.setObjectName("AuthMessageBoxUI")
        AuthMessageBoxUI.resize(560, 400)
        AuthMessageBoxUI.setMinimumSize(QtCore.QSize(560, 400))
        AuthMessageBoxUI.setMaximumSize(QtCore.QSize(560, 400))
        AuthMessageBoxUI.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        AuthMessageBoxUI.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        AuthMessageBoxUI.setModal(True)

        # Main container with glassmorphism effect matching main window
        self.central_widget = QtWidgets.QWidget(AuthMessageBoxUI)
        self.central_widget.setGeometry(QtCore.QRect(15, 15, 530, 370))
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet("""
            QWidget#central_widget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(43, 50, 178, 230),
                    stop:1 rgba(20, 136, 204, 230)
                );
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 40);
            }
        """)

        # Add shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QtGui.QColor(0, 0, 0, 120))
        self.central_widget.setGraphicsEffect(shadow)

        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        # Close button (top-right corner)
        self.close_btn = QtWidgets.QPushButton(self.central_widget)
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.close_btn.setText("⨉")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 30);
                color: white;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 48, 200);
                border-color: rgba(255, 59, 48, 255);
            }
        """)
        self.close_btn.move(485, 15)

        # Title
        self.labelTitle = QtWidgets.QLabel(self.central_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(28)
        self.labelTitle.setFont(font)
        self.labelTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTitle.setStyleSheet("color: #ff6b6b; background: transparent;")
        self.labelTitle.setText("Activation Required")
        self.layout.addWidget(self.labelTitle)

        # Message
        self.labelMessage = QtWidgets.QLabel(self.central_widget)
        font_msg = QtGui.QFont()
        font_msg.setFamily("Segoe UI")
        font_msg.setPointSize(9)
        self.labelMessage.setFont(font_msg)
        self.labelMessage.setAlignment(QtCore.Qt.AlignCenter)
        self.labelMessage.setWordWrap(True)
        self.labelMessage.setStyleSheet("""
            color: white;
        """)
        self.layout.addWidget(self.labelMessage)

        # Serial Number (highlighted)
        self.labelSerial = QtWidgets.QLabel(self.central_widget)
        font_serial = QtGui.QFont()
        font_serial.setFamily("Consolas")
        font_serial.setPointSize(16)
        font_serial.setBold(True)
        self.labelSerial.setFont(font_serial)
        self.labelSerial.setAlignment(QtCore.Qt.AlignCenter)
        self.labelSerial.setStyleSheet("""
            color: white;
            background: rgba(255, 107, 107, 150);
            border: 2px solid rgba(255, 107, 107, 200);
            border-radius: 15px;
            letter-spacing: 2px;
        """)
        self.layout.addWidget(self.labelSerial)

        # Info text
        self.labelInfo = QtWidgets.QLabel(self.central_widget)
        font_info = QtGui.QFont()
        font_info.setFamily("Segoe UI")
        font_info.setPointSize(11)
        self.labelInfo.setFont(font_info)
        self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.labelInfo.setWordWrap(True)
        self.labelInfo.setStyleSheet("color: rgba(255, 255, 255, 180);")
        self.layout.addWidget(self.labelInfo)

        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(spacer)

        # Buttons Layout
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setSpacing(15)

        # Cancel Button
        self.btnCancel = QtWidgets.QPushButton(self.central_widget)
        self.btnCancel.setMinimumSize(QtCore.QSize(0, 50))
        self.btnCancel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnCancel.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 30);
                color: white;
                border: 2px solid rgba(255, 255, 255, 80);
                border-radius: 25px;
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: bold;
                padding: 0 30px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 50);
                border-color: rgba(255, 255, 255, 150);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 70);
            }
        """)
        self.button_layout.addWidget(self.btnCancel)

        # Proceed Button (Main action)
        self.btnProceed = QtWidgets.QPushButton(self.central_widget)
        self.btnProceed.setMinimumSize(QtCore.QSize(0, 50))
        self.btnProceed.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnProceed.setDefault(True)
        self.btnProceed.setStyleSheet("""
            QPushButton {
                background: rgba(255, 107, 107, 200);
                color: white;
                border: none;
                border-radius: 25px;
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: bold;
                padding: 0 30px;
            }
            QPushButton:hover {
                background: rgba(255, 107, 107, 255);
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QPushButton:pressed {
                background: rgba(255, 80, 80, 255);
            }
        """)
        self.button_layout.addWidget(self.btnProceed)

        self.layout.addLayout(self.button_layout)

        self.retranslateUi(AuthMessageBoxUI)
        QtCore.QMetaObject.connectSlotsByName(AuthMessageBoxUI)

    def retranslateUi(self, AuthMessageBoxUI):
        _translate = QtCore.QCoreApplication.translate
        AuthMessageBoxUI.setWindowTitle(_translate("AuthMessageBoxUI", "Bookra1n - Activation"))
        self.labelTitle.setText(_translate("AuthMessageBoxUI", "Activation Required"))
        self.labelMessage.setText(_translate("AuthMessageBoxUI",
            "Your device needs to be activated with a valid serial number to continue the bypass process."))
        self.labelSerial.setText(_translate("AuthMessageBoxUI", "Serial: XXXXXXXXXXXXXX"))
        self.labelInfo.setText(_translate("AuthMessageBoxUI",
            "Click <b>Proceed to Send</b> to send sn securely."))
        self.btnCancel.setText(_translate("AuthMessageBoxUI", "Cancel"))
        self.btnProceed.setText(_translate("AuthMessageBoxUI", "Proceed to Send"))