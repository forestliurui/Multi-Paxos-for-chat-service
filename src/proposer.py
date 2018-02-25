"""
This is the proposer class
"""
import socket
import pickle

from messenger import sendMsg
from messenger import print_message
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

         self.next_slot = 0 #the slot for next client request

         self.need_prepare = True

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
        if self.proposal_id in self.proposal_count and self.proposal_count[self.proposal_id] >= self.quorum:
           return True
        else:
           return False

    def addNewRequest(self, proposal_pack_input, request_val, request_client_info):
        proposal_pack = dict(proposal_pack_input)
        proposal_pack[self.next_slot] = {}
        proposal_pack[self.next_slot]['val'] = request_val
        proposal_pack[self.next_slot]['client_info'] = request_client_info
        
        self.next_slot += 1
        return proposal_pack
           

    def getProposalPackForHoles(self, decided_log):
        msg_list = self.msg_collection[self.proposal_id]
        largest_accepted_id = {} #map from slot_idx to proposal_id
        accepted_val_with_largest_id = {} #map from slot_idx to accepted_val
        accepted_client_info = {} 

        #get info for slot holes with accepted val
        for msg in msg_list:
          for slot_idx, accepted_id in msg['accepted_id'].items():
            if slot_idx not in decided_log:
              #the proposer doesn't know about the decided val for this slot
              if slot_idx not in largest_accepted_id or accepted_id >= largest_accepted_id[slot_idx]:
                if slot_idx in largest_accepted_id and  accepted_id == largest_accepted_id[slot_idx]:
                    if accepted_val_with_largest_id[slot_idx] != accepted_id:
                        raise ValueError("Different accepted values from accepted id: %d for slot %d"%(largest_accepted_id[slot_idx], slot_idx))
                largest_accepted_id[slot_idx] = accepted_id
                accepted_val_with_largest_id[slot_idx] = msg['accepted_val'][slot_idx]
                accepted_client_info[slot_idx] = msg['accepted_client_info'][slot_idx]

        if len(decided_log ) == 0:
            last_slot_decided_log = -1
        else:
            last_slot_decided_log = max(decided_log.keys())
        if len(accepted_val_with_largest_id) == 0:
            last_slot_accepted_val = -1
        else:
            last_slot_accepted_val = max(accepted_val_with_largest_id.keys())

        self.next_slot = max( last_slot_decided_log, last_slot_accepted_val ) + 1

        proposal_pack_for_holes = {}
        for slot_idx in range(self.next_slot-1, -1, -1):
            if slot_idx in accepted_val_with_largest_id:
               accepted_val_with_largest_id[slot_idx] = {'val': accepted_val_with_largest_id[slot_idx], 'client_info': accepted_client_info[slot_idx]}
            elif slot_idx not in decided_log:
               #noop
               accepted_val_with_largest_id[slot_idx] = {'val': 'no-op', 'client_info': None}

        return proposal_pack_for_holes

    def propose(self, proposal_pack):
        if self.proposed_id is not None and self.proposal_id <= self.proposed_id:
           #no need to propose again
           return

        self.proposed_id = self.proposal_id

        for slot_idx in proposal_pack:
           msg = {"type": "propose", 'proposal_id': self.proposal_id, 'val': proposal_pack[slot_idx]['val'], 'slot_idx': slot_idx, 'proposer_id': self.server_id, 'client_info': proposal_pack[slot_idx]['client_info'] }
           for acceptor_id in self.acceptors_list:
              host = self.acceptors_list[acceptor_id]['host']
              port = self.acceptors_list[acceptor_id]['port']

              sendMsg(host, port, msg)

