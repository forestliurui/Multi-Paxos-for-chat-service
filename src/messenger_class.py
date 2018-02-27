"""
implement messenger class
"""
import socket
import pickle
import time
import numpy as np

from my_logging import MyLogging


class Messenger(object):
    def __init__(self, loss_rate=0):
        self.loss_rate = loss_rate

    def send_msg(self, host, port, msg):
        delay = np.random.rand()
        time.sleep(1 * delay)

        # if  msg['type'] != 'request': 
        if self.message_loss() is True:
            MyLogging.info("DROP: " + str(msg))

            return

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
        except socket.error:
            MyLogging.info("listening port closed, ignore this msg")
            return
        MyLogging.info("SEND: " + str(msg))

        try:
            s.sendall(pickle.dumps(msg))
        except socket.error:
            MyLogging.info("try to resend due to socket error")
            time.sleep(0.1)
            s.sendall(pickle.dumps(msg))

        s.close()

    def message_loss(self):
        if np.random.rand() < self.loss_rate:
            return True
        else:
            return False
