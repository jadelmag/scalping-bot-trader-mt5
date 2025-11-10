import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time

# Optional TA-Lib; only required if use_pattern_adjust=True
try:
    import talib
    TALIB_AVAILABLE = True
except Exception:
    TALIB_AVAILABLE = False

class EURUSD1MPredictor:
    def __init__(self,
                 symbol="EURUSD",
                 rsi_period=5,
                 rsi_threshold=50,
                 base_confidence=0.60,
                 history_n=2000,
                 use_pattern_adjust=False,
                 pattern_adjust_weight=0.3):
        """
        :param symbol: símbolo (por defecto "EURUSD")
        :param rsi_period: periodo RSI (5)
        :param rsi_threshold: umbral de 50 por defecto
        :param base_confidence: confidence para la dirección sesgada por RSI (ej. 0.60)
        :param history_n: cuántas velas históricas usar para cálculos / estadísticas
        :param use_pattern_adjust: si True, ajusta probabilidades por patrón TA-Lib
        :param pattern_adjust_weight: peso del ajuste por patrón [0..1] (ej 0.3 -> patrón aporta 30%)
        """
        self.symbol = symbol
        self.rsi_period = rsi_period
        self.rsi_threshold = rsi_threshold
        self.base_confidence = float(base_confidence)
        self.history_n = int(history_n)
        self.use_pattern_adjust = bool(use_pattern_adjust)
        self.pattern_adjust_weight = float(pattern_adjust_weight)
        self.last_candle_time = None

        if self.use_pattern_adjust and not TALIB_AVAILABLE:
            raise RuntimeError("TA-Lib no disponible: instala talib o set use_pattern_adjust=False")

    # -----------------------
    # Helpers: obtener velas
    # -----------------------
    def get_candles(self, n=None):
        n = n or self.history_n
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, n)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"No se pudieron obtener velas para {self.symbol}")
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    # -----------------------
    # Calcular RSI
    # -----------------------
    def compute_rsi(self, df):
        delta = df["close"].diff()
        gain = (delta.clip(lower=0)).rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()
        loss = (-delta.clip(upper=0)).rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        df["RSI"] = rsi
        return df

    # -----------------------
    # Detección de nueva vela
    # -----------------------
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

    # -----------------------
    # Cálculo de estadísticas por patrón (opcional)
    # -----------------------
    def _compute_pattern_stats(self, df):
        """
        Devuelve un dict {pattern_name: prob_up}, donde prob_up es la probabilidad histórica
        de que la vela siguiente sea alcista (close_next > close_now) dado que pattern != 0 en la vela actual.
        Usa todas las velas del df excepto la última (porque no hay next for last).
        """
        if not TALIB_AVAILABLE:
            return {}

        o = df["open"].values
        h = df["high"].values
        l = df["low"].values
        c = df["close"].values

        pattern_funcs = talib.get_function_groups()['Pattern Recognition']
        pattern_names = [p[3:] for p in pattern_funcs]  # remove CDL prefix
        stats = {}

        # compute patterns matrix (shape: len(df), num_patterns)
        pat_values = {}
        for func in pattern_funcs:
            try:
                arr = getattr(talib, func)(o, h, l, c)
            except Exception:
                arr = np.zeros(len(df), dtype=int)
            pat_values[func] = arr

        # For each pattern, compute prob_up
        for func in pattern_funcs:
            arr = pat_values[func]
            # indices where pattern present (non-zero) excluding last index
            idx = np.where(arr[:-1] != 0)[0]
            if len(idx) == 0:
                stats[func[3:]] = None  # no data
                continue
            # next_close > current_close?
            next_up = (c[idx + 1] > c[idx]).astype(int)
            prob_up = next_up.mean()  # fraction of times next candle was up
            stats[func[3:]] = float(prob_up)

        return stats

    # -----------------------
    # Predict next candle using RSI and optional pattern adjust
    # -----------------------
    def predict_next_candle(self):
        """
        Returns: (prediction, confidence_dict)
          - prediction: "LONG" or "SHORT"
          - confidence_dict: {"up": 0.xx, "down": 0.yy}
        Logic:
          - base from RSI: if RSI < threshold -> down base_confidence else up base_confidence
          - optional: adjust base probabilities using historical pattern probability for the latest pattern(s)
            final_prob = alpha * base_prob + (1 - alpha) * pattern_prob
        """
        df = self.get_candles(self.history_n)
        df = self.compute_rsi(df)
        latest_rsi = df["RSI"].iloc[-1]
        if np.isnan(latest_rsi):
            print("⚠️ No hay suficientes velas para calcular RSI.")
            return None

        # base probabilities from RSI rule
        if latest_rsi < self.rsi_threshold:
            base_down = self.base_confidence
            base_up = 1.0 - base_down
            base_pred = "SHORT"
        else:
            base_up = self.base_confidence
            base_down = 1.0 - base_up
            base_pred = "LONG"

        # default final probs = base
        final_up = base_up
        final_down = base_down

        # optional pattern-based adjustment
        if self.use_pattern_adjust:
            # compute pattern stats once
            stats = self._compute_pattern_stats(df)
            # get latest non-zero patterns (in last candle)
            o = df["open"].values
            h = df["high"].values
            l = df["low"].values
            c = df["close"].values
            pattern_funcs = talib.get_function_groups()['Pattern Recognition']
            latest_idx = len(df) - 1
            pattern_probs = []
            for func in pattern_funcs:
                try:
                    val = getattr(talib, func)(o, h, l, c)[-1]
                except Exception:
                    val = 0
                if val != 0:
                    pat_name = func[3:]
                    prob_up = stats.get(pat_name, None)
                    if prob_up is not None:
                        pattern_probs.append(prob_up)
            if len(pattern_probs) > 0:
                # aggregate pattern-based prob_up (mean)
                pattern_prob_up = float(np.mean(pattern_probs))
                # combine base and pattern prob with weight
                alpha = 1.0 - self.pattern_adjust_weight  # weight for base
                final_up = alpha * base_up + (1 - alpha) * pattern_prob_up
                final_down = 1.0 - final_up
            # else: no pattern available -> keep base

        # normalize (safety)
        s = final_up + final_down
        if s <= 0:
            final_up, final_down = base_up, base_down
        else:
            final_up /= s
            final_down /= s

        prediction = "LONG" if final_up >= final_down else "SHORT"

        # Print debug
        print(f"📊 RSI({self.rsi_period}) = {latest_rsi:.2f} | base: up {base_up*100:.1f}%, down {base_down*100:.1f}%")
        if self.use_pattern_adjust:
            print(f"🔁 Ajuste por patrones activado (peso ajuste {self.pattern_adjust_weight})")
        print(f"🎯 Predicción siguiente vela: {prediction}  (up {final_up*100:.1f}%  |  down {final_down*100:.1f}%)")

        return prediction, {"up": float(final_up), "down": float(final_down)}
