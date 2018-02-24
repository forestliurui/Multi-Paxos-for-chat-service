"""
This is the class for acceptor
"""
import socket
from messenger import sendMsg

class Acceptor(object):
     def __init__(self, server_id, servers_list):
         self.server_id = server_id
         self.proposers_list = dict(servers_list)
         #if self.server_id == 0:
         #   import pdb;pdb.set_trace()
         #remove itself from the acceptors list, because it doesn't need to communicate with itself
         del self.proposers_list[self.server_id]
         self.learners_list = self.proposers_list

         #self.host = host
         #self.port = port
         self.promised_proposal_id = None
         self.accepted_proposal_id = None
         self.accepted_proposal_val = None
         
     def promise(self, recvd_msg):
         if self.promised_proposal_id is None or recvd_msg['proposal_id'] >= self.promised_proposal_id:
            self.promised_proposal_id = recvd_msg['proposal_id']
            
            reply_msg = {'type': 'promise', 'accepted_id': self.accepted_proposal_id, 'accepted_val': self.accepted_proposal_val, 'proposal_id': recvd_msg['proposal_id']}

            proposer_id = recvd_msg['proposer_id']
            host = self.proposers_list[proposer_id]['host'] 
            port = self.proposers_list[proposer_id]['port']

            sendMsg(host, port, reply_msg)

     def accept(self, recvd_msg):
         if self.promised_proposal_id is None or recvd_msg['proposal_id'] >= self.promised_proposal_id:
            self.promised_proposal_id = recvd_msg['proposal_id']
            self.accepted_proposal_id = recvd_msg['proposal_id']
            self.accepted_proposal_val = recvd_msg['val']
            reply_msg = {"type": "accept", 'proposal_id': self.accepted_proposal_id, 'val': self.accepted_proposal_val}
            self.sendToAllLearners(reply_msg)

     def sendToAllLearners(self, msg):
         for learner_id in self.learners_list:
             host = self.learners_list[learner_id]['host']
             port = self.learners_list[learner_id]['port']
         
             sendMsg(host, port, msg)

