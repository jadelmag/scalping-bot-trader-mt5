import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from scipy.stats import linregress

class CandleGenerator:
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
