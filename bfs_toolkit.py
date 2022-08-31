def get_bfs_level(gnodes):
    tag_visited = [0 for i in range(len(gnodes))]
    bfs_result = [-1 for i in range(len(gnodes))]
    while 0 in tag_visited:
        for idx in range(len(gnodes)):
            pre_ok = True
            
            if gnodes[idx].type == "Constant":
                tag_visited[idx] = 1
                bfs_result[idx] = 0
                continue

            if len(gnodes[idx].src) == 0:
                tag_visited[idx] = 1
                bfs_result[idx] = 0
                continue

            for pre_id in gnodes[idx].src:
                if tag_visited[pre_id] == 0:
                    pre_ok = False
                    break

            if pre_ok:
                max_pre_stage = bfs_result[gnodes[idx].src[0]]
                for pre_id in gnodes[idx].src:
                    if max_pre_stage < bfs_result[pre_id]:
                        max_pre_stage = bfs_result[pre_id]
                tag_visited[idx] = 1
                bfs_result[idx] = max_pre_stage + 1
    # print(bfs_result)
    return bfs_result


def update_schedule(schedule, bias, gnodes, for_chain=False):
    ops_stage = [0 for i in range(len(gnodes))]
    tag_visited = [0 for i in range(len(gnodes))]
    
    while 0 in tag_visited:
        for idx in range(len(gnodes)):
            pre_ok = True
            if schedule[idx] == 0 and not for_chain:
                ops_stage[idx] = 0
                tag_visited[idx] = 1
                continue
            if len(gnodes[idx].src) == 0 and not for_chain:
                ops_stage[idx] = 0
                tag_visited[idx] = 1
                continue
            
            for pre_id in gnodes[idx].src:
                if tag_visited[pre_id] == 0:
                    pre_ok = False
                    break
            
            if pre_ok:
                if gnodes[idx].src == []:
                    ops_stage[idx] = (schedule[idx] + bias[idx])
                else:
                    max_pre_stage = ops_stage[gnodes[idx].src[0]]
                    for pre_id in gnodes[idx].src:
                        if max_pre_stage < ops_stage[pre_id]:
                            max_pre_stage = ops_stage[pre_id]
                    # if (max_pre_stage + 1) > (schedule[idx] + bias[idx]):
                    #     ops_stage[idx] = max_pre_stage + 1
                    # else:
                    #     ops_stage[idx] = (schedule[idx] + bias[idx])
                    ops_stage[idx] = (max_pre_stage + bias[idx] + 1)
                tag_visited[idx] = 1
    stage_schedule = [[] for i in range(max(ops_stage) + 1)]
    for idx in range(len(gnodes)):
        stage_schedule[ops_stage[idx]].append(idx)
    
    b = list(set(sorted(ops_stage)))
    fixed_ops_stage = [b.index(a) for a in ops_stage]

    while [] in stage_schedule:
        stage_schedule.remove([])
    # print(stage_schedule)
    return fixed_ops_stage, stage_schedule


def get_gnode_schedule_chrom_from_chain_schedule(chain_schedule, bfs):
    ops_stage = [0 for i in range(len(gnodes))]
    tag_visited = [0 for i in range(len(gnodes))]