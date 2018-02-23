"""
This is the class for acceptor
"""
import socket

class Acceptor(object):
     def __init__(self, host, port, learners_list):
         self.learners_list = learners_list
         self.host = host
         self.port = port
         self.promised_proposer_id = None
         self.accepted_proposer_val = None

     def waitForConnection(self):
         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         s.bind((self.host, self.port))
         s.listen(1)
         conn, addr = s.accept()
         print("Connected by "+ addr)

         
         data = conn.recv(1024)
         
         if data['type'] == "prepare": 
             self.promise(conn, data)
         elif data['type'] == "propose":
             self.accept(data)
         conn.close()
         
     def promise(self, conn, recvd_msg):
         if self.promised_proposer_id is None:
            self.promised_proposer_id = recvd_msg['proposer_id']
            
            reply_msg = {"type": "promise", 'proposer_id': None, 'proposer_val': None}
            conn.sendall(reply_msg)

         elif recvd_msg['proposer_id'] >= self.current_proposer_id:
            reply_msg = {"type": "promise", 'proposer_id': self.promised_proposer_id, 'proposer_val': self.accepted_proposer_val}
            self.promised_proposer_id = recvd_msg['proposer_id']
            
            conn.sendall(reply_msg)

     def accept(self, recvd_msg):
         if self.promised_proposer_id is None or recvd_msg['proposer_id'] >= self.current_proposer_id::
            self.promised_proposer_id = recvd_msg['proposer_id']
            self.accepted_proposer_val = recvd_msg['proposer_val']
            reply_msg = {"type": "accept", 'proposer_id': self.promised_proposer_id, 'proposer_val': self.accepted_proposer_val}
            self.sendToAllLearners(reply_msg)
         
