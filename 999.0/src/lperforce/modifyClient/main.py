import os
import sys
import re
import json
import traceback

from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QApplication, QComboBox, QVBoxLayout, QHBoxLayout,QPushButton,
                             QLabel, QLineEdit, QSlider,QMessageBox,QFrame,QTableWidget,QTableWidgetItem,
                             QInputDialog,QListWidget,QDialog,QListWidgetItem)
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent, QFont, QColor
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp,QCoreApplication
from importlib import reload

# 设置路径
LugwitToolDir = os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir + '/Lib')

import Lugwit_Module as LM  # noqa: E402
from Lugwit_Module.l_src.UILib.QTLib import self_qss
lprint=LM.lprint

# 获取当前目录
curDir = os.path.dirname(os.path.realpath(__file__))
curDir_Path = Path(curDir)
par_dir = curDir_Path.parent
os.chdir(curDir)

sys.path.insert(0, str(par_dir))
from lperforce import  loginP4
import p4_baselib
import showWeiTiJiao_UI


p4 = loginP4.p4_login(
    port=r'192.168.110.26:1666',
    userName='p4_operator',
    password='123'
)
p4_baselib.p4=p4

users = p4.run("users")

userDict = {x['User']: x for x in users if re.search(r'[\u4e00-\u9fa5]', x['FullName'])}
lprint(p4.user)


def get_user_groups(username):
    # 获取所有组的信息
    groups = p4.run("groups", username)
    if groups:
        # 提取组名
        group_names = [group['group'] for group in groups]
        group_miaoshu= [group['description'] for group in groups]
        return group_names,group_miaoshu
    return ["未设置"],["未设置"]

def getAllGroup():
    groups=p4.run("groups")
    lprint (groups)
    return {x['description'].strip():x["group"].strip() for x in groups}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("迁移工作区")
        self.setMinimumWidth(1200)

        self.lay = QVBoxLayout()
        uic.loadUi(r'qt_uiFile.ui', self)  # 动态加载UI文件
        
        self.groupDict=getAllGroup()
        self.departWgt.addItems(list(self.groupDict.keys())+["未设置"])

        self.connectInfo()

        self.p4_account_wgt.addItems(userDict.keys())

        self.setOldClient()

        self.setProperty('font_size', 'big')
        self.setStyleSheet(self_qss)

    def connectInfo(self):
        self.p4_account_wgt.currentTextChanged.connect(self.userNameChanged)
        self.newUserWgt.clicked.connect(self.newUserWgtFucn)
        self.departWgt.currentTextChanged.connect(self.departWgtChanged)
        self.createClientWgt.clicked.connect(self.createClientFunc)
        self.newClientWgt:QLineEdit
        self.newClientWgt.textChanged.connect(self.setOldClient)
        self.moveChangList.clicked.connect(self.moveChangeNum)
        self.deleteOldClientWgt:QPushButton
        self.deleteOldClientWgt.clicked.connect(self.deleteOldClient)
        func=lambda:os.startfile(r"\\192.168.110.26\共享盘\A\TD\文档资料\迁移工作区\迁移工作区.png")
        self.helpBtn.clicked.connect(func)
        self.refreshClientBtn.clicked.connect(self.refreshClient)
    def newUserWgtFucn(self):
        regex = QRegExp("[a-zA-Z0-9]+")  # 只允许输入英文字符
        validator = QRegExpValidator(regex)

        inputDialog = QInputDialog(self)
        inputDialog.setInputMode(QInputDialog.TextInput)
        inputDialog.setLabelText('请输入英文字符:')
        inputDialog.setWindowTitle('输入框')
        inputDialog.setTextValue('')
        inputDialog.setFixedSize(400, 200)

        lineEdit = inputDialog.findChild(QLineEdit)
        lineEdit.setValidator(validator)

        if inputDialog.exec_() == QInputDialog.Accepted:
            input_text = inputDialog.textValue()
            QMessageBox.information(self, '你好', f'请输入你的中文名和你的部门')
            self.p4_account_wgt.addItem(input_text)
            self.p4_account_wgt.setCurrentText(input_text)
        else:
            QMessageBox.warning(self, '取消输入', '您取消了输入')

    def userNameChanged(self, text):
        print ("组名称改变信号")
        zh_name=userDict.get(text,{}).get('FullName',"")
        self.zh_name_wgt.setText(zh_name)
        print ('zh_name',zh_name)
        groups_Name=get_user_groups(text)[0]
        if groups_Name:
            newClentName='_'.join(groups_Name)+'_'+LM.hostName+"_H"
            self.newClientWgt.setText(newClentName)
        groups_Description=get_user_groups(text)[1]
        print ('groups_Description',groups_Description)
        if groups_Description:
            self.departWgt.setCurrentText(groups_Description[0].strip())

    def departWgtChanged(self,text):
        newClentName=self.groupDict.get(text,"未设置")+'_'+LM.hostName+"_H"
        self.newClientWgt.setText(newClentName)

    def createClientFunc(self):
        clentName=self.newClientWgt.text()
        if "设置" in clentName:
            QMessageBox.warning(self, '提示', '请正确设置你的中文名和部门')
            return
        userName=self.p4_account_wgt.currentText()
        zh_name=self.zh_name_wgt.text()
        reload (p4_baselib)
        global p4
        p4_baselib.p4=p4
        

        if not p4_baselib.user_exist(userName):
            p4_baselib.createUser(userName, zh_name, "", userName+"@qq.com", "standard")
        # 添加用户到组

        p4 = loginP4.p4_login(
            port=r'192.168.110.26:1666',
            userName='p4_operator',
            password='123'
        )
        p4_baselib.addUserToGroup(p4,userName,self.groupDict.get(self.departWgt.currentText()))

        client=p4_baselib.createWorkSpace(p4,userName,workSpacePath='H:\\',workName=clentName,
                                   client_views=[r"//H/... //{Client}/... "],
                                   client_options=["nomodtime",'noallwrite'],
                                   description="个人H盘项目账号")
        if client:
            client_json=json.dumps(client,ensure_ascii=False,indent=4)
            msg_box = QMessageBox(None)
            msg_box.setWindowTitle("恭喜")
            msg_box.setText(f"你的新工作区已经创建完毕\n{client_json}")

            # 设置字体为小号
            font = QFont()
            font.setPointSize(10)  # 设置字体大小为小号
            msg_box.setFont(font)
            msg_box.exec()

        
    def setOldClient(self):
        OldClient = p4_baselib.getOldClient(p4)
        self.OldClientDict = {x['client']: x for x in OldClient}
        lprint (len(self.OldClientDict))
        if self.newClientWgt.text() in self.OldClientDict:
            self.OldClientDict.pop(self.newClientWgt.text())
        lprint (len(self.OldClientDict))
        self.oldClientWgt:QListWidget
        self.oldClientWgt.clear()
        self.oldClientWgt.addItems(self.OldClientDict.keys())

    def moveChangeNum(self):
        reload (p4_baselib)
        p4_baselib.p4=p4
        item_count = self.oldClientWgt.count()
        needTocleanFile={}
        for index in range(item_count):
            clientName = self.oldClientWgt.item(index).text()
            lprint (clientName)
            # changes=p4_baselib.get_changes(clientName)
            allChange = p4.run_opened('-C',clientName)
            # if not all (changes,default_change) :
            #     print ('删除工作区')
            #     return
            lprint(allChange)
            needTocleanFile[clientName]=[x["depotFile"] for x in allChange]
        if needTocleanFile:
            reload (showWeiTiJiao_UI)
            showWeiTiJiao_UI.FileListViewer(needTocleanFile,self)
        else:
            QMessageBox.information(self, '提示', '你的旧工作区已经清理完毕,现在请点击"删除旧的工作区按钮')

    def deleteOldClient(self):
        reload (p4_baselib)
        p4_baselib.p4=p4
        item_count = self.oldClientWgt.count()
        for index in range(item_count):
            clientName = self.oldClientWgt.item(index).text()
            p4_baselib.deleteOldClient(p4,clientName)
        self.setOldClient()
        if self.oldClientWgt.count()==0:
            QMessageBox.information(self,'恭喜',"你的旧工作区已经清理完毕,现在请进行第4步")
            
    def refreshClient(self):
        reload (p4_baselib)
        try:
            if p4_baselib.refresh_H_project_Client(p4):
                QMessageBox.information(self,'恭喜',"已经刷新你的文件状态,现在请通知栏图标右键>>登录P4V-项目")
        except:
            traceback.print_exc()

    def close_application(self):
        QCoreApplication.quit()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

