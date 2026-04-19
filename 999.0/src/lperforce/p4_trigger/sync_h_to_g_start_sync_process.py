import subprocess,sys
print(__file__,sys.argv)
subprocess.Popen(['python',r"D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp\Lib\LPerforce\p4_trigger\sync_h_to_g_server_cmd.py"]+sys.argv[1:], creationflags=subprocess.CREATE_NEW_CONSOLE)
# print(111)
