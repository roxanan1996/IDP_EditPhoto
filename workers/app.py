import os
import time

import redis
from rq import Worker, Queue, Connection

r = redis.StrictRedis(host='redis', port=6379, db=0)
p = r.pubsub()
p.subscribe('image')

if __name__ == '__main__':
    while True:
        message = p.get_message()
        if message:
            if message['data'] == b'start':
                print("start")
                image = []
                while True:
                    message = p.get_message()
                    if message:
                        if message['data'] == b'stop':
                            print("stop")
                            break
                        else:
                            image.append(message['data'])
                print(image)
        time.sleep(2)
