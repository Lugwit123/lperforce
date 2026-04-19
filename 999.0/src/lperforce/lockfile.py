import msvcrt
import os

def lock_file(file_path):
    """锁定文件以防止其他进程访问。

    参数:
        file_path (str): 要锁定的文件路径。
    """
    file_handle = open(file_path, 'r+')
    try:
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, os.path.getsize(file_path))
        print(f"文件 {file_path} 已锁定。")
        input("按回车键继续...")  # 等待用户输入以保持文件锁定
    finally:
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, os.path.getsize(file_path))
        file_handle.close()
        print(f"文件 {file_path} 已解锁。")

file_path = r"f:\共享盘\H\Test\874964654.txt"  # 需要锁定的文件路径
lock_file(file_path)

r'''
import sys
sys,path.append(r'D:\TD_Depot\plug_in\Lugwit_plug\Lugwit_UnrealPlug\UeGroup')
import test
'''
