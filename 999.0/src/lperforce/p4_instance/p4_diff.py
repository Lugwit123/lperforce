import os
import sys
import concurrent.futures
sys.path.append(r'D:\TD_Depot\plug_in\Python\py39Lib')
import fire

Lugwit_publicPath = os.environ.get('Lugwit_publicPath')
LugwitToolDir = os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir + '/Lib')
import Lugwit_Module as LM
from lperforce import (loginP4, p4_baselib, P4Lib)
from lperforce.P4LoginInfoModule import p4_loginInfo
from P4 import P4, P4Exception

# 使用登录信息进行 P4 登录
p4 = loginP4.p4_login(userName=p4_loginInfo['project']['User'],
                      port=p4_loginInfo['project']['port'],
                      wsDir='H:/')
P4Lib.p4 = p4

def create_p4_connection():
    # 创建一个新的 P4 实例，并从现有连接复制登录信息
    p4_thread = P4()
    p4_thread.user = p4.user
    p4_thread.port = p4.port
    p4_thread.client = p4.client
    p4_thread.connect()
    return p4_thread

def is_file_modified(depot_file):
    p4_thread = create_p4_connection()
    try:
        # 使用 p4 diff -sa 检查文件是否与工作区版本不同
        diff_output = p4_thread.run_diff("-sa", depot_file)
        return depot_file if diff_output else None
    except P4Exception as e:
        print(f"Error checking if file is modified: {e}")
        return None
    finally:
        p4_thread.disconnect()

def check_files_in_directory(depot_path):
    try:
        # 获取目录下所有文件的状态信息
        file_stats = p4.run_fstat(f"{depot_path}/...")
        depot_files = [file_stat['depotFile'] for file_stat in file_stats if 'depotFile' in file_stat]

        # 在主线程中运行 p4 have 检查文件是否存在于本地
        local_files = []
        for depot_file in depot_files:
            have_info = p4.run_have(depot_file)
            if have_info:
                local_files.append(depot_file)

        modified_files = []
        # 使用多线程来并行处理本地存在的文件
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(is_file_modified, depot_file): depot_file for depot_file in local_files}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    modified_files.append(result)

        if modified_files:
            for file in modified_files:
                print(f"文件已修改（但未打开）: {file}")
        else:
            print("所有文件均未被修改")
    except P4Exception as e:
        print(f"Error: {e}")

# 定义 Perforce 路径
depot_path = "//H/CCC"

# 调用多线程检查函数
check_files_in_directory(depot_path)

# 断开 P4Python 连接
p4.disconnect()

