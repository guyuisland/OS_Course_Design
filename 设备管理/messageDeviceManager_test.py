# TODO 这是测试指令版本

from multiprocessing import Process, Queue
import time
import queue
import deviceManagerMessage.device_sim

kernelToDeviceMess = Queue()
guiToDeviceMess = Queue()
deviceToKernelMess = Queue()
deviceToGuiMess = Queue()
deviceTimer = Queue()

check = [
    ['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'WAIT'],
    ['RES', 'KERNEL', 'DEVICE', 'DISK_STATE', 'RUN'],
    ['REQ', 'KERNEL', 'DEVICE', 'ADD_QUERY', 'K', 0, 3, 9.2],
    ['REQ', 'GUI', 'DEVICE', 'ADD_DEVICE', 'L'],
    ['REQ', 'GUI', 'DEVICE', 'ADD_DEVICE', 'T'],
    ['REQ', 'KERNEL', 'DEVICE', 'ADD_QUERY', 'M', 1, 1, 12.1],
    ['REQ', 'KERNEL', 'DEVICE', 'ADD_QUERY', 'L', 2, 4, 3.0],
    ['REQ', 'KERNEL', 'DEVICE', 'INTERRUPT_OCCOUR'],
    ['REQ', 'KERNEL', 'DEVICE', 'INTERRUPT_RECOVER'],
    ['REQ', 'GUI', 'DEVICE', 'DELETE_DEVICE', 'L'],
    ['REQ', 'GUI', 'DEVICE', 'ADD_DEVICE', 'Q'],
    ['REQ', 'KERNEL', 'DEVICE', 'ADD_QUERY', 'P', 6, 1, 4.5],
    ['REQ', 'KERNEL', 'DEVICE', 'ADD_QUERY', 'Q', 8, 4, 8.0],
    ['REQ', 'GUI', 'DEVICE', 'ADD_DEVICE', 'L'],
    ['REQ', 'KERNEL', 'DEVICE', 'ADD_QUERY', 'P', 11, 12, 3.9],
    ['REQ', 'GUI', 'DEVICE', 'DELETE_DEVICE', 'L'],
    ['REQ', 'KERNEL', 'DEVICE', 'ADD_QUERY', 'K', 12, 1, 13.9],
    ['REQ', 'GUI', 'DEVICE', 'DELETE_DEVICE', 'S'],
    ['REQ', 'GUI', 'DEVICE', 'DELETE_DEVICE', 'T'],
    ['REQ', 'GUI', 'DEVICE', 'DELETE_DEVICE', 'K'],
    ['REQ', 'GUI', 'DEVICE', 'ADD_DEVICE', 'L'],
    ['REQ', 'GUI', 'DEVICE', 'DELETE_DEVICE', 'P'],
    ['REQ', 'GUI', 'DEVICE', 'DELETE_DEVICE', 'L']
]


def write(deviceToKernelMess, deviceToGuiMess, kernelToDeviceMess, guiToDeviceMess):
    i = 0
    j = 0
    while True:
        if i < len(check):
            ret_mess_device = check[i]
            # from Gui
            if ret_mess_device[1] == 'GUI':
                guiToDeviceMess.put(ret_mess_device)

            else:
                kernelToDeviceMess.put(ret_mess_device)

            i = i + 1

        while deviceToGuiMess.qsize() != 0:
            getMess = deviceToGuiMess.get()
            print('Gui recv: ', getMess)

        while deviceToKernelMess.qsize() != 0:
            getMess = deviceToKernelMess.get()
            print('....Kernel recv: ', getMess)
            if getMess[0] == "REQ":
                # if getMess[1] == "IO_STATE":
                #     retMess = ["RES", "IO_STATE", "EMPTY"]
                #
                #     kernelToDeviceMess.put(retMess)
                #     j = j + 1
                if getMess[1] == "DISK_STATE":
                    retMess = ["RES", 'KERNEL', 'DEVICE', "DISK_STATE", "RUN"]
                    kernelToDeviceMess.put(retMess)

        time.sleep(1)


def timerForDevice(TimerDevice):
    while True:
        retMess = ['TIMER', '*', 'DEVICE']
        TimerDevice.put(retMess)
        time.sleep(1)
        # print("timer send ++++++++++++++++++++++++++++++++++")

    return


if __name__ == "__main__":
    pDevice = Process(target=deviceManagerMessage.device_sim.deviceMain,
                      args=(deviceToKernelMess, deviceToGuiMess,
                            kernelToDeviceMess, guiToDeviceMess, deviceTimer,))

    wp = Process(target=write, args=(deviceToKernelMess, deviceToGuiMess,
                                     kernelToDeviceMess, guiToDeviceMess,))

    timerDevice = Process(target=timerForDevice, args=(deviceTimer,))

    pDevice.start()

    wp.start()
    timerDevice.start()

    wp.join()
    timerDevice.join()
