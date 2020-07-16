import networkx as nx
import matplotlib.pyplot as pl
import math
import numpy

def plot(l,L,P,color_map):
    
    #create a visual graph of the input
    G=nx.DiGraph()
    for i in range(len(l)):
        G.add_node(i)
    for i in range(len(l)):
        for j in l[i].keys():
            G.add_edge(i,j)
    pl.figure()
    
    #Position the nodes in a circle, add label about length and predecessor
    pos={}
    for i in range(len(l)):
        pos[i] = [math.sin(math.pi*2*i/(len(l))),math.cos(math.pi*2*i/(len(l)))]
    for i in range(len(l)):
        pl.text(pos[i][0]*1.5,pos[i][1]*1.5, s= f"(L={L[i]}, P={P[i]})", horizontalalignment='center')
    


    nx.draw(G, node_color=color_map, pos = pos, with_labels=True)
    #Add the length of each line as a label
    for node1, (x1,y1) in pos.items():
        for node2,length in l[node1].items():
            (x2,y2) = pos[node2]
            pl.text(.2*x1+.8*x2,.2*y1+.8*y2,s=str(length))
    #display
    pl.show()
    pl.close()


def negative_length_cycle_finder(l,node,L,P,color_map):
    c=[]
    for i in range(len(l)*2):
        c.append(node)
        #it's in the cycle, so you can go from it to itself with less than
        #0 distance; length = - infinity
        color_map[node]='orange'
        plot(l,L,P,color_map)
        L[node]=-math.inf
        #These lines make a list c that goes backwards from the starting node until it
        #reaches a node that this list c has already reached by going backwards.
        
        
        node=P[node]
        
        if node in c:
            
            cycle=[node]+c[:c.index(node):-1]+[node]
            #cycle is the negative length cycle we've found
            
            #then it looks at every node reachable from this, in any number of steps...
            A=[node]
            L[node]=-math.inf
            color_map[node]='orange'
            for a in A:
                for b in l[a]:
                    if b not in A:
                        A.append(b)
                        color_map[b]='orange'
                        #...and sets their length to -infinity accordingly
                        L[b]=-math.inf
            plot(l,L,P,color_map)
            return cycle,L



def Pathgrapher(l,st):
    '''Take in a list of dictionaries representing a mathematical graph or
    network with the index of each dictionary being a node, the keys within 
    each dictionary being another node, and the value for that key in that
    dictionary is the length of the edge between them, and a starting node.
    
    At every iteration it produces a visual graph displaying which nodes have
    recently been explored and which soon will be. 
    
    Returns a Length dictionary with keys of each destination, and values of
    the distance needed to travel to get to it, and a Journeys dictionary with
    the journey needed to get to them.
    
    If, however, there exists a journey from a node to itself, this journey is
    returned instead, along with the Lengths dictionary, showing which nodes
    are affected.'''
        
    tr=0
    for i in range(1,len(l)-2):
        tr+=i
    
    #E is the list of nodes that have been and will be explored
    E=[st]
    #L is the dictionary of the total length needed to get from the start node
    #to each other node. The total distance s -> node
    L=dict()
    #P is the dictionary of the immediate predesessors of each node in the path
    #to reach it i.e. 3:2 means the shortest path to 3 ends with going from 2 to 3.
    #Will be replaced by J, the Journey, at the end.
    P=dict()
    
    #Nothing has a predesessor yet. Assume length is infinite, for comparative purposes.
    for n in range(len(l)):
        L[n]=math.inf
        P[n]='-'
    #starting at s means it has length 0
    L[st]=0
    
    #Blue nodes this algorithm doesn't know of yet.
    #Red nodes will soon be explored
    #Green nodes have recently been explored
    color_map = ['blue' for i in range(len(l))]
    color_map[st]='red'
    
    #draws a visual representation of the algorithm's current state
    plot(l,L,P,color_map)
    s=0
    for p, m in enumerate(E):
        #p is the index and m is the node
        
        for node, length in l[m].items():
            #for the nodes you can get to immediately from m
            #with length being the distance from m to node
            
            #If the length of the new path (st->m + m->node)
            #is less than the length you already have set for it:
            if length + L[m] < L[node]:
                
                #set that new, shorter length as what we have as the distance
                #to that node, and the predecessor is the node we just came from (m)
                L[node] = length + L[m]
                
                if P[node]==m:
                    s+=1
                    if s > tr:
                        #if the distance to a node, coming from the same node 
                        #is shorter len(l)+1 times in a row, we can conclude
                        #that it will go indefinitely negative.
                        #included for higher efficiency in many cases.
                        nlcf=negative_length_cycle_finder(l,node,L,P,color_map)
                        print("This graph contains at least one negative-length cycle:",nlcf[0])
                        return nlcf[1]
                else:
                    P[node] = m
                    s=0
                if node == st:
                    #we conclude that there's a path from the start to the start that
                    #is negative, hence will repeat indefinitely.
                    #included for higher efficiency in many cases.
                    nlcf=negative_length_cycle_finder(l,node,L,P,color_map)
                    print("This graph contains at least one negative-length cycle:",nlcf[0])
                    return nlcf[1]

                #This code checks whether we're already planning on looking
                #at what this node can reach later.
                if node not in E[p:]:
                    E.append(node)
                    color_map[node]='red'
                    
        color_map[m]='green'
        
        if len(E) > len(l)*(len(l)-1)/2+1:
            #If the algorithm starts going indefinitely, it has a negative length cycle
            nlcf=negative_length_cycle_finder(l,m,L,P,color_map)
            print("This graph contains at least one negative-length cycle:",nlcf[0])
            return nlcf[1]
        
        

        plot(l,L,P,color_map)
        
    #Takes the dictionary of predecessors and calculates the journeys to each node
    J=dict()
    for n,p in P.items():
        path=[P[n]]
        for pr in path:
            if P[pr] == '-' or pr == '-':
                break
            path.append(P[pr])
        path.reverse()
        J[n]=path
    return L,J

def graph_generator(n,m,s,b):
    '''takes a node number and a percentage of how many of the possible edges
    will exist along with the minimum and maximum edge length
    and returns a graph that a path can be found through'''
    l=[]
    for i in range(n):
        l.append(dict())
        for j in range(i):
            if numpy.random.randint(0,1000) < 10*m:
                l[i][j]=numpy.random.randint(s,b)
        for j in range(i+1,n):
            if numpy.random.randint(0,1000) < 10*m:
                l[i][j]=numpy.random.randint(s,b)
    return l

l=graph_generator(10,40,-25,50)

print(Pathgrapher(l,0))

# c=[{1:-1,2:1},{0:-1,3:1},{4:1},{5:1},{},{}]
# print(Pathfinder(c,0))
# # print(Pathfinder([{1:-1},{0:-1}],0))

# a=[{1:1,3:1},{2:-1,6:-50},{1:-1}]
# for i in range(4,10):
#     a.append({i:1})
# a.append({})
# print(a)
# print(Pathfinder(a,0))

# b=[{1:1,3:1,4:1},{2:-1},{1:-1},{5:1},{6:-1},{7:1},{8:-1},{9:1},{10:-1},{11:1},{12:-1},{9:-100},{4:-1},{}]
# print(b)
# print(Pathfinder(b,0))

# PWS1 = [{1:7,2:5,3:3,4:1},{2:5,3:3,4:1},{3:3,4:1},{4:1},{0:-5}]
# print(Pathfinder(PWS1,0))


PW = [{1:11,2:9,3:7,4:5,5:3,6:1},{0:-7},{1:1},{2:1},{3:1},{4:1},{5:1}]

