import sys
import threading
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt

# Cấu hình kết nối đến MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="detect_face_app"
    )

class AddUserWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thêm Người Dùng")
        self.setFixedSize(300, 200)

        # Tạo layout chính
        layout = QVBoxLayout()

        self.name_label = QLabel("Nhập tên người dùng:")
        self.name_input = QLineEdit()

        self.submit_button = QPushButton("Thêm")
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.submit_button)

        # Kết nối sự kiện cho nút "Thêm"
        self.submit_button.clicked.connect(self.add_user)

        self.setLayout(layout)

    def add_user(self):
        name = self.name_input.text()
        if name:
            # Gọi hàm thêm người dùng vào DB trong luồng
            threading.Thread(target=self.add_user_to_db, args=(name,)).start()
        self.close()

    def add_user_to_db(self, name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Đã thêm người dùng: {name}")
        except mysql.connector.Error as e:
            print(f"Lỗi kết nối DB: {e}")

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trang Chủ")
        self.setFixedSize(400, 300)

        # Tạo layout chính
        layout = QVBoxLayout()

        self.add_button = QPushButton("Thêm Người Dùng")
        layout.addWidget(self.add_button)

        # Kết nối sự kiện khi nhấn nút "Thêm Người Dùng"
        self.add_button.clicked.connect(self.open_add_user_window)

        # Tạo widget chính và thiết lập layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_add_user_window(self):
        self.add_user_window = AddUserWindow()  # Tạo cửa sổ thêm người dùng
        self.add_user_window.show()  # Hiển thị cửa sổ thêm người dùng


# Chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
