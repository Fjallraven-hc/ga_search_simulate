import geatpy as ea
import numpy as np
from gnode import *
import argparse
from bfs_toolkit import *
from simulator import *
import math

parser = argparse.ArgumentParser()
parser.add_argument('--input_log', type=str, default='./model_logs/inception.log')
parser.add_argument('--iteration', type=int, default=10)
parser.add_argument('--population', type=int, default=30)
args = parser.parse_args()

def fix_op_schedule(op_schedule):
    b = list(set(sorted(op_schedule)))
    fixed_op_schedule = [b.index(a) for a in op_schedule]
    return fixed_op_schedule

def find_chain_and_merge(gnodes, length_threshold=4):
    chains = []
    CID = 0
    for gnode in gnodes:
        if gnode.in_chain:
            continue
        node_id = gnode.id
        tmp_chain = [node_id]
        length_counter = 1
        while(len(gnodes[node_id].dst) == 1 and 
                len(gnodes[gnodes[node_id].dst[0]].src) == 1 and
                not gnodes[gnodes[node_id].dst[0]].in_chain):
            node_id = gnodes[node_id].dst[0]
            tmp_chain.append(node_id)
            length_counter += 1
        if length_counter >= length_threshold:
            chains.append(Chain(CID, tmp_chain))
            CID += 1
            for idx in tmp_chain:
                gnodes[idx].in_chain = True
    for chain in chains:
        for c in chains:
            if depends_on(chain.ops[0], c.ops[-1]):
                chain.src.append(c.id)
                c.dst.append(chain.id)

    for chain in chains:
        chain.src = list(set(chain.src))
        chain.dst = list(set(chain.dst))

    # for chain in chains:
    #     print(chain.start_op_id, ', ', chain.end_op_id, ', ', chain.src, ', ', chain.dst)
    return chains
            
def depends_on(x, y):
    downstream_node_ids = [y]
    while downstream_node_ids != []:
        if x in downstream_node_ids:
            return True
        tmp_node_ids = []
        for idx in downstream_node_ids:
            tmp_node_ids += gnodes[idx].dst
            tmp_node_ids = list(set(tmp_node_ids))
        downstream_node_ids = tmp_node_ids
    return False

def get_init_bias_from_chain_schedule(gnodes, chains, chain_bias):
    bias = [0] * len(gnodes)
    for idx in range(len(chains)):
        bias[chains[idx].ops[0]] = chain_bias[idx] * 4
    return bias

def slice_graph(gndoes, bfs, max_layers=10):
    sliced_gnodes = []
    slice_num = math.ceil(max(bfs) / 10)
    for s in range(slice_num):
        cur_slice = []
        for idx in range(len(gnodes)):
            if bfs[idx] >= s * max_layers and bfs[idx] < (s + 1) * max_layers:
                cur_slice.append(idx)
        sliced_gnodes.append(cur_slice)
    return sliced_gnodes

if __name__ == '__main__':
    gnodes = load_gnodes(args.input_log)
    # for gnode in gnodes:
    #     if gnode.type == 'Convolution':
    #         gnode.print_info()
    # chains = find_chain_and_merge(gnodes)
    # chain_bfs = get_bfs_level(chains)
    # print(chain_bfs)

    bfs = get_bfs_level(gnodes)
    sliced_gnodes = slice_graph(gnodes, bfs)
    print(sliced_gnodes)
    # print(bfs)
    # op_num = len(gnodes)
    # print('op_num:', op_num)

    # #########################################################################

    # @ea.Problem.single
    # def evalChainVars(Vars):
    #     # print(Vars)
    #     _, layer_schedule = update_schedule(chain_bfs, Vars, chains, True)
    #     chain_parallel_num = np.array([len(layer) for layer in layer_schedule])
    #     # print(chain_parallel_num)
    #     # f = get_e2e_latency(Vars, chains, chain_bfs)
    #     return chain_parallel_num.var() + chain_parallel_num.size, 0

    # problem = ea.Problem(name='chain',
    #                         M=1,
    #                         maxormins=[1],
    #                         Dim=len(chains),
    #                         varTypes=[1]*len(chains),
    #                         lb=[0]*len(chains),
    #                         ub=[2]*len(chains),
    #                         evalVars=evalChainVars)

    # algorithm = ea.soea_SEGA_templet(problem,
    #                                     ea.Population(Encoding='RI', NIND=200),
    #                                     MAXGEN=50,  # num of generations
    #                                     logTras=1,  # save log every logTras generations
    #                                     trappedValue=0.01,
    #                                     maxTrappedCount=10)
                                        
    # chain_res = ea.optimize(algorithm, dirName='./ga_results', seed=1, verbose=True, drawing=1, outputMsg=True, drawLog=True)
    
    # chain_optimal_bias = list(chain_res['Vars'])[0]
    # _, chain_schedule = update_schedule(chain_bfs, chain_optimal_bias, chains, True)
    # print(chain_optimal_bias)

    # #########################################################################   
    
    # @ea.Problem.single
    # def evalVars(Vars):
    #     # print(Vars)
    #     f = get_e2e_latency(Vars, gnodes, bfs)
    #     return f, 0

    # # print('bfs:{}'.format(get_e2e_latency([0]*len(gnodes), gnodes)))
    # problem = ea.Problem(name='soea quick start demo',
    #                         M=1,
    #                         maxormins=[1],
    #                         Dim=len(gnodes),
    #                         varTypes=[1]*len(gnodes),
    #                         lb=[0]*len(gnodes),
    #                         ub=[10]*len(gnodes),
    #                         evalVars=evalVars)

    # # print(get_init_bias_from_chain_schedule(gnodes, chains, chain_optimal_bias))
    # # chrom = np.broadcast_to(np.array(get_init_bias_from_chain_schedule(gnodes, chains, chain_optimal_bias), int), (200, len(gnodes)))
    # # print(chrom)
    # algorithm = ea.soea_SEGA_templet(problem,
    #                                     ea.Population(Encoding='RI', NIND=1000),
    #                                     MAXGEN=200,  # num of generations
    #                                     logTras=1,  # save log every logTras generations
    #                                     trappedValue=1,
    #                                     maxTrappedCount=1000)
                                        
    # res = ea.optimize(algorithm, dirName='./ga_results', seed=1, verbose=True, drawing=1, outputMsg=True, drawLog=True)
    
    # optimal_bias = list(res['Vars'])[0]
    # print(optimal_bias)
    # # ops_stage, layer_schedule = update_schedule(bfs, optimal_bias, gnodes)
    # # ops_stage = fix_op_schedule(ops_stage)
    # print()
    # print('BFS result:')
    # get_e2e_latency([0]*len(gnodes), gnodes, bfs, True)

    # print()
    # print('EA search result:')
    # get_e2e_latency(optimal_bias, gnodes, bfs, True)

    # # print()
    # # print('manual result:')
    # # print(list(chrom[0]))
    # # get_e2e_latency(list(int(x) for x in chrom[0]), gnodes, bfs, True)
    # # print('bfs:{}'.format(get_e2e_latency([0]*len(gnodes), gnodes, bfs)))