# coding:utf-8
import os,sys
import json
import codecs
import warnings
import Lugwit_Module as LM



if hasattr(LM, 'userConfigFile'):
    configFile = os.path.expandvars(LM.userConfigFile)
else:
    warnings.warn("Lugwit_Module.userConfigFile 属性不存在，使用默认降级路径")
    configFile = os.path.join(os.path.expandvars("%USERPROFILE%"), r'.Lugwit\config\config.json')


def read_config(file_path):
    """
    读取并解析JSON配置文件内容。

    参数:
    file_path (str): JSON文件的路径。

    Returns:
        dict: 返回一个字典。
    """
    try:
        # 使用codecs模块打开文件
        with codecs.open(file_path, 'r', 'utf-8') as f:
            data = json.load(f)
        
        # 返回解析后的数据
        return data

    except FileNotFoundError:
        print("文件未找到，请检查路径: ", file_path)
    except json.JSONDecodeError as e:
        print("文件解析失败: ", e)
    except Exception as e:
        print("发生错误: ", e)


p4_loginInfo = read_config(configFile) or {}

if __name__=="__main__":
    print(p4_loginInfo)



