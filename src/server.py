# Echo server program
import socket
import pickle
import numpy as np
import collections
import time
import yaml
import os

from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
from messenger import print_message
from state_backup import save_state, load_state, get_state_backup

crash_rate = 0

def server(server_id, config_file = '../config/servers.yaml'):


    server_id = int(server_id) 

    with open(config_file, 'r') as config_handler:
        config = yaml.load(config_handler)

    f = int(config['f']) #the number of failure that can be tolerated

    state_backup_folder = config['state_backup_folder']

    num_server = 2*f + 1

    #host_name = 'bigdata.eecs.umich.edu'
    #servers_list = {idx:{'host': host_name, 'port': 50000+idx} for idx in range(num_server)}

    servers_list = { server_idx: config['servers_list'][server_idx] for server_idx in range(num_server)}

    #Ideally, quorum should be  len(servers_list)/2 + 1
    #I choose len(servers_list)/2, because the current process only send message to other processes
    #thus quorum assumes that itself has already been included 
    quorum = num_server/2 + 1

    # load state
    state_backup = get_state_backup(server_id, state_backup_folder)
    if not os.path.exists(state_backup):
        state = dict(
                view=0,
                decided_log={},
                promised_proposal_id=None,
                accepted_proposal_id={},
                accepted_proposal_val={},
                accepted_client_info={}
            )
        save_state(state_backup, state)
    else:
        print "Recovering server"
        state = load_state(state_backup)

    # state = load_state(state_backup)

    proposer = Proposer(server_id, servers_list)
    acceptor = Acceptor(server_id, servers_list, state['promised_proposal_id'], state['accepted_proposal_id'],
                        state['accepted_proposal_val'], state['accepted_client_info'], state_backup)
    learner = Learner(server_id, quorum, state['decided_log'], state_backup)
    #
    view = state['view']

    num_acceptors = num_server

    HOST = servers_list[server_id]['host']                 # Symbolic name meaning all available interfaces
    PORT = servers_list[server_id]['port']             # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(100)

    #for test case 4 to skip slot x
    if 'x' in config and config['x'] >= 0:
         x = int(config['x'])
    else:
         x = None

    
    if 'num_failed_primary' in config and config['num_failed_primary'] >= 0:
         num_failed_primary = int(config['num_failed_primary'])
    else:
         num_failed_primary = None 


    #x = 3     
    server_skip = 0    
 
    request_val_queue = collections.deque()
    client_info_queue = collections.deque()

    while True:
        
        #try to crash
        if view%num_acceptors == server_id:
           server_crash(server_id, crash_rate)

        print_message("wait for connection")
        conn, addr = s.accept()
        print_message('Connection by '+str(addr))
        data = conn.recv(4096*2)
        msg = pickle.loads(data)      
        print_message('RCVD: '+str(msg))

        if msg['type'] == 'request':
           if msg['resend_idx'] != 0:
              #if this is an resent message, triger view change

              # save updated state first
              state = load_state(state_backup)
              state['view'] = view + 1
              save_state(state_backup, state)

              view += 1
              
              #new leader clears the request queue 
              request_val_queue.clear()
              client_info_queue.clear()

              proposer.need_prepare = True
              print_message("change to view %s"%(str(view)))
           if view%num_acceptors == server_id:
                #this is leader

                #testcase3(server_id, msg, view)
                if num_failed_primary is not None and server_id < num_failed_primary:
                     print_message("force the primary %s to crash"%(str(server_id)))
                     print_message("!!!!!!!!!!!!!!!!server id %s crashes"%(str(server_id)))
                     exit()



                #testcase 4
                if x is not None and x+1 in learner.decided_log and server_skip == server_id:
                     #server_skip = server_id
                     print_message('server id %s has learned slot %s'%(str(server_id), str(x+1)))
                     print_message("!!!!!!!!!!!!!!!!server id %s crashes"%(str(server_id)))
                     exit()

                request_val_queue.append( msg['request_val'] )
                client_info_queue.append( msg['client_info'] )
                if proposer.need_prepare is True:
                    #if msg['client_info']['client_id'] == 0:
                    #    time.sleep(30)         
                    proposer.prepare(view)
                    #proposer.need_prepare = False
        
                else: #directly propose without prepare stage
                    proposal_pack = {}
                    print_message("no need to prepare")
                    print_message(request_val_queue)
                  

                    #server_crash_on_msg(server_id, msg)     
                    #testcase4(msg, proposer)
 
                    for _ in range(len(request_val_queue)):
                        request_val = request_val_queue.popleft()
                        client_info = client_info_queue.popleft()
                        proposal_pack = proposer.addNewRequest(proposal_pack, request_val, client_info)
                    #if skipSlot(msg) is False:

                    #testcase 4
                    if x is not None and x in proposal_pack and server_skip == server_id:
                         print_message('At slot %s: %s'%(str(x), str(proposal_pack[x])))
                         print_message('proposer %s skips slot %s for server_skip %s'%(str(server_id), str(x), str(server_skip)))
                         del proposal_pack[x]        

                    proposer.propose(proposal_pack, without_prepare = True)

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
                if proposer.need_prepare is True:
                    proposal_pack = proposer.getProposalPackForHoles(learner.getDecidedLog())
                    print_message("proposal pack for holes: %s"%(str(proposal_pack)))
                    for _ in range(len(request_val_queue)):
                        request_val = request_val_queue.popleft()
                        client_info = client_info_queue.popleft()
                        proposal_pack = proposer.addNewRequest(proposal_pack, request_val, client_info)  

                    #testcase 4
                    if x is not None and x in proposal_pack and server_skip == server_id:
                         print_message('At slot %s: %s'%(str(x), str(proposal_pack[x])))
                         print_message('proposer %s skips slot %s for server_skip %s'%(str(server_id), str(x), str(server_skip)))
                         del proposal_pack[x]

                    proposer.propose(proposal_pack)
                proposer.need_prepare = False
        elif msg['type'] == 'prepare':
            # save updated state first
            state = load_state(state_backup)
            state['view'] = max(view, msg['proposal_id'])
            save_state(state_backup, state)

            view = max(view, msg['proposal_id'])  # update to most recent view
            print_message("change to max view %s" % (str(view)))
            acceptor.promise(msg)

        elif msg['type'] == 'propose':
            acceptor.accept(msg)

        elif msg['type'] == 'accept':
            slot_idx = msg['slot_idx']
            learner.addVote(msg, slot_idx)
            if learner.checkQuorumSatisfied(slot_idx) is True:
                learner.decide(slot_idx)
                      
        conn.close()

def testcase2(server_id, msg):
    print_message("This is test case 2")
    server_crash_on_msg(server_id, msg)

def testcase3(server_id, msg, view):
    print_message("This is test case 3")
    #primary dies
    server_crash_on_msg(server_id, msg)

    #new primary dies again
    if view == 1:
       print_message("!!!!!!!!!!!!!!!!server id %s crashes"%(str(server_id)))
       exit()

def testcase4(msg, proposer):
    print_message("This is test case 4")
    if skipSlot(msg):
        print_message("skip slot %s"%(str(proposer.next_slot)))
        proposer.next_slot += 1


def server_crash_on_msg(server_id, msg):
    client_info = msg['client_info']
    if client_info['client_id'] == 0  and client_info['clt_seq_num'] == 2 and msg['resend_idx'] == 0:
       print_message("!!!!!!!!!!!!!!!!server id %s crashes"%(str(server_id)))
       exit()


def server_crash(server_id, crash_rate):
    if np.random.rand() < crash_rate:
       print_message("!!!!!!!!!!!!!!!!server id %s crashes"%(str(server_id)))
       exit()

def forceViewChange(msg):
    return False
    client_info = msg['client_info']
    if (client_info['client_id'] == 0 or client_info['client_id'] ==1 ) and client_info['clt_seq_num'] == 3:
       return True
    else:
       return False

def skipSlot(msg):
    client_info = msg['client_info']
    if client_info['client_id'] == 0  and client_info['clt_seq_num'] == 2:
       return True
    else:
       return False


if __name__ == "__main__":
    from optparse import OptionParser, OptionGroup

    parser = OptionParser(usage = "Usage!")
    options, args = parser.parse_args()
    options = dict(options.__dict__)

    server(*args, **options)

