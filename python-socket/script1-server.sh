#!/bin/bash
PORT=60000
for((data_size=10000; data_size<=10000000; data_size*=10))
do
	for ((i=0; i<7; i++))
	do
		#redirect both output and errors to experiment1-server.log
		python3 $1 "$PORT" "$data_size" "$2" "$3"
		let "PORT+=10"
	done
done 	
	