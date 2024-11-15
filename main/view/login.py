from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
import sys
from home import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Thiết lập kích thước và tiêu đề cho cửa sổ
        self.setWindowTitle("Login")
        self.setFixedSize(400, 300)

        # Căn giữa cửa sổ
        self.center_window()

        # Tạo layout chính để căn giữa nội dung
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Tiêu đề
        title_label = QLabel("Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Layout cho username
        username_layout = QHBoxLayout()
        self.label_username = QLabel("Username:")
        self.input_username = QLineEdit()
        username_layout.addWidget(self.label_username)
        username_layout.addWidget(self.input_username)

        # Layout cho password
        password_layout = QHBoxLayout()
        self.label_password = QLabel("Password:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.label_password)
        password_layout.addWidget(self.input_password)

        # Nút Login
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)
        self.login_button.setFixedWidth(100)

        # Thêm các widget và layout vào layout chính
        main_layout.addWidget(title_label)
        main_layout.addLayout(username_layout)
        main_layout.addLayout(password_layout)
        main_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        # Thiết lập layout cho cửa sổ chính
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.frameGeometry()

        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def check_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        # Kiểm tra thông tin đăng nhập (tạm thời là username "admin" và password "password")
        if username == "admin" and password == "admin":
            QMessageBox.information(self, "Login Success", "Welcome, Admin!")
            self.open_main_window()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def open_main_window(self):
        self.main_window = MainWindow()  # Khởi tạo HomeWindow
        self.main_window.show()          # Hiển thị HomeWindow
        self.close()                     # Đóng LoginWindow sau khi đăng nhập thành công

# Chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
