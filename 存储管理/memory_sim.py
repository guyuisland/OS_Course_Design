import numpy as np
import threading
from multiprocessing import Process, Queue, Pool, Manager, Pipe
import multiprocessing as mp
import time
import datetime

class PCB:
    file_list = []  # 打开文件列表
    io = []  # IO使用情况(列表)
    # cpureg = CPUREG()

    def __init__(self):
        self.pid = None  # pid
        self.state = None  # ready, running, waiting, terminated
        self.address_code = None  # 代码段首地址
        self.process_memory_space = None  # 进程活动空间的大小
        self.code_space = None  # 代码段长度
        self.priority = None  # 进程优先级
        self.pc = None  # 存放PC的值，根据PC取指令,是一个列表，pc[0]是当前指针地址，pc[1]为前一条指令运行了多久

class Disk():
    fileBlock = ["" for i in range(100)]
    occupyBlock = np.array([0] * 100)  # 0代表不读不写，1代表读，2代表写

    def __init__(self):
        pass

MAX_PHYSICAL_MEMORY_NUMBER = 512  # 物理内存最大数量

MAX_FILE_BLOCK_NUMBER = 100
MAX_PROCESSES_NUMBER = 10
PROCESS_ACTIVITY_AREA = 64

pidBitmap = [0,0,0,0,0,0,0,0,0,0]  # 当前进程pid
# tempPCB = PCB()
# tempPCB.address_code = 0
# tempPCB.pid = 100
# tempPCB.state = "start"
# tempPCB.process_memory_space = 3
# tempPCB.code_space = 10
PCBTable = {} # 存放PCB，key是pid，value是PCB
Instruction = ["" for i in range(MAX_PHYSICAL_MEMORY_NUMBER)]  # 存放指令
MemoryBitmap = np.array([False]*MAX_PHYSICAL_MEMORY_NUMBER)  # 判断该内存块是否为空
fileMemory = ["" for i in range(32)]
actiAreaRemain = 64
currProcessNum = 0
waitFileList = []  # 等待读写的文件队列
runFileList = []  # 正在读写的文件队列

lock = threading.Lock()

    
def InitDisk():
    i = 0
    file = open("H://Users/Myth/source/repos/OS_Course_Design/存储管理/Disk.txt") 
    for line in file.readlines():  
        line=line.strip('\n')
        if i < 100:
            Disk.fileBlock[i] = line
        i += 1
    file.close()
InitDisk()

def write_back_disk():
    f = open('H://Users/Myth/source/repos/OS_Course_Design/存储管理/Disk.txt','w')
    for i in range(len(Disk.fileBlock)-1):
        f.write(Disk.fileBlock[i] + '\n')
    f.write(Disk.fileBlock[99])
    f.close()


def create_pcb(firstAddress):  # 返回一个列表，0表示是否成功，1表示pid 
    global actiAreaRemain
    #print(firstAddress)
    if actiAreaRemain < int(Instruction[firstAddress][1:4]):  # 进程活动空间不足，返回FAIL
        return ["FAIL",-1,-1,-1]
    else:
        newPCB = PCB()
        pid_ = -1
        for index in range(10):
            if pidBitmap[index] == 0:
                pidBitmap[index] = 1
                pid_ = index + 1
                break
        if pid_ == -1:
            ["FAIL",-1,-1,-1]
        newPCB.pid = pid_
        newPCB.state = "start"
        newPCB.address_code = firstAddress
        newPCB.process_memory_space = int(Instruction[firstAddress][1:4])
        res = get_code_length(firstAddress)  # res[0]是代码长度，res[1]是burstTime
        newPCB.code_space = res[0]
        newPCB.priority = int(Instruction[firstAddress + 1][1:4])
        newPCB.pc = [firstAddress + 2, 0]  # 初始化进程的PC
        PCBTable[newPCB.pid] = newPCB
        actiAreaRemain -= int(Instruction[firstAddress][1:4])
        return ["SUCCESS", newPCB.pid, newPCB.priority, res[1]]


def read_flie(blockList):
    fileMemoryIndex = 0
    for block in blockList:
        if Disk.occupyBlock[block] == 2:  # 文件块正在被写
            return "fail"
    for i in range(len(blockList)):
        fileMemory[fileMemory] = Disk.fileBlock[blockList[i]]
        Disk.occupyBlock[blockList[i]] = 1  # 把occupyBlock置为1，表示当前块正在被读

    return "succeed"


def write_file(blockContentDict):
    for blockNumber in list(blockContentDict.keys()):
        if Disk.occupyBlock[blockNumber] == 0:  # 没被读也没被写，则可以
            Disk.fileBlock[blockNumber] = blockContentDict[blockNumber]  # 把内容写入到块当中，瞬间写完，不用
        else:
            return "fail"
    return "succeed"

    
def allocate_memory_to_process(blockList):
    global currProcessNum
    global actiAreaRemain
    if currProcessNum >= 10:
        return ["FAIL", -1]
    instNum = (len(blockList) - 1) * 8 + len(Disk.fileBlock[blockList[-1]]) / 8
    startAddr = get_free_block(instNum)
    if startAddr == -1:
        return ["FAIL", -1]

    # 把这些内存块设为已被占用，不可使用
    for i in range(startAddr, int(startAddr + instNum)):
        MemoryBitmap[i] = 1

    addrIndex = startAddr
    for block in blockList[:-1]:  # 最后一个块可能不满8条指令，先对前面的块处理完
        for i in range(8):  # 每个块有8条指令
            Instruction[addrIndex] = Disk.fileBlock[block][i * 8: (i + 1) * 8]
            addrIndex += 1
    blockStr = Disk.fileBlock[blockList[-1]]  # 处理最后一个块
    for i in range(0, len(blockStr) // 8):
        Instruction[addrIndex] = blockStr[i * 8:(i + 1) * 8]
        addrIndex += 1
    currProcessNum += 1
    if actiAreaRemain <= int(Instruction[startAddr][1:4]):
        return ["FAIL", -1]
    return ["SUCCESS", startAddr]


def get_free_block(requestNum):
    startAddr = 0
    freeLength = 0
    for i in range(MAX_PHYSICAL_MEMORY_NUMBER):
        if MemoryBitmap[i] == 0:  # 当前块空闲
            freeLength += 1
            if freeLength == requestNum:  # 需要的内存空间长度足够
                return startAddr

        else:  # 当前块不空闲
            startAddr = i + 1
            freeLength = 0
    return -1

        


def modify_pcb(pid_, d_state):  # 改变进程的状态，返回成功或者失败
    if pid_ in list(PCBTable.keys()):
        PCBTable[pid_].state = d_state
        return "SUCCESS"
    else:
        return "FAIL"


def delete_process(pid_):
    global actiAreaRemain
    try:
        addr = PCBTable[pid_].address_code
        length = PCBTable[pid_].code_space
        for i in range(addr, addr + length):
            Instruction[i] = ""
            MemoryBitmap[i] = 0
        actiAreaRemain += PCBTable[pid_].process_memory_space
        del PCBTable[pid_]
        return "SUCCESS"
    except:
        return "FAIL"


def get_code_length(firstAddress_):  # 根据输入的代码首地址，返回代码段的长度
    addr = firstAddress_
    burstTime = 0
    while (Instruction[addr][0] != "Q"):
        if Instruction[addr][0] == "C":
            burstTime += int(Instruction[addr][1:4])
        addr += 1
    return [addr - firstAddress_ + 1, burstTime]


def deal_message(message):
    resMess = []
    if message[0] == "REQ":  # 消息为请求 
        if message[3] == "CREATE_PROCESS_MEMORY":  # 请求创建分配PCB
            # message:[RES][MEMORY][PROCESS][CREATE_PROCESS][SUCCESS/FAIL][pid][priority][burstTime][uipid]
            resMess.append("RES")  # 返回为应答
            resMess.append("MEMORY")
            resMess.append("PROCESS")
            resMess.append("CREATE_PROCESS")
            res = create_pcb(message[4])
            resMess.append(res[0])  # 成功或者失败
            resMess.append(res[1])  # pid的值
            resMess.append(res[2])  # 优先级
            resMess.append(res[3]) 
            resMess.append(message[5])  # uipid
        
        if message[3] == "MODIFY_STATE":  # 请求修改PCB
            # message:[RES][MEMORY][KERNEL][MOVE_QUEUE][pid][SUCCESS/FAIL]
            resMess.append("RES")  # 返回为应答
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("MODIFY_STATE")
            resMess.append(message[4])  # pid
            resMess.append(modify_pcb(message[4], message[6]))  # 成功还是失败
        
        if message[3] == "RELEASE_RESOURCES":  # 请求把进程终止掉
            # message:[RES][MEMORY][KERNEL][TERMINATE_PROCESS][pid][SUCCESS/FAIL]
            resMess.append("RES")  # 返回为应答
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("RELEASE_RESOURCES")
            resMess.append(message[4])  # pid
            resMess.append(delete_process(message[4]))  # SUCCESS/FAIL
        
        if message[3] == "LOAD":
            # 输入的message:[REQ][FILESYSTEM][MEMORY][LOAD][type][fileName][uipid][pid][readTime][block_list]
            #                 0        1        2      3     4       5        6     7      8         9
            # 输出的message:[RES][MEMORY][KERNEL][LOAD][type_str][load_res][startAddr][uipid][pid]
            # 如果是代码文件，则返回是否成功和起始地址，如果是普通文件则返回读是否成功
            resMess.append("RES")
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("LOAD")
            if message[4] == "EXEC":  # 是代码指令文件
                resMess.append("EXEC")
                if len(message[9]) == 0:  # 错误文件
                    resMess.append("FAIL")
                    resMess.append(-1)
                    resMess.append(message[6])
                    resMess.append(message[7])
                else:
                    res = allocate_memory_to_process(message[9])
                    resMess.append(res[0])  # 返回SUCCESS/FAIL
                    resMess.append(res[1])  # 返回代码段的首地址
                    resMess.append(message[6])
                    resMess.append(message[7])
            elif message[4] == "COMMON":  # 如果是普通文件
                # resMess.append("COMMON")
                # res = read_flie(message[5])
                # resMess.append(res)
                # resMess.append(-1)
                if len(message[9]) == 0:  # 错误文件
                    resMess.append("COMMON")
                    resMess.append("FAIL")
                    resMess.append(-1)
                    resMess.append(message[6])
                    resMess.append(message[7])
                else:
                    lock.acquire()
                    waitFileList.append(message)
                    lock.release()
                    return 
        
        if message[3] == "WRITE":  # 需要写文件
            if message[5] == -2:  # UI直接进行写
                if len(list(message[8].keys())) == 0:  # 文件错误
                    resMess.append("RES")
                    resMess.append("MEMORY")
                    resMess.append("UI")
                    resMess.append("WRITE")
                    resMess.append(message[4])
                    resMess.append("FAIL")
                else:
                    for BlockNumber in list(message[8].keys()):
                        Disk.fileBlock[BlockNumber] = message[8][BlockNumber]
                    resMess.append("RES")
                    resMess.append("MEMORY")
                    resMess.append("UI")
                    resMess.append("WRITE")
                    resMess.append(message[4])
                    resMess.append("SUCCESS")
            else:
                if len(list(message[8].keys())) == 0:  # 文件错误
                    resMess.append("RES")
                    resMess.append("MEMORY")
                    resMess.append("KERNEL")
                    resMess.append("WRITE")
                    resMess.append("FAIL")
                    resMess.append(message[4])  # filename
                    resMess.append(message[5])  # pid
                else:
                    lock.acquire()
                    waitFileList.append(message)
                    lock.release()
                    return 

        if message[3] == "STORE_RUNTIME":  # 进程的时间片到了，指令没有执行完，则需要对指令执行到的时间进行记录
            PCBTable[message[4]].pc[1] = message[5]
            resMess.append("RES")
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("STORE_RUNTIME")
            resMess.append(message[4])  # pid
            resMess.append("SUCCESS")

        
        if message[3] == "INSTRUCTION_FETCH":  # kernel根据pid去取指令
            resMess.append("RES")
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("INSTRUCTION_FETCH")
            pid_ = message[4]
            resMess.append(pid_)  # pid
            if PCBTable[pid_].pc[1] == 0:  # 指令未被执行过
                resMess.append(Instruction[PCBTable[pid_].pc[0]])
                resMess.append(0)
                PCBTable[pid_].pc[0] += 1
                PCBTable[pid_].pc[1] = 0
            elif PCBTable[pid_].pc[1] > 0:
                resMess.append(Instruction[PCBTable[pid_].pc[0] - 1])  # 取上一条指令
                resMess.append(PCBTable[pid_].pc[1])  # 指令运行的时间
                PCBTable[pid_].pc[1] = 0
            elif PCBTable[pid_].pc[1] < 0:
                resMess.append(Instruction[PCBTable[pid_].pc[0] - 1])  # 取上一条指令
                resMess.append(0)  # 指令运行的时间
                PCBTable[pid_].pc[1] = 0
            else:
                print('取指错误')

        if message[3] == "SHUTDOWN":
            resMess.append("RES")
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("SHUTDOWN")
            resMess.append("SUCCESS")
            write_back_disk()
    else:
        pass
    
    return resMess

def send_memory_state_to_UI():
    global PCBTable
    resMess = []
    resMess.append("RES")
    resMess.append("MEMORY")
    resMess.append("UI")
    resMess.append("MEMORY_SNAPSHOT")
    memoryDict = {}
    # print('send_memory_state_to_UI',PCBTable)
    for PCBIndex in PCBTable.keys():
        memoryDict[PCBIndex] = [PCBTable[PCBIndex].address_code, PCBTable[PCBIndex].code_space + PCBTable[PCBIndex].address_code]
    resMess.append(memoryDict)
    # message:[RES][MEMORY][UI][MEMORY_SNAPSHOT][memoryDict]
    #print(resMess)
    return resMess


def every_time_deal(Memory2Kernel, MemoryTime):
    # 输入的读message:[REQ][FILESYSTEM][MEMORY][LOAD][type][fileName][uipid][pid][readTime][block_list]
    #                  0         1        2      3     4       5        6     7      8         9
    # 输入的写message:[REQ][FILESYSTEM][MEMORY][WRITE][fileName][pid][writeTime][writeType][blockContentDict]
    while 1:
        #print(MemoryTime.empty())
        MemoryTime.get()  # 每次收到时间片执行下面的指令
        runIndex = 0
        while runIndex < (len(runFileList)):  # 处理正在读和写的文件队列
            #print('index',runIndex)
            runMess = runFileList[runIndex]
            if runMess[3] == "LOAD":  # 读文件的消息
                #print(runMess[8])
                runMess[8] -= 1  # 读文件的时间减1
                if runMess[8] == 0:  # 该文件读完成了，返回完成的message，并将这个message移除，修改文件块状态
                    # [RES][MEMORY][KERNEL][LOAD][type_str][load_res][startAddr][uipid][pid]
                    Memory2Kernel.put(["RES", "MEMORY", "KERNEL", "LOAD", "COMMON","SUCCESS",-1,-1,runMess[6]])
                    #print(["RES","MEMORY","KERNEL","LOAD","COMMON","SUCCESS",-1,-1,runMess[7]])
                    read_done(runMess[9])  # 读资源释放
                    runFileList.remove(runMess)  # 移出列表
                    runIndex -= 1
            elif runMess[3] == "WRITE":
                runMess[6] -= 1  # 写文件的时间减1
                if runMess[6] == 0:  # 该文件写完成了，返回完成的message，并将这个message移除，修改文件块状态
                    #输入：[REQ][FILESYSTEM][MEMORY][WRITE][fileName][pid][writeTime][blockContentDict]
                    #[RES][MEMORY][KERNEL][WRITE][writeRes][fileName][pid]
                    Memory2Kernel.put(["RES","MEMORY","KERNEL","WRITE","SUCCESS",runMess[4],runMess[5]])
                    #print(["RES","MEMORY","KERNEL","WRITE","SUCCESS",runMess[4],runMess[5]])
                    write_done(runMess[8].keys())
                    runFileList.remove(runMess)  # 移出列表
                    runIndex -= 1
            runIndex += 1

        waitIndex = 0
        while waitIndex < len(waitFileList):  # 处理等待队列
            #print(Disk.occupyBlock)
            waitMess = waitFileList[waitIndex]
            if waitMess[3] == "LOAD":  # 处理读文件的操作
                occupyFlag = 0
                for index in waitMess[9]:
                    if Disk.occupyBlock[index] == 1:  # 文件块正在被写
                        occupyFlag = 1
                    elif Disk.occupyBlock[index] == 0:  # 文件块未被读也未被写
                        pass
                        # for blockNumber in waitMess[9]:
                        #     Disk.occupyBlock[blockNumber] = 2
                        # runFileList.append(waitMess)
                        # waitFileList.remove(waitMess)
                        # waitIndex -= 1
                    elif Disk.occupyBlock[index] >= 2:  # 文件正在被读，不会发生读读冲突
                        # for blockNumber in waitMess[9]:
                        #     Disk.occupyBlock[blockNumber] += 1
                        # runFileList.append(waitMess)
                        # waitFileList.remove(waitMess)
                        # waitIndex -= 1
                        pass
                    else:
                        print('readFile,wait to run error')
                if occupyFlag == 0:
                    if Disk.occupyBlock[waitMess[9][0]] >= 2:
                        for blockNumber in waitMess[9]:
                            Disk.occupyBlock[blockNumber] += 1
                    elif Disk.occupyBlock[waitMess[9][0]] == 0:
                        for blockNumber in waitMess[9]:
                            Disk.occupyBlock[blockNumber] = 2
                    else:
                        print('waitList load ERROR')
                    runFileList.append(waitMess)
                    waitFileList.remove(waitMess)
                    waitIndex -= 1

            if waitMess[3] == "WRITE":  # 处理写文件的操作
                blockList_ = list(waitMess[8].keys())
                #print('Disk.occupyBlock',Disk.occupyBlock)
                #print('Disk.occupyBlock',Disk.occupyBlock)
                occupyFlag = 0
                for index in blockList_:
                    if Disk.occupyBlock[index] == 0:  # 文件块未进行读写操作
                        pass
                    elif Disk.occupyBlock[index] == 1:  # 文件正在被写
                        occupyFlag = 1
                    elif Disk.occupyBlock[index] >= 2:  # 文件正在进行读
                        occupyFlag = 1
                #print('occupyFlag',occupyFlag)
                if occupyFlag == 0:  # 可以进行写
                    blockContentDict = waitMess[8]
                    for blockNumber in blockList_:
                        Disk.occupyBlock[blockNumber] = 1  # 将文件块置为写状态
                        if waitMess[7] == "cover":
                            Disk.fileBlock[blockNumber] = blockContentDict[blockNumber]
                        elif waitMess[7] == "add":
                            Disk.fileBlock[blockNumber] += blockContentDict[blockNumber]
                        else:
                            print('block cover or add ERROR')
                    runFileList.append(waitMess)
                    waitFileList.remove(waitMess)
                    waitIndex -= 1

            waitIndex += 1
        
        if len(runFileList) == 0:  # 磁盘空闲
            Memory2Kernel.put(['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'WAIT'])
            print(['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'WAIT'])
        else:
            Memory2Kernel.put(['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'RUN'])
            print(['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'RUN'])
        uiMess = send_memory_state_to_UI()
        print(uiMess)
        print('runFileList',runFileList)
        print('waitFileList',waitFileList)
        print('***************************************************')
        Memory2Kernel.put(uiMess)


def read_done(blockList_):       
    for blockNumber in blockList_:
        if Disk.occupyBlock[blockNumber] == 2:  # 只有一个进程在读
            Disk.occupyBlock[blockNumber] = 0
        else:
            Disk.occupyBlock[blockNumber] -= 1  # 读blockNumber块的教程减1
            

def write_done(blockList_):  # 把所有写文件块置为0
    for blockNumber in blockList_:
        if Disk.occupyBlock[blockNumber] != 1:
            print('write_done ERROR!')
        Disk.occupyBlock[blockNumber] = 0

def start_memory(Kernel2Memory, Memory2Kernel, MemoryTime):
    t1 = threading.Thread(target=every_time_deal, args=(Memory2Kernel,MemoryTime))
    t1.start()
    while (1):
        while Kernel2Memory.qsize() != 0:
            message = Kernel2Memory.get()
            ret_message = deal_message(message)
            print(ret_message)
            if ret_message != None:
                Memory2Kernel.put(ret_message)

    
