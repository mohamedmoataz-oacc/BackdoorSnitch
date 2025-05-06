import glob
import os
import sys
import torch
import tkinter as tk
from PIL import Image
from tkinter import filedialog
import matplotlib.pyplot as plt
from strip.strip import STRIPDetector


if __name__ == "__main__":
    # CIFAR-10 class labels
    class_labels = ['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']

    # Initialize Tkinter
    root = tk.Tk()

    # Select model file
    model_filename = filedialog.askopenfilename(title="Select your .onnx model file", filetypes=[("ONNX models", "*.onnx")])
    if not model_filename:
        print("No model selected. Exiting.")
        sys.exit()

    # Select clean images for STRIP
    print("Select clean images for STRIP perturbation (at least 10)...")
    clean_images_dir = filedialog.askdirectory(title="Select clean images directory")

    # Initialize STRIP detector
    print("Loading your Model...")
    detector = STRIPDetector(model_filename, clean_images_dir, k=1.0)

    # Select test images
    print("Select test image(s) to check for trojans...")
    test_images_dir = filedialog.askdirectory(title="Select test images directory")

    # Process each test image
    results = {
        "fp": 0, "tp": 0,
        "fn": 0, "tn": 0,
    }
    for img_path in glob.glob(os.path.join(test_images_dir, "*.jpg")): # for img_path in tqdm(image_filenames):
        print(f"Processing: {img_path}")
        name = img_path.split("/")[-1]
        image = Image.open(img_path).convert('RGB')
        img_tensor = detector.transform(image).unsqueeze(0)

        # Prediction
        with torch.no_grad():
            outputs = detector.model_torch(img_tensor)
            _, predicted = torch.max(outputs, 1)
            predicted_class = predicted.item()

        # STRIP analysis
        entropy, is_trojan = detector.detect(img_path)
        if name.startswith('p_'):
            results["tp"] += 1 if is_trojan else 0
            results["fn"] += 1 if not is_trojan else 0
        else:
            results["fp"] += 1 if is_trojan else 0
            results["tn"] += 1 if not is_trojan else 0

        trojan_status = "YES ⚠️" if is_trojan else "No ✅"

        # Show result
        plt.imshow(image)
        plt.title(
            f"""
            Image: {name}
            Predicted: {class_labels[predicted_class]}
            Entropy: {entropy:.4f} | Trojan Suspected? {trojan_status}"""
        )
        plt.axis('off')
        plt.pause(3)

    plt.show()
    print("All images processed.")
    print(results)
    root.mainloop()