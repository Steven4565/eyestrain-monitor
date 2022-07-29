import csv
import datetime
import time

data = [1, 2, 3, 5, 3]


# with open('output.csv', 'a', newline='') as f:
#     csv.writer(f, delimiter=',').writerows([['test', *data]])


# with open('output.csv', "r", encoding="utf8") as f:
#     csv_reader = csv.reader(f)
#     for line in csv_reader:
#         print(line)

data2 = data[0:-1]
print([[time.strftime('%H:%M', time.localtime()), 'test', *data2]])
