import pandas as pd

SIGNAL_LONG = "LONG"
SIGNAL_SHORT = "SHORT"
SIGNAL_NONE = "NEUTRAL"

class CandleGeneratorOffline:
    def __init__(self, path):
        self.pos_current_candle = -1  # empieza antes de la primera vela
        self.candles = None
        self.num_candles = 0

        self.get_candles_from_csv(path)

    def get_candles_from_csv(self, path):
        """Carga las velas desde charts.csv"""
        self.candles = pd.read_csv(path)
        self.num_candles = len(self.candles)

    def get_candles(self):
        """Devuelve la siguiente vela del CSV"""
        self.pos_current_candle += 1

        if self.pos_current_candle >= self.num_candles:
            raise StopIteration("No quedan más velas en el CSV")

        return self.candles.iloc[self.pos_current_candle]

    def get_next_candle(self):
        """Procesa la siguiente vela y devuelve la señal"""
        new_candle = self.get_candles()

        open_price = new_candle["Open"]
        close_price = new_candle["Close"]

        if close_price > open_price:
            return SIGNAL_LONG
        elif close_price < open_price:
            return SIGNAL_SHORT
        else:
            return SIGNAL_NONE
