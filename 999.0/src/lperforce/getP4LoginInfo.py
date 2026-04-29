# coding:utf-8
import os,sys
import configparser

LugwitToolDir=os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir+'/Lib') 
import Lugwit_Module as LM


configFile =os.path.expandvars(LM.userConfigFile)
config = configparser.ConfigParser()
config.read(configFile,encoding='utf8')

# 将 config 对象转换为字典
p4_loginInfo = {section: dict(config.items(section)) for section in config.sections()}

