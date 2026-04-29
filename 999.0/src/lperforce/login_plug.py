import loginP4


p4=loginP4.p4_login(port='192.168.110.61:1666')
print (p4)

concileList=p4.run_reconcile('-m','-n',r'//TD_Depot/AA/...')
print ('concileList',concileList,'\n')
# if isinstance(concileList[0],list):
#     concileList={concileList[0]}
print ('concileList',concileList,'\n')
for concile in concileList:
    print ('concile',concile)
    if not isinstance(concile,dict):
        continue
    action=concile.get('action')
    if action=='edit':
        depotFile=concile['depotFile']
        p4.run_sync('-f',depotFile)
        print ('强制同步,工作区比服务器新',depotFile)