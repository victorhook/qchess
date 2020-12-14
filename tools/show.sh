#!/bin/bash

PROGRAM=engine_server.py
pids=$(ps -aux | grep $PROGRAM | awk '{print $2}' $processes)

for pid in $pids
do
    if [[ -d /proc/$pid ]]
    then
        echo $pid "running"
    fi;
done
