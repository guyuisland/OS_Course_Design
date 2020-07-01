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
    
    while 1:
        now = datetime.datetime.now()
        Kernel2Memory.put(1)   
        ret = Memory2Kernel.get()
        print(ret)
        if now.second % 3 == 0 and preSecond != now.second:
            MemoryTime.put(1)
        preSecond = now.second
        time.sleep(1)
        