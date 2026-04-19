from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys,os
LugwitToolDir=os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir+'/Lib') 
import Lugwit_Module as LM
lprint = LM.lprint
import time
import threading

class CustomProgressDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("进度")
        self._process = ''
        self._current_item = '准备中...'
        self._items = items
        self._index = 1
        self._additional_info = ""

        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView(self)
        self.web_view.setMinimumHeight(300)
        self.web_view.setHtml("<html><body style='background-color: #333;'></body></html>")  # 设置初始暗色背景
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(len(items))

        self.layout.addWidget(self.web_view)
        self.layout.addWidget(self.progressBar)

        self.setStyleSheet("background-color: #333;")

    def update_progress(self):
        """
        更新对话框的进度，并在完成所有项目时关闭对话框。
        作为类的方法，直接访问和修改实例的属性。
        """
        if self._index >= len(self._items):
            self.accept()
        else:
            self.current_item = self._items[self._index]
            self.progressBar.setValue(self._index)
            self._index += 1

    @property
    def current_item(self):
        return self._current_item

    
    @current_item.setter
    def current_item(self, value):
        self._current_item = value
        if value in self._items:
            self._index=self._items.index(value)
        self.progressBar.setValue(self._index+1)
        self.update_display_items()


    def update_display_items(self):
        start = max(0, self._index - 5)
        end = min(len(self._items), self._index + 6)
        items_display = []
        base_font_size = 20
        for idx in range(start, end):
            font_size = base_font_size - abs(self._index - idx)
            item_text = self._items[idx]
            if idx == self._index:
                item_text = f"<div style='font-size: {font_size}px; color: white; text-shadow: 0px 0px 10px cyan;'>{item_text} - {self._additional_info}</div>"
            else:
                item_text = f"<div style='font-size: {font_size}px; color: white;'>{item_text}</div>"
            items_display.append(item_text)
        full_html = f"<html><body style='background-color: #333; color: white;'>{''.join(items_display)}</body></html>"
        self.web_view.setHtml(full_html)
        # self.update_progress()
        if self._index+1 >= len(self._items):
            self.accept()
            self.close()
            lprint ('进程结束')

    def set_additional_info(self, info):
        self._additional_info = info
        self.update_display_items()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主窗口")
        self.setGeometry(100, 100, 400, 300)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        self.show_dialog_button = QPushButton("显示进度对话框")
        self.show_dialog_button.clicked.connect(self.show_progress_dialog)
        layout.addWidget(self.show_dialog_button)

        self.dialog = None
        self.timer = QTimer(self)
        self.current_item_index = 0
        self.items = ["任务1", "任务2", "任务3", "任务4", "任务5"]

    def show_progress_dialog(self):
        self.dialog = CustomProgressDialog(self.items, self)
        self.dialog.show()
        self.current_item_index = 0
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update every 100 ms

    def update_progress(self):
        if self.current_item_index < len(self.items):
            item = self.items[self.current_item_index]
            lprint(item)
            self.dialog.current_item = item
            self.dialog.set_additional_info("正在处理...")
            self.dialog.update_progress()
            self.current_item_index += 1
        else:
            self.timer.disconnect()  # Disconnect the signal to prevent multiple connections
            self.timer.stop()  # Stop the timer when done

    def show(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
