edges = {}
with open('er-02.txt') as f:
    lines = f.readlines()
    node_num = int(lines[0].split('\n')[0])
    for i in range(2, len(lines)):
        line = lines[i].split('\n')[0]
        s = line.split(' ')[0]
        e = line.split(' ')[1]
        if not e in edges:
            edges[e] = []
        if not s in edges:
            edges[s] = []
        edges[e].append(s)

gid = 0

while len(edges) != 0:
    pop_list = []
    for n in edges:
        if len(edges[n]) == 0:
            pop_list.append(n)
    for n in pop_list:
        for nn in edges:
            if n in edges[nn]:
                edges[nn].remove(n)
    for x in pop_list:
        edges.pop(x)
    if len(pop_list) > 0:
        print('subgraph cluster{} '.format(str(gid)) + '{')
        for x in pop_list:
            print(x)
        print('}')
        gid += 1
    