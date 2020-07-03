from multiprocessing import Process, Queue, Pool, Manager, Pipe
import multiprocessing as mp
import time
import threading
import datetime
import memory_sim


if __name__ == "__main__":
    Kernel2Memory = Queue()
    preSecond = 0
    Memory2Kernel = Queue()
    MemoryTime = Queue()
    p = Process(target=memory_sim.start_memory,
                        args=(Kernel2Memory, Memory2Kernel, MemoryTime,))
    p.start()

    
    i = 0
    testMessage = []
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','EXEC','a',1,-1,-1,[0,3]])
    testMessage.append(["REQ",'PROCESS','MEMORY','CREATE_PROCESS_MEMORY',0,1])
    pass
    # testMessage.append(['REQ', 'FILESYSTEM', 'MEMORY', 'WRITE', 'new_file_a', 5, 3, '', {}])
    #testMessage.append(['REQ', 'FILESYSTEM', 'MEMORY', 'WRITE', 'new_file_exec', 5, 3, 'cover', {0: 'M10     Y3      C1      C2      C3      C4      C5      C6      ', 1: 'M10     Y3      C1      C2      C3      C4      C5      C6      ', 2: 'M10     Y3      C1      C2      C3      C4      C5      C6      ', 3: 'M10     Y3      C1      C2      C3      C4      C5      C6      ', 4: 'M10     Y3      C1      C2      C3      C4      C5      C6      ', 5: 'Q       '}])
    testMessage.append(['REQ', 'FILESYSTEM', 'MEMORY', 'WRITE', 'new_file', 5, 3, 'cover', {0: 'A read-write conflict example. A read-write conflict example. A ', 1: 'read-write conflict example. A read-write conflict example. A re', 2: 'ad-write conflict example. A read-write conflict example. A read', 3: '-write conflict example. A read-write conflict example. A read-w', 4: 'rite conflict example. A read-write conflict example. '}])
    testMessage.append(['REQ', 'FILESYSTEM', 'MEMORY', 'LOAD', 'COMMON', 'new_file', -1, 7, 5, [0, 1, 2, 3, 4]])
    testMessage.append(['REQ', 'FILESYSTEM', 'MEMORY', 'WRITE', 'new_file', 6, 4, 'add', {4: 'A read-wri', 5: 'te conflict example. A read-write conflict example. A read-write', 6: ' conflict example. A read-write conflict example. A read-write c', 7: 'onflict example. A read-write conflict example. A read-write con', 8: 'flict example. A read-write conflict example. A read-write confl', 9: 'ict example. A read-write conflict example. '}])
    #testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','EXEC','a',2,-1,-1,[0,3]])
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','EXEC','a',2,-1,-1,[0,3]])
    #testMessage.append(["REQ",'PROCESS','MEMORY','CREATE_PROCESS_MEMORY',0,1])
    # testMessage.append(["REQ",'KERNEL','MEMORY','MODIFY_STATE',1,"ready","running"])
    # #testMessage.append(["REQ",'KERNEL','MEMORY','RELEASE_RESOURCES',1])
    # testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    # testMessage.append(["REQ",'KERNEL','MEMORY','STORE_RUNTIME',1,3])
    # testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    # testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    # testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','WRITE','B',5,3,'add',{}])
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMON','a',-1,3,4,[]])

    # 测试读COMMON文件和写文件(指令)
    # 读：[REQ][FILESYSTEM][MEMORY][LOAD][type][fileName][uipid][pid][readTime][block_list]
    # 写：[REQ][FILESYSTEM][MEMORY][WRITE][fileName][pid][writeTime][blockContentDict]
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMON','a',-1,1,5,[0,3]])
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMON','B',-1,2,3,[4,6]])
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMON','a',-1,3,4,[0,3]])
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','WRITE','a',4,2,'cover',{4:"abcd",6:"oooo"}])
    # testMessage.append(["REQ",'FILESYSTEM','MEMORY','WRITE','B',5,3,'add',{4:"abcd",6:"oooo"}])
    
    while 1:
        now = datetime.datetime.now()
        if i < len(testMessage):
            #print(testMessage[i])
            Kernel2Memory.put(testMessage[i])   
            if not Memory2Kernel.empty():
                ret = Memory2Kernel.get()
                #print('11111',ret)
        if now.second % 1 == 0 and preSecond != now.second:
            #print('MemoryTime.put')
            MemoryTime.put(1)
            #print(waitFileList)
            pass
        preSecond = now.second
        i += 1
        #time.sleep(0.5)
        