#!/bin/bash

for ((i=0;i<5;i=i+1))
do
    echo "start server process: ${i}"
    python server.py ${i} &
done

