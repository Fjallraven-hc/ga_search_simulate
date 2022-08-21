import geatpy as ea
import numpy as np
from gnode import *
import argparse
from bfs_toolkit import *
from simulator import *
from gnode_combine import *

parser = argparse.ArgumentParser()
parser.add_argument('--input_log', type=str, default='test2.log')
parser.add_argument('--iteration', type=int, default=10)
parser.add_argument('--population', type=int, default=30)
args = parser.parse_args()

def fix_op_schedule(op_schedule):
    b = list(set(sorted(op_schedule)))
    fixed_op_schedule = [b.index(a) for a in op_schedule]
    return fixed_op_schedule


if __name__ == '__main__':
    gnodes = load_gnodes(args.input_log)
    gnodes = combine_seq_gnode(gnodes)
    bfs = get_bfs_level(gnodes)
    op_num = len(gnodes)
    
    @ea.Problem.single
    def evalVars(Vars):
        f = get_e2e_latency(Vars, gnodes, bfs)
        return f, 0

    # print('bfs:{}'.format(get_e2e_latency([0]*len(gnodes), gnodes)))
    problem = ea.Problem(name='soea quick start demo',
                            M=1,
                            maxormins=[1],
                            Dim=len(gnodes),
                            varTypes=[1]*len(gnodes),
                            lb=[0]*len(gnodes),
                            ub=[10]*len(gnodes),
                            evalVars=evalVars)

    algorithm = ea.soea_SEGA_templet(problem,
                                        ea.Population(Encoding='RI', NIND=200),
                                        MAXGEN=500,  # num of generations
                                        logTras=1,  # save log every logTras generations
                                        trappedValue=1e-6,
                                        maxTrappedCount=10)
                                        
    res = ea.optimize(algorithm, dirName='./ga_results', seed=1, verbose=True, drawing=1, outputMsg=True, drawLog=True)
    
    optimal_bias = list(res['Vars'])[0]
    # ops_stage, layer_schedule = update_schedule(bfs, optimal_bias, gnodes)
    # ops_stage = fix_op_schedule(ops_stage)
    print()
    print('BFS result:')
    get_e2e_latency([0]*len(gnodes), gnodes, bfs, True)

    print()
    print('EA search result:')
    get_e2e_latency(optimal_bias, gnodes, bfs, True)
    # print('bfs:{}'.format(get_e2e_latency([0]*len(gnodes), gnodes, bfs)))