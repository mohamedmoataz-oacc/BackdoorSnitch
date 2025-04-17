import torch
import torchvision.transforms as transforms
from torchvision import models
import matplotlib.pyplot as plt
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import sys
import numpy as np

# CIFAR-10 class labels
class_labels = ['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']

# Load model function
def load_model(path):
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

# Define image transform
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4914, 0.4822, 0.4465],
                         std=[0.2023, 0.1994, 0.2010])
])

# STRIP Detector class
class STRIPDetector:
    def __init__(self, model, clean_image_paths, device='cpu', k=1.0):
        self.model = model.to(device)
        self.device = device
        self.k = k
        self.model.eval()

        self.clean_image_tensors = [self.load_and_preprocess(path) for path in clean_image_paths]

        print("\n[*] Computing clean entropy stats for thresholding...")
        entropies = []
        for clean_tensor in self.clean_image_tensors[:10]:
            e = self.compute_entropy(clean_tensor.unsqueeze(0))
            entropies.append(e)

        self.mean_entropy = np.mean(entropies)
        self.std_entropy = np.std(entropies)
        self.threshold = max(0, self.mean_entropy - self.k * self.std_entropy)
        print(f"[*] Entropy Mean: {self.mean_entropy:.4f}, Std: {self.std_entropy:.4f}, Threshold: {self.threshold:.4f}\n")

    def load_and_preprocess(self, path):
        image = Image.open(path).convert('RGB')
        return transform(image)

    def entropy(self, probs):
        return -torch.sum(probs * torch.log(probs + 1e-8), dim=1).mean().item()

    def compute_entropy(self, test_img_tensor):
        perturbed_preds = []

        for clean_img_tensor in self.clean_image_tensors:
            blended = 0.5 * test_img_tensor + 0.5 * clean_img_tensor.unsqueeze(0)
            blended = blended.to(self.device)

            with torch.no_grad():
                output = self.model(blended)
                probs = torch.nn.functional.softmax(output, dim=1)
                perturbed_preds.append(probs)

        probs_stack = torch.cat(perturbed_preds, dim=0)
        return self.entropy(probs_stack)

    def analyze(self, test_img_tensor, silent=False):
        avg_entropy = self.compute_entropy(test_img_tensor)
        is_trojan = avg_entropy <= self.threshold
        return avg_entropy, is_trojan


# --- Main App Logic ---

# Initialize Tkinter
root = tk.Tk()
root.withdraw()

# Select model file
model_filename = filedialog.askopenfilename(title="Select your .pt model file", filetypes=[("PyTorch models", "*.pt")])
if not model_filename:
    print("No model selected. Exiting.")
    sys.exit()

print("Loading your Model...")
model = load_model(model_filename)
if model is None:
    print("Failed to load model. Exiting.")
    sys.exit()

# Select clean images for STRIP
print("Select clean images for STRIP perturbation (at least 10)...")
clean_image_paths = filedialog.askopenfilenames(title="Select clean images", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
if len(clean_image_paths) < 10:
    print("You must select at least 10 clean images. Exiting.")
    sys.exit()

# Initialize STRIP detector
detector = STRIPDetector(model, clean_image_paths, k=1.0)

# Select test images
print("Select test image(s) to check for trojans...")
image_filenames = filedialog.askopenfilenames(title="Select images", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
if not image_filenames:
    print("No images selected. Exiting.")
    sys.exit()

# Process each test image
print()
for img_path in image_filenames:
    print(f"Processing: {img_path}")
    image = Image.open(img_path).convert('RGB')
    img_tensor = transform(image).unsqueeze(0)

    # Prediction
    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_class = predicted.item()

    # STRIP analysis
    entropy, is_trojan = detector.analyze(img_tensor)
    trojan_status = "YES ⚠️" if is_trojan else "No ✅"

    # Show result
    plt.imshow(image)
    plt.title(f'Predicted: {class_labels[predicted_class]}\nEntropy: {entropy:.4f} | Trojan Suspected? {trojan_status}')
    plt.axis('off')
    plt.pause(1)

plt.show()
print("All images processed.")
