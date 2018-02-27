#!/bin/bash

client_num=$1
config_file_server=$2

for ((i=0;i<${client_num};i=i+1))
do
    echo "start client process: ${i}"
    python client.py ${i} ${config_file_server} &
done

