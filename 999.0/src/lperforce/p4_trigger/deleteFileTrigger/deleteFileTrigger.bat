chcp 65001
echo off
cd /d D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\python_env
python %LugwitLibDir%\LPerforce\p4_trigger\deleteFileTrigger\main.py  "%1" "%2" "%3" "%4" "%5"
