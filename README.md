# Multi-Paxos for chat service

by Rui Liu (ruixliu@umich.edu) and Changfeng Liu (changfel@umich.edu)

## Overview
This project contains a Python implementation of the Multi-Paxos for replicated chat service. Clients connect to service and send chat messages. The Multi-Paxos based service is like a state-machine replication, where messages will be replicated on several different replicas or servers. 

We also implemented the recovery mechanism using stable storage. Each server process will automatically write its relevant status into file in disk. When we restart it after its crash, it will automatiicaly restore status from disk and keep running.

## Contents
* directory src/ contains the source code
* directory config/ contains the configuration files for different test cases
* directory state_backup/ contains the backup files that are used for recovery in case of server crash

## How to Use
Make sure you are under the src/ directory before you try to run any of the following commands
### Script mode 
To run servers:
```bash
python server_script_mode.py path_to_config_file
```
It will spawn 2f+1 server processes where information such as f is specified in config file.

To run clients:
```bash
bash start_clients.sh num_clients path_to_config_file
```
It will start num_clients number of client processes, and start to connect to servers, where information about servers is specified in the same config file.

### Manual mode
To run server processes separately:
```bash
python server.py server_id path_to_config_file
```
It will create a single server process with id being server_id. Note that server_id starts from 0 and should be less than 2f+1.

To run clients: the same as Script mode.

### To stop
To stop all python processes, including servers and clients
```bash
bash kill_pythons.sh
```
Note that, as a side effect, the users may not need to pay attention, the above command will also clear all the backup files. 

### To recover
To recover a server process after its crash, just restart it, i.e. use the same comand that is used to run the server. After restart, the server process will check the backup file in the disk and store status from it.
```bash
python server.py server_id path_to_config_file
```

## Test Cases
We use different config files for different test cases.
### Test case 1: normal operation
The hash value of the chat logs, i.e. executed log in our code will be printed on screen. 
```bash
python server.py server_id ../config/servers_test1.yaml
bash start_clients.sh num_clients ../config/servers_test1.yaml
```

### Test case 2: primary dies
```bash
python server.py server_id ../config/servers_test2.yaml
bash start_clients.sh num_clients ../config/servers_test2.yaml
```

### Test case 3: primary dies repeatedly up to f times
You can change the field num_failed_primary in file ../config/servers_test3.yaml to specify how many times primaries will die. The default value for num_failed_primary is 2. The protocal will continue for as manay as f times of primary death.
```bash
python server.py server_id ../config/servers_test3.yaml
bash start_clients.sh num_clients ../config/servers_test3.yaml
```

### Test case 4: skipped slot
You can change the field x in file ../config/servers_test4.yaml to specify which slot to skip. The default value for x is 3. The skipped slot will be filled with no-op by new primary.
```bash
python server.py server_id ../config/servers_test4.yaml
bash start_clients.sh num_clients ../config/servers_test4.yaml
```

### Test case 5: message loss
You can change the field msg_drop_rate in file ../config/servers_test5.yaml to specify the drop rate of messages. The default value for msg_drop_rate is 0.05. 
```bash
python server.py server_id ../config/servers_test5.yaml
bash start_clients.sh num_clients ../config/servers_test5.yaml
```


