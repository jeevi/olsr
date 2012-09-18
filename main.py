
""" 
This is the main program. upon executing "python main.py" on the console, this program, reads the first line from the input file named 'input'. The first
line must be the number of processes [nodes] in the network. This is needed to initialize the 2-D list of size n*n [n - number of nodes], which contains a mapping of links between different nodes. Next, ths control enters an infinite loop, in which the 'edge' information between two nodes is read, the control breaks out of the loop when an EOF is encountered in the file 'input'. the link information is stored in the 'edges' list. From here, the method getMPR is called , it exists in the olsr API file olsr.py. 


sample input file ---

7\n
0,1\n
0,2\n
0,3\n
0,4\n
1,5\n
1,6\n
2,4\n
3,5\n


As we can see, the first line contains 7, which is the number of nodes in the network. the following lines after this give the information about the links between nodes. e.g. take 0,1 means that there is a link between node0 and node1.

"""

import sys
import broadCast
import olsr


f = open("input", 'r')
thr = int(f.readline()[:-1])
f.close()
nodes = [0]*thr
edges = [[0 for x in range(thr)] for x in range(thr)] 

print("Enter the links between the nodes, ex. 1,2 implies there is a bi-directional link between node1 and node2. Also once done, type 'done' and press enter")

f = open("input", 'r')

while True:
    
    # read each line from the input file
    line = f.readline()[:-1]
    
    if line == '':
        #if EOF break
        break
        
    else:
               
        try:
            #split a,b at ',' 
            temp = line.split(',')
            a = int(temp[0])
            b = int(temp[1])
            
            edges[b][a] = 1
            edges[a][b] = 1

        except IndexError:
            
            continue

f.close()
i = 0
p = 0

neighborset = [[0 for x in range(thr)] for x in range(thr)] 

# for each edge finding their one hop neighbours

for each in edges:

    temp1 = []
    j = 0

    for x in each:      

        if x==1:

            temp1.append(j)
        j=j+1

    neighborset[p] = temp1            
    p=p+1
    i=i+1

i = -1
    
while(i<0):

    i = i + 1
    # get the multi point relays for the source node i.
    Set = olsr.GetMPR(neighborset, thr, i)
   
#start the broadcast
broadCast.startBroadcast(Set[-1], i, Set)

