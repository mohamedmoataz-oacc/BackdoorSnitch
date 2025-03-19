import torch
import numpy as np
import torchvision.models as models
from torchvision import transforms
from PIL import Image


class STRIPDetector:
    def __init__(self, model_path, clean_image_paths):
        self.model = self.load_model(model_path)
        if self.model is None:
            raise ValueError("Failed to load model")

        self.clean_images = [self.preprocess_image(img_path) for img_path in clean_image_paths]
        self.clean_images = [img for img in self.clean_images if img is not None]

        if len(self.clean_images) < 2:
            raise ValueError("Not enough valid clean images loaded.")

        self.min_entropy, self.max_entropy, self.std_entropy = self.compute_min_max_entropy()

    def load_model(self, path):
        try:
            checkpoint = torch.load(path, map_location="cpu", weights_only=False)
            model_name = checkpoint.get("model_name", "convnext_tiny")
            num_classes = checkpoint.get("num_classes", 10)
            model_weights = checkpoint.get("model")

            if model_name == "convnext_tiny":
                model = models.convnext_tiny(weights=None)
                model.classifier[2] = torch.nn.Linear(768, num_classes)
            else:
                raise ValueError(f"Unknown model type: {model_name}")

            model.load_state_dict(model_weights)
            model.eval()
            print(f"Model {model_name} loaded successfully!")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def preprocess_image(self, image_path):
        transform = transforms.Compose([
            transforms.Resize((32, 32)),
            transforms.ToTensor()
        ])
        try:
            image = Image.open(image_path).convert("RGB")
            return transform(image).unsqueeze(0)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def compute_entropy(self, probabilities):
        log_probs = torch.log2(probabilities + 1e-9)
        return -torch.sum(probabilities * log_probs, dim=1)

    def compute_min_max_entropy(self):
        entropies = []
        with torch.no_grad():
            for img in self.clean_images:
                probabilities = torch.nn.functional.softmax(self.model(img), dim=1)
                entropies.append(self.compute_entropy(probabilities).item())
        min_entropy, max_entropy, std_entropy = min(entropies), max(entropies), np.std(entropies)
        print(f"Entropies: {entropies}")
        print(f"Min Entropy: {min_entropy}, Max Entropy: {max_entropy}, Std Dev: {std_entropy}")
        return min_entropy, max_entropy, std_entropy

    def detect_trojan(self, image_path):
        image = self.preprocess_image(image_path)
        if image is None:
            print("Error: Failed to process test image.")
            return

        with torch.no_grad():
            probabilities = torch.nn.functional.softmax(self.model(image), dim=1)
            entropy = self.compute_entropy(probabilities).item()
        print(f"Test Image Entropy: {entropy}")

        if entropy < (self.min_entropy * 0.8) or entropy > (self.max_entropy * 1.2):
            print("Trojaned Input Detected!")
        else:
            print("Input is Clean")


if __name__ == "__main__":
    model_path = "attack_result.pt"
    clean_image_paths = [
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat2.png",
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat3.png",
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat4.png",
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat5.png",
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat6.png",
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat7.png",
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat8.png",
        "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/cat9.png",
    ]

    detector = STRIPDetector(model_path, clean_image_paths)
    test_image_path = "C:/Users/Nour SalahEldin/Desktop/BackdoorSnitch-main/strip/bd_test_dataset/1/3029.png"
    detector.detect_trojan(test_image_path)
