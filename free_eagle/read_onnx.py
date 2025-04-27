import onnx
from onnx2torch import convert
from onnx import helper, shape_inference, utils


def split_onnx_model(model: onnx.ModelProto, split_layer_index):
    # Run shape inference to enrich the model with shape information
    graph = shape_inference.infer_shapes(model).graph
    
    # Create two new ONNX graphs from the original model
    graph1 = helper.make_graph([], 'graph1', graph.input, [], graph.initializer)
    graph2 = helper.make_graph([], 'graph2', [], graph.output, graph.initializer)

    for i, node in enumerate(graph.node):
        # print(i, node.input, node.output)
        if i < split_layer_index: graph1.node.append(node)
        else: graph2.node.append(node)

    # Collect all required outputs from graph1 for graph2
    required_outputs = set()
    required_initializers = set()
    init_names = set(i.name for i in graph.initializer)
    g1_outputs = set(i for node in graph1.node for i in node.output)
    for node in graph2.node:
        for input_name in node.input:
            if input_name in g1_outputs:
                required_outputs.add(input_name)
            elif input_name in init_names:
                required_initializers.add(input_name)
    print("Required outputs:", required_outputs)

    # Find and connect all required outputs
    intermediate_tensors = []
    for output_name in required_outputs:
        for value_info in graph.value_info:
            if value_info.name == output_name:
                shape = [dim.dim_value or dim.dim_param for dim in value_info.type.tensor_type.shape.dim]
                tensor_info = helper.make_tensor_value_info(
                    output_name, value_info.type.tensor_type.elem_type, shape
                )
                intermediate_tensors.append(tensor_info)
                break
        else:
            raise ValueError(f"Required output tensor {output_name} not found in the graph.")
    
    # Remove all unused initializers from graph2
    for initializer in graph2.initializer:
        if initializer.name not in required_initializers:
            graph2.initializer.remove(initializer)

    # Assign intermediate tensors as outputs of graph1 and inputs to graph2
    graph1.output.extend(intermediate_tensors)
    graph2.input.extend(intermediate_tensors)

    # Create new ONNX models
    model1 = helper.make_model(graph1, producer_name='split_model1')
    onnx.checker.check_model(model1)

    opset = model.opset_import
    model2 = helper.make_model(graph2, producer_name='split_model2', opset_imports=opset)
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

def find_options(model: onnx.ModelProto):
    # Run shape inference to enrich the model with shape information
    graph = shape_inference.infer_shapes(model).graph
    
    for split_layer_index in range(10, len(graph.node)-10):
        g2_nodes = []
        g1_outputs = set()
        for i, node in enumerate(graph.node):
            if i >= split_layer_index: g2_nodes.append(node)
            else:
                for j in node.output:
                    g1_outputs.add(j)

        # Collect all required outputs from graph1 for graph2
        required_outputs = set()
        for node in g2_nodes:
            for input_name in node.input:
                if input_name in g1_outputs:
                    required_outputs.add(input_name)
        
        if len(required_outputs) <= 1:
            print("Split layer index:", split_layer_index, "Required outputs:", required_outputs)

if __name__ == '__main__':
    from onnx import version_converter

    # onnx_model_path = "E:\\Desktop\\Final project\\code\\cifar10_resnet18_trojannn.onnx"
    # onnx_model_path = "E:\\Downloads\\cifar10_mobilenet_v3_large.onnx"
    onnx_model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_convnext_tiny_badnet_0_1.onnx"
    # onnx_model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\tiny_vit_b_16_wanet_0_005.onnx"
    # onnx_model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_resnet18_badnet.onnx"
    onnx_model = onnx.load(onnx_model_path)
    onnx.checker.check_model(onnx_model, full_check=True)

    find_options(onnx_model)

    # model1, model2 = split_onnx_model(onnx_model, 61)
    # model1 = version_converter.convert_version(model1, target_version=21)
    # model2 = version_converter.convert_version(model2, target_version=16)

    # model1 = shape_inference.infer_shapes(model1, strict_mode=True)
    # model2 = shape_inference.infer_shapes(model2, strict_mode=True)
    # onnx.save(model1, "model1.onnx")
    # onnx.save(model2, "classifier2.onnx")
    
    # Convert onnx to pytorch
    # torch_model_2 = convert(model2)
    # print(len(list(torch_model_2.children())))
