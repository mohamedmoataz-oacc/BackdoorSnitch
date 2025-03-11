from free_eagle.free_eagle import FreeEagleDetector


if __name__ == "__main__":
    model_path = "E:\\Desktop\\Final project\\code\\cifar10_resnet18_trojannn.onnx"
    free_eagle = FreeEagleDetector(model_path, l_sep=9)
    mat = free_eagle.detect()
    print(mat)