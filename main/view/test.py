import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, \
    QLabel

# Giả sử bạn đã có HomeWindow từ file home.py
from home import HomeWindow


# Tạo một cửa sổ mới
class MainWindow1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Đây là MainWindow 1"))
        self.setLayout(layout)


# Tạo sidebar cho ứng dụng
class SidebarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng với Sidebar")

        # Khởi tạo cửa sổ HomeWindow
        # self.home = HomeWindow()

        # Tạo QStackedWidget để chứa các cửa sổ
        self.stacked_widget = QStackedWidget()
        self.window1 = MainWindow1()
        self.stacked_widget.addWidget(self.window1)
        # self.stacked_widget.addWidget(self.home)

        # Tạo sidebar với các nút
        sidebar_layout = QVBoxLayout()
        button1 = QPushButton("Chuyển sang MainWindow 1")
        button2 = QPushButton("Chuyển sang Home")

        # Kết nối sự kiện chuyển đổi giữa các cửa sổ
        button1.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.window1))
        # button2.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.home))

        sidebar_layout.addWidget(button1)
        sidebar_layout.addWidget(button2)
        sidebar_layout.addStretch()  # Đẩy các nút lên phía trên

        # Sidebar: tạo một widget cố định và đặt nó vào một layout
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)

        # Đặt sidebar và stacked_widget vào layout chính
        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar_widget, 1)  # Sidebar có tỷ lệ chiếm 1 phần không gian
        main_layout.addWidget(self.stacked_widget, 5)  # Nội dung chính chiếm 5 phần không gian

        # Đặt layout chính vào một widget và thiết lập làm central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


# Khởi chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SidebarApp()
    window.show()
    sys.exit(app.exec_())
