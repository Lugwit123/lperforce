chcp 65001

set "PATH=%PATH%;D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\python_env"
set "LugwitToolDir=D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp"
set "isTriggerEnv=1"
echo clean_ma_file
lugwit_python.exe D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp\Lib\LPerforce\p4_trigger\clean_ma_file\main.py "%1" "%2" "%3" "%4" "%5"