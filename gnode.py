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
    "Broadcast":"Broadcast",
    "BatchMatMul":"BatchMatMul",
    "Softmax":"Softmax",
    "Log":"Log",
    "Testop":"Testop"
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
        self.in_chain = False

    def __str__(self):
        return str(self.id)

    def add_src(self, snode):
        self.src.append(snode)

    def add_dst(self, dnode):
        self.dst.append(dnode)

    def set_level(self, level):
        self.level = level

    def set_latency(self, latency):
        self.latency = latency # dict

    def estimate_latency(self, resource):
        return self.latency[str(resource)]
        # return self.latency[str(math.ceil(resource / 10)*10)]

    def print_info(self):
        print("id:{}".format(self.id))
        print("- name:{}".format(self.name))
        print("- type:{}".format(self.type))
        print("- identifier:{}".format(self.identifier))
        print("- dst:{}".format(" ".join(list(str(i) for i in self.dst))))
        print("- src:{}".format(" ".join(list(str(i) for i in self.src))))
        # print("- latency:", self.latency)
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

flag = False
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
                if op_type == 'Constant':
                    continue
                identifier = line.split('identifier:')[1].split('\n')[0]
                gnodes.append(GNode(id, gid, sn[op_type]+'_'+str(gid), op_type, identifier))
                gid_map[gid] = id
                id += 1

        for line in lines:
            if line[0] == 'i':
                flag = True
                gid = int(line.split('id:')[1].split(',')[0])
                op_type = line.split('type:')[1].split(',')[0]
                if op_type == 'Constant':
                    flag = False
                    continue
                id = gid_map[gid]
            elif line[:7] == '\toutput' and flag:
                output_gid = int(line.split(':')[1].split(',')[0])
                gnodes[id].add_dst(gid_map[output_gid])
        

    for idx in range(len(gnodes)):
        for idy in range(len(gnodes)):
            if idx in gnodes[idy].dst and idy not in gnodes[idx].src:
                gnodes[idx].add_src(idy)

    # json_file = './kernel_profile/' + file.split('/')[-1].split('.')[0] + '.json'
    # jf = open(json_file)
    # data = json.load(jf)

    for gnode in gnodes:
        # if gnode.identifier in data:
        #     # print(gnode.identifier)
        #     gnode.set_latency(data[gnode.identifier])
        #     # print('Latency')
        # else:
        gnode.set_latency({'1': 33.061, '2': 18.092, '3': 13.443, '4': 11.036, '5': 9.404, '6': 8.777, '7': 7.823, '8': 7.673, '9': 7.126, '10': 6.639, '11': 6.56, '12': 6.524, '13': 6.099, '14': 6.137, '15': 5.961, '16': 5.843, '17': 5.443, '18': 5.51, '19': 5.532, '20': 5.465, '21': 5.503, '22': 5.475, '23': 5.532, '24': 5.452, '25': 4.963, '26': 4.934, '27': 4.966, '28': 5.03, '29': 4.944, '30': 4.924, '31': 4.972, '32': 4.96, '33': 4.969, '34': 4.963, '35': 5.007, '36': 4.995, '37': 5.059, '38': 5.014, '39': 5.055, '40': 4.576, '41': 5.087, '42': 5.097, '43': 5.068, '44': 5.094, '45': 5.142, '46': 5.068, '47': 5.168, '48': 5.094, '49': 4.707, '50': 4.659, '51': 4.665, '52': 4.767, '53': 4.688, '54': 4.793, '55': 4.71, '56': 4.668, '57': 4.726, '58': 4.825, '59': 4.736, '60': 4.691, '61': 4.688, '62': 4.688, '63': 4.684, '64': 4.691, '65': 4.723, '66': 4.684, '67': 4.716, '68': 4.7, '69': 4.723, '70': 4.716, '71': 4.72, '72': 4.716, '73': 4.729, '74': 4.707, '75': 4.719, '76': 4.716, '77': 4.707, '78': 4.691, '79': 4.723, '80': 4.723})
            # if gnode.type == 'Convolution' or gnode.type == 'DepthwiseConv2dNative':
            #     print('Not profiled kernel for {}, use default profile results'.format(gnode.identifier))
            # #     gnode.set_latency({"10": 201.67, "20": 112.13, "30": 76.411, "40": 63.423, "50": 51.017, "60": 51.164, "70": 51.343, "80": 38.271})
            # # else:
            # # gnode.set_latency({'10':0, '20':0, '30':0, '40':0, '50':0, '60':0, '70':0, '80':0})
            # gnode.set_latency({'10':3, '20':3, '30':3, '40':3, '50':3, '60':3, '70':3, '80':3})

    return gnodes



class Chain(GNode):
    def __init__(self, id, ops=None):
        super().__init__(id=id, gid=None, name=None, op_type=None, identifier=None, level=None)
        self.id = id
        self.ops = ops
        self.src = []
        self.dst = []

    def set_latency(self, latency):
        pass
        # self.latency = latency # dict

    def estimate_latency(self, resource):
        pass
        # return self.latency[str(resource)]
        # return self.latency[str(math.ceil(resource / 10)*10)]

    def print_info(self):
        pass
        # print("id:{}".format(self.id))
        # print("- name:{}".format(self.name))
        # print("- type:{}".format(self.type))
        # print("- identifier:{}".format(self.identifier))
        # print("- dst:{}".format(" ".join(list(str(i) for i in self.dst))))
        # print("- src:{}".format(" ".join(list(str(i) for i in self.src))))
        # # print("- latency:", self.latency)
        # print()