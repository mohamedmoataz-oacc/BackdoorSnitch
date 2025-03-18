from onnx import load_model


class BackdoorDetector:
    def __init__(self, model_path: str):
        model = load_model(model_path)
        self.model = model
    
    def get_classes(self):
        output_tensor = self.model.graph.output[0]
        output_shape = [dim.dim_value for dim in output_tensor.type.tensor_type.shape.dim]
        return list(range(output_shape[-1]))
    
    def detect(self, *args, **kwargs): ...
