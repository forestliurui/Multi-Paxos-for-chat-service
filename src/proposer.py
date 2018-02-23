"""
This is the proposer class
"""

class Proposer(object):
    def  __init__(self, acceptors_list):
         self.acceptors_list = acceptors_list
         self.quorum = len(self.acceptors_list)/2 + 1    

    def tryGetElected(self, proposer_id):
        for acceptor in self.acceptors_list:
            msg = {'type': 'prepare', 'proposer_id': proposer_id}
            self.sendMsg(acceptor, msg)

        vote_num = 0
        msg_list = []
        for acceptor in self.acceptors_list:
            msg = self.recvMsg(acceptor)
            if msg['type'] = "promise":
               msg_list.append(msg)
               vote_num += 1

        if vote_num >= self.quorum:
           proposer_val = self.getValWithLargestProposerID(msg_list)
           return True, proposer_val  #get elected as leader
        else:
           return False, None #not elected



    def getValWithLargestProposerID(self, msg_list):
        largest_id = None
        proposer_val = None
 
        for msg in msg_list:
            if largest_id is None or msg['proposer_id'] >= largest_id:
                if msg['proposer_id'] == largest_id:
                    if proposer_val != msg['proposer_val']:
                        raise ValueError("Different value from the same proposers with id %d"%largest_id)
                largest_id = msg['proposer_id']
                proposer_val = msg['proposer_val']
        return propose_val

    def proposeVal(self, proposer_id, val):
        for acceptor in self.acceptors_list:
            msg = {"type": "propose", 'proposer_id': proposer_id, 'val': val }
            self.sendMsg(acceptor, msg)

