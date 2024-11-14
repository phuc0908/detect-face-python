import sys
import threading
import subprocess
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, \
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QComboBox, QSpacerItem, QSizePolicy, QMenu
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

# Cấu hình kết nối đến MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="detect_face_app"
    )


class EditUserWindow(QWidget):
    user_updated = pyqtSignal()
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Sửa Thông Tin Người Dùng")
        self.setFixedSize(350, 350)

        # Layout setup
        layout = QVBoxLayout()

        # Create fields for user data
        self.name_edit = QLineEdit()
        self.cccd_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.avatar_edit = QLineEdit()

        # Labels and Inputs
        layout.addWidget(QLabel("Tên"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("CCCD"))
        layout.addWidget(self.cccd_edit)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Phone"))
        layout.addWidget(self.phone_edit)
        layout.addWidget(QLabel("Avatar"))
        layout.addWidget(self.avatar_edit)

        button_layout = QHBoxLayout()

        self.spacer_item = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.save_button = QPushButton("Lưu")
        self.cancel_button = QPushButton("Hủy Bỏ")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Load the existing data for the user
        self.load_user_data()

        # Save button

        self.save_button.clicked.connect(self.save_user_data)

        self.setLayout(layout)

    def load_user_data(self):
        # Load user data from the database based on `self.user_id`
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, cccd, email, phone, avatar FROM users WHERE id = %s", (self.user_id,))
            user = cursor.fetchone()
            conn.close()

            if user:
                self.name_edit.setText(user[0])
                self.cccd_edit.setText(user[1])
                self.email_edit.setText(user[2])
                self.phone_edit.setText(user[3])
                self.avatar_edit.setText(user[4])
        except mysql.connector.Error as e:
            print(f"Lỗi khi tải dữ liệu người dùng: {e}")

    def save_user_data(self):
        # Save updated data to the database
        name = self.name_edit.text()
        cccd = self.cccd_edit.text()
        email = self.email_edit.text()
        phone = self.phone_edit.text()
        avatar = self.avatar_edit.text()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET name = %s, cccd = %s, email = %s, phone = %s, avatar = %s
                WHERE id = %s
            """, (name, cccd, email, phone, avatar, self.user_id))
            conn.commit()
            conn.close()
            print("Dữ liệu người dùng đã được cập nhật.")
            self.close()  # Close the edit window
            self.user_updated.emit()
        except mysql.connector.Error as e:
            print(f"Lỗi khi cập nhật dữ liệu: {e}")

