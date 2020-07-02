
BLOCK_SIZE = 4
block_index = []


class Inode:
    __node_table = dict()  # node_no : inode

    def __init__(self, node_no):
        self.block_size = -1
        # inode type : file / directory
        # and should I consider how to change directory ?
        self.block_allocate = []
        self.allocate_blocks(1)

    # allocate blocks for a inode
    def allocate_blocks(self, block_num):
        # find 'block_num' blocks
        pass

    # find inode from node_no, then release all
    def release_blocks(self):
        pass


class Inode_FileName:
    __node_name_table = dict()  # node_no : name

    def __init__(self, file_name):
        self.file_name = file_name
        self.inode_no = hash(self.file_name)
        self.make_new_inode()
        Inode_FileName.__node_name_table[self.inode_no] = self.file_name

    def make_new_inode(self):
        inode = Inode(self.inode_no)
        Inode.__node_table[self.inode_no] = inode

    @staticmethod
    def get_inode(file_name: str):
        pass


def create_file(file_name: str) -> int:
    '''
    Interface: /used by system/
    Give a file name, use it to create a file.
    Return inode_no.
    '''
    inode_fname = Inode_FileName(file_name)
    return inode_fname.inode_no


def del_file(file_name: str) -> int:
    '''
    Interface: /used by system/
    Give a file name, use it to delete a file.
    Return status: 0 - succeed, -1 - fail, other - ...
    '''
    return 0


def read_file(file_name: str) -> int:
    '''
    Interface: /used by sytem/
    Give a file name, use it to load the file into memory.
    Return status: 0 - succeed, -1 - fail, other - ...
    '''
    return 0


def store_file(buffer, file_name: str) -> int:
    '''
    Interface: /used by system/
    Give a file name and a buffer, store the contents of buffer into the file.
    Return status: 0 - succeed, -1 - fail, other - ...
    '''
    # calculate blocks needed

    # release file blocks

    # reallocate blocks for file

    return 0


def change_file_name(file_name: str, new_file_name: str) -> int:
    '''
    Interface: /used by system/
    Give a file name and a new file name, change the file name.
    Return status: 0 - succeed, -1 - fail, other - ...
    '''
    #
    return 0
