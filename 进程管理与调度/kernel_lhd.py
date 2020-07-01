import process_sim
from multiprocessing import Process, Queue, Pool, Manager, Pipe
import multiprocessing as mp
import time
import random
import queue
import threading

# 目前时间由电脑系统时间决定
# 视目前运行状况得到负荷，决定要不要给一段时间给中断程序发送查询系统时间的请求


# 维持每个进程的信息交流队列
# 多少个待定故不列出，
# 但是都是全局变量
# 类型同communicate1
test = queue

# 用于存放未处理的命令
work_queue = queue


def code_sim(code, code_num):
    # 指令功能模拟
    # 具体指令，指令号（用于区分）
    return


if __name__ == "__main__":
    Kernel2Process = Queue()
    Process2Kernel = Queue()
    ProcessTime = Queue()
    p = Process(target=process_sim.start_process,
                args=(Kernel2Process, Process2Kernel, ProcessTime,))
    p.start()
    i = 0
    message = []
    message.append(["REQ", "*", "PROCESS", "CREATE_PROCESS", 0x00000000, 2])
    message.append(["RES", "MEMORY", "PROCESS", "CREATE_PROCESS", "SUCCESS", 2, 5, 20, 2])
    message.append(["REQ", "*", "PROCESS", "CREATE_PROCESS", 0x00000001, 3])
    message.append(["RES", "MEMORY", "PROCESS", "CREATE_PROCESS", "SUCCESS", 3, 6, 20, 3])
    message.append(["REQ", "*", "PROCESS", "CREATE_PROCESS", 0x00000002, 4])
    message.append(["RES", "MEMORY", "PROCESS", "CREATE_PROCESS", "SUCCESS", 4, 5, 20, 4])
    message.append(["REQ", "KERNEL", "PROCESS", "MOVE_QUEUE", 2, "RUNNING", "READY"])
    while(1):
        time.sleep(1)
        ProcessTime.put(1)
        Kernel2Process.put(message[i])
        ret = Process2Kernel.get()
        i += 1
