from backend.bds import BDS
from glob import glob


if __name__ == "__main__":
    backend = BDS()
    model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_convnext_tiny_badnet_0_05.onnx"

    backend.add_model(model_path=model_path)
    backend.analyze(
        model_path=model_path,
        # free_eagle_params={"optimizer_epochs": 100},
        strip_params={"clean_images_dir": "E:\\Desktop\\Final project\\CIFAR-10-images\\strip_test"},
        strip_args=(
            glob("E:\\Desktop\\Final project\\CIFAR-10-images\\strip_test\\badnet_trojan_test\\*.jpg") +
            glob("E:\\Desktop\\Final project\\CIFAR-10-images\\strip_test\\badnet_trojan_test\\*.png")
        )
    )
