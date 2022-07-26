import csv

data = [1, 2, 3, 5, 3]


# with open('output.csv', 'a', newline='') as f:
#     csv.writer(f, delimiter=',').writerows([['test', *data]])


# with open('output.csv', "r", encoding="utf8") as f:
#     csv_reader = csv.reader(f)
#     for line in csv_reader:
#         print(line)

data2 = data[0:-1]
print([['test', *data2]])
