import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

class CandleStick:
    """
    Detector avanzado de patrones de velas japonesas para timeframe 1M.
    Carga histórico inicial y analiza la última vela en busca de patrones conocidos.
    """

    def __init__(self, symbol: str, n_candles: int = 200):
        self.symbol = symbol
        self.n_candles = n_candles
        self.df = self.load_candles()

    def load_candles(self):
        """Carga las últimas n_candles velas desde MetaTrader5."""
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, self.n_candles)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def update(self):
        """Actualiza el historial con la última vela cerrada."""
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 2)
        if rates is None or len(rates) < 2:
            return self.df

        df_new = pd.DataFrame(rates)
        df_new['time'] = pd.to_datetime(df_new['time'], unit='s')

        last_closed = df_new.iloc[-2]  # La vela cerrada más reciente

        if self.df['time'].iloc[-1] != last_closed['time']:
            self.df = pd.concat([self.df, pd.DataFrame([last_closed])]).iloc[-self.n_candles:]
        return self.df

    # ------------------- FUNCIONES DE DETECCIÓN -------------------

    def detect_pattern(self):
        """Evalúa los últimos candles y detecta el patrón actual."""
        df = self.df
        c = df.iloc[-1]
        p1 = df.iloc[-2] if len(df) >= 2 else None
        p2 = df.iloc[-3] if len(df) >= 3 else None

        # 1-Vela
        pattern = (
            self.is_hammer(c) or
            self.is_shooting_star(c) or
            self.is_marubozu(c) or
            self.is_doji(c)
        )

        # 2-Velas
        if p1 is not None and pattern is None:
            pattern = (
                self.is_bullish_engulfing(p1, c) or
                self.is_bearish_engulfing(p1, c) or
                self.is_piercing(p1, c) or
                self.is_dark_cloud(p1, c) or
                self.is_harami(p1, c)
            )

        # 3-Velas
        if p2 is not None and pattern is None:
            pattern = (
                self.is_morning_star(p2, p1, c) or
                self.is_evening_star(p2, p1, c) or
                self.is_three_white_soldiers(p2, p1, c) or
                self.is_three_black_crows(p2, p1, c)
            )

        return pattern or ("NONE", "NEUTRAL")

    # ------------------- PATRONES DE UNA VELA -------------------

    def is_hammer(self, c):
        body = abs(c['close'] - c['open'])
        lower_shadow = c['open'] - c['low'] if c['close'] >= c['open'] else c['close'] - c['low']
        upper_shadow = c['high'] - max(c['open'], c['close'])
        if lower_shadow > 2 * body and upper_shadow < body and c['close'] > c['open']:
            return ("HAMMER", "LONG")
        return None

    def is_shooting_star(self, c):
        body = abs(c['close'] - c['open'])
        upper_shadow = c['high'] - max(c['open'], c['close'])
        lower_shadow = min(c['open'], c['close']) - c['low']
        if upper_shadow > 2 * body and lower_shadow < body and c['close'] < c['open']:
            return ("SHOOTING_STAR", "SHORT")
        return None

    def is_marubozu(self, c):
        body = abs(c['close'] - c['open'])
        upper_shadow = c['high'] - max(c['open'], c['close'])
        lower_shadow = min(c['open'], c['close']) - c['low']
        if upper_shadow < body * 0.1 and lower_shadow < body * 0.1:
            if c['close'] > c['open']:
                return ("MARUBOZU_BULLISH", "LONG")
            else:
                return ("MARUBOZU_BEARISH", "SHORT")
        return None

    def is_doji(self, c):
        body = abs(c['open'] - c['close'])
        total = c['high'] - c['low']
        if total == 0:
            return None
        ratio = body / total
        if ratio <= 0.05:  # antes 0.1
            return ("DOJI", "NEUTRAL")
        return None

    # ------------------- PATRONES DE DOS VELAS -------------------

    def is_bullish_engulfing(self, p1, c):
        if p1['close'] < p1['open'] and c['close'] > c['open'] and c['close'] > p1['open'] and c['open'] < p1['close']:
            return ("BULLISH_ENGULFING", "LONG")
        return None

    def is_bearish_engulfing(self, p1, c):
        if p1['close'] > p1['open'] and c['close'] < c['open'] and c['open'] > p1['close'] and c['close'] < p1['open']:
            return ("BEARISH_ENGULFING", "SHORT")
        return None

    def is_piercing(self, p1, c):
        mid = p1['open'] - (p1['open'] - p1['close']) / 2
        if p1['close'] < p1['open'] and c['open'] < p1['close'] and c['close'] > mid:
            return ("PIERCING_PATTERN", "LONG")
        return None

    def is_dark_cloud(self, p1, c):
        mid = p1['close'] - (p1['close'] - p1['open']) / 2
        if p1['close'] > p1['open'] and c['open'] > p1['close'] and c['close'] < mid:
            return ("DARK_CLOUD_COVER", "SHORT")
        return None

    def is_harami(self, p1, c):
        if (abs(c['open'] - c['close']) < abs(p1['open'] - p1['close'])) and (c['high'] <= p1['high']) and (c['low'] >= p1['low']):
            if p1['close'] > p1['open']:
                return ("HARAMI_BEARISH", "SHORT")
            else:
                return ("HARAMI_BULLISH", "LONG")
        return None

    # ------------------- PATRONES DE TRES VELAS -------------------

    def is_morning_star(self, p2, p1, c):
        if p2['close'] < p2['open'] and abs(p1['close'] - p1['open']) < abs(p2['open'] - p2['close']) and c['close'] > c['open'] and c['close'] > (p2['open'] + p2['close']) / 2:
            return ("MORNING_STAR", "LONG")
        return None

    def is_evening_star(self, p2, p1, c):
        if p2['close'] > p2['open'] and abs(p1['close'] - p1['open']) < abs(p2['open'] - p2['close']) and c['close'] < c['open'] and c['close'] < (p2['open'] + p2['close']) / 2:
            return ("EVENING_STAR", "SHORT")
        return None

    def is_three_white_soldiers(self, p2, p1, c):
        if all([
            p2['close'] > p2['open'],
            p1['close'] > p1['open'],
            c['close'] > c['open'],
            p1['open'] > p2['open'],
            c['open'] > p1['open']
        ]):
            return ("THREE_WHITE_SOLDIERS", "LONG")
        return None

    def is_three_black_crows(self, p2, p1, c):
        if all([
            p2['close'] < p2['open'],
            p1['close'] < p1['open'],
            c['close'] < c['open'],
            p1['open'] < p2['open'],
            c['open'] < p1['open']
        ]):
            return ("THREE_BLACK_CROWS", "SHORT")
        return None

    # ------------------- SALIDA PRINCIPAL -------------------

    def predict_short_or_long_candle(self):
        """
        Detecta el patrón más reciente y devuelve una señal:
        ("LONG" / "SHORT" / "NEUTRAL")
        """
        self.update()
        pattern, signal = self.detect_pattern()
        # print(f"📊 Patrón detectado: {pattern} → Señal: {signal}")
        return signal

    # ------------------- FUNCIONES -------------------

    def detect_pattern(self, offset: int = 0):
        """
        Evalúa los últimos candles y detecta el patrón actual.
        offset=0 -> analiza la última vela (por ejemplo para backtest)
        offset=1 -> analiza la vela cerrada inmediatamente anterior (útil en tiempo real)
        """
        df = self.df
        # índices relativos teniendo en cuenta offset
        idx_c = -1 - offset
        idx_p1 = -2 - offset
        idx_p2 = -3 - offset

        # comprobar que hay suficientes velas
        if len(df) + idx_p2 < 0:  # significa que no hay al menos 3 velas si offset es 0,1,etc.
            return ("NONE", "NEUTRAL")

        c = df.iloc[idx_c]
        p1 = df.iloc[idx_p1] if len(df) + idx_p1 >= 0 else None
        p2 = df.iloc[idx_p2] if len(df) + idx_p2 >= 0 else None

        # 1-Vela
        pattern = (
            self.is_hammer(c) or
            self.is_shooting_star(c) or
            self.is_marubozu(c) or
            self.is_doji(c)
        )

        # 2-Velas
        if p1 is not None and pattern is None:
            pattern = (
                self.is_bullish_engulfing(p1, c) or
                self.is_bearish_engulfing(p1, c) or
                self.is_piercing(p1, c) or
                self.is_dark_cloud(p1, c) or
                self.is_harami(p1, c)
            )

        # 3-Velas
        if p2 is not None and pattern is None:
            pattern = (
                self.is_morning_star(p2, p1, c) or
                self.is_evening_star(p2, p1, c) or
                self.is_three_white_soldiers(p2, p1, c) or
                self.is_three_black_crows(p2, p1, c)
            )

        return pattern or ("NONE", "NEUTRAL")

    def get_type_signal_when_candle_finish(self):
        """
        Detecta la señal cuando la vela termina realmente.
        Retorna None si no hay nueva vela cerrada.
        """
        last_time = self.df['time'].iloc[-1]
        updated_df = self.update()

        # Si no hay vela nueva, no hacemos nada
        if updated_df['time'].iloc[-1] == last_time:
            return None

        # Analizar la última vela cerrada
        pattern, signal = self.detect_pattern(offset=0)
        print(f"✅ Vela cerrada: {updated_df['time'].iloc[-1]} → Patrón: {pattern}, Señal: {signal}")
        return signal, pattern
