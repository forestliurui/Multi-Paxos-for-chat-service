#!/bin/bash

#kill all python processes
#if no user name is provided as argument from command-line, the current user name will be used 

if [ "$1" == "" ]; then
	user=$USER
else
	user=$1
fi

kill -9 `ps  -u ${user} |grep python |awk '{print $1}'`
