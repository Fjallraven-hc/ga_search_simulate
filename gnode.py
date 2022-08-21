import re
import json
import math

sn = {
    "Convolution":"C",
    "DepthwiseConv2dNative":"DC",
    "Add":"ADD",
    "Constant":"Constant",
    "Pad":"Pad",
    "AvgPool":"AvgPool",
    "MaxPool":"MaxPool",
    "Relu":"Relu",
    "Slice":"Slice",
    "Concat":"Concat",
    "Parameter":"Parameter",
    "Reshape":"Reshape",
    "BatchNormInference":"BN",
    "Sum":"Sum",
    "Divide":"Divide",
    "Dot":"Dot",
    "Result":"Result",
    "Combine":"Combine" # used for seq_op_fuse type
}

class GNode:
    def __init__(self, id=None, gid=None, name=None, op_type=None, identifier=None, level=None):
        self.id = id
        self.gid = gid
        self.name = name
        self.type = op_type
        self.identifier = identifier
        self.dst = []
        self.src = []
        self.combine_flag = False

    def add_src(self, snode):
        self.src.append(snode)

    def add_dst(self, dnode):
        self.dst.append(dnode)

    def set_level(self, level):
        self.level = level

    def set_latency(self, latency):
        self.latency = latency # dict

    def estimate_latency(self, resource):
        return self.latency[str(math.ceil(resource / 10)*10)]

    def print_info(self):
        print("id:{}".format(self.id))
        print("- name:{}".format(self.name))
        print("- type:{}".format(self.type))
        print("- identifier:{}".format(self.identifier))
        print("- dst:{}".format(" ".join(list(str(i) for i in self.dst))))
        print("- src:{}".format(" ".join(list(str(i) for i in self.src))))
        print("- latency:", self.latency)
        print()


def gen_key(data, dtype="float"):
    op_type = data["op_type"]
    in_shape = data["in_shape"]
    out_shape = data["out_shape"]
    parameters = data["parameters"] if "parameters" in data else {}

    key = op_type
    key += ";".join(",".join(str(i) for i in shape) for shape in in_shape)
    if op_type in conv_augmented:
        key += "float" * len(in_shape)
    else:
        key += ";" + ";".join(",".join(str(i) for i in shape)
                              for shape in out_shape)
        key += "float" * (len(in_shape) + len(out_shape))

    if op_type in conv_family:
        key += "".join(["Strides{", ", ".join(str(i)
                                              for i in parameters["window_movement_strides"]), "}"])
        key += "".join(["Strides{", ", ".join(str(i)
                                              for i in parameters["window_dilation_strides"]), "}"])
        key += "".join(["CoordinateDiff{", ", ".join(str(i)
                                                     for i in parameters["padding_below_diff"]), "}"])
        key = key.replace(op_type, "Convolution")
        for op in op_type.split("_"):
            if op in ["Fused", "Convolution"]:
                pass
            elif op == "Add":
                key += "Add" + ";".join(",".join(str(i) for i in shape)
                                        for shape in out_shape * 3) + "float" * 3 * len(out_shape)
            elif op == "Relu":
                key += "Relu" + ";".join(",".join(str(i) for i in shape)
                                         for shape in out_shape * 2) + "float" * 2 * len(out_shape)
            else:
                raise ("to be specified")
    elif op_type == "AvgPool" or op_type == "MaxPool":
        key += "Shape{" + ", ".join(str(i)
                                    for i in parameters["window_shape"]) + "}"
        key += "Strides{" + ", ".join(str(i)
                                      for i in parameters["window_stride"]) + "}"
        key += "Shape{" + ", ".join(str(i)
                                    for i in parameters["padding_below"]) + "}"
    else:
        pass

    return key


def load_gnodes(file):
    gnodes = []
    gid_map = {} # gid2id map
    id = 0
    with open(file) as f:
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

    for gnode in gnodes:
        if gnode.identifier in data:
            gnode.set_latency(data[gnode.identifier])
            # print('Latency')
        else:
            # print('Not profiled OP, use default profile results')
            gnode.set_latency({'10':3, '20':3, '30':3, '40':3, '50':3, '60':3, '70':3, '80':3})
            # gnode.set_latency({'10':142, '20':77, '30':43, '40':33, '50':44, '60':35, '70':36, '80':25})

    # for gnode in gnodes:
    #     if gnode.type == 'Convolution':
    #         gnode.print_info()
    return gnodes