from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal,QThread
from OS_gui import Ui_MainWindow
from cat_shower import cat_shower
from PyQt5.QtGui import QColor,QBrush
import sys

class catch(QThread):
    got_one = pyqtSignal(list)

    def __init__(self,recv_Q):
        super(catch, self).__init__()
        self.recv_Q = recv_Q

    def run(self):
        temp = self.recv_Q.get()
        self.got_one.emit(temp)


class gui(QMainWindow,Ui_MainWindow):
    message = ["REQ","UI"]
    fill = "-"
    colors = [QColor(234,234,234),QColor(235,158,235),QColor(245,126,126),QColor(170,235,158),QColor(158,211,235),
              QColor(158,235,232),QColor(235,208,158),QColor(255,241,132),QColor(235,158,176),QColor(202,158,235),
              QColor(158,176,235)]
    process_state = ['null','ready','waiting','running']
    process_map = {}
    process_max = 10
    process_rem = 20
    uipid = 1

    file_cols = 10
    file_rows = 10
    file_size = 64

    ram_cols = 32
    ram_rows = 16
    ram_index = [[0]*(ram_cols * ram_rows)]

    device_map = {'disc':0,'K':1, 'P':2}
    def __init__(self,recv_Q,send_Q,time_Q):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        self.time_Q = time_Q
        self.recv_Q = recv_Q
        self.send_Q = send_Q
        self.listen_thread = catch(recv_Q)


        self.process_graph.setRowCount(10)
        self.process_graph.setColumnCount(self.process_rem)
        self.process_graph.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_graph.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.file_graph.setRowCount(self.file_rows)
        self.file_graph.setColumnCount(self.file_cols)
        self.file_graph.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_graph.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_shot.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ram_graph.setRowCount(self.ram_rows)
        self.ram_graph.setColumnCount(self.ram_cols)
        self.ram_graph.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ram_graph.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.device_shot.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_shot.setRowCount(3)

        self.process_graph.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for k in self.device_map.keys():
            self.device_shot.setItem(self.device_map[k],0,QTableWidgetItem(k))
            self.device_shot.setItem(self.device_map[k],1,QTableWidgetItem("WAIT"))
            self.device_shot.setItem(self.device_map[k],2,QTableWidgetItem("WAIT"))

        self.run.clicked.connect(self.run_file)
        self.file_rename.clicked.connect(self.file_rename_req)
        self.file_write.clicked.connect(self.file_write_req)
        self.file_mkdir.clicked.connect(self.file_mkdir_req)
        self.file_vi.clicked.connect(self.file_vi_req)
        self.file_fresh.clicked.connect(self.file_ls_req)
        self.file_del.clicked.connect(self.file_del_req)
        self.file_shot.doubleClicked.connect(self.file_cat)

        #self.ram_graph.clicked.connect

        self.device_add.clicked.connect(self.device_add_req)
        self.device_del.clicked.connect(self.device_del_req)

        self.listen_thread.got_one.connect(self.listen)



    def send_message(self,message):
        print("SEND - UI ->" , message)
        self.send_Q.put(self.message + message)

    def listen(self,message):
        print("RECV - " , message)
        if message[3] == 'PROCESSSTATE':
            self.process_fresh(message)
        elif message[3] == 'MEMORY_SNAPSHOT':
            self.ram_fresh(message)
        elif message[3] == 'CREATE_PROCESS':
            self.process_create(message)
        elif message[3] == 'PWD':
            self.file_pwd_res(message)
        elif message[3] == 'LS':
            self.file_ls_res(message)
        elif message[3] == 'CAT':
            self.file_cat_res(message)
        elif message[3] == 'MAP':
            self.file_map_res(message)
        elif message[3] == 'CREATE_FILE':
            self.file_vi_res(message)
        elif message[3] == 'DEL_FILE' or message[3] == 'DEL_DIR':
            self.file_del_res(message)
        elif message[3] == 'CHANGE_FILE_NAME' or message[3] == 'CHANGE_DIR_NAME':
            self.file_rename_res(message)
        elif message[3] == 'CREATE_DIR':
            self.file_mkdir_res(message)
        elif message[3] == 'PARENT_DIR':
            self.file_par_res(message)
        elif message[3] == 'CHANGE_DIR':
            self.file_cd_res(message)
        elif message[3] == 'WRITE':
            self.file_write_res(message)
        elif message[3] == 'DISK_STATE':
            self.device_disc(message)
        elif message[3] == 'DEVICE_UPDATE':
            self.device_update(message)
        elif message[3] == 'DEVICE_FINISH':
            self.device_fin(message)
        elif message[3] == 'ADD_DEVICE':
            self.device_add_res(message)
        elif message[3] == 'DELETE_DEVICE':
            self.device_del_res(message)
        else:
            print("*********CAN NOT DO IT********")
        self.listen_thread.start()

    '''
    def listen(self):
        while True:
            message = self.recv_Q.get()
            print("RECV - " , message)
            if message[3] == 'PROCESSSTATE':
                self.process_fresh(message)
            elif message[3] == 'MEMORY_SNAPSHOT':
                self.ram_fresh(message)
            elif message[3] == 'CREATE_PROCESS':
                self.process_create(message)
            elif message[3] == 'PWD':
                self.file_pwd_res(message)
            elif message[3] == 'LS':
                self.file_ls_res(message)
            elif message[3] == 'CAT':
                self.file_cat_res(message)
            elif message[3] == 'MAP':
                self.file_map_res(message)
            elif message[3] == 'CREATE_FILE':
                self.file_vi_res(message)
            elif message[3] == 'DEL_FILE' or message[3] == 'DEL_DIR':
                self.file_del_res(message)
            elif message[3] == 'CHANGE_FILE_NAME' or message[3] == 'CHANGE_DIR_NAME':
                self.file_rename_res(message)
            elif message[3] == 'CREATE_DIR':
                self.file_mkdir_res(message)
            elif message[3] == 'PARENT_DIR':
                self.file_par_res(message)
            elif message[3] == 'CHANGE_DIR':
                self.file_cd_res(message)
            elif message[3] == 'DISK_STATE':
                self.device_disc(message)
            elif message[3] == 'DEVICE_UPDATE':
                self.device_update(message)
            elif message[3] == 'DEVICE_FINISH':
                self.device_fin(message)
            elif message[3] == 'ADD_DEVICE':
                self.device_add_res(message)
            elif message[3] == 'DELETE_DEVICE':
                self.device_del_res(message)
            else:
                print("*********CAN NOT DO IT********")
    '''

    def run_file(self):
        try:
            name = self.file_shot.selectedItems()[0].text
            type = self.file_shot.selectedItems()[1].text
            if type != 'FILE':
                return
            self.process_map[uipid] = name
            self.send_message(['KERNEL','RUN_FILE',self.uipid])
            self.uipid += 1
        except:
            return

    def process_fresh(self,message):
        self.process_ship()
        row = 0
        for i in [4,5,6]:
            info = message[i]
            keys = info.keys()
            for k in keys:
                self.process_shot.setItem(row,0,QTableWidgetItem(self.process_map.get(k)))
                self.process_shot.setItem(row,1,QTableWidgetItem(str(info[k][1])))
                self.process_shot.setItem(row,2,QTableWidgetItem(str(k)))
                self.process_shot.setItem(row,3,QTableWidgetItem(str(self.process_state[i-3])))
                state = QTableWidgetItem ( self.fill )
                state.setBackground(QBrush(self.colors[i-3]))
                self.process_graph.setItem(k-1, self.process_rem-1, state)
                row += 1

    def process_create(self,message):
        if message[4] == 'SUCCESS':
            pid = message[5]
            uipid = message[6]
            name = self.process_map[uipid]
            del self.process_map[uipid]
            self.process_map[pid] = name
        else:
            del self.process_map[message[6]]

    def process_ship(self):
        col = 1
        while col < self.process_rem:
            for i in range(self.process_max):
                temp = self.process_graph.item(i,col)
                self.process_graph.setItem(i,col-1,temp)
            col += 1

    def file_pwd_req(self):
        self.send_message(['FILESYSTEM','PWD'])

    def file_pwd_res(self,message):
        pwd = message[4]
        self.file_pwd.setText(pwd)

    def file_ls_req(self):
        self.send_message(['FILESYSTEM','LS'])

    def file_ls_res(self,message):
        ls = message[5]
        pwd = message[4]
        count = len(ls)
        self.file_pwd.setText(pwd)
        self.file_shot.setRowCount(count + 1)
        for k in ls.keys():
            self.file_shot.setItem(count,0,QTableWidgetItem(k))
            self.file_shot.setItem(count,1,QTableWidgetItem(ls[k]))
            count -= 1
        self.file_shot.setItem(0,0,QTableWidgetItem(".."))
        self.file_shot.setItem(0,0,QTableWidgetItem("DIR"))

    def file_cat(self):
        try:
            filename = self.file_shot.selectedItems()[0].text()
            type = self.file_shot.selectedItems()[1].text()
            if filename == '..':
                self.send_message(['FILESYSTEM','PARENT_DIR'])
            elif type == 'FILE':
                self.send_message(['FILESYSTEM','CAT',filename])
            else:
                self.send_message(['FILESYSTEM','CHANGE_DIR',filename])
        except:
            return

    def file_cat_res(self,message):
        name = message[4]
        text = message[5]
        cat = cat_shower(name,text)

    def file_par_res(self,message):
        name = message[4]
        ret = message[5]
        if ret == 'succeed':
            self.file_shot.clearContents()
            self.file_ls_req()
        else:
            QMessageBox.about(self,"返回上级",'返回失败')

    def file_cd_res(self,message):
        def file_del_res(self, message):
            name = message[4]
            ret = message[5]
            if ret == 'succeed':
                self.file_shot.clearContents ()
                self.file_ls_req ()
            else:
                QMessageBox.about ( self, "切换目录", '切换' + name + '失败' )

    def file_map_req(self):
        try:
            filename = self.file_shot.selectedItems()[0].text()
            if filename == '..':
                return
            self.send_message(['FILESYSTEM','CAT',filename])
        except:
            return

    def file_map_res(self,message):
        name = message[4]
        mp = message[5]
        self.file_graph.clearContents()
        for i in mp:
            filler = QTableWidgetItem ( self.fill )
            filler.setBackground(QBrush(self.colors[4]))
            filler.setText(str(i))
            self.file_graph.setItem(i / self.file_cols, i % self.file_cols, filler)

    def file_vi_req(self):
        name = self.file_line.text()
        type = 'common'
        self.send_message(['FILESYSTEM','CREATE_FILE',type, name])

    def file_vi_res(self,message):
        ret = message[5]
        name = message[4]
        rows = self.file_shot.rowCount()
        if ret == 'succeed':
            self.file_shot.setRowCount(rows + 1)
            self.file_shot.setItem(rows,0,QTableWidgetItem(name))
            self.file_shot.setItem(rows,1,QTableWidgetItem('FILE'))
        else:
            QMessageBox.about(self,"创建文件",'创建'+ name + '失败')

    def file_del_req(self):
        try:
            name = self.file_shot.selectedItems()[0].text()
            if name == '..':
                QMessageBox.about(self,"异常操作",'不可操作上级目录')
                return
            type = self.file_shot.selectedItems()[1].text()
            if type == 'FILE':
                self.send_message(['FILESYSTEM','DEL_FILE',name])
            else:
                self.send_message(['FILESYSTEM','DEL_DIR',name])
        except:
            return


    def file_del_res(self,message):
        name = message[4]
        ret = message[5]
        if ret == 'succeed':
            self.file_shot.clearContents()
            self.file_ls_req()
        else:
            QMessageBox.about(self,"删除",'删除'+ name + '失败')

    def file_rename_req(self):
        try:
            filename = self.file_shot.selectedItems()[0].text()
            if filename == '..':
                QMessageBox.about(self,"异常操作",'不可操作上级目录')
                return
            type = self.file_shot.selectedItems()[1].text()
            name = self.file_line.text()
            if type == 'FILE':
                self.send_message(['FILESYSTEM','CHANGE_FILE_NAME',filename,name])
            else:
                self.send_message(['FILESYSTEM','CHANGE_DIR_NAME',filename,name])
        except:
            return

    def file_rename_res(self,message):
        name  = message[4]
        ret = message[5]
        if ret  == 'succeed':
            self.file_shot.clearContents()
            self.file_ls_req()
        else:
            QMessageBox.about(self,"重命名",'重命名'+ name + '失败')

    def file_mkdir_req(self):
        name = self.file_line.text()
        self.send_message(['FILESYSTEM','CREATE_DIR',name])

    def file_mkdir_res(self,message):
        ret = message[5]
        name = message[4]
        rows = self.file_shot.rowCount ()
        if ret == 'succeed':
            self.file_shot.setRowCount ( rows + 1 )
            self.file_shot.setItem ( rows, 0, QTableWidgetItem ( name ) )
            self.file_shot.setItem ( rows, 1, QTableWidgetItem ( 'DIR' ) )
        else:
            QMessageBox.about ( self, "创建目录", '创建' + name + '失败' )

    def file_write_req(self):
        try:
            filename = self.file_shot.selectedItems ()[0].text ()
            if filename == '..':
                QMessageBox.about ( self, "异常操作", '不可操作上级目录' )
                return

            type = self.file_shot.selectedItems ()[1].text()
            if type == 'DIR':
                QMessageBox.about ( self, "异常操作", '不可向目录写入')
                return

            size = self.file_line.text()
            try:
                size = int(size)
            except:
                self.file_line.setText("请输入写入的块数")
                return
            self.send_message(['FILESYSTEM','WRITE_FILE',size,"",-1,0])
        except:
            return

    def file_write_res(self,message):
        name  = message[4]
        ret = message[5]
        if ret  == 'SUCCESS':
            QMessageBox.about ( self, "文件写入", '已经写入到' + name )
            self.file_map_req()
        else:
            QMessageBox.about ( self, "文件写入", '写入失败：' + name )

    def ram_fresh(self,message):
        memory = message[4]
        index = [[0] * (self.ram_rows * self.ram_cols)]
        keys = memory.keys()
        for k in keys:
            temp = memory[k]
            for t in temp:
                index[t] = k
        if index != self.ram_index:
            self.ram_index = index

    def ram_show(self):
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



    def device_add_req(self):
        name = self.device_line.text()
        self.send_message(['DEVICE', 'ADD_DEVICE', name])

    def device_del_req(self):
        try:
            name = self.device_shot.selectedItems()[0].text()
            self.send_message(['DEVICE', 'DELETE_DEVICE',name])

        except:
            return

    def device_del_res(self,message):
        rows = self.device_shot.rowCount() - 1
        ret = message[4]
        dev = message[5]
        if ret == "SUCC":
            key = dev
            dev = self.device_map[dev]
            del self.device_map[key]
            while rows > dev:
                key = self.device_shot.item(rows, 0).text()
                self.device_map[key] -= 1
                for i in range(3):
                    self.device_shot.setItem(rows - 1, i, self.device_shot.item(rows,i))
                rows -= 1
        else:
            QMessageBox.about ( self, "删除设备", dev + '删除失败' )

    def device_add_res(self,message):
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




    def device_disc(self,message):
        self.device_shot.setItem(0,1,QTableWidgetItem(str(message[4])))

    def device_update(self,message):
        flag = message[4]
        dev = message[5]
        devices = self.device_shot.rowCount()
        filler = QTableWidgetItem("WAIT")
        if flag == 'RUN':
            '''
            for i in range ( 1, devices ):
                self.device_shot.setItem ( i, 1, filler )
                self.device_shot.setItem( i,2,filler)
            '''
            self.device_shot.setItem(self.device_map[dev],1,QTableWidgetItem('RUN'))
        elif flag == "INTTERUPT":
            self.device_shot.setItem(self.device_map[dev],1,filler)
            self.device_shot.setItem(self.device_map[dev],2,QTableWidgetItem('中断'))
        elif flag == 'RECOVER':
            self.device_shot.setItem(self.device_map[dev],1,QTableWidgetItem('RUN'))
            self.device_shot.setItem(self.device_map[dev],2,filler)

    def device_fin(self,message):
        dev = message[4]
        self.device_shot.setItem(self.device_map[dev],1,QTableWidgetItem("WAIT"))


def OS_GUI(Ker2GUI,GUI2Ker,TimeQ):
    app = QApplication(sys.argv)
    a = gui(Ker2GUI,GUI2Ker,TimeQ)
    a.show()
    a.listen_thread.start()
    app.exec()

