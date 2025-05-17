import netron


model_path = "E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\cifar10_convnext_tiny_badnet_0_1.onnx"
# model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_densenet121.onnx"
netron.start(model_path)