#!/bin/python3
# author ming
# 测试csv模块
import csv

if __name__ == '__main__':
    f = open("test.csv", "a+", newline='')
    w = csv.writer(f)
    w.writerow((1, "fasdf"))

    f.seek(0,0)
    r = csv.reader(f,dialect='excel')
    for line in r:
        print(line)
