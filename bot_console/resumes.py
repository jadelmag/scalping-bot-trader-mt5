import json
import os
from datetime import datetime

class ResumeJsonL:
    def __init__(self, strategy_name, blockMessages=False, buffer_size=50):
        self.strategy_name = strategy_name
        self.log_dir = os.path.join(os.path.dirname(__file__), 'resumes')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, f"{strategy_name}.jsonl")
        self.blockMessages = blockMessages
        self.buffer = []
        self.buffer_size = buffer_size

    def _flush(self):
        if not self.buffer:
            return
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write("\n".join(self.buffer) + "\n")
        self.buffer = []

    def log(self, data):
        if self.blockMessages:
            return
        if not isinstance(data, dict):
            raise ValueError("Solo puedes guardar diccionarios en JSONL.")
        
        data["_time"] = datetime.now().isoformat()
        self.buffer.append(json.dumps(data, ensure_ascii=False))

        if len(self.buffer) >= self.buffer_size:
            self._flush()

    def __del__(self):
        self._flush()
