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
        Obtiene la señal para la próxima vela
        upper_wick: mecha superior
        lower_wick: mecha inferior
        has_upper_wick: si hay mecha superior
        has_lower_wick: si hay mecha inferior
        close_price: precio de cierre
        """
        # Verificar si hemos llegado al final
        if self.pos_current_candle >= self.num_candles:
            return "END", "END"

        # Obtener la vela actual
        last_candle = self.get_last_candle()

        if last_candle is None:
            print(f"Error: No se pudo obtener la vela en posición {self.pos_current_candle}")
            return "ERROR", "ERROR"

        # Obtener la vela anterior (si existe)
        penultimate_candle = self.get_penultimate_candle()
        
        # Avanzar a la siguiente para la próxima llamada
        self.pos_current_candle += 1
        
        # Si no hay vela anterior (primera iteración), usar valores por defecto
        if penultimate_candle is None:
            print("Primera vela - no hay vela anterior para comparar")
            # Solo procesar la vela actual
            upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price, body, signal = self.get_sticks_from_candle(last_candle, True)
            
            if signal is None:
                return SIGNAL_NONE, "INIT"
            return SIGNAL_NONE, "INIT"
            
        # Procesar ambas velas
        trend = self.get_trend()
        
        upper_wick_prev, lower_wick_prev, has_upper_wick_prev, has_lower_wick_prev, low_price_prev, high_price_prev, close_price_prev, open_price_prev, body_prev, signal_prev = self.get_sticks_from_candle(penultimate_candle, False)
        
        upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price, body, signal = self.get_sticks_from_candle(last_candle, True)
        
        print(f"Tendencia: {trend}")
        
        # --- Tienen mecha superior e inferior

        # elif (has_upper_wick and has_lower_wick):
        #     if (upper_wick > lower_wick * 2) and trend == TREND_DOWN:
        #         return SIGNAL_SHORT, "04"
        #     elif (upper_wick > lower_wick * 2) and trend == TREND_UP:
        #         return SIGNAL_LONG, "05"
        #     elif (upper_wick * 2 < lower_wick) and trend == TREND_DOWN:
        #         return SIGNAL_SHORT, "06"
        #     elif (upper_wick * 2 < lower_wick) and trend == TREND_UP:
        #         return SIGNAL_LONG, "07"
        #     elif (upper_wick > lower_wick) and trend == TREND_UP:
        #         return SIGNAL_LONG, "08"
        #     elif (upper_wick < lower_wick) and trend == TREND_DOWN:
        #         return SIGNAL_SHORT, "09"
        #     elif (upper_wick > lower_wick) and trend == TREND_DOWN:
        #         return SIGNAL_SHORT, "10"
        #     elif (upper_wick < lower_wick) and trend == TREND_UP:
        #         return SIGNAL_LONG, "11" 
        #     elif (upper_wick < lower_wick) and trend == TREND_NEUTRAL:
        #         return SIGNAL_LONG, "12" 
        #     elif (upper_wick > lower_wick) and trend == TREND_NEUTRAL:
        #         return SIGNAL_SHORT, "13"
        #     else:
        #         return SIGNAL_SHORT, "14"
                
        # --- No tiene mecha superior ni inferior

        # elif (not has_upper_wick and not has_lower_wick):
        #     if lower_wick >= body * 2 and trend == TREND_DOWN:
        #         return SIGNAL_SHORT, "20"
        #     elif lower_wick >= body * 2 and trend == TREND_UP:
        #         return SIGNAL_LONG, "21"
        #     elif (body > body_prev) and trend == TREND_UP:
        #         return SIGNAL_SHORT, "22"
        #     elif (body > body_prev) and trend == TREND_DOWN:
        #         return SIGNAL_LONG, "23"
        #     else:
        #         return SIGNAL_SHORT, "24"

        # --- Tienen mecha superior y no mecha inferior

        # elif (has_upper_wick and not has_lower_wick):
        #     # Patrón: Rechazo en soporte en tendencia alcista
        #     if (body > 0.0001 and trend == TREND_UP and signal_prev == SIGNAL_SHORT):
        #         print("40")
        #         return SIGNAL_LONG, "40"
        #     else:
        #         print("43")
        #         return SIGNAL_NONE, "43"
        
        # --- No tiene mecha superior y tienen mecha inferior

        if not has_upper_wick and has_lower_wick:
            # Patrón: Rechazo en soporte en tendencia alcista
            if (body > 0.0001 and trend == TREND_UP and signal_prev != SIGNAL_SHORT):
                print("40")
                return SIGNAL_LONG, "40"
                
            # Patrón: Pin bar alcista
            elif (body < 0.00003 and trend == TREND_UP and body_prev > 0.0001):
                print("41")
                return SIGNAL_LONG, "41"
                
            # Patrón: Cuerpo pequeño con mecha inferior larga
            elif (body < 0.00005 and trend == TREND_DOWN):
                # Posible reversión, ser conservador
                print("42")
                return SIGNAL_NONE, "42"
            # elif (signal_prev == SIGNAL_SHORT and signal == SIGNAL_LONG):
            #     upper_wick_prev = float(f"{upper_wick_prev:.5f}")
            #     lower_wick_prev = float(f"{lower_wick_prev:.5f}")
            #     upper_wick = float(f"{upper_wick:.5f}")
            #     lower_wick = float(f"{lower_wick:.5f}")
            #     if (lower_wick_prev < lower_wick):
            #         print("43")
            #         return SIGNAL_SHORT, "43"
            #     else:
            #         print("44")
            #         return SIGNAL_NONE, "44"
            else:
                print("45")
                return SIGNAL_NONE, "45"

    
        else:
            return SIGNAL_NONE, "50"



