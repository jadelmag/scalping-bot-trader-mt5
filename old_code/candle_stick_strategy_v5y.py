"""
Clase MT5StrategyM1
Estrategia de scalping para timeframe M1 basada en:
"cuerpo fuerte" vs "mecha dominante".
Solo devuelve la señal (LONG / SHORT / None),
no ejecuta operaciones.
"""

import MetaTrader5 as mt5
import pandas as pd
from enum import IntEnum

SIGNAL_NONE = "NEUTRAL"
SIGNAL_LONG = "LONG"
SIGNAL_SHORT = "SHORT"

class CandleStickStrategy:
    def __init__(self, symbol: str):
        """
        :param symbol: símbolo, ej. "EURUSD"
        """
        self.symbol = symbol
        self.candles = None
        self.numTimesShort = 0
        self.numTimesLong = 0

    def get_last_two_candles(self):
        """
        Obtiene las últimas dos velas cerradas
        """
        # start_pos=1 para saltar la vela actual (incompleta) y obtener las 2 últimas cerradas
        self.candles = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 2)
        if self.candles is None:
            raise RuntimeError(f"No se pudieron descargar velas M1 para {self.symbol}: {mt5.last_error()}")
        return self.candles
    
    def get_last_candle(self):
        """
        Obtiene la última vela cerrada
        """
        if (self.candles is None):
            self.candles = self.get_last_two_candles()
        return self.candles[1]
    
    def get_penultimate_candle(self):
        """
        Obtiene la penúltima vela cerrada
        """
        if (self.candles is None):
            self.candles = self.get_last_two_candles()
        return self.candles[0]

    def get_sticks_from_candle(self, candle, last: bool = False):
        """
        Obtiene las mechas y datos de la última vela cerrada
        """
        open_price = candle['open']
        high_price = candle['high']
        low_price = candle['low']
        close_price = candle['close']

        candle_top = max(open_price, close_price)
        candle_bottom = min(open_price, close_price)

        upper_wick = high_price - candle_top
        lower_wick = candle_bottom - low_price

        # if abs(upper_wick - 0.00001) < 1e-6: upper_wick = 0
        # if abs(lower_wick - 0.00001) < 1e-6: lower_wick = 0

        has_upper_wick = upper_wick > 0
        has_lower_wick = lower_wick > 0

        print("Última vela:" if last else "Penúltima vela:")
        print(f"🕯 Precio de cierre: Close: {close_price:.5f}")
        print(f"⬆ Mecha superior: {upper_wick:.5f} ({'Sí' if has_upper_wick else 'No'})")
        print(f"⬇ Mecha inferior: {lower_wick:.5f} ({'Sí' if has_lower_wick else 'No'})")
        print(f"has_upper_wick: {has_upper_wick}")
        print(f"has_lower_wick: {has_lower_wick}")
        print(f"low_price: {low_price}")
        print(f"high_price: {high_price}")
        print(f"close_price: {close_price}")
        print(f"open_price: {open_price}")

        return upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price

    def get_signal_from_candle(self, candle):
        """
        Obtiene la señal de la vela
        """
        close_price = candle['close']
        open_price = candle['open']

        if close_price > open_price:
            signal = SIGNAL_LONG
        elif close_price < open_price:
            signal = SIGNAL_SHORT
        else:
            signal = SIGNAL_NONE

        return signal

    def candle_strength(self, open_price, close_price, high_price, low_price):
        """
        Si la última vela tiene mecha inferior grande → presión compradora (long)
        Si tiene mecha superior grande → presión vendedora (short)
        """
        body = abs(close_price - open_price)
        range_ = high_price - low_price
        if range_ == 0:
            return 0
        return body / range_

    def wick_bias(self, upper_wick, lower_wick):
        """
        ✔ 1 = vela muy fuerte
        ✔ 0 = vela de indecisión
        ✔ 0.5 = fuerza moderada
        """
        if upper_wick > lower_wick * 2:
            return "SHORT"
        if lower_wick > upper_wick * 2:
            return "LONG"
        return None

    def predict_next_signal(self,prev_signal, last_signal, upper_wick, lower_wick, open_price, close_price, high_price, low_price):
        direction = "LONG" if close_price > open_price else "SHORT"
        strength = self.candle_strength(open_price, close_price, high_price, low_price)
        wick_direction = self.wick_bias(upper_wick, lower_wick)

        # 1. Si hay una mecha que domina → prioridad alta
        if wick_direction is not None:
            return wick_direction

        # 2. Dos velas del mismo color → continuar tendencia
        if prev_signal == last_signal:
            if strength > 0.4:
                return last_signal  # continuación fuerte

        # 3. Si la última vela cambia de dirección → considerar reversión
        if prev_signal != last_signal:
            if strength < 0.2:
                # vela pequeña → indecisión → usar penúltima
                return prev_signal
            return last_signal  # la última manda

        # 4. fallback: usar dirección de la última vela
        return direction

    def get_signal_for_new_candle(self):
        """
        Obtiene la señal para la próxima vela
        upper_wick: mecha superior
        lower_wick: mecha inferior
        has_upper_wick: si hay mecha superior
        has_lower_wick: si hay mecha inferior
        close_price: precio de cierre
        """
        self.get_last_two_candles()
        penultimate_candle = self.get_penultimate_candle()
        last_candle = self.get_last_candle()
        penultimate_singnal = self.get_signal_from_candle(penultimate_candle)
        last_singnal = self.get_signal_from_candle(last_candle)

        upper_wick_prev, lower_wick_prev, has_upper_wick_prev, has_lower_wick_prev, low_price_prev, high_price_prev, close_price_prev, open_price_prev = self.get_sticks_from_candle(penultimate_candle, False)

        upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price = self.get_sticks_from_candle(last_candle, True)

        prev_candle_info = {
            "upper_wick": f"{upper_wick_prev:.5f}",
            "lower_wick": f"{lower_wick_prev:.5f}",
            "has_upper_wick": has_upper_wick_prev,
            "has_lower_wick": has_lower_wick_prev,
            "low_price": f"{low_price_prev:.5f}",
            "high_price": f"{high_price_prev:.5f}",
            "close_price": f"{close_price_prev:.5f}",
            "open_price": f"{open_price_prev:.5f}"
        }
        info = {
            "penultimate_candle": prev_candle_info,
            "upper_wick": f"{upper_wick:.5f}",
            "lower_wick": f"{lower_wick:.5f}",
            "has_upper_wick": has_upper_wick,
            "has_lower_wick": has_lower_wick,
            "low_price": f"{low_price:.5f}",
            "high_price": f"{high_price:.5f}",
            "close_price": f"{close_price:.5f}",
            "open_price": f"{open_price:.5f}"
        }

        print(f"Señal penúltima vela: {penultimate_singnal}")
        print(f"Señal última vela: {last_singnal}")
        
        predicted = self.predict_next_signal(
            penultimate_singnal,
            last_singnal,
            upper_wick,
            lower_wick,
            open_price,
            close_price,
            high_price,
            low_price
        )

        print(f"🔮 Señal predicha para próxima vela: {predicted}")
        return predicted, "01", info
