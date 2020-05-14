import numpy as np
class PCB:
    pass

def allocate_memory_to_pcb(newPCB): #进程调用改函数传递PCB给内存，内存根据PCB大小分配空间
    pass

def allocate_page_to_process(pageNum):#内存根据PCB需要的内存分配页面给进程
    pass

def get_free_pages()->list: #返回当前内存空闲的页面编号列表，用于给进程分配空间
    pass

def find_page_number(pPid:int,virPageNum:int):#CPU根据进程号和续页号可以查找到实页号
    pass

def mov_page_to_memory(pPid:int):  #将根据进程号把虚拟内存的页调到内存中
    pass

def get_instruction(PC:int)->str:    #根据PC到内存中找到指令并返回
    pass


#磁盘的函数

def file_is_idle(nodeNumber:int)->bool: #根据节点号判断文件是否空闲
    pass

def get_free_block()->list: #获得当前空闲的文件块列表
    pass

def allocate_file_blocks(fileSize:int)->int: #根据需要分配的文件块大小分配空间，并返回起始地址startAddress
    pass

def allocate_direct_block(fileSize:int)->int:    
    #使用first-fit进行分配  
    #根据需要分配的文件块大小分配直接快,返回开始地址，若分配失败则返回-1，表示没有那么大的直接块startAddress
    pass

def get_free_direct_blocks(blockList:list)->list:   #获得直接块的bitmap返回给allocate_direct_block
    pass
#数据结构
#内存的数据结构
    #从多少块到多少块是系统区,存放PCB和页表，从多少块往后是用户去，存放指令和数据
    #页的定义
physicalMemory = [[],[],[]*MAX_USE_MEMORY_NUMBER]   #0号存放PCB，1号存放页表，2号存放指令
    
#虚拟内存的数据结构
    #一个记录进程指令的起始地址和终止地址的数组
    #存放指令的页(与物理内存相同)

virtualMemoryBlock = []*MAX_VIRTUAL_BLOCK_NUMBER


#磁盘的数据结构
fileUseCondition = np.array([False]*MAX_FILE_NUMBER) #存放最多的文件数，用来标明文件是否空闲
fileBlocksBitmap = np.array([False]*MAX_BLOCK_NUMBER)   #存放当前文件块的的位图
docIndexingWay = dict() #存放文件的索引方式1代表直接索引，2代表一级索引，3代表二级索引
#文件块的定义
fileBlocks = []*MAX_BLOCK_NUMBER