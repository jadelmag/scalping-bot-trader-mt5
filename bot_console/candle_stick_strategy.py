"""
Clase MT5StrategyM1
Estrategia de scalping para timeframe M1 basada en:
"cuerpo fuerte" vs "mecha dominante".
Solo devuelve la señal (LONG / SHORT / None),
no ejecuta operaciones.
"""

import MetaTrader5 as mt5
import pandas as pd

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
        self.candles = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 2)
        if self.candles is None:
            raise RuntimeError(f"No se pudieron descargar velas M1 para {self.symbol}: {mt5.last_error()}")
        return self.candles
    
    def get_last_candle(self):
        """
        Obtiene la última vela cerrada
        """
        if (self.candles is None):
            self.candles = self.get_last_two_candles()
        return self.candles[0]
    
    def get_penultimate_candle(self):
        """
        Obtiene la penúltima vela cerrada
        """
        if (self.candles is None):
            self.candles = self.get_last_two_candles()
        return self.candles[1]

    def get_sticks_from_last_candle(self):
        """
        Obtiene las mechas y datos de la última vela cerrada
        """
        candle = self.get_last_candle()

        open_price = candle['open']
        high_price = candle['high']
        low_price = candle['low']
        close_price = candle['close']

        candle_top = max(open_price, close_price)
        candle_bottom = min(open_price, close_price)

        upper_wick = high_price - candle_top
        lower_wick = candle_bottom - low_price

        has_upper_wick = upper_wick > 0
        has_lower_wick = lower_wick > 0

        print(f"🕯 Precio de cierre: Close: {close_price:.5f}")
        print(f"⬆ Mecha superior: {upper_wick:.5f} ({'Sí' if has_upper_wick else 'No'})")
        print(f"⬇ Mecha inferior: {lower_wick:.5f} ({'Sí' if has_lower_wick else 'No'})")

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
        last_candle = self.get_last_candle()
        penultimate_candle = self.get_penultimate_candle()

        upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price = self.get_sticks_from_last_candle()

        print(f"penultimate_candle: Close: {penultimate_candle['close']:.5f} | Open: {penultimate_candle['open']:.5f} | High: {penultimate_candle['high']:.5f} | Low: {penultimate_candle['low']:.5f}")
        print(f"upper_wick: {upper_wick:.5f}")
        print(f"lower_wick: {lower_wick:.5f}")
        print(f"has_upper_wick: {has_upper_wick}")
        print(f"has_lower_wick: {has_lower_wick}")
        print(f"low_price: {low_price}")
        print(f"high_price: {high_price}")
        print(f"close_price: {close_price}")
        print(f"open_price: {open_price}")

        # --- Tiene mecha superior e inferior, la diferencia entre mechas es pequeña y se cierra con el mismo precio

        if (has_upper_wick and has_lower_wick and open_price == close_price):
            if (upper_wick > lower_wick):
                print(f"1: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es grande")
                return SIGNAL_SHORT
            else:
                print(f"2: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es pequeña")
                return SIGNAL_LONG

        elif (has_upper_wick and has_lower_wick and open_price == close_price and upper_wick == lower_wick):
            print(f"3: tienen mechas y se abre y cierra en el mismo precio y la diferencia entre mechas es igual")
            return SIGNAL_NONE
        
        # --- Tienen mecha superior e inferior

        elif (has_upper_wick and has_lower_wick):
            diffWick = upper_wick - lower_wick
            print(f"diffWick: {diffWick:.5f}")
            if abs(diffWick) > 0.00004:
                print(f"4.1: tienen ambas mechas y la diferencia entre mechas es media")
                return SIGNAL_SHORT
            if (lower_wick > upper_wick):
                print(f"4.2: tienen ambas mechas y la mecha superior es mayor que la inferior")
                return SIGNAL_LONG
            else:
                print(f"4.3: tienen ambas mechas y la mecha inferior es mayor que la superior")
                return SIGNAL_SHORT

        # --- No tiene mecha superior ni inferior

        elif (not has_upper_wick and not has_lower_wick and upper_wick > lower_wick):
            print(f"7: no tiene mechas y se cierra cerca del máximo")
            return SIGNAL_LONG
        elif (not has_upper_wick and not has_lower_wick and lower_wick < upper_wick):
            print(f"8: no tiene mechas y se cierra cerca del mínimo")
            return SIGNAL_SHORT

        # --- Tienen mecha superior y no mecha inferior

        elif (has_upper_wick and not has_lower_wick and upper_wick > lower_wick): 
            if (lower_wick == 0):
                print(f"9: tiene mecha superior y se cierra cerca del máximo")
                return SIGNAL_SHORT
            print(f"9: tiene mecha superior y se cierra cerca del máximo")
            return SIGNAL_SHORT
        elif (has_upper_wick and not has_lower_wick and upper_wick < lower_wick):
            print(f"10: tiene mecha superior y se cierra cerca del mínimo")
            return SIGNAL_LONG

        # --- No tiene mecha inferior y tienen mecha superior

        elif (not has_upper_wick and has_lower_wick and upper_wick > lower_wick):
            print(f"11: no tiene mecha superior y se cierra cerca del máximo")
            return SIGNAL_LONG
        elif (not has_upper_wick and has_lower_wick):
            if (upper_wick == 0):
                print(f"12: no tiene mecha superior")
                return SIGNAL_SHORT
            elif (upper_wick < lower_wick):
                print(f"13: no tiene mecha superior y la mecha inferior es menor a la mecha superior")
                return SIGNAL_SHORT
            else:
                print(f"14: no tiene mecha superior y la mecha inferior es mayor a la mecha superior")
                return SIGNAL_LONG
    
        else:
            print(f"15: No arriesgamos | Operación Neutral")
            return SIGNAL_NONE
