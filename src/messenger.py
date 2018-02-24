"""
implement messenger
"""
import socket
import pickle

import time
import numpy as np

def sendMsg(host, port, msg):
    delay = np.random.rand()
    time.sleep(delay)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    s.connect((host, port))
    print(msg)
    s.sendall(pickle.dumps(msg))
    s.close()

