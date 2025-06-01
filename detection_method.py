import os
from onnx import load_model
from tqdm import tqdm

import torch
from torch import nn
import torch.optim as optim
from onnx2torch import convert


class BackdoorDetector:
    def __init__(self, model_path: str, logger=None):
        model = load_model(model_path)
        self.model = model
        self.device = 'cpu'
        self.logger = logger
    
    def log_or_print(self, message, **kwargs):
        if self.logger: self.logger.info(message)
        else: print(message, **kwargs)
    
    def get_classes(self):
        output_tensor = self.model.graph.output[0]
        output_shape = [dim.dim_value for dim in output_tensor.type.tensor_type.shape.dim]
        return list(range(output_shape[-1]))
    
    def get_params(self) -> dict:
        """
        Returns parameters of the detector as a dictionary.
        The keys are names of hyperparameters and the values are the actual values of the hyperparameters.
        The dictionary must contain all hyperparameters of the detector, including the ones that are set by default.
        """
        raise NotImplementedError
    
    def detect(self, *args, **kwargs) -> tuple[bool, dict]:
        """
        Returns:
            tuple[bool, dict]: (is_backdoor, detector_results)
        """
        raise NotImplementedError


class ONNXModelWrapper(torch.nn.Module):
    def __init__(self, model, clamp=False, logger=None):
        """
        Initializes the ONNXModelWrapper class.
        
        Args:
            model (onnx.ModelProto): The ONNX model to be converted.
            clamp (bool, optional): Whether to clamp the output of the model in the range [0, 1]. Defaults to False.
        """
        super(ONNXModelWrapper, self).__init__()
        self.model = convert(model)
        self.logger = logger
        self.clamp = clamp
        self.model.eval()

    def forward(self, x: torch.Tensor):
        return self.model(x)
    
    def log_or_print(self, message):
        if self.logger: self.logger.info(message)
        else: print(message)

    def optimize_intermediate_representation(
        self, IRc, target_class, lambda_l2, num_steps=500, learning_rate=0.001
    ):
        IRc.requires_grad = True
        
        target = torch.tensor([target_class])
        optimizer = optim.Adam([IRc], lr=learning_rate, weight_decay=lambda_l2)
        loss_fn = nn.CrossEntropyLoss()

        LOG_INTERVAL = num_steps // 10
        progress_bar = tqdm(
            range(num_steps), file=open(os.devnull, 'w') if self.logger else None,
            desc="NetCop - Optimizing IRc for class " + str(target_class)
        )
        
        best_IRc = [None, float('inf')]
        last_printed = ''
        for _ in progress_bar:
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
            
            if self.logger and progress_bar.n % LOG_INTERVAL == 0:
                if str(progress_bar) != last_printed:
                    self.log_or_print(str(progress_bar))
                    last_printed = str(progress_bar)

        self.log_or_print(f"Loss: {best_IRc[1]}")
        return best_IRc[0]
