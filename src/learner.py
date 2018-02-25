"""
This is the Learner class
"""

from messenger import sendMsg
from messenger import print_message

class Slot(object):
     def __init__(self, slot_idx, quorum):
         self.slot_idx = slot_idx
         self.quorum = quorum
         self.accept_count = {}
         self.msg_collection = {}
         self.proposal_id = None
         self.decided_id = None

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


     def checkQuorumSatisfied(self):
         if self.accept_count[self.proposal_id] >= self.quorum:
            return True
         else:
            return False


class Learner(object):
     def __init__(self, server_id, quorum, log = None):
         self.decided_log = {}
         self.executed_log = {}
         self.accept_count = {}
         self.maxCount = 0
         self.valForMaxCount = None
         self.quorum = quorum
         self.learner_id = server_id        

         self.msg_collection = {}
         self.proposal_id = None 

         #self.committed_id = None
         self.decided_id = None
         self.slots = {}

     def getDecidedLog(self):
         return dict(self.decided_log)
         
     def addVote(self, msg, slot_idx):
         if slot_idx not in self.slots:
              self.slots[slot_idx] = Slot(slot_idx, self.quorum)

         self.slots[slot_idx].addVote(msg)
    
     def checkQuorumSatisfied(self, slot_idx):
         return self.slots[slot_idx].checkQuorumSatisfied()

     def decide(self, slot_idx):
         """
         when learner receives accept message from a quorum, he knows that a value has been decided. (It is not the same as executed)
         """
         if self.slots[slot_idx].decided_id is not None and self.slots[slot_idx].proposal_id <= self.slots[slot_idx].decided_id:
             #no need to commit again
             return
         self.slots[slot_idx].decided_id = self.slots[slot_idx].proposal_id
         decided_val = self.slots[slot_idx].msg_collection[self.slots[slot_idx].proposal_id][0]['val']
         client_info = self.slots[slot_idx].msg_collection[self.slots[slot_idx].proposal_id][0]['client_info']
         client_host = client_info['client_host']
         client_port = client_info['client_port']
         self.decided_log[slot_idx] = decided_val
         if decided_val != 'noop':
            msg = {'type': 'ack', 'val': decided_val, 'client_info': client_info}
            sendMsg(client_host, client_port, msg)
         print_message("==========================learner id %s decide the value: %s"%(str(self.learner_id),str(decided_val)))
         print_message("++++++++++++++++++++++++++learner id %s decide values:"%(str(self.learner_id)))
         print_message(self.decided_log)
         self.execute()
 
     def execute(self):
         if len(self.executed_log) == 0:
             next_unexecuted_slot_idx = 0
         else:
             next_unexecuted_slot_idx = max(self.executed_log.keys())
         while next_unexecuted_slot_idx in self.decided_log:
              self.executed_log[next_unexecuted_slot_idx] = self.decided_log[next_unexecuted_slot_idx]
              next_unexecuted_slot_idx += 1
         print_message("<<<<<<<<<<<<<<<<<<<<<<learner id %s executed values: %s"%(str(self.learner_id), str(self.executed_log)))



