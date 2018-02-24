"""
implement messenger
"""
import socket
import pickle
import datetime

import time
import numpy as np

loss_rate = 0.3

def sendMsg(host, port, msg):
    delay = np.random.rand()
    time.sleep(delay)
  
    if messageLoss(loss_rate) is True:
       print("lose message for")
       print(msg)
       return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    try:
        s.connect((host, port))
    except socket.error:
       print_message("listening port closed, ignore this msg")
       return 
    print(msg)
    s.sendall(pickle.dumps(msg))
    s.close()

def messageLoss(loss_rate):
    if np.random.rand() < loss_rate:
       return True
    else:
       return False

def print_message(message = ""):
    timestamp = datetime.datetime.now().isoformat(" ").split(".")[0]
    print(timestamp + " INFO " + message) 


