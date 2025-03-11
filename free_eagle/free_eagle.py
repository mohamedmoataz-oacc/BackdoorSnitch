from detection_method import BackdoorDetector
from free_eagle.read_onnx import *
import onnxruntime as ort
from tqdm import tqdm
import numpy as np

import torch
import torch.nn.functional as F
import torch.optim as optim


class FreeEagleDetector(BackdoorDetector):
    def __init__(self, model_path: str, l_sep: int = None):
        super().__init__(model_path)
        self.l_sep = self.set_l_sep(l_sep)
        self.classifier_after_relu = False
    
    def set_l_sep(self, l_sep: int = None):
        if l_sep: self.l_sep = l_sep
        else:
            self.l_sep = compute_split_layer_index(get_layers(self.model))
        self.classifier = self._get_classifier_part()
        self.session = ort.InferenceSession(self.classifier.SerializeToString())
    
    def generate_dummy_intermediate_rep(self, target_class, scale_factor = 5e-3):
        irc = self._create_random_ir(self._get_intermediate_output_shape())

        optimizer = ONNXModelWrapper(self.session, self.classifier_after_relu)
        optimized_IRc = optimizer.optimize_intermediate_representation(irc, target_class, scale_factor)
        return optimized_IRc
    
    def detect(self):
        # Generate dummy intermediate representations. (lines 3-6 in FreeEagle algorithm)
        representations = []
        for target_class in self.get_classes():
            IRc1 = self.generate_dummy_intermediate_rep(target_class)
            IRc2 = self.generate_dummy_intermediate_rep(target_class)
            IRcavg = (IRc1 + IRc2) / 2
            representations.append(IRcavg)
        
        # Compute the  the posteriors matrix. (line 7 in FreeEagle algorithm)
        mat_p = []
        for representation in representations:
            output = self.session.run(None, {self.session.get_inputs()[0].name: representation})[0]
            mat_p.append(output)
        mat_p = np.array(mat_p)
        return mat_p
    
    def _get_classifier_part(self):
        model1, model2 = split_onnx_model(self.model, self.l_sep)
        # TODO: Set clamp
        return model2
    
    def _get_intermediate_output_shape(self):
        graph = self.model.graph

        # Get the output shape of the last node in the first part of the model
        output_tensor = graph.node[self.l_sep - 1].output[0]
        output_info = [v for v in graph.value_info if v.name == output_tensor][0]
        output_shape = [dim.dim_value for dim in output_info.type.tensor_type.shape.dim]

        return output_shape

    def _create_random_ir(output_shape):
        # Generate a random tensor with the same shape as the output tensor
        dummy_representation = np.random.rand(*output_shape).astype(np.float32)
        return dummy_representation

class ONNXModelWrapper(torch.nn.Module):
    def __init__(self, onnx_session, clamp=False):
        super(ONNXModelWrapper, self).__init__()
        self.onnx_session = onnx_session
        self.clamp = clamp

    def forward(self, x):
        input_name = self.onnx_session.get_inputs()[0].name
        ort_inputs = {input_name: x.detach().cpu().numpy()}
        ort_outs = self.onnx_session.run(None, ort_inputs)
        return torch.tensor(ort_outs[0])

    def optimize_intermediate_representation(
        self, IRc, target_class, lambda_l2, num_steps=100, learning_rate=0.01
    ):
        optimizer = optim.SGD([IRc], lr=learning_rate)

        for step in tqdm(range(num_steps), desc="FreeEagle - Optimizing IRc"):
            optimizer.zero_grad()

            # Forward pass
            output = self(IRc)
            
            # Calculate cross-entropy loss (CE)
            ce_loss = F.cross_entropy(output, target_class)
            
            # Calculate L2 norm
            l2_norm = torch.norm(IRc, p=2)
            
            # Calculate total loss
            total_loss = ce_loss + lambda_l2 * l2_norm

            # Backward pass and optimization
            total_loss.backward()
            optimizer.step()

            # Clamp the values of IRc to be in the range [0, +∞]
            if self.clamp:
                with torch.no_grad():
                    IRc.clamp_(min=0)
            
            if (step + 1) % 10 == 0:
                print(f'Step [{step + 1}/{num_steps}], Loss: {total_loss.item()}')

        return IRc
