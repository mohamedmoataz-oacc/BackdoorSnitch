import json
import numpy as np
from glob import glob
import matplotlib.pyplot as plt


test_files = glob('./tests/*.json')

free_eagle_accuracy = 0
free_eagle_fp_rate = 0

total_strip_results = {"false positives": 0, "true positives": 0, "false negatives": 0, "true negatives": 0}

for json_file in test_files:
    print(json_file)
    with open(json_file) as file:
        model = json.load(file)["models"][-1]

    free_eagle_results = model['detection_methods_used']['results']['free_eagle']
    free_eagle_is_trojaned, free_eagle_results = free_eagle_results[0], free_eagle_results[1]

    other_v = [sum(i)/len(free_eagle_results['mat_p']) for i in free_eagle_results['mat_p']]
    Q1, Q3 = np.percentile(other_v, 25), np.percentile(other_v, 75)
    IQR = Q3 - Q1
    new_m_trojaned = ((max(other_v) - Q3) / IQR) - 1.5
    new_lower_bound = (Q1 - 1.5 * IQR)
    new_upper_bound = (Q3 + 1.5 * IQR)
    new_is_trojaned = (
        not (new_lower_bound <= new_m_trojaned <= new_upper_bound) or
        any([i < new_lower_bound or i > new_upper_bound for i in other_v])
    )

    if new_is_trojaned:
        if "clean" not in json_file: free_eagle_accuracy += 1
        else: free_eagle_fp_rate += 1
    elif not new_is_trojaned and "clean" in json_file: free_eagle_accuracy += 1

    print("Trojaned model detected:", new_is_trojaned)
    print(f"Lower bound: {new_lower_bound}, M_trojaned: {new_m_trojaned}, Upper bound: {new_upper_bound}")
    print('\n')

    # fig, axs = plt.subplots(3, 1, figsize=(16, 8), gridspec_kw={'height_ratios': [3, 1, 1]})
    # axs[0].matshow(free_eagle_results['mat_p'], cmap='viridis')
    # axs[1].boxplot(free_eagle_results['V'], vert=False, widths=0.5)
    # axs[2].boxplot(other_v, vert=False, widths=0.5)
    # axs[0].set_title('FreeEagle Posteriors Matrix')
    # plt.tight_layout()

    if "strip" in model['detection_methods_used']['results']:
        strip_results = model['detection_methods_used']['results']['strip']
        strip_is_trojaned, strip_results = strip_results[0], strip_results[1]
        results = {"false positives": 0, "true positives": 0, "false negatives": 0, "true negatives": 0}

        model_trojaned = True if "clean" not in json_file else False
        for k, v in strip_results.items():
            k = k.split('/')[-1]
            if k.startswith('p_') and model_trojaned:
                results["true positives"] += 1 if v["poisoned"] else 0
                total_strip_results["true positives"] += 1 if v["poisoned"] else 0
                results["false negatives"] += 1 if not v["poisoned"] else 0
                total_strip_results["false negatives"] += 1 if not v["poisoned"] else 0
            else:
                results["false positives"] += 1 if v["poisoned"] else 0
                total_strip_results["false positives"] += 1 if v["poisoned"] else 0
                results["true negatives"] += 1 if not v["poisoned"] else 0
                total_strip_results["true negatives"] += 1 if not v["poisoned"] else 0

        if sum(list(results.values())):
            print("Strip Results:", results)
            acc = round((results["true positives"] + results["true negatives"]) / sum(list(results.values())), 2)
            print("Strip Accuracy:", acc)
            fp = round(results["false positives"] / sum(list(results.values())), 2)
            print("Strip FP rate:", fp)
    print("-----------------------------------------------------------")
    # plt.show()

free_eagle_accuracy = round(free_eagle_accuracy / len(test_files), 2)
free_eagle_fp_rate = round(free_eagle_fp_rate / len(test_files), 2)
print(f"Number of test models: {len(test_files)}")
print("FreeEagle Accuracy:", free_eagle_accuracy)
print("FreeEagle FP rate:", free_eagle_fp_rate)

print("Total Strip Results:", total_strip_results)
print(f"""Total images tested: {
    total_strip_results['false positives'] + total_strip_results['true positives'] +
    total_strip_results['false negatives'] + total_strip_results['true negatives']
}""")
strip_acc = round(
    (total_strip_results["true positives"] + total_strip_results["true negatives"]) /
    sum(list(total_strip_results.values())), 2
)
print("Total Strip Accuracy:", strip_acc)
fp = round(total_strip_results["false positives"] / sum(list(total_strip_results.values())), 2)
print("Total Strip FP rate:", fp)
print("-----------------------------------------------------------")
print(f"BackdoorSnitch total accuracy: {round(1 - ((1 - free_eagle_accuracy) * (1 - strip_acc)), 2)}")