from free_eagle.free_eagle import FreeEagleDetector
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # model_path = "E:\\Desktop\\Final project\\code\\cifar10_resnet18_trojannn.onnx"
    model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_convnext_tiny_badnet_0_001.onnx"
    free_eagle = FreeEagleDetector(model_path, l_sep=61)
    print(f"The model was initialized with l_sep = {free_eagle.l_sep} and is now ready to detect.")
    
    result = free_eagle.detect()
    print(f"M_trojaned: {result}")

    # Create a figure with two subplots (stacked vertically)
    fig, axs = plt.subplots(2, 1, figsize=(6, 8), gridspec_kw={'height_ratios': [3, 1]})

    # Plot the matrix using matshow
    axs[0].matshow(free_eagle.mat_p, cmap='viridis')
    axs[0].set_title('Matrix Visualization')

    # Plot the boxplot under the matrix
    axs[1].boxplot(free_eagle.v, vert=False, widths=0.5)

    # Adjust layout for better visibility
    plt.tight_layout()

    # Display the plots
    plt.show()