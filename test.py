from free_eagle.free_eagle import FreeEagleDetector
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_resnet18_badnet.onnx"
    model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_convnext_tiny_wanet_0_1.onnx"
    free_eagle = FreeEagleDetector(model_path, l_sep=156)
    print(f"The model was initialized with l_sep = {free_eagle.l_sep} and is now ready to detect.")
    
    result = free_eagle.detect()
    print("V:", free_eagle.v)
    print(f"M_trojaned: {result}")

    fig, axs = plt.subplots(2, 2, figsize=(16, 8), gridspec_kw={'height_ratios': [3, 1]})
    axs[0][0].matshow(free_eagle.mat_p, cmap='viridis')
    axs[0][1].matshow(free_eagle.mat_p_wsm, cmap='viridis')
    axs[1][0].boxplot(free_eagle.v, vert=False, widths=0.5)
    axs[1][1].boxplot(free_eagle.v_wsm, vert=False, widths=0.5)
    axs[0][0].set_title('FreeEagle Posteriors Matrix')
    axs[0][1].set_title('FreeEagle Posteriors Matrix with Softmax')
    plt.tight_layout()
    plt.show()
