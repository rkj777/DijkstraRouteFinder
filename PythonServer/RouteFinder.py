from graph import *
"""
Name: Rajan Jassal and Eponine Pizzy

"""
def loadfile(filename):
    """
    Function will open a file and create a graph function of all the vertices
    and edges. Also will return a dictionary of vertices and lat and longs

    """
    
    f = open(filename)
    graph = Graph()
    lat_lon = {}
    #loop will look for , and split accordingly
    for line in f:
        current_string = "" 
        if line[0] == 'V':
            counter_1 = 2
            while 1:
                if line[counter_1] != ',':
                    current_string += line[counter_1]
                    counter_1 += 1
                else:
                    current_string = int(current_string)
                    graph.add_vertex(current_string)
                    lat_lon[current_string] = []
                    counter_1 += 1
                    break
            current_lat=""
            while 1:
                if line[counter_1] != ',':
                    current_lat += line[counter_1]
                    counter_1 += 1
                else:
                    lat_lon[current_string].append(float(current_lat))
                    counter_1 += 1
                    break
            current_lon = ""
            while 1:  
                if counter_1 < len(line):
                    current_lon += line[counter_1]
                    counter_1 += 1
                else:
                    lat_lon[current_string].append(float(current_lon))
                    break
        # cases for edges
        if line[0] == 'E':
            counter_1 = 2
            while 1:
                if line[counter_1] != ',':
                    current_string += line[counter_1]
                    counter_1 += 1 
                else:
                    edge1 = int(current_string)
                    current_string = ""
                    counter_1 += 1
                    break
            while 1:
                if line[counter_1] != ',':
                    current_string += line[counter_1]
                    counter_1 += 1
                else:
                    edge2 = int(current_string)
                    graph.add_edge((edge1, edge2))
                    break
    return graph, lat_lon                 

graph, lat_lon = loadfile('roads.txt')                        

def cost_distance(edge):
    """
    This function will return the cost from one edge to another in terms of lat
    """
    first_node = edge[0]
    lat_1 = lat_lon[first_node][0]
    lon_1 = lat_lon[first_node][1]
    second_node = edge[1]
    lat_2 = lat_lon[second_node][0]
    lon_2 = lat_lon[second_node][1]
    lat_tot = lat_1 - lat_2
    lon_tot = lon_1 - lon_2
    lat_tot = lat_tot ** 2
    lon_tot = lon_tot ** 2
    distance = (lat_tot + lon_tot) ** (0.5)
    return distance

                                                                          
                                                      
def least_cost_path(G, start, dest, cost):
    """
    This function will determine the least cost path from vertice start to end
    """
    visted = set()
    prev = {}
    nodes_to_do = {start: 0}
    current =  start
    dists = {}
    
    #only tests the nodes if dest has not been found
    while nodes_to_do and (dest not in visted):
        for n in G.neighbours(current):
            #If visted already smallest possible
            if n in visted:
                continue
            
            if (n not in nodes_to_do) or nodes_to_do[n] > nodes_to_do[current] + cost((current, n)): 
                 nodes_to_do[n] = nodes_to_do[current] + cost((current, n))
                 prev[n] = current
                 dists[n] = nodes_to_do[current] + cost((current, n))


        visted.add(current)
        nodes_to_do.pop(current)
        current = min(nodes_to_do.items() , key = lambda x : x[1])[0]
    
    if dest not in visted:
        return None
    
    prev_node = dest
    path = []

    while prev_node != start:
        path.append(prev_node)
        prev_node = prev[prev_node]
        
    path.append(start)
    path.reverse()
        
    return path, len(path)

def v_lookup(lat, lon):
    for V in lat_lon:
        if lat_lon[V] == [lat, lon]:
            return V
    return None

if __name__ == "__main__":
    while 1:
        inputs =  input("Please give me your coordinates:\n").split()
        if len(inputs) != 4:
            print("Invaild inputs")
            continue 
        inputs[0] = inputs[0][:-5] + '.' + inputs[0][-5:]
        inputs[1] = inputs[1][:-5] + '.' + inputs[1][-5:]
        inputs[2] = inputs[2][:-5] + '.' + inputs[2][-5:]
        inputs[3] = inputs[3][:-5] + '.' + inputs[3][-5:]
        vertice1= v_lookup(float(inputs[0]), float(inputs[1]))
        
        if vertice1 == None:
            print("Invaild inputs")
            continue 
        
        vertice2= v_lookup(float(inputs[2]), float(inputs[3]))
     
        if vertice2 == None:
            print("Invaild inputs")
            continue
        paths, lenpaths = least_cost_path(graph, vertice1, vertice2, least_cost_path)
        print(lenpaths)
        for V in paths:
            print(V)
     
                    
