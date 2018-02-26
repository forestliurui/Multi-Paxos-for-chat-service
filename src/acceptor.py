"""
This is the class for acceptor
"""
import socket
from messenger import sendMsg
from messenger import print_message
from state_backup import load_state, save_state

class Acceptor(object):
     def __init__(self, server_id, servers_list, promised_proposal_id, accepted_proposal_id, accepted_proposal_val, accepted_client_info):
         self.server_id = server_id
         self.proposers_list = dict(servers_list)
         #if self.server_id == 0:
         #   import pdb;pdb.set_trace()
         #remove itself from the acceptors list, because it doesn't need to communicate with itself
         del self.proposers_list[self.server_id]
         self.learners_list = self.proposers_list

         #self.host = host
         #self.port = port
         self.promised_proposal_id = promised_proposal_id
         self.accepted_proposal_id = accepted_proposal_id #map from slot_idx to proposal_id
         self.accepted_proposal_val = accepted_proposal_val #map from slot_idx to accepted_val
         self.accepted_client_info = accepted_client_info

     def get_promised_proposal_id(self):
         return self.promised_proposal_id

     def get_accepted_proposal_id(self):
         return self.accepted_proposal_id

     def get_accepted_proposal_val(self):
         return self.accepted_proposal_val

     def get_accepted_client_info(self):
         return self.accepted_client_info
 
     def promise(self, recvd_msg):
         if self.promised_proposal_id is None or recvd_msg['proposal_id'] >= self.promised_proposal_id:
            # save updated state first
            state = load_state(self.server_id)
            state['promised_proposal_id'] = recvd_msg['proposal_id']
            save_state(self.server_id, state)

            self.promised_proposal_id = recvd_msg['proposal_id']
            
            reply_msg = {'type': 'promise', 'accepted_id': self.accepted_proposal_id, 'accepted_val': self.accepted_proposal_val, 'accepted_client_info': self.accepted_client_info, 'proposal_id': recvd_msg['proposal_id'], 'acceptor_id': self.server_id}

            proposer_id = recvd_msg['proposer_id']
            host = self.proposers_list[proposer_id]['host'] 
            port = self.proposers_list[proposer_id]['port']

            sendMsg(host, port, reply_msg)

     def accept(self, recvd_msg):
         if self.promised_proposal_id is None or recvd_msg['proposal_id'] >= self.promised_proposal_id:
            slot_idx = recvd_msg['slot_idx']

            # save updated state first
            state = load_state(self.server_id)
            state['promised_proposal_id'] = recvd_msg['proposal_id']
            state['accepted_proposal_id'][slot_idx] = recvd_msg['proposal_id']
            state['accepted_proposal_val'][slot_idx] = recvd_msg['val']
            state['accepted_client_info'][slot_idx] = recvd_msg['client_info']
            save_state(self.server_id, state)

            self.promised_proposal_id = recvd_msg['proposal_id']
            self.accepted_proposal_id[slot_idx] = recvd_msg['proposal_id']
            self.accepted_proposal_val[slot_idx] = recvd_msg['val']
            self.accepted_client_info[slot_idx] = recvd_msg['client_info']

            reply_msg = {"type": "accept", 'proposal_id': self.accepted_proposal_id[slot_idx], 'val': self.accepted_proposal_val[slot_idx], 'slot_idx': slot_idx, 'client_info': recvd_msg['client_info']}
            self.sendToAllLearners(reply_msg)

     def sendToAllLearners(self, msg):
         for learner_id in self.learners_list:
             host = self.learners_list[learner_id]['host']
             port = self.learners_list[learner_id]['port']
         
             sendMsg(host, port, msg)

