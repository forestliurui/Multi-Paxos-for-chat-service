# Echo client program
import socket
import pickle
import yaml

from my_logging import MyLogging
from messenger_class import Messenger

timeout = 20

def client(client_idx, config_file_server = '../config/servers.yaml'):

    host_name = 'localhost'
    clients_list = {idx:{'host': host_name, 'port': 40000+idx} for idx in range(10)} 

    with open(config_file_server, 'r') as config_handler:
        config = yaml.load(config_handler)
    f = int(config['f']) #the number of failure that can be tolerated
    num_server = 2*f + 1
    servers_list = { server_idx: config['servers_list'][server_idx] for server_idx in range(num_server)}
    loss_rate = config['msg_drop_rate']

    my_messenger = Messenger(loss_rate)
      
    client_idx = int(client_idx)
    client_host = clients_list[client_idx]['host']
    client_port = clients_list[client_idx]['port']

    request_size = 5
    request_list = ['client, seq: (%s, %s)'%(str(client_idx), str(request_idx) ) for request_idx in range(request_size) ]
    
    for request_idx in range(len(request_list)):
        clt_seq_num = request_idx
        val = request_list[request_idx]
        resend_idx = 0
        while True:
            client_info = { 'clt_seq_num': clt_seq_num, 'client_id': client_idx, 'client_host': client_host, 'client_port': client_port }
            msg = {'type': 'request', 'request_val': val, 'resend_idx': resend_idx, 'client_info': client_info}
            for server_id in servers_list:
                host = servers_list[server_id]['host']
                port = servers_list[server_id]['port']
    
                # send msg to (host, port)
                my_messenger.send_msg(host, port, msg)
            
            if waitForAck(client_host, client_port, timeout, clt_seq_num) is True:
               break

            resend_idx += 1

    MyLogging.info('client %s finished sending all %s requests'%(str(client_idx), str(len(request_list)) )) 

def waitForAck(client_host, client_port, timeout, clt_seq_num):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((client_host, client_port))
    s.listen(100)
    

    while True:
       MyLogging.debug('set timeout for %s s'%str(timeout))
       s.settimeout(timeout)
       MyLogging.debug("wwwwwwwwwwwwwwwait for ack")
       try: 
          conn, addr = s.accept()
       except socket.timeout:
          MyLogging.debug("timeout on ack")
          return False
       MyLogging.debug('Connected by '+str( addr))
       data = conn.recv(4096*2)
       msg = pickle.loads(data)
       MyLogging.debug('RCVD: '+str(msg))
       conn.close()

       #wait for the right clt_seq_num
       if msg['type'] == 'ack' and msg['client_info']['clt_seq_num'] == clt_seq_num:
           MyLogging.debug('client %s received ack for request (clt seq num) %s'%(str(msg['client_info']['client_id']), str(msg['client_info']['clt_seq_num'])) )
           return True

if __name__ == "__main__":
    from optparse import OptionParser, OptionGroup

    parser = OptionParser(usage = "Usage!")
    options, args = parser.parse_args()
    options = dict(options.__dict__)

    client(*args, **options)



