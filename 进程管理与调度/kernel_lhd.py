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
    p = Process(target=process_sim.start_process,
                args=(Kernel2Process, Process2Kernel,))
    p.start()
    i = 0
    while(1):
        message = ["REQ", "MEMORY", "PROCESS", "CREATE_PROCESS", 50]
        Kernel2Process.put(message)
        time.sleep(1)
        ret = Process2Kernel.get()
        # i += 1
        print(ret[4])
