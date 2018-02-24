# Echo client program
import socket
import pickle

from messenger import sendMsg

def client():
    host_name = 'bigdata.eecs.umich.edu'
    servers_list = {idx:{'host': host_name, 'port': 50000+idx} for idx in range(5)}

      

    val = 'how are you'

    msg = {'type': 'request', 'request_val': val, 'resend_idx': 0}
    for server_id in servers_list:
        host = servers_list[server_id]['host']
        port = servers_list[server_id]['port']
    
        sendMsg(host, port, msg) 


if __name__ == "__main__":
   client()
