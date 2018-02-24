"""
This is the proposer class
"""
import socket
import pickle
#need to make sure the acceptors_list doesn't include itself

class Proposer(object):
    def  __init__(self, server_id, servers_list):
         self.server_id = server_id
         self.acceptors_list = dict(servers_list)

         #remove itself from the acceptors list, because it doesn't need to communicate with itself
         del self.acceptors_list[self.server_id]
         self.quorum = len(self.acceptors_list)/2     

    def tryGetElected(self, proposer_id):
        socket_dict = {}
        for acceptor_id in self.acceptors_list:
            msg = {'type': 'prepare', 'proposer_id': proposer_id}
            s = self.sendMsg(acceptor_id, msg)
            socket_dict[acceptor_id] = s

        vote_num = 0
        msg_list = []
        for acceptor_id in self.acceptors_list:
            msg = self.recvMsg(acceptor_id, )
            if msg['type'] = "promise":
               msg_list.append(msg)
               vote_num += 1

        if vote_num >= self.quorum:
           proposer_val = self.getValWithLargestProposerID(msg_list)
           return True, proposer_val  #get elected as leader
        else:
           return False, None #not elected

    def recvMsg(self, acceptor_id, s):
        

    def sendMsg(self, acceptor_id, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = self.acceptors_list[acceptor_id]['host']
        port = self.acceptors_list[acceptor_id]['port']
        s.connect((host, port))
        s.sendall(pickle.dumps(msg))

        return s

    def getValWithLargestProposerID(self, msg_list):
        largest_id = None
        proposer_val = None
 
        for msg in msg_list:
            if largest_id is None or msg['proposer_id'] >= largest_id:
                if msg['proposer_id'] == largest_id:
                    if proposer_val != msg['val']:
                        raise ValueError("Different value from the same proposers with id %d"%largest_id)
                largest_id = msg['proposer_id']
                proposer_val = msg['proposer_val']
        return propose_val

    def propose(self, proposer_id, val):
        for acceptor in self.acceptors_list:
            msg = {"type": "propose", 'proposer_id': proposer_id, 'val': val }
            self.sendMsg(acceptor, msg)

