#!/bin/bash

client_num=4

for ((i=0;i<${client_num};i=i+1))
do
    echo "start client process: ${i}"
    python client.py ${i} &
done

