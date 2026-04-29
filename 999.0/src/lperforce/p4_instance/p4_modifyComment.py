# -*- coding: utf-8 -*-

import datetime
import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI  # 确保您的 OpenAI 类已正确导入
from lperforce import loginP4
from lperforce.P4LoginInfoModule import p4_loginInfo
from P4 import P4, P4Exception
import difflib
import logging
import traceback  # 导入 traceback 模块用于打印完整的异常堆栈信息
import chardet
import time
from Lugwit_Module import lprint
from typing import List, Dict, Optional, Union, TypedDict, Any
from tqdm import tqdm

# 获取当前脚本的目录
curDir = os.path.dirname(os.path.abspath(__file__))

# 从 .env 文件读取 API 密钥
load_dotenv(os.path.join(curDir, ".env"))
apiKey = os.getenv("API_KEY")

if not apiKey:
    lprint("未能读取到 API_KEY，请检查 .env 文件。")
    sys.exit(1)

lprint(f"读取到的 API 密钥: {apiKey[:10]}...")  # 调试用，确认前10个字符

# 初始化 OpenAI 客户端
client = OpenAI(api_key=apiKey, base_url="https://api.deepseek.com")  # 使用您的 OpenAI 类

# 分批大小
BATCH_SIZE = 1000  # 设置默认批次大小为1000字符

class P4FileInfo(TypedDict):
    depotFile: str
    action: str
    rev: str
    change: str
    type: str
    client: str
    user: str
    time: str

class P4ChangeSpec(TypedDict):
    Change: str
    Client: str
    User: str
    Status: str
    Description: str
    Files: List[str]

class P4RevisionInfo(TypedDict):
    headRev: str
    haveRev: str
    depotFile: str

class P4PrintResult(TypedDict):
    """P4 print命令返回的结果结构"""
    depotFile: str  # depot文件路径
    rev: str       # 版本号
    action: str    # 动作类型
    type: str      # 文件类型
    content: str   # 文件内容

def get_weekly_changes(p4: P4, days: int = 7) -> List[str]:
    """
    获取最近几天内的changelist编号列表
    """
    try:
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(days=days)
        start_time_str = start_time.strftime("%Y/%m/%d")

        user_name = p4_loginInfo['plug']['User']
        changes = p4.run_changes([
            '-s', 'submitted',
            f'@{start_time_str},@now'
        ])

        weekly_change_numbers = [int(c['change']) for c in changes]
        return weekly_change_numbers

    except P4Exception as e:
        lprint(f"[get_weekly_changes] 获取 changelist 失败: {e}")
        lprint(traceback.format_exc())  # 打印完整的异常堆栈信息
        return []

def get_file_content(p4: P4, depot_file: str, revision: Union[str, int]) -> Optional[str]:
    """获取指定版本的文件内容
    
    Args:
        p4: P4对象
        depot_file: depot文件路径
        revision: 版本号
        
    Returns:
        Optional[str]: 文件内容，如果是二进制文件则返回None
    """
    try:
        # 获取文件内容
        content: List[P4PrintResult] = p4.run_print(f"{depot_file}#{revision}")
        if content:
            # 获取实际的文件内容（第一个元素是文件信息，后面的才是内容）
            # content[0]包含文件信息: {'depotFile': '//path', 'rev': '1', 'action': 'edit', 'type': 'text'}
            # content[1:]包含实际文件内容

            lprint(type(content[1]))
            if isinstance(content[1],str):
                return content[1]
                # # 使用 chardet 检测编码格式
                # encoding = chardet.detect(content[1])['encoding'] or 'utf-8'
                
                # # 解码内容
                # return content[1].decode(encoding)
        else:
            return ''
    except P4Exception as e:
        lprint(f"[get_file_content] 获取文件 {depot_file}@{revision} 内容失败: {e}")
        lprint(traceback.format_exc())
        return ''

def generate_diff(old_content: str, new_content: str, depot_file: str, old_revision: Union[str, int], new_revision: Union[str, int]) -> str:
    """
    生成两个文件内容之间的统一差异
    """
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"{depot_file}@{old_revision}",
        tofile=f"{depot_file}@{new_revision}"
    )
    return ''.join(diff)

def split_into_diff_blocks(diffs: str) -> list[str]:
    """
    将diff文本按照diff块分割
    """
    # 使用diff文件的标准开头模式来分割
    blocks = []
    current_block = []
    
    for line in diffs.splitlines(True):  # keepends=True 保留换行符
        if line.startswith('diff --git') or line.startswith('@@'):
            if current_block:
                blocks.append(''.join(current_block))
                current_block = []
        current_block.append(line)
    
    if current_block:
        blocks.append(''.join(current_block))
    
    return blocks

def generate_summary(diffs: str, batch_size: int = BATCH_SIZE, change_num=0) -> str:
    """
    使用 OpenAI API 生成差异的摘要，支持分批处理
    """
    # 首先按diff块分割
    diff_blocks = split_into_diff_blocks(diffs)
    
    # 然后将diff块组合成批次，确保每个批次不超过batch_size
    current_batch = []
    current_size = 0
    diff_batches = []
    
    for block in diff_blocks:
        block_size = len(block)
        if current_size + block_size > batch_size:
            if current_batch:  # 如果当前批次不为空，添加到批次列表
                diff_batches.append(''.join(current_batch))
                current_batch = []
                current_size = 0
            # 如果单个块超过batch_size，需要单独处理
            if block_size > batch_size:
                diff_batches.append(block[:batch_size])
                continue
        
        current_batch.append(block)
        current_size += block_size
    
    if current_batch:
        diff_batches.append(''.join(current_batch))

    summaries = []
    
    # 使用tqdm显示处理进度
    for i, batch in enumerate(tqdm(diff_batches, desc="生成差异摘要", unit="batch")):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes code changes."},
                    {"role": "user", "content": f"请根据以下代码差异生成一个专业的提交摘要,MarkDown格式,"+
                    "不同类型的修改使用不同的颜色标记不同的文字,不要使用蓝色标记文字:"+
                    "不要包含\"```markdown这样的字样\",忽略node_modules文件夹下的文件"+
                    f"代码差异如下\n{batch}"}
                ],
                stream=False
            )
            summary = response.choices[0].message.content.strip()
            summaries.append(summary)
            lprint(f"为更改列表{change_num}生成的摘要:\n{summary[:200]}\n")  # 调试用，确认摘要内容
        except Exception as e:
            lprint(f"[generate_summary] 生成摘要失败: {e}")
            lprint(traceback.format_exc())  # 打印完整的异常堆栈信息

    return "\n".join(summaries)

def modify_change_description(p4: P4, change_num: str, new_description: str) -> None:
    """
    尝试修改指定已提交 Changelist 的描述信息
    """
    try:
        # 检查是否已登录
        login_status = p4.run("login", "-s")
        lprint(f"登录状态: {login_status}")

        # 获取 Changelist 规格
        change_spec = p4.fetch_change(change_num)
        original_description = change_spec['Description']
        lprint(f"原描述 for Changelist {change_num}:\n{original_description}")

        # 修改描述
        change_spec['Description'] = new_description

        # 尝试保存修改（需要 -f 参数）
        p4.save_change(change_spec, '-f')
        lprint(f"成功修改 Changelist {change_num} 的描述。")

    except P4Exception as e:
        lprint(f"[modify_change_description] 修改 Changelist {change_num} 描述失败: {e}")
        lprint(traceback.format_exc())  # 打印完整的异常堆栈信息

def is_text_file(file_path: str) -> bool:
    """
    简单判断文件类型，可以根据需要扩展
    """
    text_extensions = [
        '.py', '.ts', '.tsx', '.css', '.json', '.html', '.bat', '.cmd',
        '.md', '.txt', '.js', '.jsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.sh', '.rb', '.go', '.php', '.swift', '.kt', '.css', '.usf','.ush',
    ]
    return any(file_path.endswith(ext) for ext in text_extensions)

def get_previous_revision(p4: P4, depot_file: str, current_revision: Union[str, int]) -> Optional[str]:
    """
    获取指定文件的前一个 revision
    """
    try:
        filelog = p4.run_filelog(depot_file)
        
        if not filelog:
            return None
        # 假设 filelog 是一个列表，获取第一个文件的日志
        f = filelog[0]
        revisions = f.revisions
        # 遍历修订版列表，找到当前修订版的前一个修订版
        for i, rev in enumerate(revisions):
            if rev.rev == int(current_revision):
                if i > 0:
                    return revisions[i - 1].rev
                    print("revisions1111",revisions[i - 1].rev)
        os._exit(0)
        return None
    except P4Exception as e:
        lprint(f"[get_previous_revision] 获取文件 {depot_file} 前一个 revision 失败: {e}")
        lprint(traceback.format_exc())  # 打印完整的异常堆栈信息
        return None

def main() -> None:
    """
    主函数流程
    1. 登录 Perforce (p4)
    2. 获取最近一周内的所有提交的 Changelist
    3. 获取每个 Changelist 的差异
    4. 使用 OpenAI 生成摘要
    5. 修改 Changelist 描述
    6. 汇总并打印所有摘要
    """
    # 初始化汇总列表
    weekly_summaries = []

    # ----------------------------
    # 1. 登录 p4
    # ----------------------------
    try:
        p4 = loginP4.p4_login(
            userName=p4_loginInfo['plug']['User'],         # 修改为 'plug'
            port=p4_loginInfo['plug']['port'],             # 修改为 'plug'
            clientName=p4_loginInfo['plug']['clientName']  # 修改为 'plug'
        )
        lprint("已成功登录 Perforce。")

    except P4Exception as e:
        lprint(f"[main] 登录 Perforce 失败: {e}")
        lprint(traceback.format_exc())  # 打印完整的异常堆栈信息
        sys.exit(1)

    # ----------------------------
    # 2. 获取一周内所有 changelist
    # ----------------------------
    weekly_changes = get_weekly_changes(p4, days=2)
    if not weekly_changes:
        lprint("本周内没有找到任何提交的 changelist。")
        p4.disconnect()
        sys.exit(0)

    lprint(f"本周的 Changelist 编号: {weekly_changes[:10]}...")
    # ----------------------------
    # 3. 处理每个 changelist
    # ----------------------------
    for i,change_num in enumerate(weekly_changes):
        try:
            lprint(f"处理 Changelist {change_num},{i}/{len(weekly_changes)} ...")
            all_diffs = ""

            # 获取该 changelist 中的文件列表及其操作类型
            files_in_change = p4.run_describe("-s", change_num)
            if files_in_change[0].get("desc").startswith("#"):
                lprint(f"更改列表{change_num}已经有备注了,跳过")
                continue

            if not files_in_change:
                lprint(f"Changelist {change_num} 没有文件，跳过。")
                continue

            depot_files = files_in_change[0].get('depotFile', [])
            actions = files_in_change[0].get('action', [])
            file_actions = list(zip(depot_files, actions))

            # 过滤出文本文件
            text_file_actions = [(f, a) for f, a in file_actions if is_text_file(f) and 'node_modules' not in f]
            if not text_file_actions:
                lprint(f"Changelist {change_num} 中没有文本文件，跳过。")
                continue

            # 检查是否所有操作都是删除操作
            all_delete_actions = all(action.lower() == 'delete' for _, action in text_file_actions)
            
            if all_delete_actions :
                # 如果全是删除操作，只记录文件路径
                deleted_files = [depot_file for depot_file, _ in text_file_actions]
                description = f"删除了以下文件:\n" + "\n".join(f"- {file}" for file in deleted_files)
                
                try:
                    modify_change_description(p4, change_num, description)
                    lprint(f"已更新Changelist {change_num}的描述为删除文件列表。")
                    
                    # 收集摘要信息
                    weekly_summaries.append({
                        'change_num': change_num,
                        'summary': description
                    })
                    continue
                except Exception as e:
                    lprint(f"更新Changelist {change_num}描述时出错: {str(e)}")
                    continue

            all_diffs = ""
            for depot_file, action in text_file_actions:
                lprint(f"处理文件: {depot_file}，操作类型: {action}")

                if action.lower() == 'add':
                    # 新增文件，没有前一个版本
                    current_revision_info = p4.run("fstat", "-T", "headRev", depot_file)
                    if not current_revision_info:
                        lprint(f"无法获取新增文件 {depot_file} 的 headRev。")
                        continue
                    current_revision = current_revision_info[0].get('headRev')
                    if not current_revision:
                        lprint(f"无法获取新增文件 {depot_file} 的 headRev。")
                        continue
                    current_content = get_file_content(p4, depot_file, current_revision)
                    if current_content:
                        diff_str = f"--- /dev/null\n+++ {depot_file}@{current_revision}\n{current_content}"
                        all_diffs += f"\n# 文件: {depot_file}\n" + diff_str
                    else:
                        lprint(f"无法获取新增文件 {depot_file}@{current_revision} 的内容。")
                        continue

                elif action.lower() == 'edit':
                    # 编辑文件，获取前一个版本
                    current_revision_info = p4.run("fstat", "-T", "headRev", depot_file)
                    if not current_revision_info:
                        lprint(f"无法获取编辑文件 {depot_file} 的 headRev。")
                        continue
                    current_revision = current_revision_info[0].get('headRev')
                    if not current_revision:
                        lprint(f"无法获取编辑文件 {depot_file} 的 headRev。")
                        continue
                    previous_revision = int(current_revision)-1

                    if previous_revision:
                        previous_content = get_file_content(p4, depot_file, previous_revision)
                        current_content = get_file_content(p4, depot_file, current_revision)
                        if previous_content is None:
                            previous_content = ""
                        if current_content is None:
                            current_content = ""

                        diff_str = generate_diff(previous_content, current_content, depot_file, previous_revision, current_revision)
                        if diff_str:
                            all_diffs += f"\n# 文件: {depot_file}\n" + diff_str
                        else:
                            lprint(f"生成文件 {depot_file} 的差异失败。")
                    else:
                        lprint(f"文件 {depot_file} 没有前一个 revision，无法生成差异。")
                        continue

                elif action.lower() == 'delete':
                    # 如果已经在上面处理过全部删除的情况，这里就跳过
                    if all_delete_actions:
                        continue
                        
                    # 删除文件，获取最后一个版本
                    try:
                        deleted_revision_info = p4.run("fstat", "-T", "headRev", depot_file)
                        if not deleted_revision_info:
                            lprint(f"无法获取删除文件 {depot_file} 的 headRev。")
                            continue
                        deleted_revision = deleted_revision_info[0].get('headRev')
                        if not deleted_revision:
                            lprint(f"无法获取删除文件 {depot_file} 的 headRev。")
                            continue
                        deleted_content = get_file_content(p4, depot_file, deleted_revision)
                        if deleted_content:
                            diff_str = f"--- {depot_file}@{deleted_revision}\n+++ /dev/null\n{deleted_content}"
                            all_diffs += f"\n# 文件: {depot_file}\n" + diff_str
                        else:
                            lprint(f"无法获取删除文件 {depot_file}@{deleted_revision} 的内容。")
                    except Exception as e:
                        lprint(f"处理删除文件 {depot_file} 时出错: {str(e)}")
                        continue

                else:
                    lprint(f"文件 {depot_file} 的操作类型 {action} 未处理，跳过。")
                    continue

            if not all_diffs and not all_delete_actions:
                lprint(f"Changelist {change_num} 没有可用的差异进行摘要生成。")
                continue

            # 只有在非全部删除操作的情况下才使用OpenAI生成摘要
            if not all_delete_actions:
                summary = generate_summary(all_diffs, batch_size=50000, change_num=change_num)
                if summary:
                    lprint(f"生成的摘要 for Changelist {change_num}:\n{summary}")
                    # 修改 changelist 描述
                    modify_change_description(p4, change_num, summary)

                    # 收集摘要信息
                    weekly_summaries.append({
                        'change_num': change_num,
                        'summary': summary
                    })
                else:
                    lprint(f"未能为 Changelist {change_num} 生成摘要。")

        except Exception as e:
            lprint(f"[main] 处理 Changelist {change_num} 时出错: {e}")
            lprint(traceback.format_exc())  # 打印完整的异常堆栈信息

    # ----------------------------
    # 4. 汇总并打印所有摘要
    # ----------------------------
    if weekly_summaries:
        lprint("\n## 最近一周的 Changelist 摘要\n")
        with open(curDir+"/weekly_summaries.md", "w") as f:
            json.dump(weekly_summaries, f, indent=4, ensure_ascii=False) 
    else:
        lprint("\n## 最近一周内没有生成任何摘要。\n")

    # ----------------------------
    # 完成
    # ----------------------------
    lprint("\n所有操作已完成。")
    p4.disconnect()

if __name__ == "__main__":
    main()

