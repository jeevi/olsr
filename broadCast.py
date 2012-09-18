"""

def setup(node_id, addr, isMPR, mypeer):

    This method takes the arguments, 
    1. addr: The address to which the calling process binds itself to.
    2. isMPR: It is a boolean value. It is True when the calling process [node] is a Multi Point Relay of the source, else it is a two-hop neighbor or a one-hop neighbor which was not selected as an MPR of the source.
    3. node_id: Unique Identifier of the calling process[node] a.k.a receiver
    4. mypeer: It is a list of one-hop neighbors of the calling process[node].
    
def source_setup(node_id, addr, MPRset, oneHop):

    This method takes the arguments,
    1. node_id: Unique Identifier of the calling process[node] a.k.a receiver
    2. addr: The address to which the calling process binds itself to.
    3. MPRset: applicable only to the source node, its set of Multi Point relays.
    4. oneHop: applicable only to the source node, its set of one-hop neighbors who are not its Multi Point relays.

def startBroadcast(MPRset, i, allNeighbor):

    This method takes the arguments,
    1. MPRset: multi point relay set of the source node
    2. i: index of the node
    3. allNeighbor: It is a 2-D list, where each 1-D list in this 2-D list represents the one-hop neighbors of the on-hop neighbors of source node.
       e.g. allNeighbor[3] is a 1-D list of one-hop neighbor of the 4th[only in the list] one-hop neighbor of source.
    
      
"""

import olsr
import sys
import subprocess
import shlex
import logging
from multiprocessing import Process

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s - %(message)s]', datefmt = '%Y-%m-%d %H:%M:%S')

# SETUP THE NODES OTHER THAN THE SOURCE

def setup(node_id, addr, isMPR, mypeer):

    try:
        # NODES INVOKE RECEIVE TO RECEIVE MESSAGES AND INTERMEDIATE NODES ALSO INVOKE THIS TO RECEIVE ACKS FROM THEIR ONEHOP NEIGHBORS
        olsr.receive(addr, isMPR, node_id, mypeer, False)
        
    except KeyboardInterrupt:
        
        print(node_id + " terminated")

# SETUP THE SOURCE NODE

def source_setup(node_id, addr, MPRset, oneHop):

    # PROMPT THE USER TO ENTER THE MESSAGE    
    sys.stdin = open('/dev/tty')
    
    while True:
        # BLOCK TILL THE USER ENTERS A MESSAGE
        msg = raw_input('\n\nEnter message to be transmitted: \n\n')
        # IF A NULL MESSAGE BREAK
        if msg == '':
        
            break

        else:
            # SEND MESSAGE TO THE MULTI POINT RELAYS
            for x in MPRset:
                
                olsr.sendd(msg, True, "tcp://127.0.0.1:555%d" %x, "node0")
            # SEND MESSAGE TO THE ONE HOP NEIGHBORS WHO ARE NOT MULTI POINT RELAYS
            for x in oneHop:
                
                olsr.sendd(msg, True, "tcp://127.0.0.1:555%d" %x, "node0")
                
    # SOURCE INVOKES TO RECEIVE THE ACKS FROM ITS MPRS AND OTHER ONEHOP NEIGHBORS
    olsr.receive(addr, False, node_id, [], True)    
    
def startBroadcast(MPRset, i, allNeighbor):

    for j in MPRset:
        # SPAWN THE MULTI POINT RELAY NODES [PROCESSES]
        print('node%d' % j + " says: my address is " + "127.0.0.1:555%d" % j)
        Process(target=setup, args=('node%d' % j, "tcp://127.0.0.1:555%d" % j, True, allNeighbor[j])).start()
     
        for each in allNeighbor[j]:
            # FOR EACH MULTI POINT RELAY SPAWN THEIR ONE HOP NEIGHBORS
            print('node%d' % each + " says: my address is " + "127.0.0.1:655%d" % each)
            Process(target=setup, args=('node%d' % each, "tcp://127.0.0.1:655%d" % each, False, [])).start()
             
    # ONE HOP NEIGHBORS OF THE SOURCE WHO ARE MPRS
    oneHop = list(set(MPRset)&set(allNeighbor[0]))
    # REMOVE THEM FROM THE NEIGHBORSET OF SOURCE
    for j in oneHop:
    
        allNeighbor[0].remove(j)
        
    print allNeighbor[0]
    # SPAWN ONE HOP NEIGHBOR PROCESSES
    for each in allNeighbor[0]:
        
        print('node%d' % each + " says: my address is " + "127.0.0.1:555%d" % each)
        Process(target=setup, args=('node%d' % each, "tcp://127.0.0.1:555%d" % each, False, [])).start()
            
    #SPAWN SOURCE NODE
    source_addr = "tcp://127.0.0.1:5550"
    print('node0'  + " says: I am the source node, my address is " + source_addr)
    Process(target=source_setup, args=('node0', source_addr, MPRset, allNeighbor[0],)).start()
    
    
 

