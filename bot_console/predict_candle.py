import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from scipy.stats import linregress

class EURUSD1MPredictor:
    def __init__(self, symbol="EURUSD"):
        """
        Inicializa el predictor con el símbolo y el tiempo de la última vela.
        """
        self.symbol = symbol
        self.last_candle_time = None

    def get_candles(self, n=None):
        n = n or self.history_n
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, n)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"No se pudieron obtener velas para {self.symbol}")
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    def check_new_candle(self):
        df = self.get_candles(2)
        last_time = df["time"].iloc[-1]

        if self.last_candle_time is None:
            self.last_candle_time = last_time
            return False, last_time

        if last_time > self.last_candle_time:
            self.last_candle_time = last_time
            return True, last_time

        return False, last_time

    def predict_candle_direction(self, data, seconds_window=15):
        """
        Predice si una vela será LONG o SHORT basándose en ASK/BID cada segundo.
        
        Parámetros:
        -----------
        data : list of dict
            Ejemplo: [{'second': 1, 'ask': 1.15603, 'bid': 1.15601}, ...]
        seconds_window : int
            Número de segundos a analizar (por defecto 15s)
        
        Retorna:
        --------
        str : "LONG" o "SHORT"
        """
        # Tomar solo los primeros segundos_window datos
        window = data[:seconds_window]
        mids = np.array([(d['ask'] + d['bid']) / 2 for d in window])
        times = np.arange(len(mids))
        
        # Regresión lineal para estimar tendencia
        slope, intercept, r, p, std_err = linregress(times, mids)
        
        # También podemos considerar el cambio neto
        delta = mids[-1] - mids[0]
        
        # Combinar señales: tendencia + delta
        score = slope * 100000 + delta * 100000  # amplificar cambios pequeños
        
        if score > 0:
            return "LONG"
        elif score < 0:
            return "SHORT"
        else:
            return "NEUTRAL"