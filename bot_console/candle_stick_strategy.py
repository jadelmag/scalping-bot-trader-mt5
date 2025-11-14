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

        # --- Señal de la vela
        signal = self.get_signal_from_candle(candle)

        # --- Cuerpo de la vela
        body = abs(close_price - open_price) * 100000.0

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
        print(f"body: {body}")
        print(f"signal: {signal}")

        return upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price, body, signal

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

        upper_wick_prev, lower_wick_prev, has_upper_wick_prev, has_lower_wick_prev, low_price_prev, high_price_prev, close_price_prev, open_price_prev, body_prev, signal_prev = self.get_sticks_from_candle(penultimate_candle, False)

        upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price, body, signal = self.get_sticks_from_candle(last_candle, True)

        prev_candle_info = {
            "upper_wick": f"{upper_wick_prev:.5f}",
            "lower_wick": f"{lower_wick_prev:.5f}",
            "has_upper_wick": has_upper_wick_prev,
            "has_lower_wick": has_lower_wick_prev,
            "low_price": f"{low_price_prev:.5f}",
            "high_price": f"{high_price_prev:.5f}",
            "close_price": f"{close_price_prev:.5f}",
            "open_price": f"{open_price_prev:.5f}",
            "body": f"{body_prev:.5f}",
            "signal": signal_prev
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
            "open_price": f"{open_price:.5f}",
            "body": f"{body:.5f}",
            "signal": signal
        }

        # --- Tiene mecha superior e inferior, la diferencia entre mechas es pequeña y se cierra con el mismo precio

        if (has_upper_wick and has_lower_wick and open_price == close_price):
            if (lower_wick < upper_wick):
                print(f"01: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es grande")
                return SIGNAL_SHORT, "01", info
            else:
                if (body == 0.0):
                    print("02")
                    return SIGNAL_SHORT, "02", info
                else:
                    print(f"02")
                    return SIGNAL_LONG, "02", info

        elif (has_upper_wick and has_lower_wick and open_price == close_price and upper_wick == lower_wick):
            print(f"03: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es igual")
            return SIGNAL_NONE, "03", info
        
        # --- Tienen mecha superior e inferior

        elif (has_upper_wick and has_lower_wick):
            if (upper_wick > lower_wick) and body_prev > body:
                print(f"04A")
                return SIGNAL_SHORT, "04A", info
            elif (upper_wick > lower_wick):
                if (body > 20.0):
                    print(f"04B")
                    return SIGNAL_SHORT, "04B", info
                if (body > body_prev) and close_price > open_price:
                    print(f"04C")
                    return SIGNAL_LONG, "04C", info
                elif (body < body_prev) and close_price > open_price:
                    print(f"04D")
                    return SIGNAL_LONG, "04D", info
                else:
                    print(f"04E")
                    return SIGNAL_SHORT, "04E", info
            elif (upper_wick < lower_wick) and body > 20.0:
                print(f"04F")
                return SIGNAL_LONG, "04G", info
            elif (upper_wick < lower_wick) and close_price < open_price:
                print(f"04H")
                return SIGNAL_LONG, "04H", info
            elif (upper_wick < lower_wick) and close_price > open_price:
                print(f"04I")
                return SIGNAL_SHORT, "04I", info
            else:
                print(f"04J") # CONFUSA
                return SIGNAL_NONE, "04J", info

        # --- No tiene mecha superior ni inferior

        elif (not has_upper_wick and not has_lower_wick and upper_wick > lower_wick):
            print(f"06")
            return SIGNAL_LONG, "06", info
        elif (not has_upper_wick and not has_lower_wick and lower_wick < upper_wick):
            print(f"07")
            return SIGNAL_SHORT, "07", info

        # --- Tienen mecha superior y no mecha inferior

        elif (has_upper_wick and not has_lower_wick):
            if (body > 20.0):
                print(f"08A")
                return SIGNAL_LONG, "08A", info
            elif (body_prev > body):
                print(f"08B")
                return SIGNAL_SHORT, "08B", info
            elif (upper_wick > lower_wick):
                return SIGNAL_LONG, "08C", info
            elif (upper_wick < lower_wick):
                return SIGNAL_SHORT, "08D", info
            else:
                return SIGNAL_NONE, "08E", info


        # --- No tiene mecha superior y tienen mecha inferior

        elif (not has_upper_wick and has_lower_wick):
            if (body > 20.0):
                print(f"09A")
                return SIGNAL_LONG, "09A", info
            elif (lower_wick_prev < lower_wick) and signal == SIGNAL_LONG:
                print(f"11: no tiene mecha superior y la mecha inferior es mayor a la mecha superior")
                return SIGNAL_SHORT, "11", info
            else:
                print(f"12: no tiene mecha superior y la mecha inferior es menor a la mecha superior")
                return SIGNAL_LONG, "12", info
    
        else:
            print(f"13: no se cumple ninguna condición")
            return SIGNAL_NONE, "13", info
