#!/bin/bash

for ((i=0;i<5;i=i+1))
do
    echo "start client process: ${i}"
    python client.py ${i} &
done

