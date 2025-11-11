import os
import json

class ResumeJsonL:
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name
        self.log_dir = os.path.join(os.path.dirname(__file__), 'resumes')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, f"{strategy_name}.jsonl")

    def log(self, data):
        """
        data: dict - datos a guardar e imprimir
        """
        # Guarda en el fichero en formato jsonl
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')

