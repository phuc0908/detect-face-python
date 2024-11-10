from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QHeaderView, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint
import sys
import os
import subprocess


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Thiết lập kích thước và tiêu đề cho cửa sổ
        self.setWindowTitle("User Management")
        self.setFixedSize(1400, 900)

        # Căn giữa cửa sổ
        self.center_window()

        # Tạo layout chính
        main_layout = QVBoxLayout()

        # Tạo layout chứa nút "Thêm User"
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Đẩy nút sang bên phải
        self.add_button = QPushButton("Thêm User")
        button_layout.addWidget(self.add_button)

        # Bảng hiển thị danh sách người dùng
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)  # Số cột: ID, Tên, CCCD, Ảnh, Hành động
        self.user_table.setHorizontalHeaderLabels(["ID", "Tên", "CCCD", "Ảnh","Trạng thái", "Hành động"])

        # Thiết lập để bảng tự động căn chỉnh cột theo kích thước
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Thiết lập chọn toàn bộ hàng khi click vào một ô
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)

        # Thêm layout vào layout chính
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.user_table)

        # Thiết lập layout cho cửa sổ chính
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Kết nối sự kiện cho nút thêm user
        self.add_button.clicked.connect(self.add_user)

        # Thêm dữ liệu mẫu để kiểm tra
        sample_users = [
            {"id": 1, "name": "Nguyen Van A", "cccd": "012345678","status":"Updated", "image": "path/to/image1.jpg"},
            {"id": 2, "name": "Le Thi B", "cccd": "987654321","status":"None", "image": "path/to/image2.jpg"},
        ]
        self.load_users(sample_users)

        # Kết nối sự kiện menu chuột phải cho bảng
        self.user_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_table.customContextMenuRequested.connect(self.show_context_menu)

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def load_users(self, users):
        """
        Hàm để nạp danh sách người dùng vào bảng.
        :param users: Danh sách người dùng với mỗi user là một dict chứa ID, Tên, CCCD, và Ảnh.
        """
        self.user_table.setRowCount(len(users))  # Thiết lập số hàng theo số lượng người dùng

        for row, user in enumerate(users):
            # Thêm các mục vào bảng và đặt thành không thể chỉnh sửa
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
            self.user_table.setItem(row, 1, QTableWidgetItem(user['name']))
            self.user_table.setItem(row, 2, QTableWidgetItem(user['cccd']))
            self.user_table.setItem(row, 3, QTableWidgetItem(user['status']))
            self.user_table.setItem(row, 4, QTableWidgetItem(user['image']))

            for col in range(4):
                self.user_table.item(row, col).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Chỉ cho phép sao chép, không chỉnh sửa

            # Tạo nút "Sửa" và "Xóa" cho cột hành động
            edit_button = QPushButton("Sửa")
            delete_button = QPushButton("Xóa")

            # Thiết lập kích thước font chữ nhỏ hơn cho nút
            edit_button.setStyleSheet("font-size: 12px;")
            delete_button.setStyleSheet("font-size: 12px;")

            # Kết nối sự kiện nút
            edit_button.clicked.connect(lambda _, r=row: self.edit_user(r))
            delete_button.clicked.connect(lambda _, r=row: self.delete_user(r))

            # Tạo layout chứa nút trong một widget
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.addWidget(edit_button)
            action_layout.addWidget(delete_button)
            action_layout.setAlignment(Qt.AlignCenter)
            action_layout.setContentsMargins(0, 0, 0, 0)  # Loại bỏ khoảng trống xung quanh
            self.user_table.setCellWidget(row, 5, action_widget)

    def show_context_menu(self, position: QPoint):
        # Lấy hàng hiện tại theo vị trí của chuột
        selected_row = self.user_table.indexAt(position).row()

        # Kiểm tra nếu hàng có tồn tại
        if selected_row != -1:
            # Tạo menu chuột phải
            context_menu = QMenu(self)

            # Thêm các tùy chọn vào menu ngữ cảnh
            add_face_action = QAction("Thêm khuôn mặt", self)
            add_face_action.triggered.connect(lambda: self.add_face(selected_row))
            context_menu.addAction(add_face_action)

            list_face_action = QAction("Xem khuôn mặt", self)
            list_face_action.triggered.connect(lambda: self.list_face(selected_row))
            context_menu.addAction(list_face_action)

            edit_action = QAction("Sửa", self)
            edit_action.triggered.connect(lambda: self.edit_user(selected_row))
            context_menu.addAction(edit_action)

            delete_action = QAction("Xóa", self)
            delete_action.triggered.connect(lambda: self.delete_user(selected_row))
            context_menu.addAction(delete_action)

            # Hiển thị menu tại vị trí của chuột
            context_menu.exec_(self.user_table.viewport().mapToGlobal(position))

    def list_face(self, selected_row):
        pass

    def add_user(self):
        # Xử lý thêm user
        print("Thêm User")

    def edit_user(self, row):
        # Xử lý sửa user
        user_id = self.user_table.item(row, 0).text()
        print(f"Sửa User ID: {user_id}")

    def delete_user(self, row):
        # Xử lý xóa user
        user_id = self.user_table.item(row, 0).text()
        print(f"Xóa User ID: {user_id}")
        self.user_table.removeRow(row)

    def add_face(self, row):
        # Lấy ID của user từ bảng
        user_id = self.user_table.item(row, 0).text()
        print(1)

        self.run_face_detection(user_id)

    def run_face_detection(self, user_id):
        try:
            script_path = r'/main/facedetect.py'

            subprocess.run([sys.executable, script_path, user_id], check=True)
        except Exception as e:
            print(f"Error: {e}")


# Chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
