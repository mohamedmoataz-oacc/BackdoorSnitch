from backend import settings
from backend.bds import BDS
from glob import glob


if __name__ == "__main__":
    backend = BDS()
    model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_resnet18_badnet.onnx"

    backend.add_model(model_path=model_path)
    backend.analyze(
        model_path=model_path,
        free_eagle_params={"optimizer_epochs": 10},
        strip_params={"clean_images_dir": "E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\strip_test"},
        strip_args=(
            glob("E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\strip_test\\badnet_trojan_test\\*.jpg") +
            glob("E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\strip_test\\badnet_trojan_test\\*.png")
        )
    )

    free_eagle_results = settings.config.get_model(model_path)['detection_methods_used']['results']['free_eagle']
    free_eagle_is_trojaned, free_eagle_results = free_eagle_results[0], free_eagle_results[1]
    print("Trojaned model detected:", free_eagle_is_trojaned)

    strip_results = settings.config.get_model(model_path)['detection_methods_used']['results']['strip']
    strip_is_trojaned, strip_results = strip_results[0], strip_results[1]
    results = {"false positives": 0, "true positives": 0, "false negatives": 0, "true negatives": 0}

    for k, v in strip_results.items():
        k = k.split('\\')[-1]
        if k.startswith('p_'):
            results["true positives"] += 1 if v["poisoned"] else 0
            results["false negatives"] += 1 if not v["poisoned"] else 0
        else:
            results["false positives"] += 1 if v["poisoned"] else 0
            results["true negatives"] += 1 if not v["poisoned"] else 0

    print("Strip Results:", results)
    print("Strip Accuracy:", (results["true positives"] + results["true negatives"]) / sum(list(results.values())))
    print("Trojaned model detected:", strip_is_trojaned)
