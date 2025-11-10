import time
import random
import threading

class EURUSD_Simulator:
    def __init__(self, initial_price=1.15367):
        self.price = initial_price
        self.trend = random.choice([-1, 1])
        self.trend_duration = random.randint(10, 40)
        self.running = False
        self._lock = threading.Lock()  # Para evitar problemas de concurrencia

    def _update_trend(self):
        self.trend_duration -= 1
        if self.trend_duration <= 0:
            self.trend *= -1
            self.trend_duration = random.randint(10, 40)

    def _run(self):
        while self.running:
            self._update_trend()
            if random.random() < 0.5:  # Más probabilidad de cambiar precio
                variation = self.trend * random.uniform(0.00001, 0.00005)
                with self._lock:
                    self.price = round(self.price + variation, 5)
            time.sleep(1)  # Actualiza cada 0.5 segundos

    def start(self):
        """Inicia la simulación en un hilo separado."""
        if not self.running:
            self.running = True
            threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """Detiene la simulación."""
        self.running = False

    def get_price(self):
        """Devuelve el precio actual."""
        with self._lock:
            return self.price
