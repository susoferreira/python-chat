#/bin/bash

mkdir ./logs

python3 ./client.pyw > logs/client.log & 
python3 ./server.py > logs/server.log
