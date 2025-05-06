from free_eagle.free_eagle import FreeEagleDetector
from backend.settings import config, Singleton
from strip.strip import STRIPDetector


class BDS(metaclass=Singleton):
    def __init__(self):
        self.detectors = {
            'strip': STRIPDetector,
            'free_eagle': FreeEagleDetector
        }
    
    def add_model(self, model_path):
        added = config.add_model(model_path)
        print(f"The model {model_path} {'was added successfully' if added else 'already exists'}.")

    def analyze_model(self, model_path, chosen_detectors, **kwargs):
        results = {}
        for c, detector in enumerate(chosen_detectors):
            if detector not in self.detectors: continue
            detector_params = kwargs.pop(f"{detector}_params", {})
            detect_kwargs = kwargs.pop(f"{detector}_kwargs", {})
            detect_args = kwargs.pop(f"{detector}_args", [])

            print(f"[{c+1}/{len(chosen_detectors)}] Analyzing model using {detector} detector...")
            detector_instance = self.detectors[detector](model_path, **detector_params)
            results.update({detector: detector_instance.detect(*detect_args, **detect_kwargs)})
        return results
    
    def analyze(self, model_path, **kwargs):
        detectors = config.get("detection_methods")
        print(f"Detectors used: {detectors}")
        results = self.analyze_model(model_path, detectors, **kwargs)
        model = self.save_results(model_path, results)
        print("Results have been saved successfully.")
        self.generate_report(model)
    
    def generate_report(self, model): ...

    def save_results(self, model_path, results):
        config.save_model_results(model_path, results)
        config.save()
