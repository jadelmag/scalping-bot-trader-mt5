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

        # --- Tiene mecha superior e inferior, se cierra con el mismo precio

        if (has_upper_wick and has_lower_wick and open_price == close_price):
            if (upper_wick > lower_wick):
                print(f"01: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es grande")
                return SIGNAL_LONG, "01", info
            else:
                print(f"02: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es pequeña")
                return SIGNAL_SHORT, "02", info
        elif (has_upper_wick and has_lower_wick and open_price == close_price and upper_wick == lower_wick):
            print(f"03: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es igual")
            return SIGNAL_NONE, "03", info
        
        # --- Tienen mecha superior e inferior

        elif has_upper_wick and has_lower_wick:
            if (upper_wick_prev == lower_wick_prev and close_price < open_price):
                print(f"04: tienen mechas y la diferencia entre mechas es igual")
                return SIGNAL_SHORT, "04", info
            if (low_price_prev >=  0.00020 and upper_wick_prev <= upper_wick):
                print(f"05: tienen mechas y la diferencia entre mechas es igual")
                return SIGNAL_LONG, "05", info
            if (upper_wick_prev >= upper_wick and lower_wick_prev < lower_wick):
                print(f"06: tienen mechas y la diferencia entre mechas es igual")
                return SIGNAL_LONG, "06", info
            if (upper_wick_prev < upper_wick and lower_wick_prev > lower_wick):
                print(f"07: tienen mechas y la diferencia entre mechas es igual") 
                return SIGNAL_SHORT, "07", info
            else:
                print(f"08: tienen mechas y la diferencia entre mechas es igual")
                return SIGNAL_LONG, "08", info

             
        # --- No tiene mecha superior ni inferior

        elif (not has_upper_wick and not has_lower_wick and close_price > open_price):
            print(f"11: TEST")
            return SIGNAL_SHORT, "11", info # CONFUSA
        elif (not has_upper_wick and not has_lower_wick and close_price < open_price):
            print(f"12: TEST")
            return SIGNAL_LONG, "12", info
        elif (not has_upper_wick and not has_lower_wick and close_price == open_price):
            print(f"13: TEST")
            return SIGNAL_NONE, "13", info

        # --- Tienen mecha superior y no mecha inferior

        elif (has_upper_wick and not has_lower_wick and upper_wick == 0):
            print(f"14: TEST")
            return SIGNAL_SHORT, "14", info
        elif (has_upper_wick and not has_lower_wick and lower_wick_prev >= 0.00010 and lower_wick == 0):
            print(f"15: TEST")
            return SIGNAL_LONG, "15", info
        elif (has_upper_wick and not has_lower_wick and upper_wick < 0.00005):
            print(f"15: TEST")
            return SIGNAL_SHORT, "15", info

        # --- No tiene mecha superior y tienen mecha inferior

        elif (not has_upper_wick and has_lower_wick and upper_wick > lower_wick):
            print(f"16: TEST")
            return SIGNAL_LONG, "16", info
        elif (not has_upper_wick and has_lower_wick):
            if lower_wick < lower_wick_prev and upper_wick_prev > lower_wick_prev: 
                print(f"17: TEST")
                return SIGNAL_LONG, "17", info
            elif lower_wick_prev >= lower_wick * 2:
                print(f"18: TEST")
                return SIGNAL_LONG, "18", info
            else:
                print(f"19: TEST")
                return SIGNAL_LONG, "19", info
    
        else:
            print(f"20: no se cumple ninguna condición")
            return SIGNAL_NONE, "20", info
