from graph import Graph
import sys
import serial
import time
# Some little helper functions to help ease readability

ser = serial.Serial('/dev/ttyACM0', 9600)

def reconstruct_path(start, dest, parents):
    """
    reconstruct_path reconstructs the shortest path from vertex
    start to vertex dest.

    "parents" is a dictionary which maps each vertex to their
    respective parent in the lowest cost path from start to that
    vertex.

    >>> parents = {'l': ' ', 'e': 'l', 'a': 'e', 'h':'a'}
    >>> reconstruct_path('l', 'h', parents)
    ['l', 'e', 'a', 'h']

    """
    current = dest
    path = [dest]

    while current != start:
        path.append(parents[current])
        current = parents[current]

    path.reverse()
    return path

def  straight_line_dist(lat1, lon1, lat2, lon2):
    """
    Computes the straightline distance between
    two points (lat1, lon1) and (lat2, lon2)
    """
    return ((lat2-lat1)**2 + (lon2-lon1)**2)**0.5

def process_coord(coord):
    """
    given a string with a standardlatitude or
    longitude coordinate convert it be in
    100, 1000ths of a degree. Truncate to be an
    int.
    """
    return int(float(coord)*100000)

def least_cost_path(graph, start, dest, cost):
    """
    Using Dijkstra's algorithm to solve for the least
    cost path in graph from start vertex to dest vertex.
    Input variable cost is a function with method signature
    c = cost(e) where e is an edge from graph.

    >>> graph = Graph({1,2,3,4,5,6}, [(1,2), (1,3), (1,6), (2,1), (2,3), (2,4), (3,1), (3,2), \
            (3,4), (3,6), (4,2), (4,3), (4,5), (5,4), (5,6), (6,1), (6,3), (6,5)])
    >>> weights = {(1,2): 7, (1,3):9, (1,6):14, (2,1):7, (2,3):10, (2,4):15, (3,1):9, \
            (3,2):10, (3,4):11, (3,6):2, (4,2):15, (4,3):11, (4,5):6, (5,4):6, (5,6):9, (6,1):14,\
            (6,3):2, (6,5):9}
    >>> cost = lambda e: weights.get(e, float("inf"))
    >>> least_cost_path(graph, 1,5, cost)
    [1, 3, 6, 5]
    """
    # est_min_cost[v] is our estimate of the lowest cost
    # from vertex start to vertex v
    est_min_cost = {}

    # parents[v] is the parent of v in our current
    # shorest path from start to v
    parents = {}

    # todo is the set of vertices in our graph which
    # we have seen but haven't processed yet. This is
    # the list of vertices we have left "to do"
    todo = {start}

    est_min_cost[start] = 0

    while todo:
        current = min(todo, key=lambda x: est_min_cost[x])

        if current == dest:
            return reconstruct_path(start, dest, parents)

        todo.remove(current)

        for neighbour in graph.neighbours(current):
            #if neighbour isn't in est_min_cost, that means I haven't seen it before,
            #which means I should add it to my todo list and initialize my lowest
            #estimated cost and set it's parent
            if not neighbour in est_min_cost:
                todo.add(neighbour)
                est_min_cost[neighbour] = (est_min_cost[current] + cost((current, neighbour)))
                parents[neighbour] = current
            elif est_min_cost[neighbour] > (est_min_cost[current] + cost((current, neighbour))):
                #If my neighbour isn't new, then I should check if my previous lowest cost path
                #is worse than a path going through vertex current. If it is, I will update
                #my cost and record current as my new parent.
                est_min_cost[neighbour] = (est_min_cost[current] + cost((current, neighbour)))
                parents[neighbour] = current

    return []

def load_edmonton_road_map(filename):
    """
    Read in the Edmonton Road Map Data from the
    given filename and create our Graph, a dictionary
    for looking up the latitude and longitude information
    for vertices and a dictionary for mapping streetnames
    to their associated edges.
    """
    graph = Graph()
    location = {}
    streetnames = {}

    with open(filename, 'r') as f:
        for line in f:
            elements = line.split(",")
            if(elements[0] == "V"):
                graph.add_vertex(int(elements[1]))
                location[int(elements[1])] = (process_coord(elements[2]),
                                              process_coord(elements[3]))
            elif (elements[0] == "E"):
                graph.add_edge((int(elements[1]), int(elements[2])))
                streetnames[(int(elements[1]), int(elements[2]))] = elements[3]

    return graph, location, streetnames


# Main code that gets run when file is run
graph, location, streetnames = load_edmonton_road_map("edmonton-roads-2.0.1.txt")

# Define our cost_distance function that takes in an edge e = (vertexid, vertexid)
cost_distance = lambda e: straight_line_dist(location[e[0]][0], location[e[0]][1],
                                             location[e[1]][0], location[e[1]][1])

def read_points():
    while 1:
        line1 = ser.readline().decode('ASCII')
        line2 = ser.readline().decode('ASCII')
        elements1 = line1.split(", ")
        elements2 = line2.split(", ")
        lat1 = elements1[-1].rstrip()
        lat2 = elements2[-1].rstrip()
        lon1 = elements1[0]
        lon2 = elements2[0]
        ard_vert = lat1 + " " + lon1 + " " + lat2 + " " + lon2
        return ard_vert
        break
    


if __name__ == "__main__":
    while(True):
        user_input = read_points()

        # Exit if the user inputs q, Q, quit, exit, Quit, or Exit
        if user_input.strip() in {"q", "Q", "quit", "exit", "Quit", "Exit"}:
            sys.exit()

        # Get lat and lon from stdin. If input is invalid,
        # restart the while loop (thus allowing the user
        # to input new coordinates)
        coords = user_input.split()
        processed_coords = []

        try:
            for coord in coords:
                processed_coords.append(int(coord))
        except ValueError:
            sys.stdout.write(str(0)+"\n")
            continue

        # Find closest vertices to the provided lat and lon positions
        def find_closest_vertex(lat, lon):
            return min(location, key=lambda v:straight_line_dist(lat, lon, location[v][0], location[v][1]))

        start = find_closest_vertex(processed_coords[0], processed_coords[1])
        dest = find_closest_vertex(processed_coords[2], processed_coords[3])

        # Find path
        path = least_cost_path(graph, start, dest, cost_distance)

        # Send number of edges out to Arduino and Stdout 
        ser.write((str(len(path)) + "\n").encode('ASCII'))
        sys.stdout.write(str(len(path)) + "\n")
        
        # Send shortest path to Arduino and Stdin
        for v in path:
            sys.stdout.write(str(location[v][0]) + " " + \
                                 str(location[v][1]) + "\n")
            ser.write((str(location[v][0]) + "\n" + \
                       str(location[v][1]) + "\n").encode('ASCII'))
            #To account for buffer speed of Arduino
            time.sleep(0.1)
