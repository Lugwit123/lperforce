import os
import sys

# 设置路径
LugwitToolDir = os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir + '/Lib')

from lperforce import  loginP4
import p4_baselib
import P4Lib

import Lugwit_Module as LM  # noqa: E402
from Lugwit_Module.l_src.UILib.QTLib import self_qss
lprint=LM.lprint

'''
    "解析后的参数字典:",
    {
        "UI": [],
        "cleanFile": "0",
        "files": [
            "//H/CCC/新建文本文档 (3).txt",
            "//H/CCC/e1997b229fc0e0fdad7dbb0aa8e96dcd_t.jpg",
            "//H/DPCQ/..."
        ]
    }
'''

p4 = loginP4.p4_login()
P4Lib.p4 = p4

def expandDirToFiles(file):
    files = p4.run_fstat(file)
    return files
def main(files,*args,**kwargs):
    if isinstance (files,str):
        files=[files]
    fileList=P4Lib.get_ws_depot_size_List(files,method='auto')
    lprint (fileList)


