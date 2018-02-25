# Echo server program
import socket
import pickle
import numpy as np

from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
from messenger import print_message

crash_rate = 0

def server(server_id, num_server, f = None):

    server_id = int(server_id) 
    num_server = int(num_server)

    host_name = 'bigdata.eecs.umich.edu'
    servers_list = {idx:{'host': host_name, 'port': 50000+idx} for idx in range(num_server)}

    #Ideally, quorum should be  len(servers_list)/2 + 1
    #I choose len(servers_list)/2, because the current process only send message to other processes
    #thus quorum assumes that itself has already been included 
    quorum = len(servers_list)/2

    proposer = Proposer(server_id, servers_list)
    acceptor = Acceptor(server_id, servers_list)
    learner = Learner(server_id, quorum)

    view = 0
    num_acceptors = len(servers_list)

    HOST = servers_list[server_id]['host']                 # Symbolic name meaning all available interfaces
    PORT = servers_list[server_id]['port']             # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
 
    while True:
        
        #try to crash
        if view%num_acceptors == server_id:
           server_crash(server_id, crash_rate)

        print_message("wait for connection")
        conn, addr = s.accept()
        print_message('Connected by '+str(addr))
        data = conn.recv(1024)
        msg = pickle.loads(data)      

        if msg['type'] == 'request':
           if msg['resend_idx'] != 0:
              #if this is an resent message, triger view change
              view += 1
              proposer.need_prepare = True

           if view%num_acceptors == server_id:
                #this is leader
                request_val = msg['request_val']
                client_info = msg['client_info']
                if proposer.need_prepare is True:
                    proposer.prepare(view)
                    proposer.need_prepare = False
                """
                election_result, proposer_val  = proposer.tryGetElected()
                if election_result is True:
                    #get elected
                    if proposer_val is None:
                        proposer_val = msg["proposer_val"]
                    #proposer a value
                    proposer.propose(proposer_val)
                """
        elif msg['type'] == 'promise':
             proposer.addVote(msg)
             if proposer.checkQuorumSatisfied() is True:
                 proposal_pack_for_holes = proposer.getProposalPackForHoles(learner.getDecidedLog())
                 proposal_pack = proposer.addNewRequest(proposal_pack_for_holes, request_val, client_info)  
                 proposer.propose(proposal_pack)

        elif msg['type'] == 'prepare':
            acceptor.promise(msg)

        elif msg['type'] == 'propose':
            acceptor.accept(msg)

        elif msg['type'] == 'accept':
            slot_idx = msg['slot_idx']
            learner.addVote(msg, slot_idx)
            if learner.checkQuorumSatisfied(slot_idx) is True:
                learner.decide(slot_idx)
                      
        conn.close()

def server_crash(server_id, crash_rate):
    if np.random.rand() < crash_rate:
       print_message("!!!!!!!!!!!!!!!!server id %s crashes"%(str(server_id)))
       exit()

if __name__ == "__main__":
    from optparse import OptionParser, OptionGroup

    parser = OptionParser(usage = "Usage!")
    options, args = parser.parse_args()
    options = dict(options.__dict__)

    server(*args, **options)

