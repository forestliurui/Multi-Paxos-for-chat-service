# Echo server program
import socket
import pickle

from proposer import Proposer
from acceptor import Acceptor
from learner import Learner

def server(server_id, f = None):

    server_id = int(server_id) 

    host_name = 'bigdata.eecs.umich.edu'
    servers_list = {idx:{'host': host_name, 'port': 50000+idx} for idx in range(5)}

    quorum = len(servers_list)/2

    proposer = Proposer(server_id, servers_list)
    acceptor = Acceptor(server_id, servers_list)
    learner = Learner(quorum)

    view = 0
    num_acceptors = len(servers_list)

    HOST = servers_list[server_id]['host']                 # Symbolic name meaning all available interfaces
    PORT = servers_list[server_id]['port']             # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
 
    while True:
        print("wait for connection")
        conn, addr = s.accept()
        print 'Connected by', addr
        data = conn.recv(1024)
        msg = pickle.loads(data)      

        if msg['type'] == 'request':
           if msg['resend_idx'] != 0:
              #if this is an resent message, triger view change
              view += 1
           if view%num_acceptors == server_id:
                #this is leader
                request_val = msg['request_val']
                proposer.prepare(view)
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
                 accepted_val = proposer.getValWithLargestAcceptedID() 
                 if accepted_val is not None:
                     proposer.propose(accepted_val)
                 else:
                     proposer.propose(request_val)

        elif msg['type'] == 'prepare':
            acceptor.promise(msg)

        elif msg['type'] == 'propose':
            acceptor.accept(msg)

        elif msg['type'] == 'accept':
            learner.addVote(msg)
            if learner.checkQuorumSatisfied() is True:
                learner.commit()
                      
        conn.close()

if __name__ == "__main__":
    from optparse import OptionParser, OptionGroup

    parser = OptionParser(usage = "Usage!")
    options, args = parser.parse_args()
    options = dict(options.__dict__)

    server(*args, **options)

