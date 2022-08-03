

class Schedular(object):

    def __init__(self):
        self.thread_list = []
        self.window = None
        # 用来标记用户是否已经点击过停止按钮，后续为了防止重复点击
        self.terminate = False

    def start(self, window, base_dir,  start_callback_fun, stop_callback_fun, update_success_fun):
        # 1 获取表格中的每一行数据，然后每行数据都创建一个线程去执行监控任务
        # 2 每个线程在执行监控后，需要实时的更新表格中的数据，通过信号和回调函数
        self.window = window
        self.base_dir = base_dir
        self.terminate = False

        import os
        for index in range(window.table_widget.rowCount()):
            # 拿到每一行数据的索引和型号
            asin = window.table_widget.item(index, 0).text().strip()
            status = window.table_widget.item(index, 6).text().strip()
            # 如果状态不是待执行，那么久不能再次给他创建线程了
            if status != '待执行':
                continue

            log_file_path = os.path.join(base_dir, 'log')
            if not os.path.exists(log_file_path):
                os.makedirs(log_file_path)
            log_dir = os.path.join(log_file_path, '{}.log'.format(asin))
            # 循环创建线程，然后让线程去执行监控任务，并且实施更新数据，需要传递参数型号和行数
            from utils.mythreads import TaskThread
            t = TaskThread(self, log_dir, asin, index, window)
            self.thread_list.append(t)
            t.start_signal.connect(start_callback_fun)
            t.stop_signal.connect(stop_callback_fun)
            t.update_success_count.connect(update_success_fun)
            t.start()




    def stop(self):
        self.terminate = True
        # 创建一个线程实时去检测线程的个数，并展示在主页面上，需要传递两个参数，一个是self， 一个是window对象，在qt的项目中，创建线程的时候必须传递一个主窗口，否则无法运行
        from utils.mythreads import StopThread
        s = StopThread(self, self.window)
        s.update_online_count.connect(self.window.update_status_message)
        s.start()

# 使用单列模式，创建一个实列，其他模块中，如果直接导入这个实列的话，那么所有使用的都是同一个实列
SCHEDULAR = Schedular()
