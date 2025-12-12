from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CustomAlertBoxUI(object):
    def setupUi(self, CustomAlertBoxUI):
        CustomAlertBoxUI.setObjectName("CustomAlertBoxUI")
        CustomAlertBoxUI.resize(560, 400)
        CustomAlertBoxUI.setMinimumSize(QtCore.QSize(560, 400))
        CustomAlertBoxUI.setMaximumSize(QtCore.QSize(560, 400))
        CustomAlertBoxUI.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        CustomAlertBoxUI.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        CustomAlertBoxUI.setModal(True)

        # Main container with glassmorphism effect matching main window
        self.central_widget = QtWidgets.QWidget(CustomAlertBoxUI)
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

        self.retranslateUi(CustomAlertBoxUI)
        QtCore.QMetaObject.connectSlotsByName(CustomAlertBoxUI)

    def retranslateUi(self, CustomAlertBoxUI):
        _translate = QtCore.QCoreApplication.translate
        CustomAlertBoxUI.setWindowTitle(_translate("CustomAlertBoxUI", "Bookra1n - Activation"))
        self.labelTitle.setText(_translate("CustomAlertBoxUI", "Attention Required"))
        self.labelInfo.setText(_translate("CustomAlertBoxUI","Bookra1n needs your attention."))
        self.btnProceed.setText(_translate("CustomAlertBoxUI", "Accept"))