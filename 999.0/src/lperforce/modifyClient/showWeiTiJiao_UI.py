import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QHeaderView, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class FileListViewer(QDialog):
    def __init__(self, file_list, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('需要提交或者还原的文件')  # 修改窗口标题

        # 创建布局
        layout = QVBoxLayout()

        if self.file_list:
            # 创建QTableWidget
            self.tableWidget = QTableWidget()
            self.tableWidget.setColumnCount(1)  # 只有一列显示文件路径
            self.tableWidget.setHorizontalHeaderLabels(['文件路径(如果这里没有文件请直接第三步)'])

            # 设置表格宽度为父级窗口宽度
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # 设置字体为小号
            font = QFont("微软雅黑", 8)  # 使用微软雅黑字体
            self.tableWidget.setFont(font)

            # 定义不同的颜色
            colors = [Qt.red, Qt.green, Qt.blue, Qt.yellow, Qt.cyan, Qt.magenta]
            color_index = 0

            # 添加需要清理的文件到QTableWidget
            row = 0
            self.client_rows = {}  # 用于存储每个客户端的行索引

            for client, files in self.file_list.items():
                # 创建带箭头的按钮
                button = QPushButton(f"▶ {client}")
                button.setFlat(True)
                button.setStyleSheet("text-align: left;")
                button.clicked.connect(lambda checked, client=client, button=button: self.toggle_files(client, button))
                
                # 将按钮添加到QTableWidget
                self.tableWidget.insertRow(row)
                self.tableWidget.setCellWidget(row, 0, button)

                # 设置客户端行字体为粗体，增大高度
                client_font = QFont("微软雅黑", 8)
                client_font.setBold(True)
                client_item = QTableWidgetItem()
                client_item.setFont(client_font)
                self.tableWidget.setItem(row, 0, client_item)
                self.tableWidget.setRowHeight(row, 40)  # 增加客户端行高度

                self.client_rows[client] = []

                row += 1  # 下一行

                for file in files:
                    file_item = QTableWidgetItem(f"  {file}")
                    file_item.setForeground(QColor(colors[color_index % len(colors)]))
                    file_item.setTextAlignment(Qt.AlignLeft)
                    file_item.setFont(QFont("微软雅黑", 18))
                    self.tableWidget.insertRow(row)
                    self.tableWidget.setItem(row, 0, file_item)
                    self.client_rows[client].append(row)

                    row += 1  # 下一行

                # 增加颜色索引
                color_index += 1

            # 将QTableWidget添加到布局
            layout.addWidget(self.tableWidget)
        else:
            # 显示信息提示框
            QMessageBox.information(self, '提示', '你的旧工作区已经清理完毕,现在请点击"删除旧的工作区"按钮')

        self.setLayout(layout)
        self.show()

    def toggle_files(self, client, button):
        # 查找客户端对应的所有文件行并切换它们的可见性
        if client not in self.client_rows or not self.client_rows[client]:
            return  # 如果客户端没有文件行，直接返回

        hidden = not self.tableWidget.isRowHidden(self.client_rows[client][0])
        for row in self.client_rows[client]:
            self.tableWidget.setRowHidden(row, hidden)
        # 切换按钮文本中的箭头
        if hidden:
            button.setText(f"▶ {client}")
        else:
            button.setText(f"▼ {client}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置全局字体为微软雅黑
    font = QFont("微软雅黑", 10)
    app.setFont(font)

    # 示例文件列表
    need_to_clean_file = {
        'client1': ['//H/CCC/776h.txt', '//H/CCC/...', '//H/Test/123.txt'],
        'client2': ['//H/Test/123.txt'],
        'client3': []  # 示例没有文件的客户端
    }

    viewer = FileListViewer(need_to_clean_file)
    sys.exit(app.exec_())
