import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import os
import sys

import simplejson

BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))


class SendEmail(object):
    def __init__(self, text):
        super(SendEmail, self).__init__()
        self.text = text

    def send(self):
        if not os.path.exists(os.path.join(BASE_DIR, 'db', 'smtp.txt')):
            print('报警 邮箱配置不存在，请核查')
            return

        with open(os.path.join(BASE_DIR, 'db', 'smtp.txt'), mode='r', encoding='utf-8') as f:
            smtp_dict = simplejson.loads(f.read())

        msg = MIMEText(self.text, 'html', 'utf-8')
        msg['From'] = formataddr(('Mr Du', smtp_dict['form']))
        msg['to'] = smtp_dict['to']
        msg['Subject'] = '邮件报警测试'

        # 发送邮件
        server = smtplib.SMTP_SSL(smtp_dict['smtp'])
        server.login(smtp_dict['form'], smtp_dict['pwd'])
        server.sendmail(smtp_dict['form'], smtp_dict['to'], msg.as_string())
        server.quit()


# SEND_EMAIL = SendEmail()
