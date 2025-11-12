"""
Clase MT5StrategyM1
Estrategia de scalping para timeframe M1 basada en:
"cuerpo fuerte" vs "mecha dominante".
Solo devuelve la señal (LONG / SHORT / None),
no ejecuta operaciones.
"""

import MetaTrader5 as mt5
import pandas as pd

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

        if (upper_wick == 0.00001):
            upper_wick = 0.0
        if (lower_wick == 0.00001):
            lower_wick = 0.0

        has_upper_wick = upper_wick > 0
        has_lower_wick = lower_wick > 0

        print(f"🕯 Precio de cierre: {close_price}")
        print(f"⬆ Mecha superior: {upper_wick:.5f} ({'Sí' if has_upper_wick else 'No'})")
        print(f"⬇ Mecha inferior: {lower_wick:.5f} ({'Sí' if has_lower_wick else 'No'})")

        return upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price

    def getDiffWick(self, upper_wick, lower_wick, high_price, close_price):
        """
        Obtiene la diferencia entre las mechas
        """
        # margen de diferencia aceptable entre mechas
        wick_diff_tolerance = 0.00001  

        # diferencia real entre mechas
        real_wick_diff = abs(upper_wick - lower_wick)

        diff = real_wick_diff <= wick_diff_tolerance
        print(f"getDiffWick: {diff}")
        return diff

    def getCloseToHigh(self, high_price, close_price):
        """
        Obtiene la distancia entre el precio de cierre y el máximo
        """
        # distancia entre el precio de cierre y el máximo
        close_to_high = abs(high_price - close_price)

        # definimos el umbral de "proximidad"
        close_tolerance = 0.00003 

        return close_to_high <= close_tolerance
    
    def getCloseToLow(self, low_price, close_price):
        """
        Obtiene la distancia entre el precio de cierre y el mínimo
        """
        close_to_low = abs(close_price - low_price)
        close_tolerance = 0.00003
        return close_to_low <= close_tolerance

    def checkIfUpperWickIsGreaterThanLowerWick(self, upper_wick, lower_wick):
        """
        Obtiene la diferencia entre las mechas
        """
        # Define un factor para "mucho mayor"
        factor_mayor = 2.0  # por ejemplo, la mecha superior al menos 2 veces mayor que la inferior
        diff = upper_wick > lower_wick * factor_mayor
        print(f"checkIfUpperWickIsGreaterThanLowerWick: {diff}")
        return diff

    def checkIfLowerWickIsGreaterThanUpperWick(self, upper_wick, lower_wick):
        """
        Obtiene la diferencia entre las mechas
        """
        # Define un factor para "mucho mayor"
        factor_mayor = 2.0  # por ejemplo, la mecha inferior al menos 2 veces mayor que la superior
        diff = lower_wick > upper_wick * factor_mayor
        print(f"checkIfLowerWickIsGreaterThanUpperWick: {diff}")
        return diff

    def checkIfCloseIsCloseToPenultimateClose(self, close_price, penultimate_candle):
        """
        Obtiene la diferencia entre las mechas
        """
        # Define tolerancia para la proximidad del cierre con la vela anterior
        close_tolerance = 0.00003

        # Diferencia entre cierres
        diff_close = abs(close_price - penultimate_candle['close'])

        return diff_close <= close_tolerance

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

        print(f"upper_wick: {upper_wick:.5f}")
        print(f"lower_wick: {lower_wick:.5f}")
        print(f"has_upper_wick: {has_upper_wick}")
        print(f"has_lower_wick: {has_lower_wick}")
        print(f"low_price: {low_price}")
        print(f"high_price: {high_price}")
        print(f"close_price: {close_price}")
        print(f"open_price: {open_price}")

        wick_diff = self.getDiffWick(upper_wick, lower_wick, high_price, close_price)
        close_to_high = self.getCloseToHigh(high_price, close_price)
        close_to_low = self.getCloseToLow(low_price, close_price)

        if (has_upper_wick and has_lower_wick and open_price == close_price):
            print(f"tiene mechas y se abre y cierra en el mismo precio")
            return "NEUTRAL"
        elif (has_upper_wick and has_lower_wick and wick_diff and close_price > open_price):
            print(f"tiene mechas y se cierra cerca del máximo")
            return "SHORT"
        elif (has_upper_wick and has_lower_wick and wick_diff and close_price < open_price): #  OK
            print(f"tiene mechas y se cierra cerca del mínimo")
            return "LONG"
        elif (not has_upper_wick and not has_lower_wick and close_price > open_price):
            print(f"no tiene mechas y se cierra cerca del máximo")
            return "LONG"
        elif (not has_upper_wick and not has_lower_wick and close_price < open_price):
            print(f"no tiene mechas y se cierra cerca del mínimo")
            return "SHORT"
        elif (has_upper_wick and not has_lower_wick and close_price > open_price): 
            print(f"tiene mecha superior y se cierra cerca del máximo")
            return "LONG"
        elif (has_upper_wick and not has_lower_wick and close_price < open_price):
            print(f"tiene mecha superior y se cierra cerca del mínimo")
            return "SHORT"
        elif (not has_upper_wick and has_lower_wick and close_price > open_price): # REVISAR
            print(f"no tiene mecha superior y se cierra cerca del máximo")
            return "LONG"
        elif (not has_upper_wick and has_lower_wick and close_price < open_price): # REVISAR
            print(f"no tiene mecha superior y se cierra cerca del mínimo")
            return "SHORT"
        elif (has_upper_wick and has_lower_wick and 
            not self.checkIfUpperWickIsGreaterThanLowerWick(upper_wick, lower_wick) and 
            not self.checkIfCloseIsCloseToPenultimateClose(close_price, penultimate_candle)):
            print(f"tiene mechas y la mecha superior es mayor que la inferior y se cierra cerca de la vela anterior")
            return "LONG"
        elif (has_upper_wick and has_lower_wick and 
            not self.checkIfLowerWickIsGreaterThanUpperWick(upper_wick, lower_wick) and 
            not self.checkIfCloseIsCloseToPenultimateClose(close_price, penultimate_candle)): #  OK
            print(f"tiene mechas y la mecha inferior es mayor que la superior y se cierra cerca de la vela anterior")
            return "SHORT"
        


        else:
            return "NEUTRAL"
