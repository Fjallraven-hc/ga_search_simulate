import re

file = './model_logs/amoebanet.log'
conv_exprs = []
dwconv_exprs = []

with open(file) as f:
    lines = f.readlines()
    for line in lines:
        if line[0] == 'i':
            gid = int(line.split('id:')[1].split(',')[0])
            op_type = line.split('type:')[1].split(',')[0]
            identifier = line.split('identifier:')[1].split('\n')[0]
            if op_type == 'Convolution':
                shapes = re.findall(r"\d+\.?\d*", identifier.split('Convolution')[1])
                # shapes = identifier.split('float')[0].split('Convolution')[1].split(';')
                input_shape = '_'.join(shapes[:4])
                kernel_shape = '_'.join(shapes[4:8])
                output_shape = '_'.join(shapes[8:12])
                stride = '_'.join(shapes[12:14])
                dilation = '_'.join(shapes[14:16])
                padding = '_'.join(shapes[16:18])
                conv_exprs.append('conv2d|i+{}|w+{}|o+{}|ws+{}|wd+{}|p+{}'.format(\
                                        input_shape, \
                                        kernel_shape, \
                                        output_shape, \
                                        stride, \
                                        dilation, \
                                        padding
                                        ))

            if op_type == 'DepthwiseConv2dNative':
                shapes = re.findall(r"\d+\.?\d*", identifier.split('DepthwiseConv2dNative')[1])
                # shapes = identifier.split('float')[0].split('Convolution')[1].split(';')
                input_shape = '_'.join(shapes[:4])
                C = int(shapes[1])
                assert C == int(shapes[6]), '{}: Channel error!'.format(identifier)
                depth_multiplier = int(shapes[7])
                assert depth_multiplier == 1, 'depth_multiplier error!'
                OC = C * depth_multiplier
                KH = int(shapes[4])
                KW = int(shapes[5])
                kernel_shape = '_'.join([str(OC), str(C), str(KH), str(KW)])
                output_shape = '_'.join(shapes[8:12])
                stride = '_'.join(shapes[12:14])
                dilation = '_'.join(shapes[14:16])
                padding = '_'.join(shapes[16:18])
                dwconv_exprs.append('dwconv2d|i+{}|w+{}|o+{}|ws+{}|wd+{}|p+{}'.format(\
                                        input_shape, \
                                        kernel_shape, \
                                        output_shape, \
                                        stride, \
                                        dilation, \
                                        padding
                                        ))

conv_exprs = list(set(conv_exprs))
dwconv_exprs = list(set(dwconv_exprs))
for conv_expr in conv_exprs:
    print(conv_expr)

for dwconv_expr in dwconv_exprs:
    print(dwconv_expr)