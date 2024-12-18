import sys
import threading
import subprocess
import mysql.connector
import os
import cv2
import openpyxl
from addUser import AddUserWindow
from editUser import EditUserWindow
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, \
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QComboBox, QSpacerItem, QSizePolicy, QMenu, QMessageBox, \
    QSlider, QDockWidget, QDockWidget, QCalendarWidget, QStackedWidget
from PyQt5.QtCore import Qt, QPoint, QFile, QTextStream, QDate
from PyQt5.QtGui import QColor, QPalette, QWheelEvent
from main.controller.HomeController import HomeController


# Cấu hình kết nối đến MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="detect_face_app"
    )


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Nút để chuyển đến HomeWindow
        self.home_button = QPushButton("Trang Chủ")
        layout.addWidget(self.home_button)

        self.calendar_button = QPushButton("Lịch")
        layout.addWidget(self.calendar_button)

        # Spacer để đẩy các nút lên trên
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.setLayout(layout)


# HOME -------------------------------------------------------------------HOME---------------------------------->

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.edit_user_window = None
        self.add_user_window = None
        self.setAutoFillBackground(True)

        # Khởi tạo controller
        self.controller = HomeController(self)

        self.setWindowTitle("Trang Chủ")
        # self.resize(1400, 800)

        self.load_stylesheet("css/style.css")

        # Tạo layout chính
        layout = QVBoxLayout()

        add_layout = QHBoxLayout()

        self.export_button = QPushButton("Xuất Excel")
        add_layout.addWidget(self.export_button)

        self.train_button = QPushButton("Train")
        add_layout.addWidget(self.train_button)

        # Spacer để đẩy nút "Thêm Người Dùng" sang phải
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        add_layout.addItem(spacer)

        # Tạo nút "Refresh"
        self.refresh_button = QPushButton("Refresh")
        add_layout.addWidget(self.refresh_button)

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

        # Slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)  # Minimum zoom level (50%)
        self.zoom_slider.setMaximum(200)  # Maximum zoom level (200%)
        self.zoom_slider.setValue(100)  # Default zoom level (100%)
        self.zoom_slider.setTickInterval(10)  # Đặt interval giữa các tick
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)  # Đặt các tick ở dưới thanh trượt
        self.zoom_slider.valueChanged.connect(lambda value: self.controller.on_zoom_slider_changed(value))

        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignCenter)

        # Tạo một layout ngang cho thanh trượt và nhãn
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(self.zoom_label)

        # Thêm bảng, slide vào layout
        layout.addWidget(self.user_table)
        # Đặt thanh trượt và nhãn ở dưới cùng của cửa sổ
        layout.addLayout(zoom_layout)

        # Thiết lập tự động căn chỉnh cột
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Kết nối sự kiện khi nhấn nút
        self.add_button.clicked.connect(self.open_add_user_window)
        self.export_button.clicked.connect(self.export_to_excel)
        self.train_button.clicked.connect(self.train_face)
        self.refresh_button.clicked.connect(self.load_users)  # Kết nối nút với hàm load_users

        # Tạo widget chính và thiết lập layout
        self.setLayout(layout)

        # Load dữ liệu người dùng
        self.load_users()

    def wheelEvent(self, event: QWheelEvent):
        # Gọi hàm wheelEvent từ controller
        self.controller.wheelEvent(event)

    def load_stylesheet(self, filename):
        """Tải file CSS và áp dụng vào ứng dụng"""
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            self.setStyleSheet(stylesheet)
            file.close()

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

    @staticmethod
    def dummy_action(action_name, row):
        print(f"Action '{action_name}' selected for row {row}")

    def add_face(self, row):
        user_id = self.user_table.item(row, 0).text()
        print(f"Thêm khuôn mặt cho user ID: {user_id}")

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

    def export_to_excel(self):
        # Hiển thị hộp thoại xác nhận trước khi xuất
        reply = QMessageBox.question(self, "Xuất Dữ Liệu",
                                     "Bạn có muốn xuất dữ liệu người dùng ra Excel không?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Tạo workbook mới
                wb = openpyxl.Workbook()
                ws = wb.active

                # Lấy tiêu đề cột
                headers = [self.user_table.horizontalHeaderItem(i).text() for i in range(self.user_table.columnCount())]
                ws.append(headers)  # Ghi tiêu đề vào hàng đầu tiên

                # Lấy dữ liệu từ bảng và ghi vào Excel
                for row in range(self.user_table.rowCount()):
                    row_data = [self.user_table.item(row, col).text() for col in range(self.user_table.columnCount())]
                    ws.append(row_data)

                # Lưu tệp Excel
                wb.save("users_data.xlsx")

                print("Dữ liệu đã được xuất ra Excel thành công!")

            except Exception as e:
                print(f"Lỗi khi xuất dữ liệu ra Excel: {e}")


    def train_face(self):
        """
        Chạy file train.py để huấn luyện dữ liệu khuôn mặt.
        """
        try:
            # Đường dẫn file train.py
            train_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../train.py')

            # Đường dẫn Python hiện tại (môi trường IDE)
            python_executable = sys.executable

            # Gọi subprocess với Python đúng môi trường
            process = subprocess.Popen([python_executable, train_script], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                QMessageBox.information(self, "Huấn luyện", "Đào tạo hoàn tất!\n" + stdout.decode())
            else:
                QMessageBox.critical(self, "Lỗi", "Có lỗi xảy ra trong quá trình đào tạo.\n" + stderr.decode())

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi chạy train.py: {str(e)}")


# --CALENDAR---------------------------------------------------------------CALENDAR-------->
class CalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar App - Attendance")
        self.resize(800, 600)

        self.load_stylesheet("css/style.css")

        # Layout chính
        layout = QVBoxLayout()

        # Tạo lịch (Calendar)
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.display_users_on_date)
        layout.addWidget(self.calendar)

        # Tạo bảng hiển thị người dùng
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels(["User ID", "Name","CCCD","Phone","Email","Time Start"])
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.user_table)

        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Thiết lập widget chính
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_stylesheet(self, filename):
        """Tải file CSS và áp dụng vào ứng dụng"""
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            self.setStyleSheet(stylesheet)
            file.close()


    def display_users_on_date(self, date: QDate):
        selected_date = date.toString("yyyy-MM-dd")

        # Kết nối đến cơ sở dữ liệu và truy vấn người dùng tham gia ngày đó
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
                    SELECT u.id, u.name, u.cccd, u.phone, u.email, s.start_time
                    FROM users u
                    JOIN schedule s ON u.id = s.user_id
                    WHERE DATE(s.start_time) = %s;
                       """
            cursor.execute(query, (selected_date,))
            users = cursor.fetchall()
            conn.close()

            # Cập nhật bảng hiển thị người dùng
            self.user_table.setRowCount(len(users))
            for row, (user_id, name, cccd, phone, email, start_time) in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user_id)))
                self.user_table.setItem(row, 1, QTableWidgetItem(name))
                self.user_table.setItem(row, 2, QTableWidgetItem(cccd))
                self.user_table.setItem(row, 3, QTableWidgetItem(phone))
                self.user_table.setItem(row, 4, QTableWidgetItem(email))
                self.user_table.setItem(row, 5, QTableWidgetItem(start_time.strftime("%H:%M:%S")))

        except mysql.connector.Error as e:
            print(f"Lỗi kết nối DB: {e}")



# -MAIN--------------------------------------------------------MAIN------------------------>
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Khởi tạo stacked widget để chứa các cửa sổ
        self.stacked_widget = QStackedWidget(self)

        self.home_window = HomeWindow()
        self.calendar_window = CalendarApp()

        # Thêm các cửa sổ vào stacked widget
        self.stacked_widget.addWidget(self.home_window)
        self.stacked_widget.addWidget(self.calendar_window)

        # Thiết lập stacked widget làm cửa sổ chính
        self.setCentralWidget(self.stacked_widget)

        # Khởi tạo sidebar
        self.sidebar = Sidebar()

        # Tạo DockWidget cho sidebar
        self.dock = QDockWidget("Sidebar", self)
        self.dock.setWidget(self.sidebar)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)

        # Kết nối nút từ sidebar với HomeWindow
        self.sidebar.home_button.clicked.connect(self.show_home_window)
        self.sidebar.calendar_button.clicked.connect(self.show_calendar_window)

        self.setWindowTitle("Ứng Dụng Quản Lý")
        self.resize(1400, 800)

    def show_home_window(self):
        self.stacked_widget.setCurrentWidget(self.home_window)

    def show_calendar_window(self):
        self.stacked_widget.setCurrentWidget(self.calendar_window)


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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.check_login()  # Gọi hàm check_login khi nhấn Enter

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
