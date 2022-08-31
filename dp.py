from re import sub
from bfs_toolkit import *
from gnode import *
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--input_log', type=str, default='./model_logs/inception.log')
parser.add_argument('--iteration', type=int, default=10)
parser.add_argument('--population', type=int, default=30)
args = parser.parse_args()

dp_table = {}
# dp_table = {group:[latency, ending_layer]}

def gen_subset(L):
    ans = []
    for i in range(2 ** len(L)):
        subset = []
        for j in range(len(L)):
            if (i >> j) % 2:
               subset.append(L[j])
        ans.append(subset)
    
    if [] in ans:
        ans.remove([])
    # print(ans)
    return ans


DEFALUT_LATENCY = 1e8

class group:
    def __init__(self):
        self.nodes = []
        self.latency = DEFALUT_LATENCY

    def __eq__(self, other):
        if set(self.nodes) == set(other.nodes):
            return True
        return False

    def __hash__(self):
        h = 0
        for node in self.nodes:
            h += 2 ** node.id
        return h

    def add_nodes(self, nodes):
        self.nodes = nodes
    
    def add_node(self, node):
        self.nodes.append(node)

    # def remove_node(self, node):
    #     if node in self.nodes:
    #         self.nodes.remove()

    def find_ending_layers(self):
        ending_nodes = []
        for node in self.nodes:
            is_ending = True
            for dst in node.dst:
                if dst in [n.id for n in self.nodes]:
                    is_ending = False
                    break
            if is_ending:
                ending_nodes.append(node.id)
        return gen_subset(ending_nodes)

    def get_next_group(self, ending_nodes):
        next_group = group()
        for node in self.nodes:
            if node.id not in ending_nodes:
                next_group.add_node(node)
        if next_group not in dp_table:
            dp_table[next_group] = [DEFALUT_LATENCY, None]
        return next_group


def get_latency(layer):
    ava_sm = 80
    if len(layer) > ava_sm:
        raise 'No enough SM for layer!'
    sm_usage = [1] * len(layer)
    while ava_sm > 0:
        kernel_latencys = [gnodes[layer[i]].estimate_latency(sm_usage[i]) \
                                                            for i in range(len(layer))]
        max_latency = max(kernel_latencys)
        max_latency_idx = kernel_latencys.index(max_latency)
        # print(max_latency_idx)

        if sm_usage[max_latency_idx] >= 80:
            break
        else:
            sm_usage[max_latency_idx] += 1
            ava_sm -= 1
            
    return max_latency


def scheduler(group):
    if group in dp_table and dp_table[group][0] != DEFALUT_LATENCY:
        # print(dp_table[group])
        return dp_table[group][0]
    if len(group.nodes) == 0:
        return 0
    cur_layers = group.find_ending_layers()
    for cur_layer in cur_layers:
        layer_latency = get_latency(cur_layer)
        next_group = group.get_next_group(cur_layer)
        group_latency = layer_latency + scheduler(next_group)
        if group_latency < group.latency:
            group.latency = group_latency
            dp_table[group] = [group_latency, cur_layer]
            # group
    return group.latency

def graph_scheduler(dag):
    return scheduler(dag)

def slice_graph(gndoes, bfs, max_layers=4):
    sliced_gnodes = []
    slice_num = math.ceil(max(bfs) / max_layers)
    for s in range(slice_num):
        cur_slice = []
        for idx in range(len(gnodes)):
            if bfs[idx] >= s * max_layers and bfs[idx] < (s + 1) * max_layers:
                cur_slice.append(gnodes[idx])
        sliced_gnodes.append(cur_slice)
    return slice_num, sliced_gnodes

if __name__ == '__main__':
    gnodes = load_gnodes(args.input_log)
    bfs = get_bfs_level(gnodes)
    slice_num, sliced_gnodes = slice_graph(gnodes, bfs)
    
    # for gnode in gnodes:
    # print(len(sliced_gnodes[3]))
    
    for slice_idx in range(slice_num):
        dag = group()
        dp_table = {}
        dp_table[dag] = [DEFALUT_LATENCY, None]
        for gnode in sliced_gnodes[slice_idx]:
            dag.add_node(gnode)

        graph_scheduler(dag)
        print('slice_idx={}, latency={}'.format(slice_idx, dag.latency))
        cur_group = dag
        while dp_table[cur_group][1] != None:
            print(dp_table[cur_group][1])
            cur_group = cur_group.get_next_group(dp_table[cur_group][1])