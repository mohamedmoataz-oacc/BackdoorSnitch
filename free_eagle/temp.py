import onnx
import onnxruntime as ort
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim


def calculate_loss(session, dummy_representation, target_class, lambda_l2):
    # Perform forward pass
    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: dummy_representation})[0]

    # Calculate cross-entropy loss (CE)
    log_softmax = np.log(np.exp(output) / np.exp(output).sum(axis=1, keepdims=True))
    ce_loss = -log_softmax[np.arange(len(target_class)), target_class].mean()

    # Calculate L2 norm
    l2_norm = np.linalg.norm(dummy_representation)

    # Calculate total loss
    total_loss = ce_loss + lambda_l2 * l2_norm
    return total_loss
