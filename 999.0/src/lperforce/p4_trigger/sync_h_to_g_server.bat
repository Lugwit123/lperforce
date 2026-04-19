chcp 65001

set "PATH=%PATH%;D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\python_env"
set "LugwitToolDir=D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp"
set "isTriggerEnv=1"

python D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp\Lib\LPerforce\p4_trigger\sync_h_to_g_start_sync_process.py  "%1" "%2" "%3" "%4" "%5" /H /G



