"""
This is the server or replica process for multi-paxos
"""
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
from state_backup import save_state, load_state, get_state_backup
from my_logging import MyLogging
from subprocess import call

crash_rate = 0

def server(server_id, config_file = '../config/servers.yaml'):

    server_id = int(server_id) 

    #load config file
    with open(config_file, 'r') as config_handler:
        config = yaml.load(config_handler)

    f = int(config['f']) #the number of failure that can be tolerated

    state_backup_folder = config['state_backup_folder']
    if not os.path.exists(state_backup_folder):
        call(['mkdir', '-p', state_backup_folder])

    num_server = 2*f + 1
    servers_list = { server_idx: config['servers_list'][server_idx] for server_idx in range(num_server)}

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
        MyLogging.info("Recovering server")
        state = load_state(state_backup)

    loss_rate = config['msg_drop_rate']
    proposer = Proposer(server_id, servers_list, loss_rate)
    acceptor = Acceptor(server_id, servers_list, state['promised_proposal_id'], state['accepted_proposal_id'],
                        state['accepted_proposal_val'], state['accepted_client_info'], state_backup, loss_rate)
    learner = Learner(server_id, quorum, state['decided_log'], state_backup, loss_rate)

    #initialize view. The view will be used for proposal_id for elected leader
    view = state['view']

    num_acceptors = num_server

    HOST = servers_list[server_id]['host']       
    PORT = servers_list[server_id]['port']      
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

    #for test 4 to specify the server on which the skipped slot occurs
    server_skip = 0    
 
    request_val_queue = collections.deque()
    client_info_queue = collections.deque()

    while True: 
        #try to crash
        if view%num_acceptors == server_id:
           server_crash(server_id, crash_rate)

        MyLogging.debug("wait for connection")
        conn, addr = s.accept()
        MyLogging.debug('Connection by '+str(addr))
        data = conn.recv(4096*2)
        msg = pickle.loads(data)      
        MyLogging.debug('RCVD: '+str(msg))

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
              MyLogging.debug("change to view %s"%(str(view)))

           if view%num_acceptors == server_id:
                #this is leader

                #testcase 2 and 3
                if num_failed_primary is not None and server_id < num_failed_primary:
                     MyLogging.info("force the primary %s to crash"%(str(server_id)))
                     MyLogging.error("server id %s crashes"%(str(server_id)))
                     exit()

                #testcase 4
                if x is not None and x+1 in learner.decided_log and server_skip == server_id:
                     #server_skip = server_id
                     MyLogging.info('server id %s has learned slot %s'%(str(server_id), str(x+1)))
                     MyLogging.error("server id %s crashes"%(str(server_id)))
                     exit()

                request_val_queue.append( msg['request_val'] )
                client_info_queue.append( msg['client_info'] )

                if proposer.need_prepare is True:
                    proposer.prepare(view)
        
                else: #directly propose without prepare stage
                    proposal_pack = {}
                    MyLogging.debug("no need to prepare")
                    MyLogging.debug(request_val_queue)
                  
                    for _ in range(len(request_val_queue)):
                        request_val = request_val_queue.popleft()
                        client_info = client_info_queue.popleft()
                        proposal_pack = proposer.addNewRequest(proposal_pack, request_val, client_info)

                    #testcase 4
                    if x is not None and x in proposal_pack and server_skip == server_id:
                         MyLogging.debug('At slot %s: %s'%(str(x), str(proposal_pack[x])))
                         MyLogging.debug('proposer %s skips slot %s for server_skip %s'%(str(server_id), str(x), str(server_skip)))
                         del proposal_pack[x]        

                    proposer.propose(proposal_pack, without_prepare = True)

        elif msg['type'] == 'promise':
             proposer.addVote(msg)
             if proposer.checkQuorumSatisfied() is True:
                if proposer.need_prepare is True:
                    proposal_pack = proposer.getProposalPack(learner.getDecidedLog())
                    MyLogging.debug("proposal pack for holes: %s"%(str(proposal_pack)))
                    for _ in range(len(request_val_queue)):
                        request_val = request_val_queue.popleft()
                        client_info = client_info_queue.popleft()
                        proposal_pack = proposer.addNewRequest(proposal_pack, request_val, client_info)  

                    #testcase 4
                    if x is not None and x in proposal_pack and server_skip == server_id:
                         MyLogging.debug('At slot %s: %s'%(str(x), str(proposal_pack[x])))
                         MyLogging.debug('proposer %s skips slot %s for server_skip %s'%(str(server_id), str(x), str(server_skip)))
                         del proposal_pack[x]

                    proposer.propose(proposal_pack)
                proposer.need_prepare = False

        elif msg['type'] == 'prepare':
            # save updated state first
            state = load_state(state_backup)
            state['view'] = max(view, msg['proposal_id'])
            save_state(state_backup, state)

            view = max(view, msg['proposal_id'])  # try to catch up with the most recent view
            MyLogging.debug("change to max view %s" % (str(view)))
            acceptor.promise(msg)

        elif msg['type'] == 'propose':
            acceptor.accept(msg)

        elif msg['type'] == 'accept':
            slot_idx = msg['slot_idx']
            learner.addVote(msg, slot_idx)
            if learner.checkQuorumSatisfied(slot_idx) is True:
                learner.decide(slot_idx)
                      
        conn.close()

#the following are some auxilliary functions for more test cases
#they are not needed now, because the standard test cases are in config files
def testcase2(server_id, msg):
    MyLogging.debug("This is test case 2")
    server_crash_on_msg(server_id, msg)

def testcase3(server_id, msg, view):
    MyLogging.debug("This is test case 3")
    #primary dies
    server_crash_on_msg(server_id, msg)

    #new primary dies again
    if view == 1:
       MyLogging.error("server id %s crashes"%(str(server_id)))
       exit()

def testcase4(msg, proposer):
    MyLogging.debug("This is test case 4")
    if skipSlot(msg):
        MyLogging.debug("skip slot %s"%(str(proposer.next_slot)))
        proposer.next_slot += 1


def server_crash_on_msg(server_id, msg):
    client_info = msg['client_info']
    if client_info['client_id'] == 0  and client_info['clt_seq_num'] == 2 and msg['resend_idx'] == 0:
       MyLogging.error("server id %s crashes"%(str(server_id)))
       exit()


def server_crash(server_id, crash_rate):
    if np.random.rand() < crash_rate:
       MyLogging.error("server id %s crashes"%(str(server_id)))
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

