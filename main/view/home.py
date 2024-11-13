import sys
import threading
import subprocess
import mysql.connector
from addUser import AddUserWindow
from editUser import EditUserWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, \
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QComboBox, QSpacerItem, QSizePolicy, QMenu, QMessageBox
from PyQt5.QtCore import Qt, QPoint


# Cấu hình kết nối đến MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="detect_face_app"
    )


# MAIN -------------------------------------------------------------------MAIN---------------------------------->

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trang Chủ")
        self.setFixedSize(1400, 800)

        # Tạo layout chính
        layout = QVBoxLayout()

        add_layout = QHBoxLayout()

        # Tạo nút "Refresh"
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_users)  # Kết nối nút với hàm load_users
        add_layout.addWidget(self.refresh_button)

        # Spacer để đẩy nút "Thêm Người Dùng" sang phải
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        add_layout.addItem(spacer)

        # Tạo nút "Thêm Người Dùng"
        self.add_button = QPushButton("Thêm Người Dùng")
        add_layout.addWidget(self.add_button)

        # Thêm layout nút vào layout chính
        layout.addLayout(add_layout)

        # Bảng hiển thị người dùng
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(7)
        self.user_table.setHorizontalHeaderLabels(["ID", "Tên", "CCCD", "Email", "Phone", "Avatar", "Trạng thái"])
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_table.customContextMenuRequested.connect(self.open_context_menu)

        # Thiết lập tự động căn chỉnh cột
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Thêm bảng vào layout
        layout.addWidget(self.user_table)

        # Kết nối sự kiện khi nhấn nút "Thêm Người Dùng"
        self.add_button.clicked.connect(self.open_add_user_window)

        # Tạo widget chính và thiết lập layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Load dữ liệu người dùng
        self.load_users()

    def load_users(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, cccd, email, phone, avatar, status FROM users")  # Lấy tất cả người dùng từ DB
            users = cursor.fetchall()
            conn.close()

            # Đặt lại số hàng trước khi nạp dữ liệu
            self.user_table.setRowCount(0)  # Xóa tất cả các hàng hiện tại
            self.user_table.setRowCount(len(users))  # Đặt lại số hàng theo dữ liệu mới

            # Nạp dữ liệu vào bảng
            for row, user in enumerate(users):
                for col, value in enumerate(user):
                    self.user_table.setItem(row, col, QTableWidgetItem(str(value)))

            print("Dữ liệu người dùng đã được nạp thành công.")

        except mysql.connector.Error as e:
            print(f"Lỗi kết nối DB: {e}")

    def open_context_menu(self, position: QPoint):
        index = self.user_table.indexAt(position)
        row = index.row()
        col = index.column()

        if row < 0:
            return

        context_menu = QMenu(self)
        add_face_action = context_menu.addAction("Thêm khuôn mặt")
        edit_user_action = context_menu.addAction("Sửa User")
        delete_user_action = context_menu.addAction("Xóa User")

        add_face_action.triggered.connect(lambda: self.add_face(row))
        edit_user_action.triggered.connect(lambda: self.edit_user(row))
        delete_user_action.triggered.connect(lambda: self.delete_user(row))

        context_menu.exec_(self.user_table.viewport().mapToGlobal(position))

    def dummy_action(self, action_name, row):
        print(f"Action '{action_name}' selected for row {row}")

    def add_face(self, row):
        user_id = self.user_table.item(row, 0).text()  # Get user ID from the selected row
        print(f"Thêm khuôn mặt cho user ID: {user_id}")

        # Run the face detection script with the user ID as an argument
        subprocess.Popen(["python", "../facedetect.py", user_id])

    def open_add_user_window(self):
        self.add_user_window = AddUserWindow()  # Tạo cửa sổ thêm người dùng
        self.add_user_window.user_added.connect(self.load_users)  # Kết nối tín hiệu với hàm load_users
        self.add_user_window.show()  # Hiển thị cửa sổ thêm người dùng

    def edit_user(self, row):
        user_id = self.user_table.item(row, 0).text()  # Get user ID from the selected row
        print(f"Sửa user ID: {user_id}")

        # Open EditUserWindow with the selected user's data
        self.edit_user_window = EditUserWindow(int(user_id))
        self.edit_user_window.user_updated.connect(self.load_users)
        self.edit_user_window.show()  # Display the EditUserWindow

    def delete_user(self, row):
        user_id = self.user_table.item(row, 0).text()  # Lấy ID của người dùng từ hàng được chọn

        # Xác nhận người dùng có chắc chắn muốn xóa không
        reply = QMessageBox.question(self, "Xóa Người Dùng",
                                     f"Bạn có chắc chắn muốn xóa người dùng với ID {user_id} không?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                # Xóa người dùng khỏi cơ sở dữ liệu
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                cursor.close()
                conn.close()

                print(f"Đã xóa người dùng với ID: {user_id}")

                # Cập nhật bảng hiển thị sau khi xóa
                self.load_users()

            except mysql.connector.Error as e:
                print(f"Lỗi kết nối DB: {e}")



# Chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
