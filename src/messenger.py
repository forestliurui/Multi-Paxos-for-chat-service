"""
implement messenger
"""
import socket
import pickle

def sendMsg(host, port, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    s.connect((host, port))
    s.sendall(pickle.dumps(msg))
    s.close()

