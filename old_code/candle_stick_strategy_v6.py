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
from bot_console.candle_patterns import CandlePatterns1M

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
        self.patterns = CandlePatterns1M()

    def get_last_three_candles(self):
        """
        Obtiene las últimas dos velas cerradas
        """
        # start_pos=1 para saltar la vela actual (incompleta) y obtener las 2 últimas cerradas
        self.candles = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 3)
        if self.candles is None:
            raise RuntimeError(f"No se pudieron descargar velas M1 para {self.symbol}: {mt5.last_error()}")
        return self.candles
    
    def get_last_candle(self):
        """
        Obtiene la última vela cerrada
        """
        if (self.candles is None):
            self.candles = self.get_last_three_candles()
        return self.candles[2]
    
    def get_second_candle(self):
        """
        Obtiene la penúltima vela cerrada
        """
        if (self.candles is None):
            self.candles = self.get_last_three_candles()
        return self.candles[1]

    def get_third_candle(self):
        """
        Obtiene la tercera vela cerrada
        """
        if (self.candles is None):
            self.candles = self.get_last_three_candles()
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


    @staticmethod
    def interpret_signal(signals):
        """
        Interpreta la señal de la vela
        """
        bullish_score = 0
        bearish_score = 0

        # Patrones alcistas ponderados
        bullish_weights = {
            'morning_star': 3,
            'bullish_engulfing': 3,
            'piercing_pattern': 2,
            'three_white_soldiers': 3,
            'hammer_last': 2,
            'hammer_second': 2,
            'inverted_hammer_last': 2,
            'inverted_hammer_second': 2,
            'tweezer_bottoms': 2,
            'triple_bullish_bottom': 3,
        }

        # Patrones bajistas ponderados
        bearish_weights = {
            'evening_star': 3,
            'bearish_engulfing': 3,
            'dark_cloud_cover': 2,
            'shooting_star_last': 2,
            'shooting_star_second': 2,
            'hanging_man_last': 2,
            'hanging_man_second': 2,
            'three_black_crows': 3,
            'tweezer_tops': 2,
            'triple_bearish_top': 3,
        }

        for pattern, detected in signals.items():
            if detected:
                if pattern in bullish_weights:
                    bullish_score += bullish_weights[pattern]
                elif pattern in bearish_weights:
                    bearish_score += bearish_weights[pattern]

        if bullish_score > bearish_score:
            return SIGNAL_LONG
        elif bearish_score > bullish_score:
            return SIGNAL_SHORT
        else:
            return SIGNAL_NONE


    def get_signal_for_new_candle(self):
        self.get_last_three_candles()
        third_candle = self.get_third_candle()
        second_candle = self.get_second_candle()
        last_candle = self.get_last_candle()

        hanging_man_last = self.patterns.is_hanging_man(last_candle)
        shooting_star_last = self.patterns.is_shooting_star(last_candle)
        doji_last = self.patterns.is_doji(last_candle)
        spinning_top_last = self.patterns.is_spinning_top(last_candle)
        marubozu_last = self.patterns.is_marubozu(last_candle)
        hammer_last = self.patterns.is_hammer(last_candle)
        inverted_hammer_last = self.patterns.is_inverted_hammer(last_candle)

        # Patrones de 2 velas
        bearish_engulfing = self.patterns.is_bearish_engulfing(second_candle, last_candle)
        dark_cloud_cover = self.patterns.is_dark_cloud_cover(second_candle, last_candle)
        piercing_pattern = self.patterns.is_piercing_pattern(second_candle, last_candle)
        bullish_engulfing = self.patterns.is_bullish_engulfing(second_candle, last_candle)

        tweezer_bottoms = self.patterns.is_tweezer_bottoms(second_candle, last_candle)
        tweezer_tops = self.patterns.is_tweezer_tops(second_candle, last_candle)

        # # Patrones de 3 velas
        evening_star = self.patterns.is_evening_star(third_candle, second_candle, last_candle)
        three_black_crows = self.patterns.is_three_black_crows(third_candle, second_candle, last_candle)
        three_white_soldiers = self.patterns.is_three_white_soldiers(third_candle, second_candle, last_candle)
        morning_star = self.patterns.is_morning_star(third_candle, second_candle, last_candle)

        # # Patrones de series (requieren listas de velas, aquí puedes pasar como ejemplo [third, second, last])
        # triple_bearish_top = self.patterns.is_triple_bearish_top([third_candle, second_candle, last_candle])
        # triple_bullish_bottom = self.patterns.is_triple_bullish_bottom([third_candle, second_candle, last_candle])

        print(f"hanging_man_last: {hanging_man_last}")
        print(f"shooting_star_last: {shooting_star_last}")
        print(f"doji_last: {doji_last}")
        print(f"spinning_top_last: {spinning_top_last}")
        print(f"marubozu_last: {marubozu_last}")
        print(f"hammer_last: {hammer_last}")
        print(f"inverted_hammer_last: {inverted_hammer_last}")
        print(f"bearish_engulfing: {bearish_engulfing}")
        print(f"dark_cloud_cover: {dark_cloud_cover}")
        print(f"piercing_pattern: {piercing_pattern}")
        print(f"bullish_engulfing: {bullish_engulfing}")
        print(f"tweezer_bottoms: {tweezer_bottoms}")
        print(f"tweezer_tops: {tweezer_tops}")
        # print(f"evening_star: {evening_star}")
        # print(f"three_black_crows: {three_black_crows}")
        # print(f"three_white_soldiers: {three_white_soldiers}")
        # print(f"morning_star: {morning_star}")
        # print(f"triple_bearish_top: {triple_bearish_top}")
        # print(f"triple_bullish_bottom: {triple_bullish_bottom}")


        if (evening_star or three_black_crows or hanging_man_last or shooting_star_last or bearish_engulfing or dark_cloud_cover or tweezer_tops):
            return SIGNAL_SHORT, "Short Signal", "Short Signal"
        elif (three_white_soldiers or morning_star or hammer_last or inverted_hammer_last or piercing_pattern or bullish_engulfing or tweezer_bottoms):
            return SIGNAL_LONG, "Long Signal", "Long Signal"
        elif (doji_last or spinning_top_last or marubozu_last):
            prev_signal = self.get_signal_from_candle(second_candle)
            if (spinning_top_last and prev_signal == SIGNAL_LONG):
                return SIGNAL_SHORT, "Short Signal", "Short Signal"
            return SIGNAL_NONE, "Neutral Signal", "Neutral Signal"
        else:
            return SIGNAL_NONE, "Neutral Signal", "Neutral Signal"
      