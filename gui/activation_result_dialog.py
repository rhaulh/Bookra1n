import os
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QMovie


class Ui_ActivationResultDialogUI(object):
    logger = logging.getLogger("bookra1n")
    def setupUi(self, ActivationResultDialogUI):
        ActivationResultDialogUI.setObjectName("ActivationResultDialogUI")
        ActivationResultDialogUI.resize(580, 440)
        ActivationResultDialogUI.setMinimumSize(QtCore.QSize(580, 440))
        ActivationResultDialogUI.setMaximumSize(QtCore.QSize(580, 440))
        ActivationResultDialogUI.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        ActivationResultDialogUI.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        ActivationResultDialogUI.setModal(True)

        # Main container with glassmorphism effect
        self.central_widget = QtWidgets.QWidget(ActivationResultDialogUI)
        self.central_widget.setGeometry(QtCore.QRect(15, 15, 550, 410))
        self.central_widget.setStyleSheet("""
            QWidget {
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

        self.verticalLayout = QtWidgets.QVBoxLayout(self.central_widget)
        self.verticalLayout.setContentsMargins(45, 45, 45, 45)
        self.verticalLayout.setSpacing(20)

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

        # Success/Failure Animation (GIF or static icon)
        self.labelIcon = QtWidgets.QLabel(self.central_widget)
        self.labelIcon.setMinimumSize(QtCore.QSize(120, 120))
        self.labelIcon.setMaximumSize(QtCore.QSize(120, 120))
        self.labelIcon.setAlignment(QtCore.Qt.AlignCenter)
        self.labelIcon.setStyleSheet("background: transparent;")
        self.verticalLayout.addWidget(self.labelIcon, 0, QtCore.Qt.AlignCenter)

        # Title
        self.labelTitle = QtWidgets.QLabel(self.central_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(32)
        font.setBold(False)
        self.labelTitle.setFont(font)
        self.labelTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTitle.setStyleSheet("color: white; background: transparent;")
        self.verticalLayout.addWidget(self.labelTitle)

        # Message
        self.labelMessage = QtWidgets.QLabel(self.central_widget)
        font_msg = QtGui.QFont()
        font_msg.setFamily("Segoe UI")
        font_msg.setPointSize(14)
        self.labelMessage.setFont(font_msg)
        self.labelMessage.setAlignment(QtCore.Qt.AlignCenter)
        self.labelMessage.setWordWrap(True)
        self.labelMessage.setStyleSheet("""
            color: white;
            background: rgba(0, 0, 0, 80);
            padding: 20px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 30);
        """)
        self.verticalLayout.addWidget(self.labelMessage)

        # Info (only shown on failure)
        self.labelInfo = QtWidgets.QLabel(self.central_widget)
        font_info = QtGui.QFont()
        font_info.setFamily("Segoe UI")
        font_info.setPointSize(11)
        self.labelInfo.setFont(font_info)
        self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.labelInfo.setWordWrap(True)
        self.labelInfo.setVisible(False)
        self.labelInfo.setStyleSheet("""
            color: rgba(255, 255, 255, 200);
            background: rgba(255, 107, 107, 60);
            padding: 15px;
            border: 1px solid rgba(255, 107, 107, 100);
            border-radius: 15px;
        """)
        self.verticalLayout.addWidget(self.labelInfo)

        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)

        # OK Button
        self.btnOk = QtWidgets.QPushButton(self.central_widget)
        self.btnOk.setMinimumSize(QtCore.QSize(0, 50))
        self.btnOk.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnOk.setDefault(True)
        self.btnOk.setStyleSheet("""
            QPushButton {
                background: rgba(255, 107, 107, 200);
                color: white;
                border: none;
                border-radius: 25px;
                font-family: 'Segoe UI';
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 107, 107, 255);
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QPushButton:pressed {
                background: rgba(255, 80, 80, 255);
            }
        """)
        self.verticalLayout.addWidget(self.btnOk)

        self.retranslateUi(ActivationResultDialogUI)

    def retranslateUi(self, ActivationResultDialogUI):
        _translate = QtCore.QCoreApplication.translate
        ActivationResultDialogUI.setWindowTitle(_translate("ActivationResultDialogUI", "Bookra1n - Activation Result"))
        self.btnOk.setText(_translate("ActivationResultDialogUI", "Continue"))

    def set_success(self, message="Your device has been activated successfully!"):
        self.labelTitle.setText("Success!")
        self.labelTitle.setStyleSheet("color: #50fa7b; background: transparent;border:none;")
        self.labelMessage.setText(message)
        self.labelInfo.setVisible(False)
        self.btnOk.setStyleSheet("""
            QPushButton {
                background: rgba(80, 250, 123, 200);
                color: #0a0a0a;
                border: none;
                border-radius: 25px;
                font-family: 'Segoe UI';
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(80, 250, 123, 255);
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QPushButton:pressed {
                background: rgba(60, 230, 103, 255);
            }
        """)
        self.show_success_animation()

    def set_failed(self, message="Activation failed.", info="This is normal. Please try again a few times."):
        self.labelTitle.setText("Failed")
        self.labelTitle.setStyleSheet("color: #ff6b6b; background: transparent;border:none;")
        self.labelMessage.setText(message)
        self.labelInfo.setText(info)
        self.labelInfo.setVisible(False)
        self.btnOk.setStyleSheet("""
            QPushButton {
                background: rgba(255, 107, 107, 200);
                color: white;
                border: none;
                border-radius: 25px;
                font-family: 'Segoe UI';
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 107, 107, 255);
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QPushButton:pressed {
                background: rgba(255, 80, 80, 255);
            }
        """)
        self.show_failed_animation()

    def show_success_animation(self):
        gif_path = os.path.join(os.path.dirname(__file__), "success.gif").replace("\\", "/")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QtCore.QSize(120, 120))
            self.labelIcon.setMovie(movie)
            movie.start()
        else:
            # Fallback to text icon
            self.labelIcon.setText("✓")
            self.labelIcon.setStyleSheet("""
                background: transparent;
                color: #50fa7b;
                font-size: 80px;
                font-weight: bold;
                border:none;
            """)

    def show_failed_animation(self):
        gif_path = os.path.join(os.path.dirname(__file__), "failed.gif").replace("\\", "/")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QtCore.QSize(120, 120))
            self.labelIcon.setMovie(movie)
            movie.start()
        else:
            # Fallback to text icon
            self.labelIcon.setText("✕")
            self.labelIcon.setStyleSheet("""
                background: transparent;
                color: #ff6b6b;
                font-size: 80px;
                font-weight: bold;
                border:none;
            """)