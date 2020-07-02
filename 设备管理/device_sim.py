# import time

# 全局变量

# 设备,设备等待、占用、使用的长度
# [{’deviceType’: , 'num': },……]
list_deviceUseDict = [{'deviceType': 'K', 'num': 0},
                      {'deviceType': 'P', 'num': 0}]

# 设备队列 结构体
# class node:
#     def __init__(self):
#         self.ID = -1
#         self.priority = 0
#         self.deviceType = '#'
#         self.useTime = 0.0
#         self.arriveSeq = 0

# 设备队列
# [{'deviceType': '', 'ID': , 'priority': , 'useTime': , 'arriveSeq': }……]
list_deviceWaitList = []

# 设备表 结构体
# class Device(object):
#     def __init__(self):
#         self.deviceType = ' '
#         self.state = ' '
#         self.pID = -1
#         self.totalTime = 0.0
#         self.RestTime = 0.0
#         self.pPriority = 100
#         self.arriveTime = 0

# 设备表
# [{'deviceType': '', 'state': , 'pID': , 'totalTime': , 'restTime': , 'pPrority': , 'arriveTime': }……]
list_deviceTable = [
    {'deviceType': 'K', 'state': 'w', 'pID': 0, 'totalTime': 0.0, 'restTime': 0.0, 'pPrority': 0, 'arriveTime': 0},
    {'deviceType': 'P', 'state': 'w', 'pID': 0, 'totalTime': 0.0, 'restTime': 0.0, 'pPrority': 0, 'arriveTime': 0}]

# 磁盘使用情况
bool_diskUse = False

# 中断状态
bool_interruptState = False

# 是否存在正在运行的设备
bool_deviceRun = False  # TODO 是否需要这个变量  ！！！！需要！！！！

# 中断后等待恢复
bool_waitRecover = False

# 已到达的设备申请数量
int_pArrived = 0

# 设备表长度	初值=2
int_deviceTableLen = 2

# 设备队列长度 初值=0
int_deviceListLen = 0

# 正在运行的设备名称
char_device = '0'

bool_IOGlobal = True

float_timerCount = 0.0
bool_timerUp = False


def dealDeviceMess(dealMess):
    resMess = []
    global bool_interruptState

    if dealMess[0] == "TIMER":
        resMess = ''
        global float_timerCount
        global bool_timerUp
        bool_timerUp = True
        float_timerCount = float_timerCount + 1.0
        print("---- ---- TIMER Count: ", float_timerCount)

    elif dealMess[0] == "REQ":
        resMess.append("RES")
        if dealMess[3] == "ADD_QUERY":
            # 添加进程的设备申请
            resMess.append("DEVICE")
            resMess.append("KERNEL")
            resMess.append("ADD_QUERY")

            newDeviceType = dealMess[4]
            newDeviceID = int(dealMess[5])
            newDevicePriority = int(dealMess[6])
            newDeviceUseTime = float(dealMess[7])  # float
            bool_applyState = newDeviceProcessApply(newDeviceID, newDeviceType, newDeviceUseTime, newDevicePriority)

            if bool_applyState:
                resMess.append("SUCC")
                resMess.append(newDeviceID)
            else:
                resMess.append("FAIL")
                resMess.append(newDeviceID)

        elif dealMess[3] == "INTERRUPT_OCCOUR":
            # 中断发生
            resMess.append("DEVICE")
            resMess.append("KERNEL")
            resMess.append("INTERRUPT_OCCOUR")
            # global bool_interruptState
            bool_interruptState = True
            resMess.append("SUCC")

        elif dealMess[3] == "INTERRUPT_RECOVER":
            # 中断恢复
            resMess.append("DEVICE")
            resMess.append("KERNEL")
            resMess.append("INTERRUPT_RECOVER")
            # global bool_interruptState
            bool_interruptState = False
            resMess.append("SUCC")

        elif dealMess[3] == "ADD_DEVICE":
            # 添加设备
            resMess.append("DEVICE")
            resMess.append("UI")
            resMess.append("ADD_DEVICE")
            addType = dealMess[4]
            addState = addDevice(addType)
            if addState:  # 成功添加设备
                resMess.append("SUCC")
                resMess.append(addType)
            else:
                resMess.append("FAIL")
                resMess.append(addType)

        elif dealMess[3] == "DELETE_DEVICE":
            # 删除设备
            resMess.append("DEVICE")
            resMess.append("UI")
            resMess.append("DELETE_DEVICE")
            deleteType = dealMess[4]
            deleteState = deleteDevice(deleteType)
            if deleteState:  # 成功删除设备
                resMess.append("SUCC")
                resMess.append(deleteType)
            else:
                resMess.append("FAIL")
                resMess.append(deleteType)

    elif dealMess[0] == "RES":
        if dealMess[3] == "DISK_STATE":
            # 更新磁盘状态
            #发送给UI
            resMess.append("INFO")
            resMess.append("DEVICE")
            resMess.append("UI")
            resMess.append("DISK_STATE")

            if dealMess[4] == "RUN":
                resMess.append("RUN")
            elif dealMess[4] == "WAIT":
                resMess.append("WAIT")

    return resMess


# TODO 设备管理的主要调度函数
def deviceMain(deviceToKernelMess, deviceToUIMess, kernelToDeviceMess, guiToDeviceMess, deviceTimer):
    global float_timerCount
    global bool_timerUp

    # time_start = float_timerCount
    # time_startDisk = time_start
    # time_startDevice = time_start
    # time_startIO = time_start

    while True:
        global bool_IOGlobal

        # TODO 检查消息队列
        if deviceTimer.qsize() != 0:  # 仅会出现一条消息
            getMessage = deviceTimer.get()
            responseMess = dealDeviceMess(getMessage)
            print('++++++ Timer: ', getMessage)

        while guiToDeviceMess.qsize() != 0:
            # 处理从gui传来的消息
            getMessage = guiToDeviceMess.get()
            print('from UI: ', getMessage)
            responseMess = dealDeviceMess(getMessage)
            deviceToUIMess.put(responseMess)

        while kernelToDeviceMess.qsize() != 0:
            # 处理从kernel传来的消息
            getMessage = kernelToDeviceMess.get()
            responseMess = dealDeviceMess(getMessage)
            print('from Kernel: ', getMessage)
            if len(responseMess):  # 返回值非空
                if responseMess[0] == "RES":
                    # 回复消息
                    deviceToKernelMess.put(responseMess)
                elif responseMess[0] == "INFO":  # 仅在更新磁盘状态时，使用
                    deviceToUIMess.put(responseMess)

        # TODO 设备调度的主要函数
        # time_end = time.perf_counter()
        global bool_deviceRun
        global int_deviceListLen
        global char_device
        global list_deviceWaitList
        global bool_waitRecover
        global bool_interruptState

        #TODO 存储管理部分每个时间片直接发送应答结果，不需要请求消息
        '''# TODO 磁盘状态更新 每个时间片更新一次
        # 更新磁盘
        # if (time_end - time_startDisk) > 3.00 and bool_interruptState == False:
        if bool_timerUp == True and bool_interruptState == False:
            ret_mess_device = ["REQ", "DEVICE", "KERNEL", "DISK_STATE"]
            deviceToKernelMess.put(ret_mess_device)
            # bool_diskUse = diskQuery()
            # time_startDisk = time.perf_counter()'''

        '''# TODO 去掉更新IO通道
        # TODO IO通道状态每隔1s更新一次（中断未发生时）
        if (
                time_end - time_startIO) > 1.00 and char_device == '0' and int_deviceListLen > 0 and bool_interruptState == False:
            if bool_interruptState == False:
                ret_mess_device = ["REQ", "IO_STATE"]
                deviceToKernelMess.put(ret_mess_device)
                time_startIO = time.perf_counter()'''

        # TODO 设备正在运行，中断发生
        # 首次判断中断
        # 停止设备运行，释放IO通道，更新标志位
        if bool_interruptState == True and bool_waitRecover == False and bool_timerUp == True:
            if bool_deviceRun:  # 有设备正在运行
                # time_endDevice = time.perf_counter()
                # time_runDevice = time_endDevice - time_startDevice
                for line in list_deviceTable:
                    if line['deviceType'] == char_device:  # 正在运行的设备
                        temp_restTime = float(line['restTime'])

                        if temp_restTime <= 0.0:  # 设备运行结束
                            # TODO 需要告知调度中心设备运行结束

                            # 通知kernel
                            ret_mess_device = ["REQ", "DEVICE", "KERNEL", "DEVICE_FINISH"]
                            ret_mess_device.append(line["pID"])
                            deviceToKernelMess.put(ret_mess_device)

                            # 通知UI
                            ret_mess_device = ["INFO", "DEVICE", "UI", "DEVICE_FINISH"]
                            ret_mess_device.append(char_device)
                            deviceToUIMess.put(ret_mess_device)

                            print("### interr ###")
                            print(">>>> >>>> finish running: " + str(line))
                            # 更新设备表
                            # 释放资源
                            line['state'] = 'w'
                            line['pID'] = 0
                            line['totalTime'] = 0.0
                            line['restTime'] = 0.0
                            line['pPrority'] = 0
                            line['arriveTime'] = 0

                            # 更新设备使用情况
                            for newLine in list_deviceUseDict:
                                if newLine['deviceType'] == char_device:
                                    tempCount = newLine['num']
                                    tempCount -= 1
                                    newLine['num'] = tempCount
                                    # print("update list_deviceUseDict: " + str(newLine))
                                    char_device = '0'
                                    bool_deviceRun = False
                                    bool_IOGlobal = True
                                    break

                            int_deviceListLen -= 1

                        else:  # 设备没有运行结束
                            # temp_restTime = temp_restTime - time_runDevice
                            # line['restTime'] = temp_restTime
                            # print("update restTime: " + str(line))
                            # time_startDevice = time.perf_counter()  # 更新设备开始时间
                            print("### interrupt ### stop device: " + str(line))

                            # TODO 更新设备状态 发送给ui
                            ret_mess_device = ["INFO", "DEVICE", "UI", "DEVICE_UPDATE", "INTTERUPT"]
                            ret_mess_device.append(char_device)
                            deviceToUIMess.put(ret_mess_device)

                            #TODO 告知kernel设备中断
                            ret_mess_device = ['RES', 'DEVICE', 'KERNEL', 'INTERRUPT_DEVICE']
                            ret_mess_device.append(char_device)
                            deviceToKernelMess.put(ret_mess_device)

                        break

            # TODO 释放IO通道(中断)
            bool_IOGlobal = True

            bool_waitRecover = True
            print("### interrupt success ###")

        # TODO 中断结束，恢复设备运行
        # 中断前运行的设备未恢复成功时进入
        if bool_interruptState == False and bool_waitRecover == True:
            if bool_deviceRun:  # 中断结束前有设备在运行
                # bool_IO = bool_IOGlobal
                if bool_IOGlobal:  # IO通道申请成功
                    # time_startDevice = time.perf_counter()
                    bool_IOGlobal = False  # 占用IO通道

                    '''# TODO 占用IO通道
                    ret_mess_device = ["REQ", "IO_OCCUPY"]
                    deviceToKernelMess.put(ret_mess_device)'''

                    # TODO 更新设备状态
                    ret_mess_device = ["INFO", "DEVICE", "UI", "DEVICE_UPDATE", "RECOVER"]
                    ret_mess_device.append(char_device)
                    deviceToUIMess.put(ret_mess_device)

                    #print("### recover device success: " + str(list_deviceTable))
                    bool_waitRecover = False
                # else:  # 更新IO通道
                #     ret_mess_device = ["REQ", "IO_STATE"]
                #     deviceToKernelMess.put(ret_mess_device)
            else:
                bool_waitRecover = False
                print("####### recover success")

        # TODO 设备正常运行
        # print("hello..."+str(int_deviceListLen))
        if int_deviceListLen > 0 and bool_interruptState == False and bool_waitRecover == False and bool_timerUp == True:  # 有进程待等待/占用/使用设备
            if bool_deviceRun:  # 有设备正在运行 #更新设备表的时间数据
                # time_endDevice = time.perf_counter()
                # time_runDevice = time_endDevice - time_startDevice
                for line in list_deviceTable:
                    if line['deviceType'] == char_device:  # 正在运行的设备
                        temp_restTime = float(line['restTime'])

                        if 1.0 >= temp_restTime:  # 设备运行结束
                            # TODO 需要告知调度中心设备运行结束 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                            # 通知kernel
                            ret_mess_device = ["REQ", "DEVICE", "KERNEL", "DEVICE_FINISH"]
                            ret_mess_device.append(line["pID"])
                            deviceToKernelMess.put(ret_mess_device)

                            # 通知UI
                            ret_mess_device = ["INFO", "DEVICE", "UI", "DEVICE_FINISH"]
                            ret_mess_device.append(char_device)
                            deviceToUIMess.put(ret_mess_device)

                            print(">>>> >>>> finish running: " + str(line))
                            # 更新设备表
                            # 释放资源
                            line['state'] = 'w'
                            line['pID'] = 0
                            line['totalTime'] = 0.0
                            line['restTime'] = 0.0
                            line['pPrority'] = 0
                            line['arriveTime'] = 0

                            # 更新设备使用情况
                            for newLine in list_deviceUseDict:
                                if newLine['deviceType'] == char_device:
                                    tempCount = newLine['num']
                                    tempCount -= 1
                                    newLine['num'] = tempCount
                                    # print("update list_deviceUseDict: "+str(newLine))
                                    char_device = '0'
                                    bool_deviceRun = False
                                    '''# TODO 释放IO通道 (设备运行结束)
                                    ret_mess_device = ["REQ", "IO_RELEASE"]
                                    deviceToKernelMess.put(ret_mess_device)'''

                                    bool_IOGlobal = True
                                    break

                            int_deviceListLen -= 1

                            # 更新优先级（设备等待队列）
                            for line_pri in list_deviceWaitList:
                                priOld = int(line_pri['priority'])
                                if priOld > 0:
                                    priOld -= 1
                                    line_pri['priority'] = priOld



                        else:  # 设备没有运行结束 更新剩余时间，通知UI
                            temp_restTime = temp_restTime - 1.0
                            line['restTime'] = temp_restTime
                            # print("update restTime: " + str(line))
                            # time_startDevice = time.perf_counter()  # 更新设备开始时间
                            # 通知UI
                            ret_mess_device = ["INFO", "DEVICE", "UI", "DEVICE_UPDATE", "RUN"]
                            ret_mess_device.append(char_device)
                            deviceToUIMess.put(ret_mess_device)

                        break


            else:  # 没有设备正在运行
                # 设备分配

                # 是否存在设备等待分配 前期已经判断过
                # 在这里是‘有进程待等待/占用/使用设备’且‘无设备在运行’
                bool_IO = bool_IOGlobal
                if bool_IO:  # IO通道申请成功

                    list_deviceWaitList = sorted(list_deviceWaitList,
                                                 key=lambda a: (int(a["priority"]), int(a["arriveSeq"])))
                    # print(list_deviceWaitList)
                    for line_deliver in list_deviceWaitList:
                        deviceTypeDeliver = line_deliver['deviceType']
                        IDDeliver = line_deliver['ID']
                        priorityDeliver = line_deliver['priority']
                        useTimeDeliver = line_deliver['useTime']
                        arriveSeqDeliver = line_deliver['arriveSeq']
                        # print("remove from list_deviceWaitList: " + str(line_deliver))
                        list_deviceWaitList.remove(line_deliver)
                        for line_update in list_deviceTable:
                            if line_update['deviceType'] == deviceTypeDeliver:
                                # 找到需要运行的设备
                                # line_update['deviceType'] = deviceTypeDeliver
                                line_update['state'] = 'R'
                                line_update['pID'] = IDDeliver
                                line_update['totalTime'] = useTimeDeliver
                                line_update['restTime'] = useTimeDeliver
                                line_update['pPrority'] = priorityDeliver
                                line_update['arriveTime'] = arriveSeqDeliver
                                print("<<<< <<<< update list_deviceTable: " + str(line_update))

                                bool_deviceRun = True
                                char_device = deviceTypeDeliver

                                bool_IOGlobal = False
                                '''#TODO 占用IO通道
                                ret_mess_device=["REQ","IO_OCCUPY"]
                                deviceToKernelMess.put(ret_mess_device)'''

                                # TODO 更新设备状态
                                ret_mess_device = ["INFO", "DEVICE", "UI", "DEVICE_UPDATE", "RUN"]
                                ret_mess_device.append(char_device)
                                deviceToUIMess.put(ret_mess_device)

                                # time_startDevice = time.perf_counter()  # 更新设备开始时间
                                break

                        # 只取第一组数据
                        break

            # end of 'if int_deviceListLen > 0'
        bool_timerUp = False  # 时间脉冲置为假

    return


# TODO 接收新的进程的设备申请
# bool newDeviceProcessApply(int newpID, char newDeviceType, float newTotalTime, int newPriority)
def newDeviceProcessApply(newpID, newDeviceType, newTotalTime, newPriority):
    # 检查是否存在设备
    # 若有，则添加至设备队列尾部，等待调度 return true
    # 若没有，则设备申请失败 return false

    bool_newApply = False

    for line in list_deviceUseDict:
        if line['deviceType'] == newDeviceType:  # 设备在设备表中
            dict_newApply = {}
            dict_newApply['deviceType'] = newDeviceType
            dict_newApply['ID'] = newpID
            dict_newApply['priority'] = newPriority
            dict_newApply['useTime'] = newTotalTime
            global int_pArrived
            global int_deviceListLen
            dict_newApply['arriveSeq'] = int_pArrived
            list_deviceWaitList.append(dict_newApply)
            int_pArrived += 1
            int_deviceListLen += 1
            # print('dict_newApply: ',dict_newApply)
            # print('int_pArrived: ',int_pArrived)

            newCount = line['num']
            newCount += 1
            line['num'] = newCount
            # print(line)

            bool_newApply = True
            break

    # print(list_deviceUseDict)
    return bool_newApply


# TODO 接收添加设备申请
# bool addDevice(char addDeviceType)
def addDevice(addDeviceType):
    # 新的设备种类未在设备表中，添加设备,初始化设备信息
    # 否则，设备添加失败
    bool_addState = True

    for line in list_deviceTable:
        if line['deviceType'] == addDeviceType:
            bool_addState = False
            break

    if bool_addState:
        # 设备表 update
        new_device = {}
        new_device['deviceType'] = addDeviceType
        new_device['state'] = 'w'
        new_device['pID'] = 0
        new_device['totalTime'] = 0.0
        new_device['restTime'] = 0.0
        new_device['pPrority'] = 0
        new_device['arriveTime'] = 0
        list_deviceTable.append(new_device)
        # 设备使用情况 update
        new_use = {}
        new_use['deviceType'] = addDeviceType
        # new_use['Dstate'] = 'w'
        new_use['num'] = 0
        list_deviceUseDict.append(new_use)
        # 设备表长度 update
        global int_deviceTableLen
        int_deviceTableLen += 1

    # print(list_deviceTable)
    # print(list_deviceUseDict)
    # print('int_deviceTableLen: ',int_deviceTableLen)

    return bool_addState


# TODO 接收删除设备申请
# bool deleteDevice(char deleteDeviceType)
def deleteDevice(deleteDeviceType):
    # 禁止删除K、P
    # 设备的等待、占用、运行均不存在，则成功删除设备
    # 否则，禁止删除设备，或不存在待删除的设备
    bool_deleteState = False

    if deleteDeviceType == 'K' or deleteDeviceType == 'P':
        # 禁止删除K、P
        bool_deleteState = False
    else:
        for line in list_deviceUseDict:
            if line['deviceType'] == deleteDeviceType:
                print("use have device")
                if line['num'] == 0:
                    print("device num is 0")
                    # 设备使用情况 update
                    list_deviceUseDict.remove(line)
                    for newline in list_deviceTable:
                        if newline['deviceType'] == deleteDeviceType:
                            print("list have device")
                            # 设备表 update
                            list_deviceTable.remove(newline)
                            # 设备表长度 update
                            global int_deviceTableLen
                            int_deviceTableLen -= 1
                            bool_deleteState = True
                            break

                break

    # print(list_deviceTable)
    # print(list_deviceUseDict)
    # print('int_deviceTableLen: ',int_deviceTableLen)

    return bool_deleteState

# TODO 查询设备使用情况
# 直接访问全局变量即可
