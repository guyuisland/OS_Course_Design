import time

ready_dict = {}  # ready队列
running_dict = {}  # running队列
waiting_dict = {}  # waiting队列


class PCB:
    file_list = []  # 打开文件列表
    io = []  # IO使用情况(列表)
    # cpureg = CPUREG()

    def __init__(self, pid_, state_, address_code_, address_process_, code_space_, priority_):
        self.pid = pid_  # pid
        self.state = state_  # ready, running, waiting, terminated
        self.address_code = address_code_  # 代码段首地址
        self.address_process = address_process_  # 进程活动空间首地址
        self.code_space = code_space_  # 代码段长度
        self.priority = priority_  # 进程优先级


# def if_create_PCB(PCB_queue):  # 能否开辟PCB
#     if len(PCB_queue) == PROCESS_MAXNUM:
#         return False
#     else:
#         return True

# PCB队列由内存管理模块维护


def move_from_running_to_waiting(pid, running_dict, waiting_dict):
    if pid in running_dict:
        waiting_dict[pid] = running_dict[pid]
        del(running_dict[pid])
        pid_ret = choose_to_run()
    else:
        print('move_from_running_to_waiting ERROR')
        return pid_ret


def move_from_waiting_to_ready(pid, waiting_dict, ready_dict):
    if pid in ready_dict:
        ready_dict[pid] = waiting_dict[pid]
        del(waiting_dict[pid])
    else:
        print('move_from_waiting_to_ready ERROR')


def move_from_new_to_ready(pid, priority, burst_time, ready_dict):
    ready_dict[pid] = [0, priority, burst_time]  # 等待时间，优先级


def move_from_running_to_ready(pid, running_dict, ready_dict):
    if pid in running_dict:
        ready_dict[pid] = running_dict[pid]
        del(running_dict[pid])
        pid_ret = choose_to_run()
    else:
        print('move_from_running_to_ready ERROR')
    return pid_ret


def move_from_ready_to_running(pid, ready_dict, running_dict):
    if pid in ready_dict:
        running_dict[pid] = ready_dict[pid]
        del(ready_dict[pid])
    else:
        print('move_from_ready_to_running ERROR')


def move_to_terminated(pid, ready_dict, running_dict, waiting_dict):
    if pid in ready_dict:
        del(ready_dict[pid])
    elif pid in running_dict:
        del(running_dict[pid])
    elif pid in waiting_dict:
        del(waiting_dict[pid])
    else:
        print('move_to_terminated ERROR')


def choose_to_run():
    """
    ready_dict[pid] = [0(waited time), priority, burst_time] 
    1. Check if there is any process has waited in ready_dict for too long
        1.1 If no then go to 2
        1.2 If yes then choose the process that has waited for longest time
    2. Find the process with highest priority
        2.1 If the there are multiple processes with the same priority goto 3
        2.2 If only one process has the highest priority then choose it
    3. HRRN: choose the process with maximum 1 + (wait time / burst time)
    """

    time_threshold = 10  # decide whether a process has been waited for too long

    if max(ready_dict.values()) >= time_threshold:
        ret_pid = max(ready_dict.items(), key=lambda x: x[1][0])
    else:
        tmpDict = ready_dict.items()
        tmpDict.sort(key=lambda x: (x[1][1], -(1 + x[1][0] / x[1][2])))
        ret_pid = tmpDict[0][0]

    ready_dict[ret_pid][0] = 0  # set the chosen process waited time to zero

    return ret_pid


def deal_message(message):
    ret_message = []  # 返回消息
    if message[0] == "REQ":  # 消息类型为请求
        if message[3] == "CREATE_PROCESS":  # 请求创建进程
            # message:[REQ][*][PROCESS][CREATE_PROCESS][0x00000000][uipid]
            ret_message.append("REQ")  # 返回消息类型为请求
            ret_message.append("PROCESS")  # 返回消息的消息源是PROCESS
            ret_message.append("MEMORY")  # 返回消息的消息目的是MEMORY
            ret_message.append("CREATE_PROCESS_MEMORY")  # 请求MEMORY分配内存
            ret_message.append(message[4])  # 程序在内存中的首地址
            ret_message.append(message[5])
            # message:[REQ][PROCESS][MEMORY][CREATE_PROCESS_MEMORY][0x00000000][uipid]

        if message[3] == "MOVE_QUEUE":  # 消息类型为将进程移动到某个状态
            # message:[REQ][*][PROCESS][MOVE_QUEUE][pid][s_state][d_state]
            pid = message[4]
            if message[5] == 'RUNNING' and message[6] == 'READY':
                pid_ret = move_from_running_to_ready(
                    pid, running_dict, ready_dict)

            elif message[5] == 'RUNNING' and message[6] == 'WAITING':
                pid_ret = move_from_running_to_waiting(
                    pid, running_dict, waiting_dict)
            elif message[5] == 'WAITING' and message[6] == 'READY':
                move_from_waiting_to_ready(pid, waiting_dict, ready_dict)
            else:
                print("WRONGLY MOVE QUEUE!")

            ret_message.append("RES")  # return REQ
            ret_message.append("PROCESS")
            ret_message.append("KERNEL")  # 消息目的为kernel
            ret_message.append("MOVE_QUEUE")
            ret_message.append(pid_ret)
            # message:[RES][PROCESS][KERNEL][MOVE_QUEUE][pid_ret]

        if message[3] == "TERMINATE_PROCESS":  # 消息类型为kernel崩掉某个进程
            # message:[REQ][*][PROCESS][TERMINATE_PROCESS][pid]
            pid = message[4]
            move_to_terminated(pid, ready_dict, running_dict, waiting_dict)

    if message[0] == "RES":
        if message[3] == "CREATE_PROCESS":  # 响应请求创建进程
            if message[4] == "SUCCESS":  # 内存创建进程成功
                # message:[RES][*][PROCESS][CREATE_PROCESS][SUCCESS][pid][priority][burst_time][uipid]
                pid = message[5]
                priority = message[6]
                burst_time = message[7]
                uipid = message[8]
                # 队列里面的信息包括pid, 进程优先级，等待时间(int计数方式)
                move_from_new_to_ready(pid, priority, burst_time, ready_dict)

                ret_message.append("RES")  # 返回消息类型为请求
                ret_message.append("PROCESS")  # 返回消息的消息源是PROCESS
                ret_message.append("KERNEL")  # 返回消息的消息目的是KERNEL
                ret_message.append("CREATE_PROCESS")  # 进程创建成功
                ret_message.append(uipid)  # 消息对应的序号
                # message:[RES][PROCESS][KERNEL][CREATE_PROCESS_UI_SUCCESS][SUCCESS][pid][priority][uipid]

            if message[4] == "FAIL":
                ret_message.append("RES")  # 返回消息类型为请求
                ret_message.append("PROCESS")  # 返回消息的消息源是PROCESS
                ret_message.append("UI")  # 返回消息的消息目的是UI
                ret_message.append("CREATE_PROCESS_UI_FAIL")  # 进程创建失败
                ret_message.append(uipid)  # 消息对应的序号
    return ret_message
    # 消息加编号


def send_state_to_UI():
    ret_message = []
    ret_message.append("RES")
    ret_message.append("PROCESS")
    ret_message.append("UI")
    ret_message.append("PROCESSSTATE")
    ret_message.append(ready_dict)
    ret_message.append(waiting_dict)
    ret_message.append(running_dict)
    # message:[RES][PROCESS][UI][PROCESSSTATE][ready_dict][waiting_dict][running_dict]
    return ret_message


def start_process(Kernel2Process, Process2Kernel, ProcessTime):
    while (1):
        ProcessTime.get()
        print("A")
        while Kernel2Process.qsize() != 0:
            message = Kernel2Process.get()
            ret_message = deal_message(message)
            ui_message = send_state_to_UI()
            Process2Kernel.put(ret_message)
            Process2Kernel.put(ui_message)
