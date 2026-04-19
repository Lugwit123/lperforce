import loginP4,time,traceback,codecs,datetime,os,sys,json
import unlockFile,re

p4=loginP4.p4_login(
    port=r'192.168.110.26:1666',
    userName='Administrator',
    wsDir=r'f:\共享盘\H'
)
p4.exception_level = 1
# 例如：年-月-日 时:分:秒
date_time_format = "%Y_%m_%d"

os.chdir(r'F:\共享盘\H')
print ('p4.client',p4.client)

def extract_error_file_paths(error_messages):
    """
    从错误消息列表中提取所有出错的文件路径。
    
    :param error_messages: 错误消息列表
    :return: 出错的文件路径列表
    """
    file_paths = []

    matches = re.findall(r'failed to rename (\w:.+?) after', error_messages)
    for match in matches:
        match=match.replace('\\\\','\\')
        file_paths.append(match)
    
    return file_paths
    return file_paths

while True:
    now = datetime.datetime.now()
    # 格式化当前日期和时间
    formatted_date_time = now.strftime(date_time_format)
    syncErrorFile=fr'A:\temp\Log\SyncProject\{formatted_date_time}_sync_error.log'
    syncFile=fr'A:\temp\Log\SyncProject\{formatted_date_time}_sync.log'
    print(f'开始同步{now.strftime("%Y_%m_%d_%H:%M:%S")}')
    try:
        # print ('正在同步')
        # p4.run('set', f'net.maxwait={1}')
        # command = ['-r{}'.format(1), 'sync'] + ' F:\\共享盘\\H\\SNXYJ2\\Anima final\\Lyout\\EP025\\mov\\...'
        # # files=p4.run_sync('--parallel=threads=4,batch=10','-r3','F:\\共享盘\\H\\SNXYJ2\\Anima final\\Lyout\\EP025\\mov\\...')
        # p4.run('configure', 'set', 'variable','-r','1')
        command = ['sync', 'F:\\共享盘\\H\\...']
        
        # 执行同步命令
        files = p4.run(*command)  # 使用 * 解包参数列表
        # files=p4.run(command)
        for file_info in files:
            local_path = file_info.get('clientFile')
            if local_path and local_path.endswith('.holder'):
                try:
                    os.remove(local_path)
                    print(f'Deleted: {local_path}')
                except OSError as e:
                    print(f'Error deleting file {local_path}: {e}')
        print (f'同步完成{len(files)}个文件')
        with codecs.open(syncFile,'a+',encoding='utf8') as f:
            json.dump(files,f,ensure_ascii=False,indent=4)

    except:
        error=traceback.format_exc()
        if 'up-to-date' in error:
            print (u'没有要更新的文件')
        elif '系统找不到指定' in error:
            print (f'系统找不到指定错误:\n{error}')
            file_paths = extract_error_file_paths(error)
            print  (f'出错的文件{file_paths}')
            for file_path in file_paths:
                print (f'解锁文件{file_path}')
                unlockFile.unlock_file(file_path)
            with codecs.open(syncErrorFile,'a+',encoding='utf8') as f:
                f.write(error)
        else:
            print (error)
            with codecs.open(syncErrorFile,'a+',encoding='utf8') as f:
                f.write(error)
    time.sleep(60)
    try:
        print ('检查工作区比服务器新的版本，并同步')
        concileList=p4.run_reconcile('-mn',r'F:\共享盘\H\CCC\...')
        for concile in concileList:
            if not isinstance(concile,dict):
                continue
            action=concile.get('action')
            if action=='edit':
                depotFile=concile['depotFile']
                p4.run_sync('-f',depotFile)
                print ('强制同步,工作区比服务器新',depotFile)
                with codecs.open(syncFile,'a+',encoding='utf8') as f:
                    json.dump(concile,f,ensure_ascii=False,indent=4)
    except:
        error=traceback.format_exc()
        if 'up-to-date' in error:
            print (u'没有要更新的文件')
        else:
            print (error)
            with codecs.open(syncErrorFile,'a+',encoding='utf8') as f:
                f.write(error)
    print ('\n')
    time.sleep(60)