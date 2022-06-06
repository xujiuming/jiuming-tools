#!/bin/python3
# author ming
import redis

if __name__ == '__main__':
    r = redis.Redis(host='show.xujiuming.com', port=16379, db=0, password='Ming1234')
    print(r.execute_command("get ming"))