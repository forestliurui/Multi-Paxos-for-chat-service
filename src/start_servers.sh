#!/bin/bash

server_num=$1
config_file=$2

for ((i=0;i<${server_num};i=i+1))
do
    echo "start server process: ${i}"
    python server.py ${i} ${config_file}  &
done

