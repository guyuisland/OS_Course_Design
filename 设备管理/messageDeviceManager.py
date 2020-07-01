# TODO 这是最终的使用版本

from multiprocessing import Process, Queue
import time
import queue
import deviceManagerMessage.device_sim

kernelToDeviceMess = Queue()
guiToDeviceMess = Queue()
deviceToKernelMess = Queue()
deviceToGuiMess = Queue()
deviceTimer = Queue()

if __name__ == "__main__":
    pDevice = Process(target=deviceManagerMessage.device_sim.deviceMain,
                      args=(deviceToKernelMess, deviceToGuiMess,
                            kernelToDeviceMess, guiToDeviceMess, deviceTimer,))

    pDevice.start()
