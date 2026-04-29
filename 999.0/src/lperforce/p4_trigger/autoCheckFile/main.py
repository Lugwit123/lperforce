# -*- coding: utf-8 -*-
"""
P4触发器检查ABC文件的主模块
用于检查提交的ABC文件是否符合命名规范
"""

# 标准库导入
import os
import sys
import io
from pathlib import Path
import datetime
import time
import json
import subprocess
from typing import List, Dict, Optional, TypedDict, Any, Union

# 第三方库导入
from P4 import P4

# 本地模块导入
from ChatRoom.clientend import sendAbcMessage
import Lugwit_Module as LM
from lperforce import loginP4
from lperforce.P4LoginInfoModule import p4_loginInfo
from L_Tools.AbcTools.get_abc_data import process_alembic_files, AbcFileData
from L_DeadLine.DeadLinePy3 import deadline_submit
lprint=LM.lprint

# 类型定义
class P4ChangelistData(TypedDict):
    """Perforce变更集数据结构"""
    depotFile: List[str]
    change: str
    user: str
    client: str
    time: str
    desc: str

class P4WhereData(TypedDict):
    """Perforce文件路径映射数据结构"""
    path: str
    depotFile: str
    clientFile: str

if not os.path.exists(r'B:/'):
    subprocess.run(r'net use B: \\192.168.110.27\ShareDir', shell=True)
ABC_CHECK_DATA_DIR: str = r'B:/TD/fileCheck/'
LUGWIT_TOOL_DIR: str = os.environ["LugwitToolDir"]
SYNC_ERROR_FILE: str = r"D:\TD_Depot\Log\p4_triggers_error.log"
SYNC_LOG_FILE: str = r"D:\TD_Depot\Log\p4_triggers.log"
DATE_TIME_FORMAT: str = "%Y_%m_%d__%H_%M_%S"
CALL_PYD: str = r'D:\TD_Depot\plug_in\Lugwit_plug\mayaPlug\l_scripts\IOLib\CallPyd.py'
ANI_EX_BAT_FILE: str = r'A:/TD/RenderFarm/MayaToUE/P4Triggers/autoExFile/发送到MayaToUE_不带日志_强制全部重新导出并发送到Deadline.bat'

def setup_environment() -> None:
    """设置运行环境"""
    # 设置当前工作目录
    cur_dir: str = os.path.dirname(os.path.realpath(__file__))
    cur_dir_path: Path = Path(cur_dir)
    par_dir: Path = cur_dir_path.parent
    sys.path.insert(0, str(par_dir))
    
    # 设置标准输出编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # 确保网络驱动器已连接
    if not os.path.exists(r'A:/'):
        subprocess.run(r'net use A: \\192.168.110.61\A', shell=True)

def init_p4() -> P4:
    """初始化P4连接"""
    p4: P4 = loginP4.p4_login(
        userName=p4_loginInfo['project']['User'],  # type: ignore
        port=p4_loginInfo['project']['port'],  # type: ignore
        clientName=p4_loginInfo['project']['clientName']  # type: ignore
    )
    p4.exception_level = 1
    p4.charset = "utf8"
    return p4

def get_local_paths(p4: P4, changelist: P4ChangelistData) -> List[str]:
    """获取需要处理的本地ABC文件路径列表"""
    local_paths: List[str] = []
    depot_files: Optional[List[str]] = changelist.get("depotFile")
    
    if depot_files:
        for depot_file in depot_files:
            where_result: List[P4WhereData] = p4.run_where(depot_file)
            if where_result:
                local_path: str =os.path.normpath(where_result[0].get('path'))
                local_path = local_path.replace('\\','/')
                
                if os.path.exists(local_path) and local_path.endswith('.abc'):
                    LM.lprint(f"处理ABC文件: {depot_file} -> {local_path}")
                    local_paths.append(local_path)
    
    return local_paths

def check_abc_files(recipient: str,local_paths: List[str]) -> bool:
    """检查ABC文件是否有问题,返回是否存在问题"""
    lprint(local_paths)
    abc_data_dict: List[AbcFileData] = process_alembic_files(local_paths)
    LM.lprint(abc_data_dict)
    has_issue_list: List[str] = []
    last_abc_file: Optional[str] = None

    # 检查每个ABC文件
    for abc_data in abc_data_dict:
        table_data_info = abc_data.get('table_data')
        abc_file = abc_data.get('abc_path')
        if table_data_info and abc_file:
            last_abc_file = abc_file
            for table_data in table_data_info:
                if table_data.get('has_issue'):
                    has_issue_list.append(abc_file.replace('D:/H','H:'))

    # 如果存在问题,生成报告并发送消息
    if has_issue_list and last_abc_file:
        json_file_path: str = ABC_CHECK_DATA_DIR + \
            fr'{datetime.datetime.now().strftime(DATE_TIME_FORMAT)}_abc_data.json'

        with open(json_file_path, 'w', encoding='utf8') as f:
            json.dump(abc_data_dict, f, ensure_ascii=False, indent=4)
        # os.startfile(os.path.dirname(json_file_path))

        sendAbcMessage.send_message(recipient=recipient,
                                jsonFilePath=json_file_path)
        print("你上传的abc文件有误，请在日志中查看")
        LM.lprint(has_issue_list)
        return True
    return False

def main() -> None:
    """主函数"""
    setup_environment()
    
    # 初始化P4连接
    p4 = init_p4()
    
    # 获取变更集号
    change_num: Union[str, int] = sys.argv[1] if len(sys.argv) > 1 else 30755
    LM.lprint(f'处理变更集: {change_num}')
    
    # 获取变更集信息
    changelist: P4ChangelistData = p4.run_describe(change_num)[0]
    LM.lprint(changelist)
    
    # 获取需要处理的本地文件路径
    local_paths = get_local_paths(p4, changelist)
    
    # 检查ABC文件
    check_abc_files(changelist.get('user'),local_paths)
    # sys.exit(1)

if __name__ == "__main__":
    main()

