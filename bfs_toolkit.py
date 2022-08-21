from pickletools import read_unicodestringnl


def get_bfs_level(gnodes):
    # tag_visited = [0 for i in range(len(gnodes))]
    # add combine case
    tag_visited = []
    bfs_result = []
    for gnode in gnodes:
        if gnode.combine_flag or gnode.type == "Constant" or len(gnode.src) == 0:
            tag_visited.append(1)
            if not gnode.combine_flag:
                bfs_result.append(0)
            else:
                bfs_result.append(-1)
        else:
            tag_visited.append(0)
            bfs_result.append(-1)

    while 0 in tag_visited:
        for idx in range(len(gnodes)):
            pre_ok = True

            if tag_visited[idx]:
                continue

            for pre_id in gnodes[idx].src:
                if tag_visited[pre_id] == 0:
                    pre_ok = False
                    break

            if pre_ok:
                try:
                    max_pre_stage = bfs_result[gnodes[idx].src[0]]
                    for pre_id in gnodes[idx].src:
                        if max_pre_stage < bfs_result[pre_id]:
                            max_pre_stage = bfs_result[pre_id]
                    tag_visited[idx] = 1
                    bfs_result[idx] = max_pre_stage + 1
                except:
                    print("wrong idx: ", idx)
                    read_unicodestringnl
    # print(bfs_result)
    return bfs_result


def update_schedule(schedule, bias, gnodes):
    ops_stage = []
    tag_visited = []
    for gnode in gnodes:
        if gnode.combine_flag or schedule[gnode.id] == 0 or len(gnode.src) == 0:
            tag_visited.append(1)
            if not gnode.combine_flag:
                ops_stage.append(0)
            else:
                ops_stage.append(-1)
        else:
            tag_visited.append(0)
            ops_stage.append(0)
    
    while 0 in tag_visited:
        for idx in range(len(gnodes)):
            pre_ok = True
            if tag_visited[idx]:
                continue
            
            for pre_id in gnodes[idx].src:
                if tag_visited[pre_id] == 0:
                    pre_ok = False
                    break
            
            if pre_ok:
                max_pre_stage = ops_stage[gnodes[idx].src[0]]
                for pre_id in gnodes[idx].src:
                    if max_pre_stage < ops_stage[pre_id]:
                        max_pre_stage = ops_stage[pre_id]
                if (max_pre_stage + 1) > (schedule[idx] + bias[idx]):
                    ops_stage[idx] = max_pre_stage + 1
                else:
                    ops_stage[idx] = (schedule[idx] + bias[idx])
                tag_visited[idx] = 1
    stage_schedule = [[] for i in range(max(ops_stage) + 1)]
    for idx in range(len(gnodes)):
        if ops_stage[idx] != -1:
            stage_schedule[ops_stage[idx]].append(idx)
    
    b = list(set(sorted(ops_stage)))
    fixed_ops_stage = [b.index(a) for a in ops_stage]

    while [] in stage_schedule:
        stage_schedule.remove([])
    return fixed_ops_stage, stage_schedule