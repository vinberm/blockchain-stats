# coding=utf-8
import requests
import matplotlib.pyplot as plt
import time
from datetime import datetime
import matplotlib.dates as mdates

#转换成localtime
# time_local = time.localtime(timestamp)
# #转换成新的时间格式(2016-05-05 20:28:54)
# dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
# meta = 'http://blockmeta.com/api/block/'
# num = [x+1 for x in range(25212) if x % 2016 == 0]
# print num
diff = [15154807, 57518846, 92450348, 68145068, 68194019, 160077945, 425793387, 631259843, 959339400, 1225071929, 1814785054, 2100998542, 2661802590]

times = [1524550736, 1524629301, 1524817443, 1525227678, 1525530002, 1525658709, 1525772373, 1525976362, 1526175407, 1526412152, 1526616681, 1526877699, 1527116187]



dates = []

for t in times:
    local = time.localtime(t)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", local)
    dates.append(dt)
print dates

xs = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S').date() for d in dates]
print xs
# xs = dates
ys = diff

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
# plt.xticks(range(len(xs)), xs)

plt.xlabel('date')
plt.ylabel('difficulty')

plt.plot(xs, ys)
plt.gcf().autofmt_xdate()
plt.show()


def change_percent(list):
    y = []
    for i in range(len(list) - 1):
        x = (list[i + 1] - list[i]) / float(list[i]) * 100

        y.append(str(float('%.2f' % x)) + '%')
    print y
