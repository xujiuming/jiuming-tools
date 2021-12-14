#!/bin/python3
# author ming
# 测试dbm模块
import dbm

if __name__ == '__main__':
    print(dbm.whichdb("test.db"))
    # c 打开读写 如果不存在就创建一个
    db = dbm.open("test.db", "c")
    db["id"] = "1"
    db["id1"] = "2"

    print(db.keys())
