"""
This is the API file for my OLSR protocol implementation. The methods defined in this file are as follows:

def all_indices(value, qlist):

     This method takes the arguments value and a list qlist. it returns the list containing the indices of the 'value' in qlist.
    
def receive(addr, isMPR, i, mypeer, source):

     This method takes the arguments, 
    1. addr: The address to which the calling process binds itself to.
    2. isMPR: It is a boolean value. It is True when the calling process [node] is a Multi Point Relay of the source, else it is a two-hop neighbor or a one-hop neighbor which was not selected as an MPR of the source.
    3. i: Unique Identifier of the calling process[node] a.k.a receiver
    4. mypeer: It is a list of one-hop neighbors of the calling process[node].
    5. source: It is a boolean value, True only for the source node.
    
def sendd(mesg, isMPR, worker_addr, me):

     This method takes the arguments, 
    1. mesg: It is a string, representing the message to be sent.
    2. isMPR: It is a boolean value. It is True when the calling process [node] is a Multi Point Relay of the source, else it is a two-hop neighbor or  a one-hop neighbor which was not selected as an MPR of the source.
    3. worker_addr: It is the receiver[IP+Port number] to whom the message is to be sent.
    4. me: Unique Identifier of the calling process[node] a.k.a sender

def GetMPR(allNeighbor, thr, i):

     This method takes the arguments, 
    1. allNeighbor: It is a 2-D list, where each 1-D list in this 2-D list represents the one-hop neighbors of the on-hop neighbors of source node.
        e.g. allNeighbor[3] is a 1-D list of one-hop neighbor of the 4th[only in the list] one-hop neighbor of source.
    2. thr: It is the number of processes [nodes].
    3. i: the Identifier of the node whose Multi Point Relays are to be found.


zmq - zeromq, The socket library that provides a API framework for sending messages in IPC. for more information goto - http://www.zeromq.org/
"""

import Node
import zmq
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s - %(message)s]', datefmt = '%Y-%m-%d %H:%M:%S')
# RETURN THE SET OF INDICES OF value IN qlist

def all_indices(value, qlist):

    indices = []
    idx = -1
    
    while True:

        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
            
        except ValueError:
            break
            
    return indices     
# RECEIVE MESSAGES
def receive(addr, isMPR, i, mypeer, source):

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(addr)
    logging.debug(str(i)+ ": is being bound to its address - " + addr)
    # IF A MULTI POINT RELAY DO THIS
    if(isMPR):
    
        while True:
            
            msg = socket.recv()
            logging.debug( str(i) + ": received "+ str(msg))
            time.sleep(1)    
            socket.send("ACK of receipt of message: "+str(msg) + " by " + str(i))
            logging.debug(str(i) + ": Forwarding to my oneHop neighbors ...")
                
            for each in mypeer:
            # SEND MESSAGE TO EACH PEER
                sendd(msg, False, "tcp://127.0.0.1:655%d" %each, i)
                
    # IF NOT AN MPR DO THIS                   
    else:
    
        while True:
    
            msg = socket.recv()    
            logging.debug( str(i) + ": received "+ str(msg))
            time.sleep(1)
            if(not source):
                socket.send("ACK of receipt of message: "+str(msg) + " by " + str(i))
                        
# SEND MESSAGE
def sendd(mesg, isMPR, worker_addr, me):
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(worker_addr)
    
    if worker_addr[16:17] == '6':
        to = "node"+ worker_addr[19:]
    elif worker_addr[16:17] == '5':
        to = "node"+ worker_addr[19:]
        
    logging.debug(str(me) + " sending message to: " + to)    
    socket.send(mesg)    
    msg = socket.recv()
    logging.debug(msg) 
# GET THE MPR SET OF THE NODE i
def GetMPR(allNeighbor, thr, i):

    each = allNeighbor[0]
    degree = [0]*thr
    twoHop = []
    MPRset = []
        
    print("\nnode"+str(i)+" says : my one-hop neighbors are as follows---")
    print("------------------------------------------------------")
    print(each)
    print("------------------------------------------------------")
    # FIND THE TWO-HOP NEIGHBOR SET OF THE SOURCE NODE
    
    for l in each:
    
        for pseudo in allNeighbor[l]:
        
            if pseudo in each:
                continue
        
            else:
                twoHop.append(pseudo)
        
    while i in twoHop:
        twoHop.remove(i)
                    
    twoHop = list(set(twoHop))
    laterUse = twoHop[:]
    
    print("\nnode"+str(i)+" says : my two-hop neighbors are as follows---")
    print("------------------------------------------------------")
    print(twoHop)
    print("------------------------------------------------------")
    print("\n\n")
    
    # FOR EACH ONE-HOP NEIGHBOR OF THE SOURCE COMPUTE THE DEGREE
    for node in each:
    
        temp = allNeighbor[node]
                   
        degree[node] = 0
        
        for p in temp:
            
            flag = False
            for q in each:
            
                if (p==q or p==i):
                    flag = True
            
            if(not flag):
                degree[node] = degree[node] + 1
               
        # IF A TWO HOP NEIGHBOR OF THE SOURCE HAS ONLY ONE ONE-HOP NEIGHBOR WHICH IS A ONE-HOP NEIGHBOR OF THE SOURCE, REMOVE IT FROM THE TWO-HOP NEIGHBOR SET AND ADD THE ONE-HOP NEIGHBOR TO THE MPR SET 
        
        for p in temp:
             if(len(allNeighbor[p])==1):
                 MPRset[len(MPRset):] = allNeighbor[p]
                 for element in twoHop:
                     if (element==p):
                         twoHop.remove(p)
            
    reach = [0]*len(each)            
    # IF THERE ARE STILL SOME NODES IN THE TWO-HOP SET DO THE FOLLOWING
    while(len(twoHop)>0):
   
        j = 0
        # CALCULATE THE REACHABILITY OF EACH ONE-HOP NEIGHBOR SET OF THE SOURCE
        for n in each:
             reach[j] = len(set(allNeighbor[n])&set(twoHop))
             j = j+1
        # CALCULATE THE MAX OF THE REACHABILITY SET
        w = max(reach)
        ix = all_indices(w, reach)
        
        if(len(ix)>1):
        
            MAX=0
            m=0
        
            for idx in ix:
        
                if(degree[idx]>MAX):
        
                    MAX=degree[idx]
                    m=idx
        
            MPRset.append(each[m])
            rem = list(set(allNeighbor[each[m]])&set(twoHop))
        
        else:
            
            MPRset.append(each[ix[0]])
            rem = list(set(allNeighbor[each[ix[0]]])&set(twoHop))
                     
        for z in rem:
            twoHop.remove(z)
            

    MPRset = list(set(MPRset))
    print("\nnode"+str(i)+" says : MPR set is as follows---")
    print("------------------------------------------------------")
    print(MPRset)
    print("------------------------------------------------------")
    print("\n\n")
    
    for l in allNeighbor[0]:
        
        allNeighbor[l] = list(set(laterUse)&set(allNeighbor[l]))

        for k in allNeighbor[l]:

            laterUse.remove(k)
    
    allNeighbor.append(MPRset)
    
    return allNeighbor
