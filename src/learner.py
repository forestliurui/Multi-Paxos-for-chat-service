"""
This is the Learner class
"""

from state_backup import save_state, load_state, get_state_backup
from my_logging import MyLogging
from messenger_class import Messenger

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
             self.accept_count[msg['proposal_id']] = {}
         
         self.accept_count[msg['proposal_id']][msg['acceptor_id']] = True

         if msg['proposal_id'] not in self.msg_collection:
               self.msg_collection[msg['proposal_id']] = []
         self.msg_collection[msg['proposal_id']].append(msg)         

     def checkQuorumSatisfied(self):
         if len(self.accept_count[self.proposal_id]) >= self.quorum:
            return True
         else:
            return False


class Learner(object):
     def __init__(self, server_id, quorum, decided_log, state_backup, loss_rate, log = None):
         self.messenger = Messenger(loss_rate)
         self.decided_log = decided_log
         self.state_backup = state_backup
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
         self.decided_clt_seq = {}

         self.execute()  # recovery

     def getDecidedLog(self):
         return dict(self.decided_log)
         
     def addVote(self, msg, slot_idx):
 
         if msg['val'] != 'no-op': 
             #avoid adding the same request (clt_seq_num) from the same client
             client_id =  msg['client_info']['client_id']
             client_seq =  msg['client_info']['clt_seq_num']

             #if client_id in self.decided_clt_seq and self.decided_clt_seq[client_id] >= client_seq:
             #    return
             
         if slot_idx not in self.slots:
              self.slots[slot_idx] = Slot(slot_idx, self.quorum)

         self.slots[slot_idx].addVote(msg)
    
     def checkQuorumSatisfied(self, slot_idx):
         if slot_idx not in self.slots:
            return False
         return self.slots[slot_idx].checkQuorumSatisfied()

     def decide(self, slot_idx):
         """
         when learner receives accept message from a quorum, he knows that a value has been decided. (It is not the same as executed)
         """
         #if self.slots[slot_idx].decided_id is not None and self.slots[slot_idx].proposal_id <= self.slots[slot_idx].decided_id:
         #    #no need to commit again
         #    return

         self.slots[slot_idx].decided_id = self.slots[slot_idx].proposal_id
         decided_val = self.slots[slot_idx].msg_collection[self.slots[slot_idx].proposal_id][0]['val']
         client_info = self.slots[slot_idx].msg_collection[self.slots[slot_idx].proposal_id][0]['client_info']

         # save updated state first
         state = load_state(self.state_backup)
         state['decided_log'][slot_idx] = decided_val
         save_state(self.state_backup, state)

         self.decided_log[slot_idx] = decided_val
         if decided_val != 'no-op':
            client_host = client_info['client_host']
            client_port = client_info['client_port']
            client_id = client_info['client_id']
            client_seq = client_info['clt_seq_num']
            self.decided_clt_seq[client_id] = client_seq
            msg = {'type': 'ack', 'val': decided_val, 'client_info': client_info}
            self.messenger.send_msg(client_host, client_port, msg)
         MyLogging.debug("==========================learner id %s decide the value: %s"%(str(self.learner_id),str(decided_val)))
         MyLogging.debug("++++++++++++++++++++++++++learner id %s decide values:"%(str(self.learner_id)))
         MyLogging.debug(self.decided_log)
         self.execute()
 
     def execute(self):
         if len(self.executed_log) == 0:
             next_unexecuted_slot_idx = 0
         else:
             next_unexecuted_slot_idx = max(self.executed_log.keys())
         while next_unexecuted_slot_idx in self.decided_log:
              self.executed_log[next_unexecuted_slot_idx] = self.decided_log[next_unexecuted_slot_idx]
              next_unexecuted_slot_idx += 1
         MyLogging.info("learner id %s executed values: %s"%(str(self.learner_id), str(self.executed_log)))
         MyLogging.info("learner id %s executed hash: %s"%(str(self.learner_id), str(hash(tuple(self.executed_log.items()))  )))


