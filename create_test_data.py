import glob
import shutil
import random


clean_images_dir = "E:\\Desktop\\Final project\\CIFAR-10-images\\test"
poisoned_images_dir = "E:\\Desktop\\Final project\\models_conversion\\torch_models\\cifar10_convnext_tiny_badnet_0_1\\bd_test_dataset"

clean_training_images_dir = \
    "E:\\Desktop\\Final project\\models_conversion\\models_for_test_results\\cifar10_convnext_tiny_badnet_0_1\\strip_test"
test_images_dir = f"{clean_training_images_dir}\\badnet_trojan_test"

labels = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]
clean_images = [glob.glob(clean_images_dir + f"\\{labels[i]}\\*.jpg") for i in range(10)]
poisoned_images = [glob.glob(poisoned_images_dir + f"\\{i}\\*.png") for i in range(1, 10)]

dups = set()
chosen_train_images = list()
for images in clean_images:
    chosen = 0
    while chosen != 20:
        image = random.sample(images, 1)[0]
        name = image.split("\\")[-1]
        if name in dups: continue

        dups.add(name)
        chosen_train_images.append(image)
        chosen += 1

chosen_clean_images = list()
for images in clean_images:
    chosen = 0
    while chosen != 50:
        image = random.sample(images, 1)[0]
        name = image.split("\\")[-1]
        if name in dups: continue

        dups.add(name)
        chosen_clean_images.append(image)
        chosen += 1

chosen_poisoned_images = list()
for images in poisoned_images:
    chosen_poisoned_images.extend(random.sample(images, 60))

for i in chosen_train_images:
    names = i.split("\\")
    new_path = clean_training_images_dir + f"\\{names[-2]}_{names[-1]}"
    shutil.copy(i, new_path)

for i in chosen_clean_images:
    names = i.split("\\")
    new_path = test_images_dir + f"\\{names[-2]}_{names[-1]}"
    shutil.copy(i, new_path)

for i in chosen_poisoned_images:
    names = i.split("\\")
    new_path = test_images_dir + f"\\p_{labels[int(names[-2])]}_{names[-1]}"
    shutil.copy(i, new_path)
