from itertools import chain
from sys import excepthook
from gnode import *
from bfs_toolkit import *

def combine_seq_gnode(gnodes):
    #gnodes = load_gnodes("nasnet_imagenet_large.log")
    bfs = get_bfs_level(gnodes)
    # print(bfs)
    _, layer_schedule = update_schedule(bfs, [0 for _ in gnodes], gnodes)
    chains = []

    # print(layer_schedule)
    # print('-'*200)

    for layer in layer_schedule:
        for op in layer:
            temp_chain = []
            temp_op = gnodes[op]
            while temp_op.combine_flag == False and len(temp_op.src) == 1 and len(temp_op.dst) == 1:# 这个限制条件，似乎有待商榷
                #print(temp_op, temp_op.src, temp_op.dst)
                temp_chain.append(temp_op.id)
                #temp_chain.append((temp_op.gid, temp_op.id))
                temp_op = gnodes[temp_op.dst[0]]
            if len(temp_chain) > 1:
                chains.append(temp_chain)
                for chain_op in temp_chain:
                    gnodes[chain_op].combine_flag = True

    gid_next = 0
    for gnode in gnodes:
        if gid_next < gnode.gid:
            gid_next = gnode.gid

    for chain in chains:
        # print(chain)
        gid_next += 1
        id_next = len(gnodes)
        identifier = "Combine"
        latency = {'10': 0, '20': 0, '30': 0, '40': 0, '50': 0, '60': 0, '70': 0, '80': 0}
        for op in chain:
            identifier += ","+str(op)
            for sm_num in latency:
                latency[sm_num] += gnodes[op].estimate_latency(int(sm_num))
        combine_gnode = GNode(id=id_next, gid=gid_next, name="Combine"+'_'+str(gid_next), op_type="Combine", identifier=identifier)
        combine_gnode.set_latency(latency)
        # rewrite src and dst
        if len(gnodes[chain[0]].src) > 0:
            combine_gnode.add_src(gnodes[chain[0]].src[0])
            gnodes[gnodes[chain[0]].src[0]].dst.remove(chain[0])
            gnodes[gnodes[chain[0]].src[0]].dst.append(id_next)

        if len(gnodes[chain[-1]].dst) > 0:
            combine_gnode.add_dst(gnodes[chain[-1]].dst[0])
            gnodes[gnodes[chain[-1]].dst[0]].src.remove(chain[-1])
            gnodes[gnodes[chain[-1]].dst[0]].src.append(id_next)

        gnodes.append(combine_gnode)
    return gnodes
"""gnodes = load_gnodes("test2.log")
gnodes = combine_seq_gnode(gnodes)
    
bfs = get_bfs_level(gnodes)
_, layer_schedule = update_schedule(bfs, [0 for _ in gnodes], gnodes)
print(layer_schedule)
for i in range(20,27):
    print(gnodes[i].identifier)"""
