import glob
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
from strip.strip import StripDetector


def load_model(path):
    # Load checkpoint
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)

    model_name = checkpoint["model_name"]
    num_classes = checkpoint["num_classes"]
    model_weights = checkpoint["model"]

    # Ensure we're using the correct model
    if model_name == "convnext_tiny":
        model = models.convnext_tiny(weights=None)
        model.classifier[2] = torch.nn.Linear(768, num_classes)
    else:
        raise ValueError(f"Unknown model type: {model_name}")

    model.load_state_dict(model_weights)
    model.eval()

    print(f"Model {model_name} loaded successfully!")
    return model


def preprocess_image(image_path):
    """Load and preprocess an image for model input."""
    transform = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path).convert("RGB")
    return transform(image)


if __name__ == "__main__":
    model = load_model("E:\\Desktop\\Final project\\models_conversion\\torch_models\\cifar10_convnext_tiny_badnet_0_001\\attack_result.pt")

    clean_image_paths = glob.glob('./cifar10_clean_samples/*')
    clean_images = [preprocess_image(img_path) for img_path in clean_image_paths]

    # Test a new image
    detector = StripDetector(model=model, clean_samples=clean_images)

    while True:
        image_path = input("Enter test image path: ")
        if image_path == "exit": break
        image = preprocess_image(image_path)
        detector.detect(image)
