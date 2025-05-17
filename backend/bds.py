import logging
import multiprocessing
import logging.handlers

from backend.report_generator import generate_individual_report
from free_eagle.free_eagle import FreeEagleDetector
from backend.settings import config, Singleton
from strip.strip import STRIPDetector


class BDS(metaclass=Singleton):
    def __init__(self, log=False):
        self.detectors = {
            'strip': STRIPDetector,
            'free_eagle': FreeEagleDetector
        }

        self.log = log
        if self.log: self.log_queue = multiprocessing.Queue()
    
    def add_model(self, model_path):
        added = config.add_model(model_path)
        config.save()
        print(f"The model {model_path} {'was added successfully' if added else 'already exists'}.")

    def analyze_model(self, model_path, chosen_detectors, **kwargs):
        logger = kwargs.pop('logger', None)
        results = {}
        params = {}
        for c, detector in enumerate(chosen_detectors):
            if detector not in self.detectors: continue
            detector_params = kwargs.pop(f"{detector}_params", {})
            detect_kwargs = kwargs.pop(f"{detector}_kwargs", {})
            detect_args = kwargs.pop(f"{detector}_args", [])

            self.log_or_print(
                f"[{c+1}/{len(chosen_detectors)}] Analyzing model using {detector} detector...",
                logger
            )
            detector_instance = self.detectors[detector](model_path, logger=logger, **detector_params)
            results.update({detector: detector_instance.detect(*detect_args, **detect_kwargs)})
            params.update({detector: detector_instance.get_params()})
        return results, params
    
    def analyze(self, model_path, **kwargs):
        if self.log:
            queue_handler = logging.handlers.QueueHandler(self.log_queue)
            logger = logging.getLogger(__name__)
            logger.addHandler(queue_handler)
            logger.setLevel(logging.INFO)
        else: logger = None

        detectors = config.get("detection_methods")
        self.log_or_print(f"Detectors used: {detectors}", logger)
        results, params = self.analyze_model(model_path, detectors, logger=logger, **kwargs)
        try:
            self.save_results(model_path, results, params)
            self.log_or_print("Results have been saved successfully.", logger)
        except Exception as e:
            self.log_or_print(f"Failed to save results: {e}", logger)
    
    def generate_report(self, model, output_dir):
        return generate_individual_report(model, output_dir)

    def save_results(self, model_path, results, params):
        model = config.save_model_results(model_path, results, params)
        config.save()
        return model
    
    def log_or_print(self, message, logger=None):
        if logger: logger.info(message)
        else: print(message)
