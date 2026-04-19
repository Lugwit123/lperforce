chcp 65001

set "PATH=%PATH%;D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\python_env"
set "LugwitToolDir=D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp"
set "isTriggerEnv=1"
lugwit_python.exe D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp\Lib\LPerforce\p4_trigger\autoExFbx\autoExFile.py "%1" "%2" "%3" "%4" "%5"