# Echo client program
import socket
import pickle

HOST = 'bigdata.eecs.umich.edu'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
msg = {'type':'propose', 'val': 'this is our chat', 'id': 2}
#s.sendall('Hello, world')
s.sendall(pickle.dumps(msg))
data = s.recv(1024)
s.close()
print(pickle.loads(data))
#print 'Received', repr(data)
