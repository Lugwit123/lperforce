import json
from dataclasses import dataclass, asdict, field
from typing import List, Literal ,Optional
import codecs
import os
import sys
import Lugwit_Module as LM
lprint=LM.lprint
import traceback

filename = os.path.expandvars(LM.userConfigFile)

@dataclass
class GroupInfo:
    name: str
    description: str

@dataclass
class P4LoginInfo:
    Access: str
    AuthMethod: int
    Email: str
    FullName: str
    Type: str
    Update: str
    User: str
    userGroups: List[GroupInfo]  # 组名称,组描述
    clientName: str
    clientType: Literal["plug", "project"]
    port: Literal["192.168.110.61:1666", "192.168.110.26:1666"]
    customGroups: List[str] = field(default_factory=list)
    passwordChange:str=""
    clientRoot: str = ""

# 手动列出所有 P4LoginInfo 的属性，用于智能提示
P4LoginInfoKeys = Literal[
    "Access", "AuthMethod", "Email", "FullName", "Type", 
    "Update", "User", "userGroups", "clientName", 
    "clientType", "port", "customGroups"
]

def write_p4login_info(login_infos: List[P4LoginInfo], skip_keys: List[P4LoginInfoKeys] = ["customGroups"]) -> None:
    """
    将多个 P4LoginInfo 实例写入 JSON 文件中，每个实例以其 clientType 为根键。
    如果指定的键在 skip_keys 中且文件中已有该值，则保留原值。
    
    :param login_infos: P4LoginInfo 的列表
    :param skip_keys: 要跳过写入的键列表，默认跳过 "customGroups"
    """
    data = {}
    lprint(locals(),filename)
    # 检查文件是否存在，存在则读取原有数据
    if os.path.exists(filename):
        with codecs.open(filename, "r", encoding='utf8') as f:
            try:
                data = json.load(f)
            except:
                traceback.print_exc()


    # 更新数据
    lprint(login_infos)
    for info in login_infos:
        if not info:
            continue
        info_dict = asdict(info)
        client_type = info_dict['clientType']
        
        # 如果 clientType 已存在于现有数据中，需要保留 skip_keys 中的值
        if client_type in data:
            existing_info = data[client_type]
            for key in skip_keys:
                # 保留已有数据中的值
                if key in existing_info:
                    info_dict[key] = existing_info[key]
        
        # 更新或添加新的信息
        data[client_type] = info_dict

    # 写入合并后的数据到文件
    with codecs.open(filename, "w", encoding='utf8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data written to {filename} successfully.")



def read_p4login_info(filename: str) -> List[P4LoginInfo]:
    """
    从 JSON 文件中读取多个 P4LoginInfo 实例。
    """
    if not os.path.exists(filename): return

    with codecs.open(filename, "r", encoding='utf8') as f:
        try:
            data = json.load(f)
        except:
            traceback.print_exc()
            return
    login_infos = []
    for client_type, info_dict in data.items():
        groups = [GroupInfo(**group) for group in info_dict['userGroups']]
        login_info = P4LoginInfo(
            Access=info_dict['Access'],
            AuthMethod=info_dict['AuthMethod'],
            Email=info_dict['Email'],
            FullName=info_dict['FullName'],
            Type=info_dict['Type'],
            Update=info_dict['Update'],
            User=info_dict['User'],
            userGroups=groups,
            clientName=info_dict['clientName'],
            clientType=client_type,
            port=info_dict['port'],
            customGroups=info_dict.get('customGroups', [])
        )
        login_infos.append(login_info)
    
    return login_infos

def update_p4login_info(client_type: str, key: P4LoginInfoKeys, value) -> None:
    """
    更新 JSON 文件中指定 clientType 的 P4LoginInfo 实例的某个参数。
    """
    # 读取现有数据
    login_infos = read_p4login_info(filename)
    
    # 查找指定 clientType 的对象并修改参数
    for info in login_infos:
        if info.clientType == client_type:
            setattr(info, key, value)
            print(f"Updated {client_type} {key} to {value}.")
    
    # 将修改后的数据重新写入文件
    write_p4login_info(login_infos,skip_keys=[])

def get_p4login_info_value(client_type: Literal["plug", "project"], key: P4LoginInfoKeys):
    """
    获取 JSON 文件中指定 clientType 的 P4LoginInfo 实例的某个参数值。
    """
    # 读取现有数据
    if not os.path.exists(filename):
        return
    login_infos = read_p4login_info(filename)
    LM.lprint(login_infos)
    if not login_infos:
        return
    # 查找指定 clientType 的对象并获取参数值
    for info in login_infos:
        if info.clientType == client_type:
            return getattr(info, key)

    print(f"Client type '{client_type}' not found.")
    return None

def get_user_group_names(client_type: Literal["plug", "project"]) -> Optional[List[str]]:
    """
    获取指定 clientType 的用户组名称列表。
    
    :param client_type: 指定的 clientType ("plug" 或 "project")。
    :return: 用户组名称列表，如果 clientType 不存在或没有数据，返回 None。
    """
    # 读取现有数据
    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist.")
        return None

    login_infos = read_p4login_info(filename)
    if not login_infos:
        return None

    # 查找指定 clientType 的对象并获取用户组名称
    for info in login_infos:
        if info.clientType == client_type:
            return [group.name for group in info.userGroups]

    print(f"Client type '{client_type}' not found.")
    return None

def get_user_group_descriptions(client_type: Literal["plug", "project"]) -> Optional[List[str]]:
    """
    获取指定 clientType 的用户组名称列表。
    
    :param client_type: 指定的 clientType ("plug" 或 "project")。
    :return: 用户组名称列表，如果 clientType 不存在或没有数据，返回 None。
    """
    # 读取现有数据
    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist.")
        return None

    login_infos = read_p4login_info(filename)
    if not login_infos:
        return None

    # 查找指定 clientType 的对象并获取用户组名称
    for info in login_infos:
        if info.clientType == client_type:
            return [group.description for group in info.userGroups]

    print(f"Client type '{client_type}' not found.")
    return None
    
# 示例使用
if __name__ == "__main__":
    # 创建示例数据
    group1 = GroupInfo(name="Admin", description="Administrators group")
    group2 = GroupInfo(name="Dev", description="Developers group")
    login_info_1 = P4LoginInfo(
        Access="2024-10-25",
        AuthMethod=2,
        Email="user1@example.com",
        FullName="User One",
        Type="standard",
        Update="2024-10-20",
        User="userone",
        userGroups=[group1],
        clientName="client_01",
        clientType="plug",
        port="192.168.110.61:1666"
    )
    login_info_2 = P4LoginInfo(
        Access="2024-10-26",
        AuthMethod=1,
        Email="user2@example.com",
        FullName="User Two",
        Type="admin",
        Update="2024-10-21",
        User="usertwo",
        userGroups=[group2],
        clientName="client_02",
        clientType="project",
        port="192.168.110.26:1666"
    )

    # 写入示例数据到 JSON 文件
    write_p4login_info([login_info_1, login_info_2])

    # 读取 JSON 文件中的数据
    read_data = read_p4login_info(filename)
    for info in read_data:
        print(info)

    # 获取某个 clientType 的指定键值
    email = get_p4login_info_value("project", "customGroups")
    print(f"Email for 'plug': {email}")
    
    # 获取一个不存在的键
    # invalid_key = get_p4login_info_value("plug", "NonExistentKey")  # 这行将会导致静态检查报错
    # print(f"Non-existent key result: {invalid_key}")
