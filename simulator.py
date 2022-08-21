# author: yhc
import json
import numpy as np
from random import shuffle
from bfs_toolkit import *
# Single_OP_Schedule = [{layer_idx:, sm_usage:},...]  len(gnodes) items


class Simulator:
    def __init__(self, layer_schedule, pe_num, gnodes):
        self.layer_schedule = layer_schedule
        self.pe_num = pe_num
        self.gnodes = gnodes

        self.sm_info = {}
        for i in range(self.pe_num):
            self.sm_info[i] = {
                "sm_id": i,
                "last_used_time": 0,
                "status": "unused"
            }

        self.op_info = {}
        for idx in range(len(self.gnodes)):
            self.op_info[idx] = {
                "operator_id": idx,
                "begin_time": -1,
                'sm_used': 0,
                "latency": gnodes[idx].latency,
                "status": "unexecuted"
            }
        self.unused_pe_num = self.pe_num
        self.total_latency = 0

    def step_sm_allocate(self, layer_idx):
        
        # min-max method
        # print()
        self.unused_pe_num = self.pe_num
        if layer_idx >= len(self.layer_schedule):
            return
        current_step_schedule_list = self.layer_schedule[layer_idx]

        if len(current_step_schedule_list) == 0:
            return
        if self.pe_num < len(current_step_schedule_list):
            print("warning, pe_num too few, could not support entirely parallel!")
            return

        for idx in current_step_schedule_list:
            self.op_info[idx]["sm_used"] = 1
            self.unused_pe_num -= 1
        
        while(self.unused_pe_num >= 1):
            kernel_latencys = [self.gnodes[idx].estimate_latency(self.op_info[idx]["sm_used"]) \
                                                            for idx in current_step_schedule_list]
            
            max_latency = max(kernel_latencys)
            max_latency_idx = current_step_schedule_list[kernel_latencys.index(max_latency)]
            # print(max_latency_idx)

            if self.op_info[max_latency_idx]["sm_used"] >= 80:
                break
            else:
                self.op_info[max_latency_idx]["sm_used"] += 1
                self.unused_pe_num -= 1
        
        self.total_latency += max([self.gnodes[idx].estimate_latency(self.op_info[idx]["sm_used"]) \
                                                            for idx in current_step_schedule_list])

    def print_schedule(self):
        for layer_idx in range(1, len(self.layer_schedule)):
            kernel_names = [self.gnodes[idx].type for idx in self.layer_schedule[layer_idx]]
            gids = [self.gnodes[idx].gid for idx in self.layer_schedule[layer_idx]]
            info = [kernel_names[i] + '(' + str(gids[i]) + ')' for i in range(len(self.layer_schedule[layer_idx]))]
            # print(' '.join(info))

            kernel_latencys = [self.gnodes[idx].estimate_latency(self.op_info[idx]["sm_used"]) \
                                                            for idx in self.layer_schedule[layer_idx]]
            sm_usage = [self.op_info[idx]["sm_used"] for idx in self.layer_schedule[layer_idx]]
            info = ['(' + str(kernel_latencys[i]) + ', ' + str(sm_usage[i]) + ')' for i in range(len(self.layer_schedule[layer_idx]))]
            print('- layer {}:'.format(layer_idx) + ',' + ' '.join(info))

def get_e2e_latency(bias, gnodes, bfs, show_schedule = False):
    _, layer_schedule = update_schedule(bfs, bias, gnodes)
    pe_num = 80
    simulator = Simulator(layer_schedule, pe_num, gnodes)
    for layer_idx in range(1, len(layer_schedule)):
        simulator.step_sm_allocate(layer_idx)
    if show_schedule == True:
        print('end-to-end latency: {} us'.format(simulator.total_latency))
        print('schedule:')
        simulator.print_schedule()
    return simulator.total_latency