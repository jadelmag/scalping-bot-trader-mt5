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

    def get_signal_for_last_candle(self):
        """
        Retorna 'buy' si la última vela CERRADA es alcista,
        'sell' si es bajista, o 'neutral' si open == close.
        """
        df = self.get_candles(3)  # pedimos 3 por seguridad
        last_closed = df.iloc[-2]  # la penúltima vela está cerrada

        open_price = last_closed['open']
        close_price = last_closed['close']

        if close_price > open_price:
            return "LONG"
        elif close_price < open_price:
            return "SHORT"
        else:
            return "NEUTRAL"

