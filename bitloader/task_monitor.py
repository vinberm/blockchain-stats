#! /usr/bin/env python
# -*- coding: utf-8 -*-

# 对于需要监控task
# 出现错误时给管理员发送邮件

import threading
import subprocess
import re
import time
from application import app
from tasks import tasks, TASK_MONITOR_LIST


def monitor_task(f):
    p = subprocess.Popen(['tail', '-f', f], stdout=subprocess.PIPE)
    msg = ''
    task_already_send = {}
    while True:
        line = p.stdout.readline()
        if 'ERROR' in line or not line.startswith('['):
            msg += '%s' % line
        else:
            if msg:
                # rex = '.*?(?:[a-z][a-z0-9_]*).*?(?:[a-z][a-z0-9_]*).*?(?:[a-z][a-z0-9_]*).*?((?:[a-z][a-z0-9_]*))'
                # pattern = re.compile(rex, re.IGNORECASE | re.DOTALL)
                # m = pattern.search(msg)
                # if m:
                #     task = m.group(1)
                task = msg.split(']', 1)[1].split('[')[0].replace(' Task ', '')
                if task in TASK_MONITOR_LIST:
                    # 是否是所需要监控的任务
                    if task not in task_already_send:
                        # 是否时间段内第一次错误的产生
                        task_already_send[task] = time.time()
                        tasks.t_tasks_error_mail.delay(msg)
                    else:
                        # 时间段内已经发送过
                        if int(time.time() - task_already_send[task]) > app.conf['WARN_EMAIL_TIME_SPACE']:
                            task_already_send[task] = time.time()
                            tasks.t_tasks_error_mail.delay(msg)
            msg = ''


if __name__ == '__main__':
    threading.Thread(target=monitor_task, args=(app.conf['CELERYD_LOG_FILE'],)).start()
