class DotDict(dict):
    """
    A dictionary that supports dot notation for getting and setting items.
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{key}'")

class RunFstat(DotDict):
    """
    A specialized dictionary with default elements for RunFstat.
    """
    def __init__(self, initial_dict=None):
        super().__init__()
        # 默认属性
        self.clientFile = ''
        self.depotFile = ''
        self.headAction = ''
        self.headChange = ''
        self.headModTime = ''
        self.haveRev = ''
        self.headRev = ''
        self.headTime = ''
        self.headType = ''
        self.isMapped = ''
        self.fileSize = ''
        
        # 如果提供了初始字典，则更新属性
        if initial_dict:
            for key, value in initial_dict.items():
                setattr(self, key, value)

# 示例使用
initial_data = {
    'clientFile': 'example.txt',
    'depotFile': '//depot/example.txt'
}

data = RunFstat(initial_data)

# 获取元素
print(data.clientFile)  # 输出: example.txt
print(data.depotFile)   # 输出: //depot/example.txt

# 获取不存在的元素
print(data.nonExistentAttribute)  # 输出: AttributeError

# 设置元素
data.headAction = 'edit'
print(data.headAction)  # 输出: edit
