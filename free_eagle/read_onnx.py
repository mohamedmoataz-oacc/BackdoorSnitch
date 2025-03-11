import onnx
from onnx import helper
from onnx import numpy_helper


def split_onnx_model(model, split_layer_index):
    # Define new graphs for the two parts
    graph = model.graph
    graph1 = helper.make_graph([], 'graph1', graph.input, [], graph.initializer)
    graph2 = helper.make_graph([], 'graph2', [], graph.output, [])

    for i, node in enumerate(graph.node):
        if i < split_layer_index: graph1.node.append(node)
        else: graph2.node.append(node)

    # Set the output of the first part as the input to the second part
    last_node_of_graph1 = graph1.node[-1]
    intermediate_tensor = helper.make_tensor_value_info(last_node_of_graph1.output[0], onnx.TensorProto.FLOAT, None)
    graph1.output.append(intermediate_tensor)
    graph2.input.append(intermediate_tensor)

    # Create new ONNX models
    model1 = helper.make_model(graph1, producer_name='split_model1')
    print(numpy_helper.to_array(model.graph.initializer))
    onnx.checker.check_model(model1)
    model2 = helper.make_model(graph2, producer_name='split_model2')
    onnx.checker.check_model(model2)

    return model1, model2

def compute_split_layer_index(model_layers):
    """
    Not Ready yet.
    """

    # TODO: Implement the right way to find the split layer
    split_layer_index = len(model_layers) // 2
    return split_layer_index

def get_layers(model):
    """
    Not Ready yet.
    """

    # TODO: Implement the right way to get layers
    model_nodes = list(model.graph.node)[::-1]
    c = len(model_nodes)
    layers = []

    current_layer = []
    is_layer = False
    branches = 1
    for node in model_nodes:
        if len(node.input) > 1 and node.op_type != "Gemm":
            branches = len(node.input)
        
        if node.op_type in ("Gemm", "Conv") and branches == 1:
            layers.append({"node_num": c, "layer": [node]})
        
        c -= 1

    print(layers)

if __name__ == '__main__':
    onnx_model_path = "E:\\Desktop\\Final project\\code\\cifar10_resnet18_trojannn.onnx"
    # onnx_model_path = "E:\\Desktop\\Final project\\vgg16-7\\vgg16\\vgg16.onnx"
    # onnx_model_path = "E:\\Downloads\\cifar10_mobilenet_v3_large.onnx"
    onnx_model = onnx.load(onnx_model_path)
    onnx.checker.check_model(onnx_model, full_check=True)

    model1, model2 = split_onnx_model(onnx_model, 3)
    onnx.checker.check_model(model1, full_check=True)
    onnx.checker.check_model(model2, full_check=True)
    
    # Convert onnx to pytorch
    # torch_model_2 = convert(onnx_model)
    # print(len(list(torch_model_2.children())))

    # split_onnx_model(onnx_model, 9)
