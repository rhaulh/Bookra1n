from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class Ui_InstructionDialogUI(object):
    def setupUi(self, InstructionDialogUI):
        InstructionDialogUI.setObjectName("InstructionDialogUI")
        InstructionDialogUI.resize(580, 450)
        InstructionDialogUI.setMinimumSize(QtCore.QSize(580, 450))
        InstructionDialogUI.setMaximumSize(QtCore.QSize(580, 450))
        InstructionDialogUI.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        InstructionDialogUI.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        InstructionDialogUI.setModal(True)

        # Main container with glassmorphism effect
        self.central_widget = QtWidgets.QWidget(InstructionDialogUI)
        self.central_widget.setGeometry(QtCore.QRect(15, 15, 550, 420))
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
        self.layout.setSpacing(18)

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
        self.close_btn.move(505, 15)

        # Title
        self.labelTitle = QtWidgets.QLabel(self.central_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(28)
        self.labelTitle.setFont(font)
        self.labelTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTitle.setStyleSheet("color: #ff6b6b; background: transparent;")
        self.labelTitle.setText("Setup Instructions")
        self.layout.addWidget(self.labelTitle)

        # Step 1
        self.instructions_text = QtWidgets.QLabel()
        font_step = QtGui.QFont()
        font_step.setFamily("Segoe UI")
        font_step.setPointSize(9)
        self.instructions_text.setFont(font_step)
        self.instructions_text.setStyleSheet("color: white;")
        self.instructions_text.setText("Before starting the activation process, please ensure your device is properly set up:<br>"
            "🔹 <b>Step 1:</b> Connect your device to <b>WIFI</b><br>"
            "🔹 <b>Step 2:</b> Proceed to the <b>Activation Lock</b> section on your device<br>"
            "🔹 <b>Step 3:</b> Make sure the device is showing the activation lock screen<br>"
            "If you've completed these steps, click 'Continue' to begin the activation process."
        )

        self.instructions_text.setWordWrap(True)
        self.instructions_text.setTextFormat(Qt.RichText)
        self.layout.addWidget(self.instructions_text)

        # Warning label
        self.warning_label = QtWidgets.QLabel(self.central_widget)
        font_warning = QtGui.QFont()
        font_warning.setFamily("Segoe UI")
        font_warning.setPointSize(10)
        font_warning.setBold(True)
        self.warning_label.setFont(font_warning)
        self.warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            color: white;
            background: rgba(255, 107, 107, 120);
            border: 2px solid rgba(255, 107, 107, 180);
            border-radius: 15px;
        """)
        self.warning_label.setText("Activation will not work if these steps are not completed!")
        self.warning_label.setTextFormat(Qt.RichText)
        self.layout.addWidget(self.warning_label)
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

        # Continue Button
        self.btnContinue = QtWidgets.QPushButton(self.central_widget)
        self.btnContinue.setMinimumSize(QtCore.QSize(0, 50))
        self.btnContinue.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnContinue.setDefault(True)
        self.btnContinue.setStyleSheet("""
            QPushButton {
                background: rgba(80, 250, 123, 200);
                color: #0a0a0a;
                border: none;
                border-radius: 25px;
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: bold;
                padding: 0 30px;
            }
            QPushButton:hover {
                background: rgba(80, 250, 123, 255);
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QPushButton:pressed {
                background: rgba(60, 230, 103, 255);
            }
        """)
        self.button_layout.addWidget(self.btnContinue)

        self.layout.addLayout(self.button_layout)

        self.retranslateUi(InstructionDialogUI)
        QtCore.QMetaObject.connectSlotsByName(InstructionDialogUI)

    def retranslateUi(self, InstructionDialogUI):
        _translate = QtCore.QCoreApplication.translate
        InstructionDialogUI.setWindowTitle(_translate("InstructionDialogUI", "Bookra1n - Setup Instructions"))
        self.btnCancel.setText(_translate("InstructionDialogUI", "Cancel"))
        self.btnContinue.setText(_translate("InstructionDialogUI", "Continue"))