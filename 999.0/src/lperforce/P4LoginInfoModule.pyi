from dataclasses import dataclass, field
from typing import List, Dict, Literal

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
    userGroups: List[GroupInfo]  # 组名称和描述
    clientName: str
    clientType: Literal["plug", "project"]
    port: Literal["192.168.110.61:1666", "192.168.110.26:1666"]
    customGroups: List[str] = field(default_factory=list)
    passwordChange: str = ""
    clientRoot: str = ""
    
LoginInfoDict = Dict[Literal["project", "plug"], P4LoginInfo]
p4_loginInfo : LoginInfoDict 