import time

from PyQt5.QtCore import QThread, pyqtSignal


class NewTaskThread(QThread):
    # 从线程中获取数据之后，如何把数据传递给住程序中的函数，并更新窗体呢？此处需要使用到信号，信号被触发的时候，就会去执行函数，从而更新数据
    # 创建两个信号，一个成功，一个失败，都需要传递四个参数
    success = pyqtSignal(int, str, str, str)
    error = pyqtSignal(int, str, str, str)

    def __init__(self, row_index, asin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_index = row_index
        self.asin = asin

    def run(self):
        ''' 使用爬虫获取数据，解析数据，然后更新窗体 '''
        #  待完成，根据型号，利用爬虫去抓取网路数据，然后解析，然后触发信号，回调函数，更新数据
        # 假设查到数据之后，触发信号，我们在创建这个线程的时候，可以指定，如果在线程内触发了这两个信号，则去执行主窗体中的那些函数
        from utils.get_data import GetData
        data = GetData(self.asin)
        try:
            title, price, url = data.get_origin_data()
            self.success.emit(self.row_index, title, price, url)
        except Exception as e:
            self.error.emit(self.row_index, '', '', '')
            print(e)




class TaskThread(QThread):
    # 创建一个更改是否执行的状态的信号
    start_signal = pyqtSignal(int)
    # 创建一个信号，用来执行当该线程结束的时候去更新状态
    stop_signal = pyqtSignal(int)

    # 创建一个更新成功次数的信号
    update_success_count = pyqtSignal(int, str, str, str)

    # 创建一个更新失败次数的信号
    update_error_count = pyqtSignal(int)

    def __init__(self, schedular, log_dir, asin, row_index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asin = asin
        self.row_index = row_index
        self.log_dir = log_dir
        self.schedular = schedular

    def run(self):
        self.start_signal.emit(self.row_index)
        # print(self.asin, self.row_index)

        # 循环去爬取数据解析，然后更新
        # TODO: 利用爬虫去监控，然后更新
        import time
        import random
        from utils.get_data import GetData
        data = GetData(self.asin)
        while True:
            if self.schedular.terminate:
                self.schedular.thread_list.remove(self)
                self.stop_signal.emit(self.row_index)
                return
            try:
                title, price, url = data.get_origin_data()
                self.update_success_count.emit(self.row_index, title, price, url)
            except Exception as e:
                self.update_error_count.emit(self.row_index, '', '', '')
                with open(self.log_dir, mode='a', encoding='utf-8') as f:
                    f.write('日志:{}\n'.format(e))
                print(e)

            time.sleep(random.randint(5, 10))


class StopThread(QThread):
    update_online_count = pyqtSignal(str)
    def __init__(self, schedular, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedular = schedular

    def run(self):
        total_count = len(self.schedular.thread_list)
        while True:
            running_count = len(self.schedular.thread_list)
            if running_count == 0:
                self.update_online_count.emit('已终止')
                break
            # 更新数据到页面中上
            self.update_online_count.emit('正在终止，存活数量:{}'.format(running_count))
            time.sleep(2)

