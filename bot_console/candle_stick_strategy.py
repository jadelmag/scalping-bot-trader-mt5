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
from bot_console.resumes import ResumeJsonL
from datetime import datetime

SIGNAL_NONE = "NEUTRAL"
SIGNAL_LONG = "LONG"
SIGNAL_SHORT = "SHORT"

TREND_UP = "UP"
TREND_DOWN = "DOWN"
TREND_NEUTRAL = "NEUTRAL"

resume_logger = ResumeJsonL(f"candle_stick_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}", blockMessages=True)

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

    def get_trend(self):
        """
        Obtiene el tendencia de las últimas dos velas cerradas
        """
        last_candle = self.get_last_candle()
        penultimate_candle = self.get_penultimate_candle()

        if last_candle['close'] > penultimate_candle['close']:
            trend = TREND_UP
        elif last_candle['close'] < penultimate_candle['close']:
            trend = TREND_DOWN
        else:
            trend = TREND_NEUTRAL

        return trend

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
        body = abs(close_price - open_price)

        resume_logger.log({"message": f"Última vela:" if last else "Penúltima vela:", "type": "info"})
        resume_logger.log({"message": f"🕯 Precio de cierre: Close: {close_price:.5f}", "type": "info"})
        resume_logger.log({"message": f"⬆ Mecha superior: {upper_wick:.5f} ({'Sí' if has_upper_wick else 'No'})", "type": "info"})
        resume_logger.log({"message": f"⬇ Mecha inferior: {lower_wick:.5f} ({'Sí' if has_lower_wick else 'No'})", "type": "info"})
        resume_logger.log({"message": f"has_upper_wick: {has_upper_wick}", "type": "info"})
        resume_logger.log({"message": f"has_lower_wick: {has_lower_wick}", "type": "info"})
        resume_logger.log({"message": f"low_price: {low_price}", "type": "info"})
        resume_logger.log({"message": f"high_price: {high_price}", "type": "info"})
        resume_logger.log({"message": f"close_price: {close_price}", "type": "info"})
        resume_logger.log({"message": f"open_price: {open_price}", "type": "info"})
        resume_logger.log({"message": f"body: {body}", "type": "info"})
        resume_logger.log({"message": f"signal: {signal}", "type": "info"})

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
        MODELO ULTRA CONSERVADOR
        - Maximiza operaciones correctas
        - Minimiza operaciones incorrectas (lo más cercano a 0)
        - Filtra TODO lo dudoso
        """

        # 1. FIN DATOS
        if self.pos_current_candle >= self.num_candles:
            return "END", "END"

        last = self.get_last_candle()
        if last is None:
            return "ERROR", "ERROR"

        prev = self.get_penultimate_candle()
        self.pos_current_candle += 1

        if prev is None:
            return SIGNAL_NONE, "INIT"

        # Obtener valores
        trend = self.get_trend()

        up_prev, low_prev, has_up_prev, has_low_prev, lprev, hprev, cprev, oprev, body_prev, signal_prev = \
            self.get_sticks_from_candle(prev, False)

        up, low, has_up, has_low, l, h, close, open_, body, signal_raw = \
            self.get_sticks_from_candle(last, True)

        # ------------------------------------------------------------
        # ESTADÍSTICA REAL
        # ------------------------------------------------------------
        stats = {
            (True, True):   {"LONG": 989, "SHORT": 948, "NEUTRAL": 196, "id": "P11"},
            (True, False):  {"LONG": 471, "SHORT": 367, "NEUTRAL": 71,  "id": "P10"}, # LONG = 52% (válido)
            (False, True):  {"LONG": 315, "SHORT": 489, "NEUTRAL": 63,  "id": "P01"}, # SHORT = 56% (válido)
            (False, False): {"LONG": 181, "SHORT": 225, "NEUTRAL": 75,  "id": "P00"}, # Muy poco fiable
        }

        key = (has_up, has_low)
        s = stats[key]
        total = s["LONG"] + s["SHORT"] + s["NEUTRAL"]
        pattern_id = s["id"]

        stat_signal = max(["LONG", "SHORT", "NEUTRAL"], key=lambda x: s[x])
        stat_conf = s[stat_signal] / total

        # ------------------------------------------------------------
        # ULTRA FILTROS (los que reducen errores a 0)
        # ------------------------------------------------------------

        # ❌ Bloquear patrones dudosos
        if key == (True, True):     # Ambas mechas
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-BOTHWICKS"
        if key == (False, False):   # Sin mechas
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-NOWICKS"

        # ❌ Bloquear cuerpos pequeños (indecisión)
        if body < 0.00004:
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-SMALLBODY"

        # ❌ Requiere estadística fuerte
        if stat_conf < 0.55:
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-LOWSTAT"

        # ❌ Señal previa debe acompañar
        if stat_signal == "LONG" and signal_prev == "SHORT":
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-PREVCONTRA"
        if stat_signal == "SHORT" and signal_prev == "LONG":
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-PREVCONTRA"

        # ❌ Tendencia debe acompañar SIEMPRE
        if stat_signal == "LONG" and trend != TREND_UP:
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-TREND"
        if stat_signal == "SHORT" and trend != TREND_DOWN:
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-TREND"

        # ❌ Velas contradictorias
        if stat_signal == "LONG" and close < open_:
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-BEARCANDLE"
        if stat_signal == "SHORT" and close > open_:
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-BULLCANDLE"

        # ❌ Rechazos deben ser coherentes
        # LONG → rechazo inferior
        if stat_signal == "LONG" and not (has_low and not has_up):
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-NOREJECTLOW"

        # SHORT → rechazo superior
        if stat_signal == "SHORT" and not (has_up and not has_low):
            return SIGNAL_NONE, f"{pattern_id}-BLOCK-NOREJECTHIGH"

        # ------------------------------------------------------------
        # SEÑAL FINAL (altísima calidad)
        # ------------------------------------------------------------
        return stat_signal, f"{pattern_id}-ULTRACONSERV"
