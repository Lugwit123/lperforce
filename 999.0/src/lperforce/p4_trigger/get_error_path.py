import os,sys,re

def extract_error_file_paths(error_messages):
    """
    从错误消息列表中提取所有出错的文件路径。
    
    :param error_messages: 错误消息列表
    :return: 出错的文件路径列表
    """
    file_paths = set()

    # 合并正则表达式匹配模式
    patterns = ['(\w:\\\\.*?):* ', '\'(\w:\\\\.*?)\'','(\w:\\\\.*?):']
    for pattern in patterns:
        matches = re.findall(pattern, error_messages, re.DOTALL)
        for match in matches:
            normalized_path = os.path.normpath(match)
            if os.path.isfile(normalized_path):
                file_paths.add(normalized_path)
    
    return file_paths