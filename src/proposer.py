"""
This is the proposer class
"""
import socket
import pickle

from messenger import sendMsg
#need to make sure the acceptors_list doesn't include itself

class Proposer(object):
    def  __init__(self, server_id, servers_list):
         self.server_id = server_id
         self.acceptors_list = dict(servers_list)

         #if self.server_id == 0:
         #   import pdb;pdb.set_trace()
         #remove itself from the acceptors list, because it doesn't need to communicate with itself
         del self.acceptors_list[self.server_id]
         self.quorum = len(self.acceptors_list)/2     
         
         self.proposal_id = None
         self.proposal_count = {}
         self.msg_collection = {}

         self.proposed_id = None

    def prepare(self, proposal_id):
        #propose_id is always increasing
        self.proposal_id = proposal_id
        msg = {'type': 'prepare', 'proposal_id': proposal_id, 'proposer_id': self.server_id}
        for acceptor_id in self.acceptors_list:
            host = self.acceptors_list[acceptor_id]['host']
            port = self.acceptors_list[acceptor_id]['port']
            sendMsg(host, port, msg)

    def addVote(self, msg): 
        proposal_id = msg['proposal_id']
        if proposal_id != self.proposal_id:
           #the received proposal_id is not the same as the current one
           return 

        if proposal_id not in self.proposal_count:
           self.proposal_count[proposal_id] = 1
        else:
           self.proposal_count[proposal_id] += 1

        if proposal_id not in self.msg_collection:
           self.msg_collection[proposal_id] = []
        self.msg_collection[proposal_id].append(msg) 

    def checkQuorumSatisfied(self):
        if self.proposal_count[self.proposal_id] >= self.quorum:
           return True
        else:
           return False

    def getValWithLargestAcceptedID(self):
        msg_list = self.msg_collection[self.proposal_id]
        largest_accepted_id = None
        accepted_val_with_largest_id = None
 
        for msg in msg_list:
          if msg['accepted_id'] is not None:
            if largest_accepted_id is None or msg['accepted_id'] >= largest_accepted_id:
                if msg['accepted_id'] == largest_accepted_id:
                    if accepted_val_with_largest_id != msg['accepted_val']:
                        raise ValueError("Different accepted values from accepted id: %d"%largest_accepted_id)
                largest_accepted_id = msg['accepted_id']
                accepted_val_with_largest_id = msg['accepted_val']
        return accepted_val_with_largest_id

    def propose(self, val, client_info):
        if self.proposed_id is not None and self.proposal_id <= self.proposed_id:
           #no need to propose again
           return

        self.proposed_id = self.proposal_id
        msg = {"type": "propose", 'proposal_id': self.proposal_id, 'val': val, 'proposer_id': self.server_id, 'client_info': client_info }
        for acceptor_id in self.acceptors_list:
            host = self.acceptors_list[acceptor_id]['host']
            port = self.acceptors_list[acceptor_id]['port']

            sendMsg(host, port, msg)

