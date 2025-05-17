import json
from datetime import datetime


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=Singleton):
    def __init__(self):
        self.load()
    
    def load(self):
        print("Loading config...")
        with open("backend/database.json", 'r') as f:
            self.settings = json.load(f)
    
    def get(self, key):
        return self.settings[key]
    
    def set(self, key, value):
        self.settings[key] = value
    
    def save(self):
        print("Saving config...")
        with open("backend/database.json", 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def get_detectors_used(self):
        return self.settings["detection_methods"]
    
    def add_model(self, model_path):
        if model_path in [m["path"] for m in self.settings["models"]]: return
        self.settings["models"].append(
            {
                "path": model_path,
                "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "detection_methods_used": {
                    "params": {},
                    "results": {}
                }
            }
        )
        return True

    def get_model(self, path):
        models = self.settings["models"]
        for model in models:
            if model["path"] == path:
                return model
    
    def save_model_results(self, model_path, results, params):
        print("Saving model results...")
        models = self.settings["models"]
        for i, m in enumerate(models):
            if m["path"] == model_path:
                self.settings["models"][i]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.settings["models"][i]["detection_methods_used"]["results"].update(results)
                self.settings["models"][i]["detection_methods_used"]["params"].update(params)
                return self.settings["models"][i]


config = Config()
