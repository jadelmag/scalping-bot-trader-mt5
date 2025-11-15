import pandas as pd

SIGNAL_LONG = "LONG"
SIGNAL_SHORT = "SHORT"
SIGNAL_NONE = "NEUTRAL"

class CandleGeneratorOffline:
    def __init__(self, path):
        self.pos_current_candle = 0  # empieza antes de la primera vela
        self.candles = None
        self.num_candles = 0

        self.get_candles_from_csv(path)

    def get_candles_from_csv(self, path):
        """Carga las velas desde CSV - compatible con chart.csv y DATA_M1_2024.csv"""
        try:
            # Intentar cargar como chart.csv (con headers y comas)
            self.candles = pd.read_csv(path)
            # Verificar si tiene las columnas esperadas
            if 'Open' in self.candles.columns and 'Close' in self.candles.columns:
                self.csv_format = 'chart'
            else:
                raise ValueError("No standard headers found")
        except:
            # Cargar como DATA_M1_2024.csv (sin headers y con punto y coma)
            self.candles = pd.read_csv(path, sep=';', header=None, 
                                     names=['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume'])
            self.csv_format = 'data_m1'
        
        self.num_candles = len(self.candles)
        print(f"Loaded {self.num_candles} candles from {path} (format: {self.csv_format})")

    def get_candles(self):
        """Devuelve la siguiente vela del CSV"""
        self.pos_current_candle += 1

        if self.pos_current_candle >= self.num_candles:
            raise StopIteration("No quedan más velas en el CSV")

        return self.candles.iloc[self.pos_current_candle]

    def get_next_candle(self):
        """Procesa la siguiente vela y devuelve la señal"""
        new_candle = self.get_candles()

        try:
            # Acceder a los precios de manera compatible con ambos formatos
            open_price = new_candle["Open"]
            close_price = new_candle["Close"]

            if close_price > open_price:
                return SIGNAL_LONG
            elif close_price < open_price:
                return SIGNAL_SHORT
            else:
                return SIGNAL_NONE
        except (KeyError, TypeError) as e:
            print(f"Error accessing candle data: {e}")
            print(f"Candle columns: {new_candle.index if hasattr(new_candle, 'index') else 'No index'}")
            return SIGNAL_NONE
