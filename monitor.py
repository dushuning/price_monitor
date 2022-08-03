import sys
import os
import time
import simplejson
from utils.log import Log

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QBrush, QColor, QPixmap, QMovie
from PyQt5.QtCore import *

# 获取当前项目的绝对路径
from utils.scheduler import SCHEDULAR
log = Log('main')
logger = log.getLog()
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# 全局的状态隐射
STSTUS_MAPPING = {
    0: '初始化',
    1: '待执行',
    2: '正在执行',
    3: '完成并提醒',
    10: '异常并停止',
    11: '初始化失败'
}
RUNNING = 1
STOPPING = 2
STOP = 3
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
class MyWindow(QWidget):

    # 初始化构造方法
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("价格监控 V1.0")
        # icon = QIcon()
        # icon.addPixmap(QPixmap('utils/head.ico'))
        # self.setWindowIcon(icon)
        self.resize(1280, 500)
        # self.setMinimumSize(1220, 500)
        # self.setMaximumSize(1220, 500)
        # QIcon()
        # self.setWindowIcon()
        self.line_edit = None
        self.table_widget = None
        # 默认情况下，刚启动的项目是处于停止状态
        self.switch = STOP
        self.initUI()

    def initUI(self):
        # QMessageBox.
        # 首先创建一个全局的布局layout，这个布局是垂直布局的
        lay_out = QVBoxLayout()

        # 初始化水平头布局
        lay_out.addLayout(self.initHeaderLayOut())

        # 初始化文本布局
        lay_out.addLayout(self.initTxtLayOut())

        # 初始化表格布局
        lay_out.addLayout(self.initTbaleLayOut())

        # 初始化底端布局
        lay_out.addLayout(self.initFontLayout())

        # 添加弹簧
        # lay_out.addStretch()
        # 添加全局布局到这个窗口中
        self.setLayout(lay_out)

    def initHeaderLayOut(self):
        # 需要一个顶头布局
        header_layout = QHBoxLayout()
        start_button = QPushButton('开始')
        start_button.clicked.connect(self.start_buuton_fun)
        start_button.setStyleSheet('background-color: rgb(0,255,0)')

        stop_button = QPushButton('停止')
        stop_button.clicked.connect(self.stop_button_fun)
        stop_button.setStyleSheet('background-color: rgb(255,0,0)')

        header_layout.addWidget(start_button)
        header_layout.addWidget(stop_button)
        # 添加一个弹簧，把前面两个按钮压在左边
        header_layout.addStretch()
        return header_layout

    def initTxtLayOut(self):
        txt_layout = QHBoxLayout()
        line_edit = QLineEdit()
        self.line_edit = line_edit
        line_edit.setPlaceholderText('请输入需要监控的商品url')
        add_button = QPushButton('添加')
        add_button.clicked.connect(self.event_add_click)
        txt_layout.addWidget(line_edit)
        txt_layout.addWidget(add_button)
        return txt_layout

    def event_add_click(self):
        # 获取输入框中的数据
        text = self.line_edit.text()
        text = text.strip()
        if not text:
            QMessageBox.warning(self, '错误', '输入的商品型号有误！')
            return
        asin, price = text.split('=')
        price = float(price)
        # print(f'asin:{asin},price:{price}')
        # 将数据添加到表格中
        new_data_item = [asin, '', '', price, 0, 0, 0, 0]
        current_index = self.table_widget.rowCount()
        self.table_widget.insertRow(current_index)
        for i, item in enumerate(new_data_item):
            # 数字与状态值之间的转换
            item = STSTUS_MAPPING[item] if item in STSTUS_MAPPING and i == 6 else item
            cell = QTableWidgetItem(str(item))
            self.table_widget.setItem(current_index, i, cell)
            # 设置某个单元格是否可以被选中和编辑
            if i in [0, 4, 5, 6]:
                cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        # 根据输入框的数据去远程爬取数据
        from utils.mythreads import NewTaskThread
        task = NewTaskThread(current_index, asin, self)
        # # 假如线程内触发了该信号，则执行这个回调函数
        task.success.connect(self.init_task_success_callback)
        task.error.connect(self.init_task_error_callback)
        task.start()
        # 更新表格中的数据


    def initTbaleLayOut(self):
        table_layout = QHBoxLayout()
        table_widget = QTableWidget(0, 8)
        self.table_widget = table_widget
        # 在这里可以先添加一些表头
        table_header = [
            {"field": "asin", "text": "ASIN", 'width': 120},
            {"field": "title", "text": "标题", 'width': 150},
            {"field": "url", "text": "URL", 'width': 400},
            {"field": "price", "text": "底价（￥）", 'width': 105},
            {"field": "success", "text": "成功次数", 'width': 105},
            {"field": "error", "text": "503次数", 'width': 105},
            {"field": "status", "text": "状态", 'width': 105},
            {"field": "frequency", "text": "现价（￥）", 'width': 130}
        ]
        for index, item in enumerate(table_header):
            header = QTableWidgetItem()
            header.setText(item['text'])
            table_widget.setHorizontalHeaderItem(index, header)
            table_widget.setColumnWidth(index, item['width'])

        # 初始化一些数据,也可以后期用爬到的数据动态的填充进去
        db_path = os.path.join(BASE_DIR, 'db')
        if not os.path.exists(db_path):
            os.mkdir(db_path)

        data_list = {}
        if os.path.exists(os.path.join(db_path, 'data.json')):
            with open(os.path.join(db_path, 'data.json'), mode='r', encoding='utf-8') as f:
                data_list = simplejson.loads(f.read())

        # 获取当前表格中的行数
        current_count = table_widget.rowCount()
        for data in data_list:
            table_widget.insertRow(current_count)
            for i, item in enumerate(data):
                # 数字与状态值之间的转换
                item = STSTUS_MAPPING[item] if item in STSTUS_MAPPING and i == 6 else item
                cell = QTableWidgetItem(str(item))
                table_widget.setItem(current_count, i, cell)
                # 设置某个单元格是否可以被选中和编辑
                if i in [0, 4, 5, 6]:
                    cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            current_count += 1

        # 开启右键复制功能
        table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        table_widget.customContextMenuRequested.connect(self.table_right_mean)
        table_layout.addWidget(table_widget)
        return table_layout
    def table_right_mean(self, pos):

        selected_item_list = self.table_widget.selectedItems()
        if len(selected_item_list) == 0:
            return
        mean = QMenu()
        item_copy = mean.addAction('复制')
        item_log = mean.addAction('查看日志')
        clean_log = mean.addAction('清除日志')

        row_index = selected_item_list[0].row()
        asin = self.table_widget.item(row_index, 0).text().strip()

        # 此处代表的就是前面的三个action哪个被选中了
        action = mean.exec_(self.table_widget.mapToGlobal(pos))
        if action == item_copy:
            # 获取粘贴板对象
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_item_list[0].text())
        elif action == item_log:
            # 查看日志的对话框
            from utils.dialog import CheckLogDialog
            dialog = CheckLogDialog(asin)
            dialog.setWindowModality(Qt.ApplicationModal)
            dialog.exec()
        elif action == clean_log:
            file_path = os.path.join(BASE_DIR, 'log', '{}.log'.format(asin))
            if file_path:
                os.remove(file_path)
                QMessageBox.information(self, '提示', '日志删除成功！')
    def initFontLayout(self):
        font_layout =  QHBoxLayout()
        self.font_labal = QLabel('未检测')
        # self.font_labal.setPixmap(QPixmap('load.gif'))
        # self.font_labal.setGeometry(100, 50, 300, 200)
        # self.font_labal.setScaledContents(True)
        # movie = QMovie('load.gif')
        # self.font_labal.setMovie(movie)
        # movie.start()
        font_layout.addWidget(self.font_labal)
        font_layout.addStretch()
        btn_rest_init = QPushButton('重新初始化')
        btn_rest_init.clicked.connect(self.btn_rest_init_fun)
        btn_rest_check = QPushButton('重新检测')
        btn_rest_check.clicked.connect(self.btn_rest_check_fun)
        btn_clean_count = QPushButton('次数清零')
        btn_clean_count.clicked.connect(self.btn_clean_count_fun)
        btn_del_item = QPushButton('删除检测项')
        btn_del_item.clicked.connect(self.btn_del_item_fun)
        btn_smtp_alter = QPushButton('SMTP报警配置')
        btn_smtp_alter.clicked.connect(self.btn_smtp_alter_fun)
        btn_daili_ip = QPushButton('联系我')
        btn_daili_ip.clicked.connect(self.btn_daili_ip_fun)

        font_layout.addWidget(btn_rest_init)
        font_layout.addWidget(btn_rest_check)
        font_layout.addWidget(btn_clean_count)
        font_layout.addWidget(btn_del_item)
        font_layout.addWidget(btn_smtp_alter)
        font_layout.addWidget(btn_daili_ip)

        return font_layout

    # 初始化成功的回调函数
    def init_task_success_callback(self, index, title, price, url):
        # 做窗体上数据的更新，是否初始化成功
        # print(index, asin, title, url)
        # 一列一列的去更新
        # 更新标题
        cell_title = QTableWidgetItem(title)
        self.table_widget.setItem(index, 1, cell_title)
        # 更新url
        cell_url = QTableWidgetItem(url)
        self.table_widget.setItem(index, 2, cell_url)
        # 更新状态
        cell_status = QTableWidgetItem(STSTUS_MAPPING[1])
        self.table_widget.setItem(index, 6, cell_status)

        # 获取完整的初始化之后的数据，并且把数据保存在本地
        org_asin = self.table_widget.item(index, 0).text().strip()
        org_title = self.table_widget.item(index, 1).text().strip()
        org_url = self.table_widget.item(index, 2).text().strip()
        org_price = self.table_widget.item(index, 3).text().strip()
        org_suc_count = self.table_widget.item(index, 4).text().strip()
        org_err_count = self.table_widget.item(index, 5).text().strip()
        org_status = self.table_widget.item(index, 6).text().strip()
        org_fre = self.table_widget.item(index, 7).text().strip()
        org_data_item = [org_asin, org_title, org_url, org_price, org_suc_count, org_err_count, org_status, org_fre]

        data_path = os.path.join(BASE_DIR, 'db', 'data.json')

        all_data_item = []
        if os.path.exists(data_path):
            with open(data_path, mode='r', encoding='utf-8') as f:
                all_data_item = simplejson.loads(f.read())
        all_data_item.append(org_data_item)
        data_str = simplejson.dumps(all_data_item, ensure_ascii=False)
        with open(data_path, mode='w', encoding='utf-8') as f:
            f.write(data_str)
        # 清空输入框
        self.line_edit.clear()

    # 初始化失败的回调函数
    def init_task_error_callback(self, index, asin, title, url):
        # 更新状态
        cell_status = QTableWidgetItem(STSTUS_MAPPING[11])
        cell_status.setBackground(QBrush(QColor(255, 0, 0)))
        self.table_widget.setItem(index, 6, cell_status)

        # 清空输入框
        self.line_edit.clear()

    '''         所有的按钮点击槽函数          '''
    # 点击重新初始化
    def btn_rest_init_fun(self):
        # 首先获取所有被选中的行
        row_list = self.table_widget.selectionModel().selectedRows()
        if not row_list:
            QMessageBox.warning(self, '错误', '请选择需要重新初始化的行')
            return
        for row_object in row_list:
            # 所选中行的索引
            index = row_object.row()
            # 获取型号
            asin = self.table_widget.item(index, 0).text().strip()
            # 修改窗体中的状态为初始化中
            # 更新状态
            cell_status = QTableWidgetItem(STSTUS_MAPPING[0])
            self.table_widget.setItem(index, 6, cell_status)

            # 创建线程，去异步执行初始化这个逻辑，也就是去爬虫拿数据，然后更新
            from utils.mythreads import NewTaskThread
            task = NewTaskThread(index, asin, self)
            task.success.connect(self.init_task_success_callback)
            task.error.connect(self.init_task_error_callback)
            task.start()

    def btn_rest_check_fun(self):
        pass

    # 清零表中某某一列的数据，也就是更新为0即可
    def btn_clean_count_fun(self):
        # 首先获取所有被选中的行
        row_list = self.table_widget.selectionModel().selectedRows()
        if not row_list:
            QMessageBox.warning(self, '错误', '请选择需要清零的行')
            return
        for row_object in row_list:
            # 所选中行的索引
            index = row_object.row()
            # 更新次数为零
            cell_status = QTableWidgetItem(str(0))
            self.table_widget.setItem(index, 4, cell_status)

            cell_status = QTableWidgetItem(str(0))
            self.table_widget.setItem(index, 5, cell_status)

            cell_status = QTableWidgetItem(str(0))
            self.table_widget.setItem(index, 7, cell_status)

    # 删除需要监控的项目，注意索引要从后往前删
    def btn_del_item_fun(self):
        # 首先获取所有被选中的行
        row_list = self.table_widget.selectionModel().selectedRows()
        if not row_list:
            QMessageBox.warning(self, '提示', '请选择需要删除的行')
            return
        # 反转索引，目的是为了从最后一个开始删除，如果顺序删除的话，表格中的数据会自动顶上去，会造成索引错乱
        row_list.reverse()
        for row_object in row_list:
            # 所选中行的索引
            index = row_object.row()
            # 删除改行即可
            self.table_widget.removeRow(index)
            QMessageBox.information(self, '提示', '删除成功！')

    # 弹框配置报警邮件
    def btn_smtp_alter_fun(self):
        # 首先需要弹出一个对话框
        from utils.dialog import EmailDialog
        dialog = EmailDialog()
        # 设置蒙版，就是当前窗口如果未关闭的话，则不能操作下层的窗口
        dialog.setWindowModality(Qt.ApplicationModal)
        # dialog.show()
        dialog.exec()
        # 对话框中需要输入发送报警的邮件配置
        # 然后保存，把数据存入文本当中
        # 下次再打开的时候，先去文件中读取，如果有则回显上去，如果没有则为空
        # 关闭对话框

    # 配置代理ip
    def btn_daili_ip_fun(self):
        # from utils.dialog import ProxyDialog
        # dialog = ProxyDialog()
        # dialog.setWindowModality(Qt.ApplicationModal)
        # dialog.exec()
        QMessageBox.information(self, '提示', '联系我QQ:260034951')

    # 点击开始
    def start_buuton_fun(self):
        # 创建多个线程，去执行列别中的查询数据，然后每个线程查到之后都选哟重新更新一个窗体

        # 点击开始之前，先判断，，此时项目是否处于停止状态，只有在停止状态下才可以点击开始按钮
        if self.switch != STOP:
            QMessageBox.warning(self, '提示', '检测正在进行中或者正在停止中，请勿重复操作！')
            return
        self.switch = RUNNING
        # 修改状态
        self.update_status_message('执行中')

        SCHEDULAR.start(
            self,
            BASE_DIR,
            self.start_callback_fun,
            self.stop_callback_fun,
            self.update_success_fun
        )

    # 这个函数就是用来更新表格中的状态，从待执行，变成执行中
    def start_callback_fun(self, row_index):
        cell_status = QTableWidgetItem(STSTUS_MAPPING[2])
        self.table_widget.setItem(row_index, 6, cell_status)

    def stop_callback_fun(self, row_index):
        cell_status = QTableWidgetItem(STSTUS_MAPPING[1])
        self.table_widget.setItem(row_index, 6, cell_status)

    def update_success_fun(self, row_index, title, price, url):
        old_price = float(self.table_widget.item(row_index, 3).text().strip())
        new_price = float(price)
        asin = window.table_widget.item(row_index, 0).text().strip()
        logger.info(f'标题为：{title},原价为：{old_price}, 最新价格为：{new_price}')
        log_path = os.path.join(BASE_DIR, 'log')
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        with open(os.path.join(log_path, '{}.log'.format(asin)), mode='a', encoding='utf-8') as f:
            f.write('{}\n'.format(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())},标题为：{title},原价为：{old_price}, 最新价格为：{new_price}'))
        if new_price < old_price:
            from utils.send_email import SendEmail
            text = f'降价报警,标题为：{title},原价为：{old_price}, 最新价格为：{new_price},降价比列为：{(old_price - new_price) / old_price * 100}%'
            mail = SendEmail(text)
            mail.send()
            # return
        # 更新次数
        old_count = self.table_widget.item(row_index, 4).text().strip()
        new_count = int(old_count) + 1
        cell_count = QTableWidgetItem(str(new_count))
        self.table_widget.setItem(row_index, 4, cell_count)

        # 更新价格
        cell_price = QTableWidgetItem(str(new_price))
        self.table_widget.setItem(row_index, 7, cell_price)

    def stop_button_fun(self):
        if self.switch != RUNNING:
            QMessageBox.warning(self, '提示', '检测未开始或者正在停止中，请勿重复操作！')
            return
        self.switch = STOPPING
        SCHEDULAR.stop()

    def update_status_message(self, message):
        if message == '已终止':
            self.switch = STOP
        self.font_labal.setText(message)
        self.font_labal.repaint()


if __name__ == '__main__':
    import test
    app = QApplication(sys.argv)
    icon = QIcon()
    # icon.addPixmap(QPixmap('images/head.ico'))
    # app.setWindowIcon(icon)
    app.setWindowIcon(QIcon(':/images/head.ico'))
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())


