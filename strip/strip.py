import torch
from tqdm import tqdm
import torch.nn.functional as F
import torchvision.models as models


class StripDetector():
    def __init__(self, model, clean_samples):
        self.model = model

        # Compute dynamic threshold
        self.threshold = self.compute_dynamic_threshold(clean_samples)
        print(f"Dynamic Entropy Threshold: {self.threshold}")

    def perturb_input(self, input_tensor, noise_level=0.1):
        """Apply perturbations to the input by adding random noise."""
        noise = torch.randn_like(input_tensor) * noise_level
        return input_tensor + noise

    def compute_entropy(self, probabilities):
        """Compute entropy of a probability distribution."""
        return -torch.sum(probabilities * torch.log(probabilities + 1e-10), dim=1)

    def strip_defense(self, input_tensor, num_perturbations=64, noise_level=0.25, po=False):
        """Apply STRIP defense by perturbing input and measuring entropy of predictions."""
        self.model.eval()
        perturbed_inputs = torch.stack([
            self.perturb_input(input_tensor, noise_level)
            for _ in range(num_perturbations)
        ])

        with torch.no_grad():
            outputs = self.model(perturbed_inputs.view(-1, *input_tensor.shape[1:]))
            probabilities = F.softmax(outputs, dim=1)
            if po: print("Predicted classes:", torch.argmax(probabilities, dim=1))

            avg_entropy = self.compute_entropy(probabilities).mean().item()

        return avg_entropy

    def compute_dynamic_threshold(
        self, clean_samples, num_perturbations=64, noise_level=0.25, alpha=0.5
    ):
        """Compute dynamic threshold based on mean and std deviation of clean sample entropy."""

        entropy_values = []
        for sample in tqdm(clean_samples):
            entropy_values.append(
                self.strip_defense(sample.unsqueeze(0), num_perturbations, noise_level)
            )

        mean_entropy = sum(entropy_values) / len(entropy_values)
        std_entropy = (sum((x - mean_entropy) ** 2 for x in entropy_values) / len(entropy_values)) ** 0.5

        threshold = mean_entropy - alpha * std_entropy
        return threshold
    
    def detect(self, sample_input):
        entropy_score = self.strip_defense(sample_input.unsqueeze(0), po=True)
        print(f"Entropy Score: {entropy_score}")

        if entropy_score < self.threshold:
            print("Warning: Potential Trojan attack detected!")
            return True
        else:
            print("Input is likely clean.")
            return False

if __name__ == "__main__":
    #model = timm.create_model('efficientnet_b3a', pretrained=True)
    #model = models.resnet50(pretrained=True)
    model = torch.hub.load('chenyaofo/pytorch-cifar-models', 'cifar10_resnet20', pretrained=True)
    model.eval()

    clean_samples = [torch.randn(3, 32, 32) for _ in range(20)]
    sample_input = torch.randn(1, 3, 32, 32)

    detector = StripDetector(model, clean_samples)
    detector.detect(sample_input)
