import os,sys
sys.path.append(r'D:\TD_Depot\plug_in\Python\py39Lib')
import fire


Lugwit_publicPath=os.environ.get('Lugwit_publicPath')
LugwitToolDir=os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir+'/Lib') 
import Lugwit_Module as LM
from lperforce import (loginP4,p4_baselib,P4Lib)
from lperforce.P4LoginInfoModule import p4_loginInfo

p4 = loginP4.p4_login(userName=p4_loginInfo['project']['User'],
                      port=p4_loginInfo['project']['port'],
                      clientName=p4_loginInfo['project']['clientName'])

P4Lib.p4 = p4
p4.run_edit('//H/DPCQ/6.FX/...')
p4_baselib.revert(p4,changeNum='default',showProcess=True,) 

