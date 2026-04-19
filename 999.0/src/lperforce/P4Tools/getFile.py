import sys
import os
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
import  fire

# 获取当前文件目录
curDir = os.path.dirname(__file__)
# 设置 .ui 文件路径
uiFile = fr"{curDir}/uiFile/manaual.ui"

class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        # 使用 uic 模块加载 .ui 文件
        uic.loadUi(uiFile, self)

        # 假设你的 QTableWidget 名称为 tableWidget
        self.tableWidget: QTableWidget = self.findChild(QTableWidget, 'tableWidget')
        
        # 设置表格列宽度自适应
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 添加示例数据
        self.populate_table()

    def populate_table(self):
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)
        
        for row,filePath in enumerate(needUserProcessFile):
            # 添加普通单元格
            item = QTableWidgetItem(filePath)
            self.tableWidget.setItem(row, 0, item)
            
            # 添加按钮到第二列
            button1 = QPushButton(f"执行")
            button1.clicked.connect(lambda: self.on_button_click(row, 1))
            self.tableWidget.setCellWidget(row, 1, button1)
            
            # 添加按钮到第三列
            button2 = QPushButton(f"执行")
            button2.clicked.connect(lambda: self.on_button_click(row, 2))
            self.tableWidget.setCellWidget(row, 2, button2)
    
    def on_button_click(self, row, col):
        print(f"Button clicked at row {row}, column {col}")

def main():
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    print(f"sys.argv: {sys.argv}")
    needUserProcessFile = sys.argv[2:]
    print ('needUserProcessFile',needUserProcessFile)
    fire.Fire()
