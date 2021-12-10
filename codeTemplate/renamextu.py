#!/bin/python3
# author ming
# 重命名指定文件夹下的骁途的所有照片 并且复制到指定目录
import os

if __name__ == '__main__':
    # 读取所有骁途的目录
    dir_list = os.listdir(".")
    for i in len(dir_list):
        c_dir = os.listdir(dir_list[i])



