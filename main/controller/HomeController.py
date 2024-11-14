# HomeController.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWheelEvent

class HomeController:
    def __init__(self, home_window):
        self.home_window = home_window


    def on_zoom_slider_changed(self, value):
        scale_factor = value / 100

        font = self.home_window.font()
        font.setPointSize(int(10 * scale_factor))  # Điều chỉnh kích thước chữ dựa trên tỷ lệ
        self.home_window.setFont(font)

        self.home_window.user_table.setFont(font)

        # Cập nhật giá trị phần trăm ở label
        self.home_window.zoom_label.setText(f"{value}%")

    def wheelEvent(self, event: QWheelEvent):
        # Kiểm tra xem Ctrl có được nhấn cùng lúc không
        if event.modifiers() == Qt.ControlModifier:
            angle = event.angleDelta().y()
            if angle > 0:
                self.home_window.zoom_slider.setValue(self.home_window.zoom_slider.value() + 10)
            else:
                self.home_window.zoom_slider.setValue(self.home_window.zoom_slider.value() - 10)

