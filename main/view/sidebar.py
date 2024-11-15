from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.home_button = QPushButton("Trang Chủ")
        layout.addWidget(self.home_button)

        self.calendar_button = QPushButton("Lịch")
        layout.addWidget(self.calendar_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.setLayout(layout)
