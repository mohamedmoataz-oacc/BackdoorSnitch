import os
import glob
import torch
import random
import numpy as np
from PIL import Image
from tqdm import tqdm
import torchvision.transforms as transforms
from detection_method import BackdoorDetector, ONNXModelWrapper


# STRIP Detector class
class STRIPDetector(BackdoorDetector):
    def __init__(
        self, model_path, clean_images_dir=None, k=1.0, image_size: tuple = None,
        logger=None, mean_entropy=None, std_entropy=None, threshold=None
    ):
        """
        Initialize the STRIPDetector.

        Args:
            model_path (str): Path to the ONNX model file.
            clean_images_dir (str): Directory containing clean images for perturbation.
            k (float, optional): Multiplicative factor for threshold calculation. Default is 1.0.

        The initialization process involves loading the model, setting up the image transformation
        pipeline, loading and preprocessing clean images, and computing entropy statistics for 
        thresholding purposes.
        """

        super().__init__(model_path, logger)
        self.model_torch = ONNXModelWrapper(self.model)
        self.clean_images_dir = clean_images_dir
        self.k = k

        # Define image transform
        image_transforms = [
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.2010])
        ]
        if image_size is not None: image_transforms.insert(0, transforms.Resize(image_size))
        self.transform = transforms.Compose(image_transforms)

        self.clean_image_tensors = [
            self.load_and_preprocess(path)
            for path in (
                glob.glob(os.path.join(self.clean_images_dir, '*.jpg')) +
                glob.glob(os.path.join(self.clean_images_dir, '*.png'))
            )
        ]

        if mean_entropy is not None and std_entropy is not None and threshold is not None:
            self.mean_entropy = mean_entropy
            self.std_entropy = std_entropy
            self.threshold = threshold
        else:
            LOG_INTERVAL = len(self.clean_image_tensors) // 10
            progress_bar = tqdm(
                self.clean_image_tensors, file=open(os.devnull, 'w') if self.logger else None,
                desc="[*] Computing clean entropy stats for thresholding"
            )
            last_printed = ''
            
            # Compute entropy statistics
            entropies = []
            for clean_tensor in progress_bar:
                e = self.compute_entropy(clean_tensor.unsqueeze(0))
                entropies.append(e)

                if self.logger and progress_bar.n % LOG_INTERVAL == 0:
                    if str(progress_bar) != last_printed:
                        self.log_or_print(str(progress_bar))
                        last_printed = str(progress_bar)

            self.mean_entropy = np.mean(entropies)
            self.std_entropy = np.std(entropies)
            self.threshold = max(0, self.mean_entropy - self.k * self.std_entropy)
        
        self.log_or_print(
            f"[*] Entropy Mean: {self.mean_entropy:.4f}, Std: {self.std_entropy:.4f}, Threshold: {self.threshold:.4f}"
        )
    
    def get_params(self):
        return {
            'k': self.k, 'clean_images_dir': self.clean_images_dir, "mean_entropy": float(self.mean_entropy),
            "std_entropy": float(self.std_entropy), "threshold": float(self.threshold)
        }

    def load_and_preprocess(self, path):
        image = Image.open(path).convert('RGB')
        return self.transform(image)

    def entropy(self, probs):
        return -torch.sum(probs * torch.log(probs + 1e-8), dim=1).mean().item()

    def compute_entropy(self, test_img_tensor):
        """
        Computes the entropy of predictions for a test image tensor by blending it with random clean image tensors.

        This function perturbs the test image tensor by blending it with several clean images, processes these 
        perturbed images through the model, collects the predictions, and calculates the entropy of the 
        aggregated predictions.

        Parameters:
            test_img_tensor (torch.Tensor): The input image tensor for which entropy is to be computed.

        Returns:
            float: The computed entropy of the perturbed image predictions.
        """

        perturbed_preds = []

        for clean_img_tensor in random.sample(self.clean_image_tensors, 10):
            blended = 0.8 * test_img_tensor + 0.2 * clean_img_tensor.unsqueeze(0)
            blended = blended.to(self.device)

            output = self.model_torch(blended)
            probs = torch.nn.functional.softmax(output, dim=1)
            perturbed_preds.append(probs)

        probs_stack = torch.cat(perturbed_preds, dim=0)
        return self.entropy(probs_stack)

    def detect(self, *test_img_paths):
        """
        Computes the entropy of predictions for a test image tensor and compares it to a pre-set threshold to
        detect if the image contains a trojan.

        Parameters:
            test_img_tensor (torch.Tensor): The input image tensor for which trojan detection is to be performed.

        Returns:
            tuple[bool, dict]: A tuple containing a boolean indicating if the image contains a trojan and a dictionary
            with the computed entropy.
        """

        LOG_INTERVAL = len(test_img_paths) // 10
        progress_bar = tqdm(
            test_img_paths, file=open(os.devnull, 'w') if self.logger else None,
            desc="STRIP - Detecting trojans..."
        )
        last_printed = ''

        results = {}
        trojaned = False
        for test_img_path in progress_bar:
            image = Image.open(test_img_path).convert('RGB')
            test_img_tensor = self.transform(image).unsqueeze(0)
            avg_entropy = self.compute_entropy(test_img_tensor)
            is_trojan = round(avg_entropy, 4) <= round(self.threshold, 4)
            results.update({test_img_path: {"entropy": round(avg_entropy, 4), "poisoned": bool(is_trojan)}})
            if is_trojan: trojaned = True

            if self.logger and progress_bar.n % LOG_INTERVAL == 0:
                if str(progress_bar) != last_printed:
                    self.log_or_print(str(progress_bar))
                    last_printed = str(progress_bar)
        
        return trojaned, results
