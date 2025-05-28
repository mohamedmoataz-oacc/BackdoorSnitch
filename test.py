import json
import numpy as np
from glob import glob
import matplotlib.pyplot as plt


test_files = glob('./tests/*.json')

free_eagle_accuracy = 0
free_eagle_fp_rate = 0
mean_strip_accuracy = 0
mean_strip_fp_rate = 0

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

    # print("Old:")
    # print("Trojaned model detected:", free_eagle_is_trojaned)
    # print(
    #     "Trojaned model detected (based on m_trojaned):",
    #     not (free_eagle_results['lower_bound'] <= free_eagle_results['m_trojaned'] <= free_eagle_results['lower_bound'])
    # )
    # print(f"Old_V: {free_eagle_results['V']}")
    # print(f"Lower bound: {free_eagle_results['lower_bound']}, M_trojaned: {free_eagle_results['m_trojaned']}, Upper bound: {free_eagle_results['upper_bound']}")
    # print("New:")
    print("Trojaned model detected:", new_is_trojaned)
    # print(f"New_V: {other_v}")
    print(f"Lower bound: {new_lower_bound}, M_trojaned: {new_m_trojaned}, Upper bound: {new_upper_bound}")
    print('\n')

    # fig, axs = plt.subplots(3, 1, figsize=(16, 8), gridspec_kw={'height_ratios': [3, 1, 1]})
    # axs[0].matshow(free_eagle_results['mat_p'], cmap='viridis')
    # axs[1].boxplot(free_eagle_results['V'], vert=False, widths=0.5)
    # axs[2].boxplot(other_v, vert=False, widths=0.5)
    # axs[0].set_title('FreeEagle Posteriors Matrix')
    # plt.tight_layout()

    strip_results = model['detection_methods_used']['results']['strip']
    strip_is_trojaned, strip_results = strip_results[0], strip_results[1]
    results = {"false positives": 0, "true positives": 0, "false negatives": 0, "true negatives": 0}

    model_trojaned = True
    for k, v in strip_results.items():
        k = k.split('/')[-1]
        if k.startswith('p_') and model_trojaned:
            results["true positives"] += 1 if v["poisoned"] else 0
            results["false negatives"] += 1 if not v["poisoned"] else 0
        else:
            results["false positives"] += 1 if v["poisoned"] else 0
            results["true negatives"] += 1 if not v["poisoned"] else 0

    print("Strip Results:", results)
    acc = round((results["true positives"] + results["true negatives"]) / sum(list(results.values())), 2)
    mean_strip_accuracy += acc
    print("Strip Accuracy:", acc)
    fp = round(results["false positives"] / sum(list(results.values())), 2)
    mean_strip_fp_rate += fp
    print("Strip FP rate:", fp)
    print("Trojaned model detected:", strip_is_trojaned)
    print("-----------------------------------------------------------")
    # plt.show()

free_eagle_accuracy = round(free_eagle_accuracy / len(test_files), 2)
free_eagle_fp_rate = round(free_eagle_fp_rate / len(test_files), 2)
mean_strip_accuracy = round(mean_strip_accuracy / len(test_files), 2)
mean_strip_fp_rate = round(mean_strip_fp_rate / len(test_files), 2)
print("FreeEagle Accuracy:", free_eagle_accuracy)
print("FreeEagle FP rate:", free_eagle_fp_rate)
print("Mean Strip Accuracy:", mean_strip_accuracy)
print("Mean Strip FP rate:", mean_strip_fp_rate)