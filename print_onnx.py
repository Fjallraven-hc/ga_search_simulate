import onnx
import onnxruntime

model = onnx.load('/data1/v-chengyu/benchmarks/nimble/experiment/amoebanet.onnx')
onnx.checker.check_model(model)
session = onnxruntime.InferenceSession('/data1/v-chengyu/benchmarks/nimble/experiment/amoebanet.onnx')
inp = session.get_inputs()[0]
# conv1=session.get_inputs()['conv1']
# out1=session.get_outputs()[1]
out=session.get_provider_options()
# print(inp,conv1,out1)
print(inp)
# print(out)
for node in model.graph.node:
    print('=============')
    print(node.name)
    print('=============')
    print(node.output)
    # for a in node.attribute:
    #     print(a.tensors)
# graph=onnx.helper.printable_graph(model.graph)
# print(graph)

from onnx import shape_inference
inferred_model = shape_inference.infer_shapes(model)
print(inferred_model.graph.value_info)