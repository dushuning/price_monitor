import simplejson
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import simplejson
import os, sys

# 获取当前项目的绝对路径
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))


class EmailDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_dict = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('报警邮件设置')
        self.resize(400, 300)

        # 创建垂直一个布局
        layout = QVBoxLayout()
        from_data_list = [
            {'title': 'SMTP服务器', 'filed': 'smtp'},
            {'title': '发件箱', 'filed': 'form'},
            {'title': '密码', 'filed': 'pwd'},
            {'title': '收件人（多个用逗号分隔）', 'filed': 'to'},
        ]
        # 判断本地文件中是否有之前配置的信息，如果有，则反写，如果没有，则为空
        smtp_dict = {}
        smtp_path = os.path.join(BASE_DIR, 'db')
        if not os.path.exists(smtp_path):
            os.makedirs(smtp_path)

        if os.path.exists(os.path.join(smtp_path, 'smtp.txt')):
            with open(os.path.join(BASE_DIR, 'db', 'smtp.txt'), mode='r', encoding='utf-8') as f:
                smtp_dict = simplejson.loads(f.read())

        for item in from_data_list:
            label = QLabel(item['title'])
            layout.addWidget(label)

            txt = QLineEdit()
            try:
                txt.setText(smtp_dict[item['filed']])
            except Exception as e:
                txt.setText('')
            layout.addWidget(txt)

            # 把所有的文本框控件都保存在这个字典中，方便后续获取控件中输入的文本值
            self.field_dict[item['filed']] = txt

        btn_save = QPushButton('保存')
        btn_save.clicked.connect(self.save_email_fun)
        layout.addWidget(btn_save, 0, Qt.AlignCenter)

        # layout.addStretch()
        self.setLayout(layout)

    def save_email_fun(self):
        data_dict = {}
        for key, filed in self.field_dict.items():
            value = filed.text().strip()
            if not value:
                QMessageBox.warning(self, '提示', '邮件报警配置项不能为空！')
                return
            data_dict[key] = value
        # 把数据写入到文本文件中保存起来，下次点击的时候需要反写到表格中
        with open(os.path.join(BASE_DIR, 'db', 'smtp.txt'), mode='w', encoding='utf-8') as f:
            f.write(simplejson.dumps(data_dict))
        QMessageBox.information(self, '提示', '邮件报警配置项保存成功！')
        self.close()

class ProxyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('配置代理ip')
        self.resize(500, 400)

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setPlaceholderText('可用换行来设置多个代理ip，每个代理ip设置格式为：10.20.225.221:8080')

        ip_text = ''
        if os.path.exists(os.path.join(BASE_DIR, 'db', 'proxyip.txt')):
            with open(os.path.join(BASE_DIR, 'db', 'proxyip.txt'), mode='r', encoding='utf-8') as f:
                ip_text = f.read()

        text_edit.setText(ip_text)
        self.text_edit = text_edit
        layout.addWidget(text_edit)

        btn_save = QPushButton('重置')
        btn_save.clicked.connect(self.save_proxyip_fun)
        layout.addWidget(btn_save, 0, Qt.AlignCenter)
        self.setLayout(layout)

    def save_proxyip_fun(self):
        ip_text = self.text_edit.toPlainText()
        if ip_text.strip():
            with open(os.path.join(BASE_DIR, 'db', 'proxyip.txt'), mode='w', encoding='utf-8') as f:
                f.write(ip_text)
        self.close()


class CheckLogDialog(QDialog):

    def __init__(self, asin):
        super().__init__()
        self.asin = asin
        self.initUI()

    def initUI(self):
        self.setWindowTitle('查看日志')
        self.resize(400, 300)

        layout = QVBoxLayout()

        txt_edit = QTextEdit()
        log_txt = ''
        # 此处需要初始化日志，读取本地文件中的日志，然后写入到这个文本框中
        if os.path.exists(os.path.join(BASE_DIR, 'log', '{}.log'.format(self.asin))):
            with open(os.path.join(BASE_DIR, 'log', '{}.log'.format(self.asin)), mode='r', encoding='utf-8') as f:
                log_txt = f.read()
        txt_edit.setText(log_txt)
        layout.addWidget(txt_edit)

        self.setLayout(layout)
