import sys
import threading
import subprocess
import mysql.connector
import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, \
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QComboBox, QSpacerItem, QSizePolicy, QMenu, QFileDialog
from PyQt5.QtCore import Qt, QPoint, pyqtSignal


# Cấu hình kết nối đến MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="detect_face_app"
    )


class AddUserWindow(QWidget):
    user_added = pyqtSignal()

    def __init__(self):
        super().__init__()



        self.setWindowTitle("Thêm Người Dùng")
        self.setFixedSize(350, 450)

        # Tạo layout chính
        layout = QVBoxLayout()

        # Các trường nhập liệu
        self.name_label = QLabel("Nhập tên người dùng:")
        self.name_input = QLineEdit()

        self.cccd_label = QLabel("Nhập CCCD:")
        self.cccd_input = QLineEdit()

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()

        self.phone_label = QLabel("Số điện thoại:")
        self.phone_input = QLineEdit()

        self.avatar_label = QLabel("Đường dẫn avatar:")
        self.avatar_input = QLineEdit()
        self.avatar_input.setReadOnly(True)  # Chỉ hiển thị, không cho phép chỉnh sửa

        self.select_avatar_button = QPushButton("Chọn Ảnh")
        self.select_avatar_button.clicked.connect(self.select_avatar)

        self.status_label = QLabel("Trạng thái:")
        self.status_input = QComboBox()
        self.status_input.addItems(["Chưa cập nhật khuôn mặt", "None", "Đã cập nhật khuôn mặt"])

        button_layout = QHBoxLayout()

        self.spacer_item = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.submit_button = QPushButton("Thêm Người Dùng")
        self.cancel_button = QPushButton("Hủy Bỏ")

        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)

        # Thêm các trường vào layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.cccd_label)
        layout.addWidget(self.cccd_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.avatar_label)
        layout.addWidget(self.avatar_input)
        layout.addWidget(self.select_avatar_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_input)

        layout.addItem(self.spacer_item)

        layout.addLayout(button_layout)

        # Kết nối sự kiện cho nút "Thêm"
        self.submit_button.clicked.connect(self.add_user)
        self.cancel_button.clicked.connect(self.close)

        self.setLayout(layout)

    def select_avatar(self):
        # Mở hộp thoại để chọn file ảnh
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")

        if file_path:
            # Lấy tên tệp và lưu vào thư mục avatar
            filename = os.path.basename(file_path)
            avatar_folder = "avatar"
            if not os.path.exists(avatar_folder):
                os.makedirs(avatar_folder)

            # Sao chép tệp vào thư mục avatar
            destination_path = os.path.join(avatar_folder, filename)
            shutil.copy(file_path, destination_path)

            # Hiển thị đường dẫn ảnh mới trong trường avatar
            self.avatar_input.setText(file_path)

    def add_user(self):
        name = self.name_input.text()
        cccd = self.cccd_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        avatar = self.avatar_input.text()
        status = self.status_input.currentText()

        if name and cccd and email and phone and avatar:
            # Gọi hàm thêm người dùng vào DB trong luồng
            threading.Thread(target=self.add_user_to_db, args=(name, cccd, email, phone, avatar, status)).start()
            self.close()

    def add_user_to_db(self, name, cccd, email, phone, avatar, status):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, cccd, email, phone, avatar, status) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, cccd, email, phone, avatar, status))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Đã thêm người dùng: {name}")

            # Phát tín hiệu sau khi thêm thành công
            self.user_added.emit()
        except mysql.connector.Error as e:
            print(f"Lỗi kết nối DB: {e}")
