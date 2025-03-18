from detection_method import BackdoorDetector
from onnx import version_converter
from free_eagle.read_onnx import *
import onnxruntime as ort
from tqdm import tqdm
import numpy as np

import torch
from torch import nn
import torch.optim as optim
from onnx2torch import convert


class FreeEagleDetector(BackdoorDetector):
    def __init__(self, model_path: str, l_sep: int = None):
        super().__init__(model_path)
        self.model = shape_inference.infer_shapes(self.model)
        self.set_l_sep(l_sep)
        self.classifier_after_relu = False
    
    def set_l_sep(self, l_sep: int = None):
        if l_sep: self.l_sep = l_sep
        else:
            self.l_sep = compute_split_layer_index(get_layers(self.model))
        self.classifier = self._get_classifier_part()

        # This line is needed for now because we are using a version of ONNX (V1.17.0) that uses Opset 22,
        # which is still under development and not officially supported by the version of ONNX Runtime
        # we are using (V1.20.1, which is the latest at the time this code was written).
        # ONNX Runtime only guarantees support for models stamped with officially released
        # opset versions, and the current official support for the ai.onnx domain is up to Opset 21.
        # TODO: Remove this line when ONNX Runtime starts supporting Opset 22.

        # self.classifier = version_converter.convert_version(self.classifier, target_version=21)

        # UPDATE: We commented that line because we now set the opset version to 16 as this is the
        # latest version that onnx2torch supports.

        self.session = ort.InferenceSession(self.classifier.SerializeToString())
    
    def generate_dummy_intermediate_rep(self, target_class, scale_factor = 5e-3):
        irc = torch.tensor(self._create_random_ir(self._get_intermediate_output_shape()))

        optimizer = ONNXModelWrapper(self.classifier, self.classifier_after_relu)
        optimized_IRc = optimizer.optimize_intermediate_representation(irc, target_class, scale_factor)
        # optimized_IRc = irc
        return optimized_IRc.detach().cpu().numpy()
    
    def generate_posteriors_matrix(self, intermediate_representations):
        mat_p = []
        for representation in intermediate_representations:
            output = self.session.run(None, {self.session.get_inputs()[0].name: representation})[0]
            mat_p.append(output)
        mat_p = np.array(mat_p).transpose()
        return mat_p
    
    def detect(self):
        # Generate dummy intermediate representations. (lines 3-6 in FreeEagle algorithm)
        representations = []
        for target_class in self.get_classes():
            IRc1 = self.generate_dummy_intermediate_rep(target_class)
            IRc2 = self.generate_dummy_intermediate_rep(target_class)
            IRcavg = (IRc1 + IRc2) / 2
            representations.append(IRcavg)
        
        # Compute the  the posteriors matrix. (line 7 in FreeEagle algorithm)
        self.mat_p = np.squeeze(self.generate_posteriors_matrix(representations))

        # Posterior Outlier Detection and Anomaly Metric Computation (lines 8-13 in FreeEagle algorithm)
        np.fill_diagonal(self.mat_p, 0)
        self.v = np.mean(self.mat_p, axis=0)
        Q1, Q3 = np.percentile(self.v, 25), np.percentile(self.v, 75)
        m_trojaned = (max(self.v) - Q3) / (Q3 - Q1)
        return m_trojaned
    
    def _get_classifier_part(self):
        _, model2 = split_onnx_model(self.model, self.l_sep)
        # TODO: Set clamp
        return model2
    
    def _get_intermediate_output_shape(self):
        graph = self.model.graph

        # Get the output shape of the last node in the first part of the model
        output_tensor = graph.node[self.l_sep - 1].output[0]
        output_info = [v for v in graph.value_info if v.name == output_tensor][0]
        output_shape = [dim.dim_value for dim in output_info.type.tensor_type.shape.dim]

        return output_shape

    def _create_random_ir(self, output_shape):
        # Generate a random tensor with the same shape as the output tensor
        dummy_representation = np.random.rand(*output_shape).astype(np.float32)
        return dummy_representation

class ONNXModelWrapper(torch.nn.Module):
    def __init__(self, model, clamp=False):
        super(ONNXModelWrapper, self).__init__()
        self.model = convert(model)
        self.clamp = clamp

    def forward(self, x: torch.Tensor):
        return self.model(x)

    def optimize_intermediate_representation(
        self, IRc, target_class, lambda_l2, num_steps=1000, learning_rate=0.001
    ):
        self.model.eval()
        IRc.requires_grad = True
        
        target = torch.tensor([target_class])
        optimizer = optim.Adam([IRc], lr=learning_rate, weight_decay=lambda_l2)
        loss_fn = nn.CrossEntropyLoss()

        best_IRc = [None, float('inf')]
        for step in tqdm(range(num_steps), desc="FreeEagle - Optimizing IRc for class " + str(target_class)):
            optimizer.zero_grad()

            # Forward pass
            output = self(IRc)
            
            # Calculate cross-entropy loss (CE)
            ce_loss = loss_fn(output, target)
            if ce_loss < best_IRc[1]:
                best_IRc = [IRc.detach().clone(), ce_loss]

            # Backward pass and optimization
            ce_loss.backward()
            optimizer.step()

            # Clamp the values of IRc to be in the range [0, +∞]
            if self.clamp:
                with torch.no_grad():
                    IRc.clamp_(min=0)
            
            # if (step + 1) % 100 == 0:
            #     print(f'Step [{step + 1}/{num_steps}], Loss: {ce_loss.item()}')

        print(f"Loss: {best_IRc[1]}")
        return best_IRc[0]
