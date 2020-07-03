from fileSystem import *
from multiprocessing import Queue, Process
import time

if __name__ == '__main__':
    Kernel2FS = Queue()
    FS2Kernel = Queue()

    p = Process(target=start_fs, args=(Kernel2FS, FS2Kernel))
    p.start()

    test_message = []
    prefix = ['REQ', 'UI', 'FILESYSTEM']
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CREATE_FILE', 'EXEC', 'new_file_exec'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CREATE_FILE', 'COMMON', 'new_file_a'])
    test_message.append(['REQ', 'UI', 'FILESYSTEM', 'DEL_FILE', 'new_file_a'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CHANGE_FILE_NAME', 'new_file_exec', 'new_file_exec_change'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CREATE_DIR', 'new_dir'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'PWD'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'LS'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'MAP', 'new_file_exec_change'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CHANGE_DIR', 'new_dir'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CREATE_FILE', 'COMMON', 'new_file_com'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'PWD'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'PARENT_DIR'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CHANGE_DIR_NAME', 'new_dir', 'new_dir_change'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'DEL_DIR', 'new_dir_change'])
    test_message.append(
        ['REQ', 'UI', 'FILESYSTEM', 'WRITE_FILE', 'new_file_exec', 2, '', -2, 0])

    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CREATE_FILE', 'COMMON', 'new_file_exec_change'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'DEL_FILE', 'new_file'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CAT', 'new_file'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'MAP', 'new_file'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'DEL_FILE', 'new_file'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CHANGE_FILE_NAME', 'new_file', 'new_file_exec_change'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'DEL_DIR', 'new_dir'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'CHANGE_DIR', 'new_dir'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'PARENT_DIR'])
    # test_message.append(['REQ', 'UI', 'FILESYSTEM', 'WRITE_FILE', 'new_file_exec', 2, '', -2, 0])

    # test_message.append(['REQ', 'KERNEL', 'FILESYSTEM', 'LOAD_FILE', 'EXEC', 'new_file_exec_change', 3, -1, -1])
    # test_message.append(['REQ', 'KERNEL', 'FILESYSTEM', 'LOAD_FILE', 'COMMON', 'new_file_a', -1, 6, 5])
    # test_message.append(['REQ', 'KERNEL', 'FILESYSTEM', 'WRITE_FILE', 'new_file_a', 2, '', 5, 3])

    # test_message.append(['REQ', 'KERNEL', 'FILESYSTEM', 'LOAD_FILE', 'EXEC', 'new_file_a', 3, -1, -1])
    # test_message.append(['REQ', 'KERNEL', 'FILESYSTEM', 'LOAD_FILE', 'COMMON', 'new_file', -1, 6, 5])
    # test_message.append(['REQ', 'KERNEL', 'FILESYSTEM', 'WRITE_FILE', 'new_file', 2, '', 5, 3])
    test_message.append(['REQ', 'KERNEL', 'FILESYSTEM', 'SHUTDOWN'])

    for m in test_message:
        Kernel2FS.put(m)
        print(m[3])
        print(FS2Kernel.get())
        print()
