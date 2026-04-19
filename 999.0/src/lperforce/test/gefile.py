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



p4 = loginP4.p4_login(
    port=r'192.168.110.26:1666',
    userName='fengqingqing',
    password='123',
    wsDir='H:/'
)

print (p4)
p4.run("configure", "set", "sys.rename.max=2")  # 设置重试次数为50次
p4.run("sync", "//H/WXXJDGD/13.CFX/ep003/ep003_sc001_shot0030/ep003_sc001_shot0030_LiWuWang.abc")
