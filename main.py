import networkx as nx
from collections import OrderedDict

G = nx.Graph()  # define a graph
H = nx.Graph()
G.add_nodes_from(range(1, 12))  # add nodes in the graph(1 to 11)

# define edges in graph
edges = [(1, 2), (1, 3), (3, 4), (4, 5), (4, 8),
         (5, 8), (8, 9), (5, 9), (5, 6), (6, 7),
         (9, 10), (6, 10), (10, 11), (6, 11), (7, 11),
         (2, 7), (2, 6), (3, 6)]
G.add_edges_from(edges)  # add all edges

links = [(4, 2), (4, 3)]  # requests to provision
total_requests = len(links)

fails = [[(1, 3), (1, 2)], [(6, 3)]]  # list of failures  list of lists
failures = []
# sort failure tuple
for failure in fails:
    fl = []
    for fail_nd in failure:
        fl.append(tuple(sorted(fail_nd)))
    failures.append(fl)
print(f"sorted failure sequence: {failures}")

total_wavelength = 2  # define total available wavelength
failure_dic = {}
paths = OrderedDict()  # store link:paths

# compute all the shortest paths
for link in links:
    for path in nx.all_shortest_paths(G, source=link[0], target=link[1]):  # dijkstra's shortest path
        if paths.get(link):
            paths[link].append(path)
        else:
            paths[link] = [path]

print(f"paths are: {paths}")
print(f"failures = {failures}")

# define final output
results = {'nodes': [],
           'primary_path': [],
           'backup_path': [],
           'wavelength': [],  # 0-NaN
           'provisioned': []  # 0-NO and 1-YES
           }

request_id = 1

# iterate through all the links and paths
for key, values in paths.items():
    results['nodes'].append(key)
    index = 0

    # compute primary path and associated wavelength
    while (len(results['primary_path']) != request_id) and (index < len(values)):
        wavelength = 0
        path = values[index]
        path1 = {tuple(sorted((path[i], path[i + 1]))) for i in range(len(path) - 1)}  # create pairs
        primaries = results['primary_path']
        k = 0
        while (wavelength < total_wavelength) and len(results['wavelength']) != request_id:
            if k > len(primaries):
                break
            if not primaries:
                results['primary_path'].append(path)
                results['wavelength'].append(wavelength)
            else:
                try:
                    temp = primaries[k]
                except IndexError:
                    temp = []
                temp = {tuple(sorted((temp[i], temp[i + 1]))) for i in range(len(temp) - 1)}  # create pairs
                # if pairwise intersection is null -> assign immediate available wavelength
                if len(temp.intersection(path1)) == 0:
                    results['primary_path'].append(path)
                    results['wavelength'].append(wavelength)
            k += 1
            wavelength += 1
        index += 1

    if len(results['primary_path']) < request_id:
        results['provisioned'].append(0)
        continue

    request_id += 1
print(f"Primary paths are: {results['primary_path']}")
print("######################################################")
# compute backup path
for id, (key, values) in enumerate(paths.items()):
    node = results['nodes'][id]  # do we need?
    index = 0
    # 1. check if failure is on primary path:
    for failure in failures:
        lp = results['primary_path'][id]
        lp_pairs = {tuple(sorted((lp[i], lp[i + 1]))) for i in range(len(lp) - 1)}  # create pairs
        fail_nodes = lp_pairs.intersection(set(failure))
        print(f"failure: {sorted(failure)}")
        print(f"primary path tuple pairs:{lp_pairs}")
        print(f"failure nodes: {fail_nodes}")
        # 2. if failure exists, remove the paths containing failures
        # 3. keep the very first path even with overlaping path with other primary path with diff. wavelength as a backup.
        # 4. remove all the primary paths from the remaining set of paths
        # 5. also remove the preassigned previous backup paths [with same failure],
        # 6. if still a path exists, assign it the wavelength(it will ensure sharing)
        if len(fail_nodes) > 0:
            print(f"type of values: {type(values)} and values are: {values}")
            vals = values[:]
            vals.remove(lp)  # remove primary path
            print(f"av_paths: {vals}")
            if len(failure_dic) == 0:
                failure_dic[1] = {list(fail_nodes)[0]: {'backup': [vals[0]],
                                         'wavelength': [1]}}
            print(failure_dic)
        else:
            print("no failures")
    print("-------------------------------------------------------------")

print(results)
