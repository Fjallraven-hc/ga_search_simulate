import numpy
import copy
import random

from simulator import layer_schedule_to_runtime
from bfs_toolkit import get_bfs_level, combine_bfs_bias_to_schedule
from model_config_nasnet_imagenet_cell_1 import dependency, op_id_to_type
from gnode import *

"""
note: this version search, base on the bfs_bias vector
author: Haochen Yuan
time: 2022-07-22
chromosome: bias on bfs
"""

iteration_times = 100
solution_per_population = 300
saved_parents_per_population = 30
mating_parents_per_population = 20
mutation_per_population = 20
op_num = 435

fitness_record = [0 for i in range(solution_per_population)]
temp_population = []
temp_saved_parents = []
temp_mating_parents = []
temp_children = []
temp_min_runtime = [999999]
temp_best_schedule = []
temp_best_chromosome = []

best_solution_per_generation = []

bfs = get_bfs_level(gnodes)

op_num = len(gnodes)


def fitness_func(layer_schedule):
    fitness = layer_schedule_to_runtime(layer_schedule=layer_schedule) # runtime越短，fitness越高
    return fitness

def on_start():
    # initialize the population
    for i in range(solution_per_population):
        highest_bfs_level = max(bfs) # maybe useful?
        temp_chromosome = [0 if len(gnode.src)==0 else random.randint(0,20) for gnode in gnodes]
        temp_population.append(temp_chromosome) # here, parameter 3 can be modifieds

    # for i in range(solution_per_population):
    #     highest_bfs_level = max(bfs) # maybe useful?
    #     temp_chromosome = [random.randint(0,2) if op_id_to_type(i) in [-2,-3] else random.randint(0,20) for i in range(length)]
    #     temp_population.append(temp_chromosome) # here, parameter 3 can be modifieds
    #for i in temp_population:
    #    print(i)
    print("on_start()")

def on_fitness():
    index = 0
    for chromosome in temp_population:
        ops_stage, schedule = combine_bfs_bias_to_schedule(schedule=bfs, bias=chromosome, gnodes=gnodes)
        #print(schedule)
        fitness_record[index] = fitness_func(layer_schedule=schedule)

        """if fitness_record[index] < 59.5:
            print('*'*150)
            print("runtime: ", fitness_record[index])
            print("whole schedule: ", schedule)
            print('*'*150)"""

        index += 1

    if temp_min_runtime[0] > min(fitness_record):
        temp_min_runtime[0] = min(fitness_record)
    best_solution_per_generation.append((min(fitness_record), temp_population[fitness_record.index(min(fitness_record))]))
    print("on calculate fitness()")

def on_parents():
    temp_fitness_record = sorted(fitness_record) # 这里优先取运行时间短的，作为优良的
    for i in range(saved_parents_per_population):
        temp_saved_parents.append(temp_population[fitness_record.index(temp_fitness_record[i])])
    print("on parents()")

def on_crossover():
    for i in range(int(mating_parents_per_population/2)):
        father_bias = temp_saved_parents[2*i]
        mother_bias = temp_saved_parents[2*i+1]
        child_one_bias = father_bias[:(int)(len(father_bias)/2)] + mother_bias[(int)(len(mother_bias)/2):]
        child_two_bias = mother_bias[:(int)(len(mother_bias)/2)] + father_bias[(int)(len(father_bias)/2):]
        temp_children.append(child_one_bias)
        temp_children.append(child_two_bias)
    print("on_crossover()")

def on_mutation():
    for i in range(mutation_per_population):
        index = random.randint(0,solution_per_population-1)
        chromosome_mutate = temp_population[index]
        for bias_index in range(len(chromosome_mutate)):
            if random.random() > 0.75:
                option = random.randint(0,2)
                if option == 0:
                    chromosome_mutate[bias_index] += 1
                elif option == 1 and chromosome_mutate[bias_index] > 0:
                    chromosome_mutate[bias_index] -= 1
                else:
                    pass
        temp_population[index] = chromosome_mutate
    print("on_mutation()")

def on_generation():
    temp_population = temp_saved_parents + temp_children
    print("on_generation()")

def on_stop():
    print("final population: ", temp_population)
    print("on_stop()")



gnodes = []
gid_map = {} # gid2id map
id = 0
with open('nasnet_imagenet_large.txt') as f:
    lines = f.readlines()
    for line in lines:
        if line[0] == 'i':
            gid = int(line.split('id:')[1].split(',')[0])
            op_type = line.split('type:')[1].split(',')[0]
            identifier = line.split('identifier:')[1].split('\n')[0]
            gnodes.append(GNode(id, gid, sn[op_type]+'_'+str(gid), op_type, identifier))
            gid_map[gid] = id
            id += 1

    for line in lines:
        if line[0] == 'i':
            gid = int(line.split('id:')[1].split(',')[0])
            id = gid_map[gid]
        elif line[:7] == '\toutput':
            output_gid = int(line.split(':')[1].split(',')[0])
            gnodes[id].add_dst(gid_map[output_gid])
    

for idx in range(len(gnodes)):
    for idy in range(len(gnodes)):
        if idx in gnodes[idy].dst and idy not in gnodes[idx].src:
            gnodes[idx].add_src(idy)

jf = open('latency.json')
data = json.load(jf)
print(type(data))

# with open("latency.json",'r', encoding='UTF-8') as f:
#      load_dict = json.load(f)
#      print(type(load_dict))

for gnode in gnodes:
    if gnode.identifier in data:
        gnode.set_latency(data[gnode.identifier])
        # print('Latency')
    else:
        # print('Not profiled OP, use default profile results')
        gnode.set_latency({10:3, 20:3, 30:3, 40:3, 50:3, 60:3, 70:3, 80:3})

for gnode in gnodes:
    if gnode.type == 'Convolution':
        gnode.print_info()

on_start()
for i in range(iteration_times):
    on_fitness()
    on_parents()
    on_crossover()
    on_mutation()
    on_generation()
    print("generation {}".format(i), "-"*150)


print("\niteration ended")
for solution in best_solution_per_generation:
    runtime = solution[0]
    schedule = combine_bfs_bias_to_schedule(bfs, solution[1], gnodes)[1]
    count = 0
    fix_schedule = []
    for layer in schedule:
        fix_layer = []
        for op in layer:
            if op_id_to_type(op) not in [-2,-3]:
                fix_layer.append(op)
        if len(fix_layer) != 0:
            fix_schedule.append(fix_layer)
    if solution[0] == temp_min_runtime[0]:
        temp_best_schedule = fix_schedule
        temp_best_chromosome = solution[1]
    print("runtime: ", solution[0], " schedule: ", fix_schedule)

bias = [0 for i in range(len(bfs))]
schedule = combine_bfs_bias_to_schedule(bfs, bias, gnodes)[1]
runtime = fitness_func(layer_schedule=schedule)

fix_schedule = []
for layer in schedule:
    fix_layer = []
    for op in layer:
        if op_id_to_type(op) not in [-2,-3]:
            fix_layer.append(op)
    if len(fix_layer) != 0:
        fix_schedule.append(fix_layer)
print("compare with bfs schedule", '-'*150) 
print("runtime: ", runtime, " schedule: ", fix_schedule)
print('-'*150)
print("chromosome: ", bias)
print('-'*150)
print("whole schedule: ", combine_bfs_bias_to_schedule(bfs, bias, gnodes)[1])

print()

print("compare with the best schedule", '-'*150)
print("runtime: ", temp_min_runtime, " schedule: ", temp_best_schedule)
print('-'*150)
print("chromosome: ", temp_best_chromosome)
print('-'*150)
print("whole schedule: ", combine_bfs_bias_to_schedule(bfs, temp_best_chromosome, gnodes)[1])
