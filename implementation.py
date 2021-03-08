import networkx as nx
from collections import OrderedDict, defaultdict
import sys

G = nx.Graph()  # define a graph
H = nx.Graph()
G.add_nodes_from(range(1, 12))  # add nodes in the graph(1 to 11)

# define edges in graph
edges = [(1, 2), (1, 3), (3, 4), (4, 5), (4, 8),
         (5, 8), (8, 9), (5, 9), (5, 6), (6, 7),
         (9, 10), (6, 10), (10, 11), (6, 11), (7, 11),
         (2, 7), (2, 6), (3, 6)]
G.add_edges_from(edges)  # add all edges

links = [(4, 2), (4, 7), (4,10), (4,11), (2,8)]  # requests to provision
total_requests = len(links)

fails = [[(1, 3)], [(3, 6)], [(5, 6)]]  # list of failures  list of lists

failures = []
# sort failure tuple
for failure in fails:
    fl = []
    for fail_nd in failure:
        fl.append(tuple(sorted(fail_nd)))
    failures.append(fl)

total_wavelength = 2  # define total available wavelength
failure_dic = {}
paths = OrderedDict()  # store link:paths

# compute all the shortest paths
for link in links:
    for path in nx.all_shortest_paths(G, source=link[0], target=link[1]):  # dijkstra's shortest path
        if link[0] > link[1]:
            link = (link[1],link[0])
        if paths.get(link):
            paths[link].append(path)
        else:
            paths[link] = [path]
print("All the shortest paths for the requests are:")
for key, value in paths.items():
    print(f"{key}: {value}")
print()

primary_paths = defaultdict(lambda: None)  # initialize primary_paths dictionary with None

for i, (node, all_paths) in enumerate(paths.items()):
    pi = (None, sys.maxsize)
    if not primary_paths:
        # if it's 1st request, assign the first available wavlength and path
        if total_wavelength:  # check if wavlengths are not None
            primary_paths[tuple(sorted(node))] = (all_paths[0], 1)
            try:
                all_paths.pop(0)
                paths[node] = all_paths
            except ValueError:
                print("Not enough paths to compute the operation.")
        else:
            pi = (all_paths[0], None)
        continue
    j=0
    success = False  # True if found a (path, wav) to provision serving request
    while j < len(all_paths) and (not success):
        path = all_paths[j]
        wav = 0
        path1 = {tuple(sorted((path[index], path[index + 1]))) for index in range(len(path) - 1)}  # create pairs

        # check if the path is unique with all the previously computed primary paths
        for value in primary_paths.values():
            temp = value[0]
            temp = {tuple(sorted((temp[i], temp[i + 1]))) for i in range(len(temp) - 1)}  # create pairs
            if len(temp.intersection(path1)):
                if value[1] < total_wavelength:
                    wav = value[1]+1
                else:
                    wav = sys.maxsize
                    
        if wav != sys.maxsize:
            if not wav:
                wav += 1
            pi = (path, wav)
            success = True # found a wavelength to provision the request with the current path
        j += 1
    if success:
        # if request is provisioned, remove the selected path from the list of shortest paths
        # and add it to the primary_paths list
#        print(pi)
        primary_paths[tuple(sorted(node))] = (pi[0],wav)
        all_paths.remove(pi[0])
        paths[node] = all_paths
    else:
        print(f"--> No path found to provision for the request: {node}")

print()
        
print("The primary paths are: ")
for key, value in primary_paths.items():
    print(f"{key}: {value}")
#print("\nFinal set of paths :", paths)
print()
# lightpath
success = True
i = 0
while success and i < len(failures):
    f1 = set()
    f = failures[i][0]
    if f[0] > f[1]:  # keep the vertices sorted as it is undirected graph
        f = (f[1],f[0])
    f1.add(f)
    K_f = []  # stores requests with failure in their primary path
    for key, values in primary_paths.items():
        temp = values[0]
        temp = {tuple(sorted((temp[i], temp[i + 1]))) for i in range(len(temp) - 1)}
        if len(temp.intersection(f1)):
            K_f.append(key)
    print(f"Failed lightpaths: {K_f}, for failure:{f}")
    L_rest_f = [paths.get(req) for req in K_f]  # list of all possible shortest paths
    print("remaining protection paths = ",L_rest_f)
    success_f = False
    j = 0
    protection_paths = []
    while not success_f and j < len(L_rest_f):
        C = []
        for each_path in L_rest_f[j]:
            temp = {tuple(sorted((each_path[i], each_path[i + 1]))) for i in range(len(each_path) - 1)}
            if len(temp.intersection(f1)) == 0:
                C.append(each_path)
        pi = (None, sys.maxsize)
        for index, path in enumerate(C):
            wav = 0
            path = {tuple(sorted((path[i], path[i + 1]))) for i in range(len(path) - 1)}  # create pairs
            for value in primary_paths.values():
                # check for all primary paths if there's an overlapping path or not
                temp = value[0]                
                temp = {tuple(sorted((temp[i], temp[i + 1]))) for i in range(len(temp) - 1)}  # create pairs
                if len(temp.intersection(path)):
                    if value[1] < total_wavelength:
                        wav = (value[1]+1)
                    else:
                        wav = sys.maxsize
            if wav <= pi[1]:
                pi = (C[index], wav)
            path = {tuple(sorted((pi[0][i], pi[0][i + 1]))) for i in range(len(pi[0]) - 1)}  # create pairs
            for each_path in protection_paths:
                # check for previously computed protection paths if there's an overlapping or not
                temp = each_path
                temp = {tuple(sorted((path[i], path[i + 1]))) for i in range(len(temp)-1)}
                if len(temp.intersection(path)):
                    if pi[1] < total_wavelength:
                        wav += (pi[1]+1)
                    else:
                        wav = sys.maxsize
        if pi[1] == 0:
            wav = 1
        if wav != sys.maxsize:
            print("Protection path=", (pi[0],wav))
#            success_f = True
        else:
            print(f"--> No protection path found to provision for the request: {K_f[j]}, failure:{f}")
        j+=1
#    if success_f == False:
#        success = False
    print()
    i+=1