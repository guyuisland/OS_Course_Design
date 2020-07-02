from multiprocessing import Process, Queue, Pool, Manager, Pipe
import multiprocessing as mp
import time
import threading
import datetime
import memory_sim

nowSecond = 100

def count_time(Memory2Kernel,MemoryTime):
    while 1:
        MemoryTime.get()
        Memory2Kernel.put(nowSecond)
    

def deal(Kernel2Memory, Memory2Kernel, MemoryTime):
    t1 = threading.Thread(target=count_time, args=(Memory2Kernel,MemoryTime,))
    t1.start()
    while (1):
        #MemoryTime.get()
        while Kernel2Memory.qsize() != 0:
            message = Kernel2Memory.get()
            ret_message = ['RES','MEMORY']
            Memory2Kernel.put(ret_message)

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


    testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','EXEC','a',2,-1,-1,[0,3]])
    testMessage.append(["REQ",'PROCESS','MEMORY','CREATE_PROCESS_MEMORY',10,2])
    testMessage.append(["REQ",'KERNEL','MEMORY','MODIFY_STATE',1,"ready","running"])
    #testMessage.append(["REQ",'KERNEL','MEMORY','RELEASE_RESOURCES',1])
    testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    testMessage.append(["REQ",'KERNEL','MEMORY','STORE_RUNTIME',1,3])
    testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    testMessage.append(["REQ",'KERNEL','MEMORY','INSTRUCTION_FETCH',1])
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','WRITE','B',5,3,'add',{}])
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMOM','a',-1,3,4,[]])

    # 测试读COMMOM文件和写文件(指令)
    # 读：[REQ][FILESYSTEM][MEMORY][LOAD][type][fileName][uipid][pid][readTime][block_list]
    # 写：[REQ][FILESYSTEM][MEMORY][WRITE][fileName][pid][writeTime][blockContentDict]
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMOM','a',-1,1,5,[0,3]])
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMOM','B',-1,2,3,[4,6]])
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','LOAD','COMMOM','a',-1,3,4,[0,3]])
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','WRITE','a',4,2,'cover',{0:"abcd",3:"oooo"}])
    testMessage.append(["REQ",'FILESYSTEM','MEMORY','WRITE','B',5,3,'add',{4:"abcd",6:"oooo"}])
    
    while 1:
        now = datetime.datetime.now()
        if i < len(testMessage):
            Kernel2Memory.put(testMessage[i])   
            ret = Memory2Kernel.get()
            print(ret)
        
        if now.second % 1 == 0 and preSecond != now.second:
            #print('MemoryTime.put')
            #MemoryTime.put(1)
            #print(waitFileList)
            pass
        MemoryTime.put(1)
        preSecond = now.second
        i += 1
        time.sleep(0.2)
        