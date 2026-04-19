import fire
import os,sys

os.environ['LugwitToolDir'] = r"D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp"
LugwitToolDir = os.getenv('LugwitToolDir')
sys.path.append(LugwitToolDir+'/Lib')

from Lugwit_Module import *
from Lugwit_Module.l_src import l_parse_args
sys.argv[1]=eval(f"fr\"{sys.argv[1]}\"")
print ('原始输入变量',' '.join([sys.executable,*sys.argv]))
sys.argv = sys.argv[1:]
print (sys.argv)
os.environ['QT_API'] = 'PyQt6'

if __name__ == '__main__':
    exec_func = sys.argv[1]
    print ('sys.argv[0]',sys.argv[0])
    while "\"" in sys.argv:
        sys.argv.remove("\"")
    mod=dynamic_import(sys.argv[0])
    exec_func=getattr(mod, exec_func)
    lprint (mod)
    parsed_args = l_parse_args.parse_args(sys.argv[2:])
    print ('parsed_args',parsed_args)
    os.environ['Lugwit_Debug']=str(parsed_args.get('Lugwit_Debug'))
    lprint("解析后的参数字典:", parsed_args)
    exec_func(**parsed_args)




