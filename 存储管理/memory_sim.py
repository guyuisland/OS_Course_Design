import numpy as np
import threading


MAX_PHYSICAL_MEMORY_NUMBER = 512  # 物理内存最大数量

MAX_FILE_BLOCK_NUMBER = 100
MAX_PROCESSES_NUMBER = 10
PROCESS_ACTIVITY_AREA = 64

pidBitmap = [0,0,0,0,0,0,0,0,0,0]  # 当前进程pid
PCBTable = {} # 存放PCB，key是pid，value是PCB
processPCTable = {}  # 存放PC
PageTable= {}  # 一个映射的页表
codeLengthTable = {}
Instruction = ["" for i in range(MAX_PHYSICAL_MEMORY_NUMBER)]  # 存放指令
MemoryBitmap = np.array([False]*MAX_PHYSICAL_MEMORY_NUMBER)  # 判断该内存块是否为空
fileMemory = ["" for i in range(32)]
actiAreaRemain = 64
currProcessNum = 0
waitFileList = []  # 等待读写的文件队列
runFileList = []  # 正在读写的文件队列

lock = threading.Lock()
class Disk():
    fileBlock = ["" for i in range(100)]
    occupyBlock = np.array([0]*100)  # 0代表不读不写，1代表读，2代表写
    def __init__(self):
        pass
    
#disk = Disk()
#print(Disk.fileBlock)

class PCB:
    file_list = []  # 打开文件列表
    io = []  # IO使用情况(列表)
    # cpureg = CPUREG()

    def __init__(self, pid_, state_, address_code_, process_memory_space_, code_space_, priority_,pc_):
        self.pid = pid_  # pid
        self.state = state_  # ready, running, waiting, terminated
        self.address_code = address_code_  # 代码段首地址
        self.process_memory_space = process_memory_space_  # 进程活动空间的大小
        self.code_space = code_space_  # 代码段长度
        self.priority = priority_  # 进程优先级
        self.pc = pc_  # 存放PC的值，根据PC取指令,是一个列表，pc[0]是当前指针地址，pc[1]为前一条指令运行了多久


def create_pcb(firstAddress):  # 返回一个列表，0表示是否成功，1表示pid 
    if actiAreaRemain < int(Instruction[firstAddress][2]):  # 进程活动空间不足，返回FAIL
        return ["FAIL",-1,-1]
    else:
        newPCB = PCB()
        pid_ = -1
        for index in range(10):
            if pidBitmap[index] == 0:
                pid_ = index + 1
        if pid_ == -1:
            ["FAIL",-1,-1]
        newPCB.pid = pid_
        newPCB.state = "ready"
        newPCB.address_code = firstAddress
        newPCB.process_memory_space = int(Instruction[firstAddress][2])
        newPCB.code_space = get_code_length(firstAddress)
        newPCB.priority = int(Instruction[firstAddress+1][2])
        newPCB.pc = [firstAddress + 2,0]  # 初始化进程的PC
        PCBTable[newPCB.pid] = newPCB
        actiAreaRemain -= int(Instruction[firstAddress][2])
        return ["SUCCESS",newPCB.pid,newPCB.priority]


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
    for blockNumber in blockContentDict.keys():
        if Disk.occupyBlock[blockNumber] == 0:  # 没被读也没被写，则可以
            Disk.fileBlock[blockNumber] = blockContentDict[blockNumber]  # 把内容写入到块当中，瞬间写完，不用
        else:
            return "fail"
    return "succeed"

    
def allocate_memory_to_process(blockList):
    if currProcessNum >= 10:
        return ["fail",-1]
    instNum = (len(blockList) - 1) * 8 + len(Disk.fileBlock[blockList[-1]])/8
    startAddr = get_free_block(instNum)
    if startAddr == -1:
        return ["fail",-1]

    # 把这些内存块设为已被占用，不可使用
    for i in range(startAddr,startAddr+instNum+1):
        MemoryBitmap[i] = 1

    addrIndex = startAddr
    for block in blockList[:-1]:  # 最后一个块可能不满8条指令，先对前面的块处理完
        for i in range(8):  # 每个块有8条指令
            Instruction[addrIndex] = Disk.fileBlock[block][i*8 : (i+1)*8]
            addrIndex += 1
    blockStr = Disk.fileBlock[blockList[-1]]  # 处理最后一个块
    for i in range(0,len(blockStr)//8):
        Instruction[addrIndex] = blockStr[i*8:(i+1)*8]
        addrIndex += 1
    currProcessNum += 1
    return ["succeed",startAddr]


def get_free_block(requestNum):
    startAddr = 0
    freeLength = 0
    for i in range(MAX_PHYSICAL_MEMORY_NUMBER):
        if MemoryBitmap[i] == 0:  # 当前块空闲
            freeLength += 1
            if freeLength == requestNum:  # 需要的内存空间长度足够
                return startAddr

        else:  #当前块不空闲
            startAddr = i + 1
            freeLength = 0
    return -1

        


def modify_pcb(pid_,d_state):  # 改变进程的状态，返回成功或者失败
    if pid_ in PCBTable.keys():
        PCBTable[pid_].state = d_state
        return "SUCCESS"
    else:
        return "FAIL"


def delete_process(pid_):
    try:
        addr = PCBTable[pid_].address_code
        length = PCBTable[pid_].code_space
        for i in range(addr, addr+length+1):
            Instruction[i] = ""
            MemoryBitmap[i] = 0
        actiAreaRemain += PCBTable[pid_].process_memory_space
        del PCBTable[pid_]
        return "SUCCESS"
    except:
        return "FAIL"


def get_code_length(firstAddress_):  # 根据输入的代码首地址，返回代码段的长度
    addr = firstAddress_
    while(Instruction[addr] != "Q"):
        addr += 1
    return addr - firstAddress_ + 1


def deal_message(message, PCB_queue):
    resMess = []
    if message[0] == "REQ": # 消息为请求 
        if message[3] == "CREATE_PROCESS_MEMORY":  # 请求创建分配PCB
            # message:[RES][MEMORY][PROCESS][CREATE_PROCESS][SUCCESS/FAIL][pid][priority][uipid]
            resMess.append("RES")  # 返回为应答
            resMess.append("MEMORY")
            resMess.append("PROCESS")
            resMess.append("CREATE_PROCESS")
            res = create_pcb(message[4])
            resMess.append(res[0])  # 成功或者失败
            resMess.append(res[1])  # pid的值
            resMess.append(res[2])  # 优先级
            resMess.append(message[5])  # uipid
        
        if message[3] == "MOVE_QUEUE":  # 请求修改PCB
            # message:[RES][MEMORY][KERNEL][MOVE_QUEUE][pid][SUCCESS/FAIL]
            resMess.append("RES")  # 返回为应答
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("MOVE_QUEUE")
            resMess.append(message[4])  #pid
            resMess.append(modify_pcb(message[4],message[6]))  # 成功还是失败
        
        if message[3] == "TERMINATE_PROCESS":  # 请求把进程终止掉
            # message:[RES][MEMORY][KERNEL][TERMINATE_PROCESS][pid][SUCCESS/FAIL]
            resMess.append("RES")  # 返回为应答
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("TERMINATE_PROCESS")
            resMess.append(message[4])  # pid
            resMess.append(delete_process(message[4]))  # SUCCESS/FAIL
        
        if message[3] == "LOAD":
            # 输入的message:[REQ][FILESYSTEM][MEMORY][type][fileName][uipid][pid][readTime][block_list]
            #                 0        1        2      3       4       5      6      7           8
            # 输出的message:[RES][MEMORY][KERNEL][LOAD][type_str][load_res][startAddr][uipid][pid]
            # 如果是代码文件，则返回是否成功和起始地址，如果是普通文件则返回读是否成功
            resMess.append("RES")
            resMess.append("MEMORY")
            resMess.append("KERNEL")
            resMess.append("LOAD")
            if message[4] == "EXEC":  # 是代码指令文件
                resMess.append("EXEC")
                res = allocate_memory_to_process(message[8])
                resMess.append(res[0])  # 返回SUCCESS/FAIL
                resMess.append(res[1])  # 返回代码段的首地址
                resMess.append(message[5])
                resMess.append(message[6])
            elif message[4] == "COMMOM":  # 如果是普通文件
                # resMess.append("COMMOM")
                # res = read_flie(message[5])
                # resMess.append(res)
                # resMess.append(-1)
                waitFileList.append(message)
        
        if message[3] == "WRITE":  # 需要写文件
            # 收到的message:[REQ][FILESYSTEM][MEMORY][WRITE][fileName][pid][writeTime][blockContentDict]
            # [RES][MEMORY][FILESYSTEM][LOAD][type_str][load_res][pid]
            # resMess.append("RES")
            # resMess.append("MEMORY")
            # resMess.append("KERNEL")
            # resMess.append("LOAD")
            # res = write_file(message[4])
            # resMess.append(res)
            waitFileList.append(message)

        if message[3] == "STORE_RUNTIME":  # 进程的时间片到了，指令没有执行完，则需要对指令执行到的时间进行记录
            PCBTable[message[4]].pc[1] = message[5]
        
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
                PCBTable[pid_].pc[0] = 0
            else:
                resMess.append(Instruction[PCBTable[pid_].pc[0] - 1])
                resMess.append(PCBTable[pid_].pc[1])

    else:
        pass
    
    return resMess

def send_memory_state_to_UI():
    resMess = []
    resMess.append("RES")
    resMess.append("MEMORY")
    resMess.append("UI")
    resMess.append("MEMORY_SNAPSHOT")
    memoryDict = {}
    for PCB_ in PCBTable:
        memoryDict[PCB_.pid] = [PCB_.address_code_, PCB_.code_space_ + PCB_.address_code_]
    resMess.append(memoryDict)
    # message:[RES][MEMORY][UI][MEMORY_SNAPSHOT][memoryDict]
    return resMess

def send_disk_state_to_device():
    pass


def every_time_deal(Memory2Kernel,MemoryTime):
    # 输入的读文件message:[REQ][FILESYSTEM][MEMORY][type][fileName][uipid][pid][readTime][block_list]
    #                      0        1        2      3       4       5      6      7           8
    while 1:
        MemoryTime.get()  # 每次收到时间片执行下面的指令
        for runMess in runFileList:  # 处理正在读和写的文件队列
            if runMess[3] == "LOAD":  # 读文件的消息
                runMess[7] -= 1  # 读文件的时间减1
                if runMess[7] == 0:  # 该文件读完成了，返回完成的message，并将这个message移除，修改文件块状态
                    # [RES][MEMORY][KERNEL][LOAD][type_str][load_res][startAddr][uipid][pid]
                    Memory2Kernel.put(["RES","MEMORY","KERNEL","LOAD","COMMOM","SUCCESS",-1,-1,runMess[6]])
                    read_done(runMess[8])  #  读资源释放
                    runFileList.remove(runMess)  # 移出列表
            elif runMess[3] == "WRITE":
                runMess[6] -= 1  # 写文件的时间减1
                if runMess[6] == 0:  # 该文件写完成了，返回完成的message，并将这个message移除，修改文件块状态
                    #[RES][MEMORY][KERNEL][WRITE][writeRes][fileName][pid]
                    Memory2Kernel.put(["RES","MEMORY","KERNEL","WRITE","SUCCESS",runMess[4],runMess[5]])
                    write_done(runMess[7].keys())
                    runFileList.remove(runMess)  # 移出列表
        
        for waitMess in waitFileList:  # 处理等待队列
            if waitMess[3] == "LOAD":  # 处理读文件的操作
                if Disk.occupyBlock[waitMess[8][0]] == 1:  # 文件块正在被读
                    continue
                elif Disk.occupyBlock[waitMess[8][0]] == 0:  # 文件块未被读也未被写
                    for blockNumber in waitMess[8]:
                        Disk.occupyBlock[blockNumber] = 2
                    runFileList.append(waitMess)
                elif Disk.occupyBlock[waitMess[8][0]] >= 2:  # 文件正在被读，不会发生读读冲突
                    for blockNumber in waitMess[8]:
                        Disk.occupyBlock[blockNumber] += 1
                    runFileList.append(waitMess)
                else:
                    print('readFile,wait to run error')

            if waitMess[3] == "WRITE":  # 处理写文件的操作
                if Disk.occupyBlock[waitMess[8][0]] == 0:  # 文件块未进行读写操作
                    for blockNumber in runMess[7].keys():
                        Disk.occupyBlock[blockNumber] = 1  # 将文件块置为读状态
        
        if len(runFileList) == 0:  # 磁盘空闲
            Memory2Kernel.put(['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'WAIT'])
        else:
            Memory2Kernel.put(['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'RUN'])


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
    t1 = threading.Thread(target=every_time_deal, args=(Memory2Kernel,MemoryTime,))
    t1.start()
    while (1):
        while Kernel2Memory.qsize() != 0:
            message = Kernel2Memory.get()
            ret_message = deal_message(message)
            ui_message = send_memory_state_to_UI()
            Memory2Kernel.put(ret_message)
            Memory2Kernel.put(ui_message)
            