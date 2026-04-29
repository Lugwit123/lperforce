import codecs
import psutil
import subprocess
import sys
import os
import time
import json
from multiprocessing import Pool, cpu_count
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
import ctypes
import win32gui
import win32process
from concurrent.futures import ProcessPoolExecutor, as_completed
import fire
from tqdm import tqdm

def get_hwnds_for_pid(pid):
    hwnds = []
    
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True
    
    win32gui.EnumWindows(callback, None)
    return hwnds

def get_window_title_from_pid(pid):
    hwnds = get_hwnds_for_pid(pid)
    titles = [win32gui.GetWindowText(hwnd) for hwnd in hwnds]
    return titles

def check_files(proc_info, normalized_paths_set):
    print(proc_info, list(normalized_paths_set)[:5])
    locked_files = []
    pid, proc_name = proc_info
    try:
        proc = psutil.Process(pid)
        open_files = proc.open_files()
        exe_path = proc.exe()
        window_title = get_window_title_from_pid(pid)

        for file in open_files:
            file_path = file.path.replace('\\', '/').lower()
            for path in normalized_paths_set:
                if path.endswith('/'):
                    # Check if file_path starts with path (directory)
                    if file_path.startswith(path.rstrip('/')):
                        locked_files.append((proc_name, file.path, pid, exe_path, window_title))
                        break
                else:
                    # Check for exact match
                    if file_path == path:
                        locked_files.append((proc_name, file.path, pid, exe_path, window_title))
                        break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    return locked_files

def find_locked_files_in_paths(paths):
    target_processes = {'maya.exe', 'houdini.exe', 'houdinifx.exe', 'hython.exe', 'unrealeditor.exe'}
    locked_files = []

    # 预处理路径
    normalized_paths = set()
    for path in paths:
        if path.startswith('//'):
            path = path.lstrip('/')
        path = path.replace('//H', 'H:')
        path = path.replace('\\', '/')
        path = path.replace('/...', '/')
        path = path.lower()
        normalized_paths.add(path)
    print("normalized_paths:", list(normalized_paths)[:10])

    # 获取目标进程信息
    target_proc_info = []
    proc_list = psutil.process_iter(['pid', 'name'])
    for proc in proc_list:
        if proc.info['name'].lower() in target_processes:
            target_proc_info.append((proc.info['pid'], proc.info['name']))
            print(f"打开的进程有 {proc.info['name']}")

    print(f"找到 {len(target_proc_info)} 个目标进程，开始检查锁定的文件...")

    # 设置最大线程数量
    cpu_amount = min(cpu_count(), 50)

    # 使用 ProcessPoolExecutor 进行并行处理
    with ProcessPoolExecutor(max_workers=cpu_amount) as executor:
        print("开始多进程检查")
        future_to_proc = {executor.submit(check_files, proc_info, normalized_paths): proc_info for proc_info in target_proc_info}
        
        # 使用 tqdm 显示进度
        for future in tqdm(as_completed(future_to_proc), total=len(future_to_proc), desc="检查进程文件"):
            try:
                result = future.result()
                locked_files.extend(result)
            except Exception as e:
                print(f"任务执行时出错: {e}")

    print(f"完成检查，共找到 {len(locked_files)} 个被锁定的文件。")
    return locked_files

def check_files(proc_info, normalized_paths_set):
    print(proc_info, list(normalized_paths_set)[:5])
    locked_files = []
    pid, proc_name = proc_info
    try:
        proc = psutil.Process(pid)
        open_files = proc.open_files()
        print(f"进程 {proc_name} (PID: {pid}) 打开的文件数量: {len(open_files)}")
        exe_path = proc.exe()
        window_title = get_window_title_from_pid(pid)

        for file in open_files:
            file_path = file.path.replace('\\', '/').lower()
            for path in normalized_paths_set:
                if path.endswith('/'):
                    if file_path.startswith(path.rstrip('/')):
                        locked_files.append((proc_name, file.path, pid, exe_path, window_title))
                else:
                    print(file_path , path)
                    break
                    if file_path == path:
                        locked_files.append((proc_name, file.path, pid, exe_path, window_title))
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        print(f"无法处理进程 {proc_name} (PID: {pid})：{e}")
    except Exception as e:
        print(f"处理进程 {proc_name} 时发生意外错误: {e}")
    return locked_files


class LockedFilesWindow(QMainWindow):
    def __init__(self, locked_files):
        super().__init__()
        self.setWindowTitle("下面的文件被占用,你需要关闭这些软件或者强制解锁文件,强制解锁文件可能会关闭这些程序")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(locked_files))
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Process", "Locked File", "PID"])
        layout.addWidget(self.table_widget)

        for row, (process, file, pid, exe_path, window_title) in enumerate(locked_files):
            item = QTableWidgetItem(process)
            item.setToolTip(f"Window Title: {window_title}\nExecutable Path: {exe_path}")
            self.table_widget.setItem(row, 0, item)
            self.table_widget.setItem(row, 1, QTableWidgetItem(file))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(pid)))

        self.table_widget.resizeColumnsToContents()

        self.unlock_button = QPushButton("强制解锁文件")
        self.unlock_button.clicked.connect(self.confirm_close_pids)
        layout.addWidget(self.unlock_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def confirm_close_pids(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("强制解锁文件可能会关闭表格中打开文件的程序，请注意保存你的文件。")
        msg_box.setWindowTitle("警告")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg_box.button(QMessageBox.Yes).setText("这些文件不需要保存,我要直接关闭这些打开文件的程序")
        msg_box.button(QMessageBox.Cancel).setText("请暂且退下,我要手动处理这些文件")
        msg_box.setDefaultButton(QMessageBox.Cancel)
        
        result = msg_box.exec()

        if result == QMessageBox.Yes:
            self.close_pids()
        else:
            os._exit(666)
    def close_pids(self):
        selected_rows = range(self.table_widget.rowCount())
        pid_list = []
        for row in selected_rows:
            pid = self.table_widget.item(row, 2).text()
            if pid not in pid_list:
                os.system(f'taskkill /F /PID {pid} /T')
                pid_list.append(pid)
        os._exit(0)

    def closeEvent(self, event):
        os._exit(666)
        event.accept()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(command):
    if is_admin():
        subprocess.run(command)
    else:
        print('command', " ".join(command))
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", " ".join(command), None, 1)

def main(recordOnlockFile=''):
    # with codecs.open(recordOnlockFile, 'r',encoding='utf8') as f:
    #     paths_to_check = json.load(f)  
    paths_to_check = [r"H:/DPCQ/..."]
    print (f'检查文件{paths_to_check[:5]}...,一共{len(paths_to_check)}个') 
    locked_files = find_locked_files_in_paths(paths_to_check)
    print("获取解锁文件花费时间",time.time() - st)
    #print("Locked files:", locked_files)
    if locked_files:
        app = QApplication(sys.argv)
        window = LockedFilesWindow(locked_files)
        window.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    st = time.time()
    paths_to_check=[]
    print ('sys.argv',sys.argv)
    fire.Fire(main)

        
