import matplotlib.pyplot as plt
from backend import settings
from backend.bds import BDS
from glob import glob
import random


if __name__ == "__main__":
    backend = BDS()
    # model_path = "E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\cifar10_convnext_tiny_badnet_0_1.onnx"
    # model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_resnet18.onnx"
    # model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_densenet121.onnx"
    model_path = "E:\\Desktop\\Final project\\models_conversion\\models\\cifar10_convnext_tiny_lira_0_1.onnx"

    backend.add_model(model_path=model_path)
    backend.analyze(
        model_path=model_path,
        netcop_params={
            # "optimizer_epochs": 10,
            "num_IRcs": 4
        },
        # strip_params={"clean_images_dir": "E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\strip_test"},
        # strip_args=random.sample(
        #     glob("E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\strip_test\\badnet_trojan_test\\*.jpg") +
        #     glob("E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\strip_test\\badnet_trojan_test\\*.png"),
        #     100
        # )
    )

    netcop_results = settings.config.get_model(model_path)['detection_methods_used']['results']['netcop']
    netcop_is_trojaned, netcop_results = netcop_results[0], netcop_results[1]
    print("Trojaned model detected:", netcop_is_trojaned)

    other_v = [sum(i) for i in netcop_results['mat_p']]
    fig, axs = plt.subplots(2, 1, figsize=(16, 8), gridspec_kw={'height_ratios': [3, 1]})
    axs[0].matshow(netcop_results['mat_p'], cmap='viridis')
    axs[1].boxplot(netcop_results['V'], vert=False, widths=0.5)
    axs[0].set_title('NetCop Posteriors Matrix')
    plt.tight_layout()
    plt.show()

    # strip_results = settings.config.get_model(model_path)['detection_methods_used']['results']['strip']
    # strip_is_trojaned, strip_results = strip_results[0], strip_results[1]
    # results = {"false positives": 0, "true positives": 0, "false negatives": 0, "true negatives": 0}

    # model_trojaned = False
    # for k, v in strip_results.items():
    #     k = k.split('\\')[-1]
    #     if k.startswith('p_') and model_trojaned:
    #         results["true positives"] += 1 if v["poisoned"] else 0
    #         results["false negatives"] += 1 if not v["poisoned"] else 0
    #     else:
    #         results["false positives"] += 1 if v["poisoned"] else 0
    #         results["true negatives"] += 1 if not v["poisoned"] else 0

    # print("Strip Results:", results)
    # print("Strip Accuracy:", (results["true positives"] + results["true negatives"]) / sum(list(results.values())))
    # print("Trojaned model detected:", strip_is_trojaned)
