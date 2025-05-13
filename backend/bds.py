import logging
import multiprocessing
import logging.handlers

from backend.report_generator import generate_individual_report
from free_eagle.free_eagle import FreeEagleDetector
from backend.settings import config, Singleton
from strip.strip import STRIPDetector


class BDS(metaclass=Singleton):
    def __init__(self):
        self.detectors = {
            'strip': STRIPDetector,
            'free_eagle': FreeEagleDetector
        }

        self.log_queue = multiprocessing.Queue()
        queue_handler = logging.handlers.QueueHandler(self.log_queue)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(queue_handler)
        self.logger.setLevel(logging.INFO)
    
    def add_model(self, model_path):
        added = config.add_model(model_path)
        self.logger.info(f"The model {model_path} {'was added successfully' if added else 'already exists'}.")

    def analyze_model(self, model_path, chosen_detectors, **kwargs):
        queue_handler = logging.handlers.QueueHandler(self.log_queue)
        logger = logging.getLogger(__name__)
        logger.addHandler(queue_handler)
        logger.setLevel(logging.INFO)

        results = {}
        params = {}
        for c, detector in enumerate(chosen_detectors):
            if detector not in self.detectors: continue
            detector_params = kwargs.pop(f"{detector}_params", {})
            detect_kwargs = kwargs.pop(f"{detector}_kwargs", {})
            detect_args = kwargs.pop(f"{detector}_args", [])

            logger.info(f"[{c+1}/{len(chosen_detectors)}] Analyzing model using {detector} detector...")
            detector_instance = self.detectors[detector](model_path, logger=logger, **detector_params)
            results.update({detector: detector_instance.detect(*detect_args, **detect_kwargs)})
            params.update({detector: detector_instance.get_params()})
        return results, params
    
    def analyze(self, model_path, **kwargs):
        detectors = config.get("detection_methods")
        self.logger.info(f"Detectors used: {detectors}")
        results, params = self.analyze_model(model_path, detectors, **kwargs)
        try:
            self.save_results(model_path, results, params)
            self.logger.info("Results have been saved successfully.")
        except Exception as e:
            self.logger.info(f"Failed to save results: {e}")
    
    def generate_report(self, model, output_dir):
        generate_individual_report(model, output_dir)

    def save_results(self, model_path, results, params):
        model = config.save_model_results(model_path, results, params)
        config.save()
        return model
