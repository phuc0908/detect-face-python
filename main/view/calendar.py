import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCalendarWidget, QTableWidget, QTableWidgetItem, QLabel
from PyQt5.QtCore import QDate

# Hàm kết nối đến cơ sở dữ liệu MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="detect_face_app"
    )

class CalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar App - Attendance")
        self.resize(800, 600)

        # Layout chính
        layout = QVBoxLayout()

        # Tạo lịch (Calendar)
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.display_users_on_date)
        layout.addWidget(self.calendar)

        # Tạo bảng hiển thị người dùng
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["User ID", "Name"])
        layout.addWidget(self.user_table)

        # Thiết lập widget chính
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def display_users_on_date(self, date: QDate):
        selected_date = date.toString("yyyy-MM-dd")

        # Kết nối đến cơ sở dữ liệu và truy vấn người dùng tham gia ngày đó
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
                           SELECT u.id, u.name
                           FROM users u
                           JOIN attendance a ON u.id = a.user_id
                           WHERE a.attendance_date = %s
                       """
            cursor.execute(query, (selected_date,))
            users = cursor.fetchall()
            conn.close()

            # Cập nhật bảng hiển thị người dùng
            self.user_table.setRowCount(len(users))
            for row, (user_id, name) in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user_id)))
                self.user_table.setItem(row, 1, QTableWidgetItem(name))

        except mysql.connector.Error as e:
            print(f"Lỗi kết nối DB: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec_())
