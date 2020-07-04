import math
import json

BLOCK_SIZE = 64
BLOCK_AMOUNT = 100
block_index = [0 for i in range(BLOCK_AMOUNT)]
file_hash_table = ['' for j in range(BLOCK_AMOUNT)]
TYPE_DIR = 'DIR'
TYPE_FILE = 'FILE'
TYPE_COMMON_FILE = 'COMMON'
TYPE_EXEC_FILE = 'EXEC'
HEAD_REQ = 'REQ'
HEAD_RES = 'RES'
HEAD_UI = 'UI'
HEAD_KERNEL = 'KERNEL'
HEAD_MEMORY = 'MEMORY'
HEAD_FS = 'FILESYSTEM'


def find_block_for_allocation(block_num: int) -> list:
    alloc = []
    for i in range(BLOCK_AMOUNT):
        if block_num == 0:
            break
        elif block_index[i] == 0:
            alloc.append(i)
            block_num -= 1
    return alloc


def occupy_blocks(block_list):
    for b in block_list:
        block_index[b] = 1


def release_blocks(block_list):
    for b in block_list:
        block_index[b] = 0


class Inode:
    node_table = dict()  # node_no : inode

    def __init__(self, file_type, file_size=0, block_allocation=None):
        if block_allocation is None:
            block_allocation = []
        self.file_size = int(file_size)
        # inode type : common / exec
        self.file_type = file_type
        self.block_allocation = block_allocation
        if len(block_allocation) == 0:
            self.allocate(1)
        else:
            occupy_blocks(block_allocation)

    # allocate blocks for a inode
    def allocate(self, block_num):
        # add blocks
        if block_num > 0:
            # find 'block_num' blocks
            allocation = find_block_for_allocation(block_num)
            occupy_blocks(allocation)
            self.block_allocation.extend(allocation)
        elif block_num < 0:
            new_len = len(self.block_allocation) + block_num
            self.block_allocation = self.block_allocation[:new_len]
            del_allocation = self.block_allocation[new_len:]
            release_blocks(del_allocation)
        else:
            return

    # find inode from node_no, then release all
    @classmethod
    def remove_inode(cls, node_no: int):
        inode = cls.get_inode(node_no)
        release_blocks(inode.block_allocation)
        cls.node_table.pop(node_no)

    @classmethod
    def get_inode(cls, node_no: int):
        return Inode.node_table[node_no]


# def __del__(self):
#     for b in self.block_allocation:
#         block_index[b] = 0


class InodeFileName:
    node_name_table = {'/': []}  # key: name ; value: (type,name,inode_for_file)
    starting_node_no = 2
    pwd_name = '/'

    def __init__(self, file_name, file_type, dir_name):
        self.file_name = file_name
        self.inode_no = InodeFileName.get_new_node_no()  # get a inode_no
        inode = Inode(file_type)
        Inode.node_table[self.inode_no] = inode
        InodeFileName.node_name_table[dir_name].append((TYPE_FILE, file_name, self.inode_no))

    @classmethod
    def get_node_no(cls, file_name: str, dir_name) -> int:
        dir_contents = cls.node_name_table[dir_name]
        for content_item in dir_contents:
            if content_item[0] == TYPE_FILE and content_item[1] == file_name:
                return content_item[2]
        return -1

    @classmethod
    def remove_node_no(cls, file_name: str, dir_name) -> int:
        node_no = cls.get_node_no(file_name, dir_name)
        if node_no != -1:
            Inode.remove_inode(node_no)
            cls.node_name_table[dir_name].remove((TYPE_FILE, file_name, node_no))
            return 0
        else:
            return -1

    @classmethod
    def get_new_node_no(cls):
        cls.starting_node_no += 1
        return cls.starting_node_no


def create_file(file_type: str, file_name: str, dir_name) -> int:
    """
    Interface: /used by system/
    Give a file name, use it to create a file.
    Return inode_no.
    """
    if InodeFileName.get_node_no(file_name, dir_name) != -1:
        return -1
    else:
        inode_file = InodeFileName(file_name, file_type, dir_name)
        return inode_file.inode_no


def del_file(file_name: str, dir_name) -> int:
    """
    Interface: /used by system/
    Give a file name, use it to delete a file.
    Return status: >0 - succeed, -1 - fail, other - ...
    """
    node_no = InodeFileName.get_node_no(file_name, dir_name)
    if node_no != -1:
        InodeFileName.remove_node_no(file_name, dir_name)
    return node_no


def read_file(file_name: str, dir_name) -> list:
    """
    Interface: /used by system/
    Give a file name, use it to load the file into memory.
    Return status:  - succeed, -1 - fail, other - ...
    """
    node_no = InodeFileName.get_node_no(file_name, dir_name)
    block_list = []
    if node_no != -1:
        inode = Inode.get_inode(node_no)
        block_list = inode.block_allocation
    return block_list


def store_file(file_name: str, dir_name, buffer='', block_size=0):
    """
    Interface: /used by system/
    Give a file name and a buffer, store the contents of buffer into the file.
    Return status: >0 - succeed, -1 - fail, other - ...
    """
    # calculate blocks needed
    # buffer = 'M10     Y3      C1      C2      C3      C4      C5      C6      Q       '
    if buffer == '':
        buffer = 'a' * block_size * 64
    node_no = InodeFileName.get_node_no(file_name, dir_name)
    # new_blocks = []
    block_contents_dict = {}
    if node_no != -1:
        # allocate more file blocks
        inode = Inode.get_inode(node_no)
        block_num = math.ceil((inode.file_size + len(buffer)) / BLOCK_SIZE)
        new_block_allocation = block_num - len(inode.block_allocation)
        if new_block_allocation == 0:
            new_blocks = inode.block_allocation[-1]
            block_contents_dict[new_blocks] = buffer
            # store_buffer(block_contents_dict)
        elif new_block_allocation > 0:
            inode.allocate(new_block_allocation)
            first_seg = 64 - inode.file_size % 64
            # construct dict
            if first_seg > 0:
                # new_blocks.append(inode.block_allocation[-new_block_allocation - 1])
                block_contents_dict[inode.block_allocation[-new_block_allocation - 1]] = buffer[0:first_seg]
            for b in inode.block_allocation[-new_block_allocation:-1]:
                # new_blocks.append(b)
                block_contents_dict[b] = buffer[first_seg:first_seg + 64]
                first_seg += 64
            # new_blocks.append(inode.block_allocation[-1])
            block_contents_dict[inode.block_allocation[-1]] = buffer[first_seg:]
            # store_buffer_into()
        inode.file_size += len(buffer)
    # reallocate blocks for file
    # print(block_contents_dict)
    return block_contents_dict


def change_file_name(file_name: str, new_file_name: str, dir_name) -> int:
    """
    Interface: /used by system/
    Give a file name and a new file name, change the file name.
    Return status: 0 - succeed, -1 - fail, other - ...
    """
    #
    node_no = InodeFileName.get_node_no(file_name, dir_name)
    if node_no != -1:
        InodeFileName.node_name_table[dir_name].remove((TYPE_FILE, file_name, node_no))
        InodeFileName.node_name_table[dir_name].append((TYPE_FILE, new_file_name, node_no))
    return node_no


def create_dir(dir_name: str, parent_dir) -> int:
    dir_contents = InodeFileName.node_name_table[parent_dir]
    new_dir = (TYPE_DIR, dir_name)
    if new_dir in dir_contents:
        return -1
    else:
        InodeFileName.node_name_table[parent_dir].append(new_dir)
        new_dir_name = parent_dir + dir_name + '/'
        InodeFileName.node_name_table[new_dir_name] = []
        return 1


def change_dir(dir_name: str, parent_dir) -> int:
    dir_contents = InodeFileName.node_name_table[parent_dir]
    new_dir = (TYPE_DIR, dir_name)
    if new_dir in dir_contents:
        InodeFileName.pwd_name = parent_dir + new_dir[1] + '/'
        return 1
    else:
        return -1


def del_dir_recursive(dir_name: str):
    for path in InodeFileName.node_name_table[dir_name]:
        if path[0] == TYPE_DIR:
            del_dir_recursive(dir_name + path[1] + '/')
        elif path[0] == TYPE_FILE:
            del_file(path[1], dir_name)
        del InodeFileName.node_name_table[dir_name]


def del_dir(dir_name: str, parent_dir) -> int:
    dir_contents = InodeFileName.node_name_table[parent_dir]
    new_dir = (TYPE_DIR, dir_name)
    if new_dir in dir_contents:
        del_dir_recursive(parent_dir + dir_name + '/')
        InodeFileName.node_name_table[parent_dir].remove(new_dir)
        return 1
    else:
        return -1


def change_dir_name(dir_name: str, new_dir_name: str, parent_dir):
    dir_contents = InodeFileName.node_name_table[parent_dir]
    old_dir = (TYPE_DIR, dir_name)
    if old_dir in dir_contents:
        new_dir = (TYPE_DIR, new_dir_name)

        InodeFileName.node_name_table[parent_dir].remove(old_dir)
        InodeFileName.node_name_table[parent_dir].append(new_dir)

        old_dir_content = InodeFileName.node_name_table[parent_dir + dir_name + '/']
        InodeFileName.node_name_table.pop(parent_dir + dir_name + '/')
        InodeFileName.node_name_table[parent_dir + new_dir_name + '/'] = old_dir_content.copy()
        return 1
    return -1


def goto_parent_dir():
    parent_dir = '/'
    pwd = InodeFileName.pwd_name
    if pwd != '/':
        for i in range(-2, -len(pwd)):
            if pwd[i] == '/':
                parent_dir = pwd[:i + len(pwd) + 1]
        InodeFileName.pwd_name = parent_dir
    return parent_dir


def cat_file(file_name: str, dir_name) -> list:
    node_no = InodeFileName.get_node_no(file_name, dir_name)
    block_list = []
    if node_no != -1:
        inode = Inode.get_inode(node_no)
        block_list = inode.block_allocation
    return block_list


def pwd_contents(dir_name):
    dir_contents = InodeFileName.node_name_table[dir_name]
    dir_dict = {}
    for item in dir_contents:
        dir_dict[item[1]] = item[0]
    return dir_dict


def get_file_map(file_name: str, dir_name) -> list:
    node_no = InodeFileName.get_node_no(file_name, dir_name)
    map_list = []
    if node_no != -1:
        inode = Inode.get_inode(node_no)
        map_list = inode.block_allocation
    return map_list


# noinspection DuplicatedCode
def deal_message(message):
    ret_message = []
    if message[0] == HEAD_REQ:  # REQ
        ret_message.append(HEAD_RES)  # RES
        if message[1] == HEAD_UI and message[2] == HEAD_FS:  # UI -> FILESYSTEM
            ret_message.append(HEAD_FS)  # FILESYSTEM
            ret_message.append(HEAD_UI)  # UI
            if message[3] == 'PWD':  # PWD
                ret_message.append('PWD')  # PWD
                pwd_str = InodeFileName.pwd_name
                ret_message.append(pwd_str)  # pwd_str
            elif message[3] == 'LS':  # LS
                ret_message.append('LS')  # LS
                pwd_str = InodeFileName.pwd_name
                ret_message.append(pwd_str)
                content_dict = pwd_contents(pwd_str)
                ret_message.append(content_dict)
            elif message[3] == 'CAT':
                ret_message.append('CAT')  # CAT
                file_name = message[4]
                # file_name and file_content
                ret_message.append(file_name)  # file_name
                block_list = cat_file(file_name, InodeFileName.pwd_name)
                ret_message = send_load_message('COMMON', file_name, -1, -2, 0, block_list)
            elif message[3] == 'MAP':
                ret_message.append('MAP')  # MAp¬
                file_name = message[4]
                # file_name and map_list
                map_list = get_file_map(file_name, InodeFileName.pwd_name)
                ret_message.append(file_name)
                ret_message.append(map_list)
            elif message[3] == 'CREATE_FILE':
                ret_message.append('CREATE_FILE')
                file_type = message[4]
                file_name = message[5]
                ret_message.append(file_name)  # file_name
                res = create_file(file_type, file_name, InodeFileName.pwd_name)  # create_res
                if res != -1:
                    ret_message.append('succeed')
                else:
                    ret_message.append('fail')
            elif message[3] == 'DEL_FILE':
                ret_message.append('DEL_FILE')
                file_name = message[4]
                ret_message.append(file_name)  # file_name
                res = del_file(file_name, InodeFileName.pwd_name)
                if res != -1:
                    ret_message.append('succeed')  # del_res
                else:
                    ret_message.append('fail')  # del_res
            elif message[3] == 'CHANGE_FILE_NAME':
                ret_message.append('CHANGE_FILE_NAME')
                file_name = message[4]
                ret_message.append(file_name)  # filename
                new_file_name = message[5]
                res = change_file_name(file_name, new_file_name, InodeFileName.pwd_name)
                if res != -1:
                    ret_message.append('succeed')  # change_res
                else:
                    ret_message.append('fail')  # change_res
            elif message[3] == 'CREATE_DIR':
                ret_message.append('CREATE_DIR')
                dir_name = message[4]
                ret_message.append(dir_name)
                res = create_dir(dir_name, InodeFileName.pwd_name)
                if res != -1:
                    ret_message.append('succeed')
                else:
                    ret_message.append('fail')
            elif message[3] == 'DEL_DIR':
                ret_message.append('DEL_DIR')
                dir_name = message[4]
                res = del_dir(dir_name, InodeFileName.pwd_name)
                if res != -1:
                    ret_message.append('succeed')
                else:
                    ret_message.append('fail')
            elif message[3] == 'CHANGE_DIR':
                ret_message.append('CHANGE_DIR')
                dir_name = message[4]
                res = change_dir(dir_name, InodeFileName.pwd_name)
                if res != -1:
                    ret_message.append('succeed')
                else:
                    ret_message.append('fail')
            elif message[3] == 'PARENT_DIR':
                ret_message.append('PARENT_DIR')
                parent_dir = goto_parent_dir()
                ret_message.append(parent_dir)
                ret_message.append('succeed')
            elif message[3] == 'CHANGE_DIR_NAME':
                ret_message.append('CHANGE_DIR_NAME')
                dir_name = message[4]
                ret_message.append(dir_name)
                new_dir_name = message[5]
                res = change_dir_name(dir_name, new_dir_name, InodeFileName.pwd_name)
                if res != -1:
                    ret_message.append('succeed')
                else:
                    ret_message.append('fail')
            elif message[3] == 'WRITE_FILE':
                file_name = message[4]
                size = message[5]
                contents = message[6]
                pid = message[7]
                using_time = message[8]
                write_type = ''
                # block_list = []
                block_contents_dict = {}
                node_no = InodeFileName.get_node_no(file_name, InodeFileName.pwd_name)
                if node_no != -1:
                    inode = Inode.get_inode(node_no)
                    if inode.file_size == 0:
                        write_type = 'cover'
                    else:
                        write_type = 'add'
                    block_contents_dict = store_file(file_name, InodeFileName.pwd_name, buffer=contents,
                                                     block_size=size)
                ret_message = send_write_message(file_name, pid, using_time, write_type, block_contents_dict)
        elif message[1] == HEAD_KERNEL and message[2] == HEAD_FS:
            if message[3] == 'LOAD_FILE':
                load_type = message[4]
                file_name = message[5]
                ui_pid = message[6]
                pid = message[7]
                using_time = message[8]
                block_list = []
                node_no = InodeFileName.get_node_no(file_name, InodeFileName.pwd_name)
                if node_no != -1:
                    inode = Inode.get_inode(node_no)
                    if not (load_type == 'EXEC' and inode.file_type == 'COMMON'):
                        block_list = read_file(file_name, InodeFileName.pwd_name)
                ret_message = send_load_message(load_type, file_name, ui_pid, pid, using_time, block_list)
            elif message[3] == 'WRITE_FILE':
                file_name = message[4]
                size = message[5]
                contents = message[6]
                pid = message[7]
                using_time = message[8]
                write_type = ''
                # block_list = []
                block_contents_dict = {}
                node_no = InodeFileName.get_node_no(file_name, InodeFileName.pwd_name)
                if node_no != -1:
                    inode = Inode.get_inode(node_no)
                    if inode.file_size == 0:
                        write_type = 'cover'
                    else:
                        write_type = 'add'
                    block_contents_dict = store_file(file_name, InodeFileName.pwd_name, buffer=contents,
                                                     block_size=size)
                ret_message = send_write_message(file_name, pid, using_time, write_type, block_contents_dict)
            elif message[3] == 'SHUTDOWN':
                store_before_end()
                ret_message = [HEAD_RES, HEAD_FS, HEAD_KERNEL, 'SHUTDOWN', 'succeed']
    return ret_message


def send_load_message(type_str, file_name, ui_pid, pid, read_time, block_list):
    message = [HEAD_REQ, HEAD_FS, HEAD_MEMORY, 'LOAD', type_str, file_name, ui_pid, pid, read_time, block_list]
    return message


def send_write_message(file_name, pid, write_time, write_type, block_contents_dict):
    message = [HEAD_REQ, HEAD_FS, HEAD_MEMORY, 'WRITE', file_name, pid, write_time, write_type, block_contents_dict]
    return message


def init_before_start(node_name_table_file='node_name_table.json', node_table_file='node_table.json'):
    with open(node_name_table_file, 'r', encoding='utf-8') as f:
        node_name_dict = json.load(f)
    max_node_no = 2
    for dir_name, contents in node_name_dict.items():
        for content in contents:
            if len(content) == 3 and content[2] > max_node_no:
                max_node_no = content[2]
            InodeFileName.node_name_table[dir_name].append(tuple(content))
    InodeFileName.starting_node_no = max_node_no

    with open(node_table_file, 'r', encoding='utf-8') as f:
        node_table_dict = json.load(f)
        for k, v in node_table_dict.items():
            node_no = int(k)
            file_size = int(v[0])
            file_type = v[1]
            block_allocation = v[2]
            Inode.node_table[node_no] = Inode(file_type, file_size, block_allocation)
        # for k, v in Inode.node_table.items():
        #     print(str(k) + ':(' + str(v.file_size) + ',' + str(v.file_type) + ',' + str(v.block_allocation) + ')')


def store_before_end(node_name_table_file='node_name_table.json', node_table_file='node_table.json'):
    with open(node_name_table_file, 'w+', encoding='utf-8') as f:
        json.dump(InodeFileName.node_name_table, f)
    with open(node_table_file, 'w+', encoding='utf-8') as f:
        node_table_dict = {}
        for k, v in Inode.node_table.items():
            node_table_dict[k] = (v.file_size, v.file_type, v.block_allocation)
        json.dump(node_table_dict, f)


def start_fs(kernel2fs, fs2kernel):
    init_before_start()
    while True:
        while not kernel2fs.empty():
            message = kernel2fs.get()
            ret_message = deal_message(message)
            print(InodeFileName.node_name_table)
            # print(InodeFileName.pwd_name)
            # for k, v in Inode.node_table.items():
            #     print(str(k) + ':(' + str(v.file_size) + ',' + str(v.file_type) + ',' + str(v.block_allocation) + ')')
            # print()
            fs2kernel.put(ret_message)