#!/bin/bash

server_num=9

for ((i=0;i<${server_num};i=i+1))
do
    echo "start server process: ${i}"
    python server.py ${i} ${server_num}  &
done

