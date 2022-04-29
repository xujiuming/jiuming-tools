if __name__ == '__main__':
    r = open('./ttt','r+')
    o = open('./result','w+')
    for l in r:
        if l.startswith('magnet'):
            o.write(l)
