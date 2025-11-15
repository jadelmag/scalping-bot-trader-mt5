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

TREND_UP = "UP"
TREND_DOWN = "DOWN"
TREND_NEUTRAL = "NEUTRAL"

class CandleStickOffline:
    def __init__(self, path):
        self.pos_current_candle = 0
        self.candles = None
        self.num_candles = 0

        self.get_candles_from_csv(path)

    def get_candles_from_csv(self, path):
        """Carga las velas desde CSV - compatible con chart.csv y DATA_M1_2024.csv"""
        try:
            # Intentar cargar como chart.csv (con headers y comas)
            self.candles = pd.read_csv(path)
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
        print(f"CandleStickOffline: Loaded {self.num_candles} candles (format: {self.csv_format})")

    def get_last_candle(self):
        """
        Obtiene la última vela cerrada
        """
        if self.pos_current_candle >= self.num_candles:
            return None
        return self.candles.iloc[self.pos_current_candle]

    def get_penultimate_candle(self):
        """
        Obtiene la penúltima vela cerrada
        """
        if self.pos_current_candle - 1 < 0:
            return None
        return self.candles.iloc[self.pos_current_candle - 1]

    def get_signal_from_candle(self, candle):
        """
        Obtiene la señal de la vela
        """
        if candle is None:
            return SIGNAL_NONE
            
        try:
            # Acceso compatible con ambos formatos de CSV
            close_price = candle['Close']
            open_price = candle['Open']
            
            if close_price is None or open_price is None:
                return SIGNAL_NONE
                
            if close_price > open_price:
                return SIGNAL_LONG
            elif close_price < open_price:
                return SIGNAL_SHORT
            return SIGNAL_NONE
            
        except (KeyError, AttributeError, TypeError) as e:
            print(f"Error getting signal from candle: {e}")
            print(f"Available columns: {candle.index.tolist() if hasattr(candle, 'index') else 'No index'}")
            return SIGNAL_NONE

    def get_trend(self):
        """
        Obtiene el tendencia de las últimas dos velas cerradas
        """
        try:
            # Calcular tendencia basada en la posición actual
            current_pos = self.pos_current_candle - 1  # Posición actual (ya se incrementó)
            
            # Necesitamos al menos 2 velas para calcular tendencia
            if current_pos < 1:
                print("get_trend: No hay suficientes velas para calcular tendencia (inicio)")
                return TREND_NEUTRAL
                
            if current_pos >= self.num_candles:
                print("get_trend: Posición fuera de rango")
                return TREND_NEUTRAL
                
            # Acceder a las dos últimas velas procesadas
            penultimate_candle = self.candles.iloc[current_pos - 1]  # Vela anterior
            last_candle = self.candles.iloc[current_pos]  # Vela actual
                
            # Acceso compatible con ambos formatos de CSV
            last_close = last_candle['Close']
            penult_close = penultimate_candle['Close']
            
            if last_close > penult_close:
                trend_result = TREND_UP
            elif last_close < penult_close:
                trend_result = TREND_DOWN
            else:
                trend_result = TREND_NEUTRAL
                
            return trend_result
                
        except (KeyError, AttributeError, TypeError, IndexError) as e:
            print(f"Error getting trend: {e}")
            print(f"Current pos: {current_pos if 'current_pos' in locals() else 'undefined'}, Num candles: {self.num_candles}")
            return TREND_NEUTRAL

    def get_sticks_from_candle(self, candle, last: bool = False):
        """
        Obtiene las mechas y datos de la última vela cerrada
        """
        if candle is None:
            print(f"Error: candle is None (last={last})")
            return None, None, False, False, 0, 0, 0, 0, 0, SIGNAL_NONE
            
        try:
            # Acceso compatible con ambos formatos de CSV
            open_price = candle['Open']
            high_price = candle['High']
            low_price = candle['Low']
            close_price = candle['Close']
            
            if any(price == 0 for price in [open_price, high_price, low_price, close_price]):
                print(f"Error: Missing price data in candle: {candle}")
                return None, None, False, False, 0, 0, 0, 0, 0, SIGNAL_NONE
                
        except (KeyError, AttributeError, TypeError) as e:
            print(f"Error accessing candle data: {e}")
            print(f"Candle type: {type(candle)}")
            print(f"Available columns: {candle.index.tolist() if hasattr(candle, 'index') else 'No index'}")
            print(f"Candle content: {candle}")
            return None, None, False, False, 0, 0, 0, 0, 0, SIGNAL_NONE

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
