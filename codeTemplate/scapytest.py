#!/bin/python3
# author ming
# install  PyX its
# https://stackoverflow.com/questions/50914059/pyx-not-installed-correctly-when-using-scapy
# sudo apt install texlive-latex-base

from scapy.utils import rdpcap

if __name__ == '__main__':
    # 读取 $PATH
    a=rdpcap('./test.cap')
    a.pdfdump('test.pdf',layer_shift=1)

