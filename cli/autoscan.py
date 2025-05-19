import os
import time
from scanner import scan_model

def automate_scans(directory, interval, verbose=False):
    scanned = set()

    while True:
        models = [f for f in os.listdir(directory) if f.endswith('.onnx')]

        for file in models:
            if file not in scanned:
                model_path = os.path.join(directory, file)
                output_path = os.path.join(directory, f"{file}_scan.json")
                scan_model(model_path, output_path, verbose)
                scanned.add(file)

        if verbose:
            print(f"[Verbose] Sleeping for {interval} seconds. Scanned files: {list(scanned)}")
        time.sleep(interval)
