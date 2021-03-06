from collections import OrderedDict
import pickle
import threading
import socket
import sys

import numpy as np
import lz4.frame

import data_arr as arr
import data_commu as commu

HOST = ''                       # Socket is reachable by any address the machine happens to have
PORT = int(sys.argv[1])         # Port to listen on (non-privileged ports are > 1023)
test_size = int(sys.argv[2])
compression_flag = int(sys.argv[3])
num_thread = int(sys.argv[4])

# Data arrange
data = arr.generate_data(test_size)

threads = OrderedDict()

def threaded(name, p):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, p))
        s.listen(5)
        conn, addr = s.accept()
        print('Connected by socket no.{}, address {}'.format(name, addr))
        with conn:
            if compression_flag == 0:
                commu.transmit_notcompressed(conn,data)
            else:
                commu.transmit_compressed(conn,data)
            print(f"Packet {name} successfully sent the formal data packets")
            confirm = commu.receive(conn)
            if confirm != test_size:
                sys.exit(f"Error: client do not receive all {test_size} bytes data.")

# Create threads
for i in range(1, num_thread+1):
    threads[i] = threading.Thread(target=threaded, args=(i, PORT+i))    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT)) #binds it to a specific ip and port so that it can listen to incoming requests on that ip and port
    s.listen(1) #puts the server into listen mode, allows the server to listen to incoming connections. Passing an empty string means that the server can listen to incoming connections from other computers as well.
    conn, addr = s.accept() #block and wait for an incoming connection
    print('Experiment on {} bytes.\nConnected by {}'.format(test_size, addr))
    with conn: 
        #Reply to client: send a numpy array of 1000 characters
        commu.transmit_notcompressed(conn, arr.data_pre)
        print("Successfully sent the small packet")

        # Formal test
        # Start threads
        for name, thread in threads.items():
            thread.start()

        # Wait until all threads finish their jobs
        for name, thread in threads.items():
            thread.join()

        # Send back a request for closing
        commu.transmit_notcompressed(conn, 0)
        
