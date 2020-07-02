"""
GUI部分入口，启动函数见末尾
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal,QThread
from OS_gui import Ui_MainWindow
from cat_shower import cat_shower
from PyQt5.QtGui import QColor,QBrush
import sys

#队列监听线程
class catch(QThread):
    got_one = pyqtSignal(list)

    def __init__(self,recv_Q):
        super(catch, self).__init__()
        self.recv_Q = recv_Q

    def run(self):
        #阻塞等待
        temp = self.recv_Q.get()
        self.got_one.emit(temp)

#主线程，UI控制线程
class gui(QMainWindow,Ui_MainWindow):
    message = ["REQ","UI"]
    fill = "-"
    colors = [QColor(234,234,234),QColor(235,158,235),QColor(245,126,126),QColor(170,235,158),QColor(158,211,235),
              QColor(158,235,232),QColor(235,208,158),QColor(255,241,132),QColor(235,158,176),QColor(202,158,235),
              QColor(158,176,235)]
    process_state = ['null','ready','waiting','running']
    process_map = {} #pid和文件名称的对应关系
    process_max = 10
    process_rem = 20
    uipid = 1

    file_cols = 10
    file_rows = 10
    file_size = 64

    ram_cols = 32
    ram_rows = 16
    ram_index = [[0]*(ram_cols * ram_rows)] #内存使用情况的位图

    device_map = {'disc':0,'K':1, 'P':2} #设备名称和设备编号的对应关系
    def __init__(self,recv_Q,send_Q,time_Q):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        #通信相关初始化
        self.time_Q = time_Q
        self.recv_Q = recv_Q
        self.send_Q = send_Q
        self.listen_thread = catch(recv_Q) #监听线程

        #进程模块相关格式设置
        self.process_graph.setRowCount(10)
        self.process_graph.setColumnCount(self.process_rem)
        self.process_graph.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_graph.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #文件相关格式设置
        self.file_graph.setRowCount(self.file_rows)
        self.file_graph.setColumnCount(self.file_cols)
        self.file_graph.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_graph.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_shot.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #内存相关格式设置
        self.ram_graph.setRowCount(self.ram_rows)
        self.ram_graph.setColumnCount(self.ram_cols)
        self.ram_graph.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ram_graph.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #设备相关格式设置
        self.device_shot.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_shot.setRowCount(3)
        for k in self.device_map.keys():
            self.device_shot.setItem(self.device_map[k],0,QTableWidgetItem(k))
            self.device_shot.setItem(self.device_map[k],1,QTableWidgetItem("WAIT"))
            self.device_shot.setItem(self.device_map[k],2,QTableWidgetItem("WAIT"))

        #操作连接
        self.run.clicked.connect(self.run_file) #单击运行
        self.file_rename.clicked.connect(self.file_rename_req) #单击重命名
        self.file_write.clicked.connect(self.file_write_req) #单击写入
        self.file_mkdir.clicked.connect(self.file_mkdir_req) #单击新建目录
        self.file_vi.clicked.connect(self.file_vi_req) #单击新建文件
        self.file_fresh.clicked.connect(self.file_ls_req) #单击刷新
        self.file_del.clicked.connect(self.file_del_req) #单击删除
        self.file_shot.doubleClicked.connect(self.file_cat) #双击文件

        #self.ram_graph.clicked.connect

        self.device_add.clicked.connect(self.device_add_req) #单击插入设备
        self.device_del.clicked.connect(self.device_del_req) #单击弹出设备

        self.listen_thread.got_one.connect(self.listen) #监听线程收到信息



    def send_message(self,message): #发信息，前缀已经指定
        print("SEND - UI ->" , message)
        self.send_Q.put(self.message + message)

    def listen(self,message):   #信息分发
        print("RECV - " , message)
        if message[3] == 'PROCESSSTATE':#进程快照
            self.process_fresh(message)
        elif message[3] == 'MEMORY_SNAPSHOT':#内存快照
            self.ram_fresh(message)
        elif message[3] == 'CREATE_PROCESS':#进程创建成功，构建pid和文件名的索引
            self.process_create(message)
        elif message[3] == 'RUN_FILE':#执行文件结果反馈
            self.run_file_res(message)
        elif message[3] == 'PWD':#获取当前目录
            self.file_pwd_res(message)
        elif message[3] == 'LS':#获取当前目录下的内容
            self.file_ls_res(message)
        elif message[3] == 'CAT':#打开文件
            self.file_cat_res(message)
        elif message[3] == 'MAP':#文件的外存映射
            self.file_map_res(message)
        elif message[3] == 'CREATE_FILE':#新建文件反馈
            self.file_vi_res(message)
        elif message[3] == 'DEL_FILE' or message[3] == 'DEL_DIR':#删除反馈
            self.file_del_res(message)
        elif message[3] == 'CHANGE_FILE_NAME' or message[3] == 'CHANGE_DIR_NAME':#重命名反馈
            self.file_rename_res(message)
        elif message[3] == 'CREATE_DIR':#创建目录反馈
            self.file_mkdir_res(message)
        elif message[3] == 'PARENT_DIR':#返回上一级目录反馈
            self.file_par_res(message)
        elif message[3] == 'CHANGE_DIR':#进入下一级目录反馈
            self.file_cd_res(message)
        elif message[3] == 'WRITE':#写文件反馈
            self.file_write_res(message)
        elif message[3] == 'DISK_STATE':#硬盘状态更新
            self.device_disc(message)
        elif message[3] == 'DEVICE_UPDATE':#其它设备快照
            self.device_update(message)
        elif message[3] == 'DEVICE_FINISH':#其它设备释放
            self.device_fin(message)
        elif message[3] == 'ADD_DEVICE':#添加设备反馈
            self.device_add_res(message)
        elif message[3] == 'DELETE_DEVICE':#弹出设备反馈
            self.device_del_res(message)
        else:
            print("*********CAN NOT DO IT********")
        self.listen_thread.start() #开始接受新的信息


    def run_file(self): #执行文件
        try:
            name = self.file_shot.selectedItems()[0].text
            type = self.file_shot.selectedItems()[1].text
            if type != 'FILE':#如果选择了目录，无操作
                return
            self.process_map[uipid] = name #建立临时索引
            self.send_message(['KERNEL','RUN_FILE',self.uipid])
            self.uipid += 1
        except: #如果没有选择文件，则无操作
            return

    def run_file_res(self,message): #执行文件失败反馈
        name = message[4]
        uipid = message[5]
        res = message[6]
        if res == "FAIL":
            del self.process_map[uipid]
            QMessageBox.about ( self, "执行", '打开' + name + '时失败' )


    def process_fresh(self,message): #进程快照
        self.process_ship()
        row = 0
        for i in [4,5,6]:
            info = message[i]
            keys = info.keys()
            for k in keys:
                #更新快照
                self.process_shot.setItem(row,0,QTableWidgetItem(self.process_map.get(k)))
                self.process_shot.setItem(row,1,QTableWidgetItem(str(info[k][1])))
                self.process_shot.setItem(row,2,QTableWidgetItem(str(k)))
                self.process_shot.setItem(row,3,QTableWidgetItem(str(self.process_state[i-3])))
                #更新时序图
                state = QTableWidgetItem ( self.fill )
                state.setBackground(QBrush(self.colors[i-3]))
                self.process_graph.setItem(k-1, self.process_rem-1, state)
                row += 1

    def process_create(self,message): #创建进程反馈
        if message[4] == 'SUCCESS':
            pid = message[5]
            uipid = message[6]
            #解除临时索引，建立永久索引
            name = self.process_map[uipid]
            del self.process_map[uipid]
            self.process_map[pid] = name
        else:#进程创建失败，删除临时索引
            del self.process_map[message[6]]

    def process_ship(self): #将时序图后移
        col = 1
        while col < self.process_rem:
            for i in range(self.process_max):
                temp = self.process_graph.item(i,col)
                self.process_graph.setItem(i,col-1,temp)
            col += 1

    def file_pwd_req(self): #请求当前工作目录
        self.send_message(['FILESYSTEM','PWD'])

    def file_pwd_res(self,message): #当前目录反馈
        pwd = message[4]
        self.file_pwd.setText(pwd)

    def file_ls_req(self): #请求当前目录内容
        self.send_message(['FILESYSTEM','LS'])

    def file_ls_res(self,message): #目录内容反馈
        ls = message[5]
        pwd = message[4]
        count = len(ls)
        self.file_pwd.setText(pwd)
        self.file_shot.setRowCount(count + 1)
        for k in ls.keys():
            self.file_shot.setItem(count,0,QTableWidgetItem(k))
            self.file_shot.setItem(count,1,QTableWidgetItem(ls[k]))
            count -= 1
        #首行为上级目录
        self.file_shot.setItem(0,0,QTableWidgetItem(".."))
        self.file_shot.setItem(0,0,QTableWidgetItem("DIR"))

    def file_cat(self): #双击文件
        try:
            filename = self.file_shot.selectedItems()[0].text()
            type = self.file_shot.selectedItems()[1].text()
            if filename == '..': #返回上级目录
                self.send_message(['FILESYSTEM','PARENT_DIR'])
            elif type == 'FILE': #读取文件内容
                self.send_message(['FILESYSTEM','CAT',filename])
            else:#进入下级目录
                self.send_message(['FILESYSTEM','CHANGE_DIR',filename])
        except: #未选择文件，不操作
            return

    def file_cat_res(self,message): #读取文件内容反馈
        name = message[4]
        text = message[5]
        cat = cat_shower(name,text)

    def file_par_res(self,message): #返回上级目录反馈
        name = message[4]
        ret = message[5]
        if ret == 'succeed':
            self.file_shot.clearContents()
            self.file_ls_req()
        else:
            QMessageBox.about(self,"返回上级",'返回失败')

    def file_cd_res(self,message): #进入下级目录反馈
        name = message[4]
        ret = message[5]
        if ret == 'succeed':
            self.file_shot.clearContents ()
            self.file_ls_req ()
        else:
            QMessageBox.about ( self, "切换目录", '切换' + name + '失败' )

    def file_map_req(self): #单击文件，请求文件映射
        try:
            filename = self.file_shot.selectedItems()[0].text()
            if filename == '..': #若选择上级目录，不操作
                return
            self.send_message(['FILESYSTEM','CAT',filename])
        except:#若未选择，不操作
            return

    def file_map_res(self,message):#文件映射反馈
        name = message[4]
        mp = message[5]
        self.file_graph.clearContents()
        for i in mp:
            filler = QTableWidgetItem ( self.fill )
            filler.setBackground(QBrush(self.colors[4]))
            filler.setText(str(i))
            self.file_graph.setItem(i / self.file_cols, i % self.file_cols, filler)

    def file_vi_req(self): #输入文件名，单击新建文件
        name = self.file_line.text()
        type = 'common'
        self.send_message(['FILESYSTEM','CREATE_FILE',type, name])

    def file_vi_res(self,message): #新建文件反馈
        ret = message[5]
        name = message[4]
        rows = self.file_shot.rowCount()
        if ret == 'succeed':
            self.file_shot.setRowCount(rows + 1)
            self.file_shot.setItem(rows,0,QTableWidgetItem(name))
            self.file_shot.setItem(rows,1,QTableWidgetItem('FILE'))
        else:
            QMessageBox.about(self,"创建文件",'创建'+ name + '失败')

    def file_del_req(self): #选择文件，单击删除
        try:
            name = self.file_shot.selectedItems()[0].text()
            if name == '..':
                QMessageBox.about(self,"异常操作",'不可操作上级目录')
                return
            type = self.file_shot.selectedItems()[1].text()
            if type == 'FILE':#删除文件
                self.send_message(['FILESYSTEM','DEL_FILE',name])
            else:#递归删除目录
                self.send_message(['FILESYSTEM','DEL_DIR',name])
        except:#未选择文件，不操作
            return


    def file_del_res(self,message): #删除反馈
        name = message[4]
        ret = message[5]
        if ret == 'succeed':
            self.file_shot.clearContents()
            self.file_ls_req()
        else:
            QMessageBox.about(self,"删除",'删除'+ name + '失败')

    def file_rename_req(self): #选择文件并输入新名称，单击重命名
        try:
            filename = self.file_shot.selectedItems()[0].text()
            if filename == '..':
                QMessageBox.about(self,"异常操作",'不可操作上级目录')
                return
            type = self.file_shot.selectedItems()[1].text()
            name = self.file_line.text()
            if type == 'FILE': #文件重命名
                self.send_message(['FILESYSTEM','CHANGE_FILE_NAME',filename,name])
            else: #目录重命名
                self.send_message(['FILESYSTEM','CHANGE_DIR_NAME',filename,name])
        except: #未选择文件，不操作
            return

    def file_rename_res(self,message): #重命名反馈
        name  = message[4]
        ret = message[5]
        if ret  == 'succeed':
            self.file_shot.clearContents()
            self.file_ls_req()
        else:
            QMessageBox.about(self,"重命名",'重命名'+ name + '失败')

    def file_mkdir_req(self): #输入名称，单击新建目录
        name = self.file_line.text()
        self.send_message(['FILESYSTEM','CREATE_DIR',name])

    def file_mkdir_res(self,message): #新建目录反馈
        ret = message[5]
        name = message[4]
        rows = self.file_shot.rowCount ()
        if ret == 'succeed':
            self.file_shot.setRowCount ( rows + 1 )
            self.file_shot.setItem ( rows, 0, QTableWidgetItem ( name ) )
            self.file_shot.setItem ( rows, 1, QTableWidgetItem ( 'DIR' ) )
        else:
            QMessageBox.about ( self, "创建目录", '创建' + name + '失败' )

    def file_write_req(self): #选择文件，输入写文件块数，单击写入
        try:
            #检测是否选中了有效文件
            filename = self.file_shot.selectedItems ()[0].text ()
            if filename == '..':
                QMessageBox.about ( self, "异常操作", '不可操作上级目录' )
                return

            type = self.file_shot.selectedItems ()[1].text()
            if type == 'DIR':
                QMessageBox.about ( self, "异常操作", '不可向目录写入')
                return

            size = self.file_line.text()
            try: #检测输入的是否是个整数
                size = int(size)
            except:
                self.file_line.setText("请输入写入的块数")
                return
            self.send_message(['FILESYSTEM','WRITE_FILE',size,"",-1,0])
        except:
            return

    def file_write_res(self,message): #写文件反馈
        name  = message[4]
        ret = message[5]
        if ret  == 'SUCCESS':
            QMessageBox.about ( self, "文件写入", '已经写入到' + name )
            self.file_map_req()
        else:
            QMessageBox.about ( self, "文件写入", '写入失败：' + name )

    def ram_fresh(self,message): #内存快照
        memory = message[4]
        index = [[0] * (self.ram_rows * self.ram_cols)] #临时位图
        keys = memory.keys()
        for k in keys:
            temp = memory[k]
            for t in temp:
                index[t] = k
        if index != self.ram_index:
            self.ram_index = index
            self.ram_show()

    def ram_show(self): #显示内存快照
        sum = 0
        used = 0
        for i in self.ram_index:
            sum += 1
            pid = str(i)
            state = QTableWidgetItem(self.fill)
            if i == 0:
                pid = self.fill
                used += 1
            state.setText(pid)
            state.setBackground(QBrush(self.colors[i]))
            self.ram_graph.setItem(sum / self.ram_cols, sum % self.ram_cols, state)
        self.ram_total.setText(str(sum))
        self.ram_used.setText(str(sum - used))



    def device_add_req(self): #输入设备名称，单击插入设备
        name = self.device_line.text()
        self.send_message(['DEVICE', 'ADD_DEVICE', name])

    def device_del_req(self): #选中设备，单击弹出设备
        try:
            name = self.device_shot.selectedItems()[0].text()
            self.send_message(['DEVICE', 'DELETE_DEVICE',name])

        except:
            return

    def device_del_res(self,message): #弹出设备反馈
        rows = self.device_shot.rowCount() - 1
        ret = message[4]
        dev = message[5]
        if ret == "SUCC":
            key = dev
            dev = self.device_map[dev]
            del self.device_map[key] #删除设备映射
            while rows > dev: #重整设备快照表
                key = self.device_shot.item(rows, 0).text()
                self.device_map[key] -= 1
                for i in range(3):
                    self.device_shot.setItem(rows - 1, i, self.device_shot.item(rows,i))
                rows -= 1
        else:
            QMessageBox.about ( self, "删除设备", dev + '删除失败' )

    def device_add_res(self,message): #插入
        rows = self.device_shot.rowCount()
        ret = message[4]
        dev = message[5]
        if ret == "SUCC":
            self.device_map[dev] = rows
            self.device_shot.setRowCount(rows + 1)
            self.device_shot.setItem(rows,0,dev)
            self.device_shot.setItem(rows,1,QTableWidgetItem("WAIT"))
            self.device_shot.setItem(rows,2,QTableWidgetItem("WAIT"))
        else:
            QMessageBox.about ( self, "添加设备", dev + '添加失败' )


    def device_disc(self,message): #磁盘状态更新
        self.device_shot.setItem(0,1,QTableWidgetItem(str(message[4])))

    def device_update(self,message): #设备快照更新
        flag = message[4]
        dev = message[5]
        devices = self.device_shot.rowCount()
        filler = QTableWidgetItem("WAIT")
        if flag == 'RUN': #设备运行
            '''
            for i in range ( 1, devices ):
                self.device_shot.setItem ( i, 1, filler )
                self.device_shot.setItem( i,2,filler)
            '''
            self.device_shot.setItem(self.device_map[dev],1,QTableWidgetItem('RUN'))
        elif flag == "INTTERUPT": #设备中断
            self.device_shot.setItem(self.device_map[dev],1,filler)
            self.device_shot.setItem(self.device_map[dev],2,QTableWidgetItem('中断'))
        elif flag == 'RECOVER': #设备恢复
            self.device_shot.setItem(self.device_map[dev],1,QTableWidgetItem('RUN'))
            self.device_shot.setItem(self.device_map[dev],2,filler)

    def device_fin(self,message): #设备释放
        dev = message[4]
        self.device_shot.setItem(self.device_map[dev],1,QTableWidgetItem("WAIT"))


def OS_GUI(Ker2GUI,GUI2Ker,TimeQ): #GUI进程入口
    app = QApplication(sys.argv)
    a = gui(Ker2GUI,GUI2Ker,TimeQ)
    a.show()
    a.listen_thread.start() #开始监听队列
    app.exec()

