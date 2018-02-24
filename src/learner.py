"""
This is the Learner class
"""

from messenger import sendMsg
from messenger import print_message

class Learner(object):
     def __init__(self, server_id, quorum, log = None):
         self.log = []
         self.accept_count = {}
         self.maxCount = 0
         self.valForMaxCount = None
         self.quorum = quorum
         self.learner_id = server_id        

         self.msg_collection = {}
         self.proposal_id = None 

         self.committed_id = None


     def addVote(self, msg):
         if msg['proposal_id'] < self.proposal_id:
             return
         #only consider the proposal with largest id that has been seen by the learner
         self.proposal_id = max(msg['proposal_id'], self.proposal_id)

         if msg['proposal_id'] not in self.accept_count:
             self.accept_count[msg['proposal_id']] = 1
         else:
             self.accept_count[msg['proposal_id']] += 1

         if msg['proposal_id'] not in self.msg_collection:
               self.msg_collection[msg['proposal_id']] = []
         self.msg_collection[msg['proposal_id']].append(msg)
         """
         if self.maxCount < self.count[msg['val']]:
            self.valForMaxCount = msg['val']
            self.maxCount = self.count[msg['val']]
         """
     def checkQuorumSatisfied(self):
         if self.accept_count[self.proposal_id] >= self.quorum:
            return True
         else:
            return False

     def commit(self):
         if self.committed_id is not None and self.proposal_id <= self.committed_id:
             #no need to commit again
             return
         self.committed_id = self.proposal_id
         commit_val = self.msg_collection[self.proposal_id][0]['val']
         client_info = self.msg_collection[self.proposal_id][0]['client_info']
         client_host = client_info['client_host']
         client_port = client_info['client_port']
         self.log.append(commit_val)
         msg = {'type': 'ack', 'val': commit_val, 'client_info': client_info}
         sendMsg(client_host, client_port, msg)
         print_message("==========================learner id %s commit the value: %s"%(str(self.learner_id),str(commit_val)))
         print_message("++++++++++++++++++++++++++learner id %s commit values:"%(str(self.learner_id)))
         print_message(self.log)

     def writeToLog(self, val, slot):
         self.log[slot] = val



