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

class CandleStickOffline:
    def __init__(self):
        self.pos_current_candle = 0
        self.candles = None
        self.num_candles = 0

        self.get_candles_from_csv()

    def get_candles_from_csv(self):
        """Carga las velas desde charts.csv"""
        self.candles = pd.read_csv("offline/csv/chart.csv")
        self.num_candles = len(self.candles)

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
            # Para pandas Series, usar bracket notation con nombres capitalizados
            close_price = candle['Close'] if 'Close' in candle else candle.get('close')
            open_price = candle['Open'] if 'Open' in candle else candle.get('open')
            
            if close_price is None or open_price is None:
                return SIGNAL_NONE
                
            if close_price > open_price:
                return SIGNAL_LONG
            elif close_price < open_price:
                return SIGNAL_SHORT
            return SIGNAL_NONE
            
        except (KeyError, AttributeError, TypeError) as e:
            print(f"Error getting signal from candle: {e}")
            return SIGNAL_NONE

    def get_trend(self):
        """
        Obtiene el tendencia de las últimas dos velas cerradas
        """
        try:
            # Usar las velas ya obtenidas en get_signal_for_new_candle
            # En lugar de obtener nuevas velas que podrían cambiar la posición
            current_pos = self.pos_current_candle - 1  # Restar 1 porque ya se incrementó en get_penultimate_candle
            
            if current_pos < 0 or current_pos + 1 >= self.num_candles:
                return TREND_NEUTRAL
                
            penultimate_candle = self.candles.iloc[current_pos]
            last_candle = self.candles.iloc[current_pos + 1]
                
            # Para pandas Series, usar bracket notation
            last_close = last_candle['Close'] if 'Close' in last_candle else last_candle['close']
            penult_close = penultimate_candle['Close'] if 'Close' in penultimate_candle else penultimate_candle['close']

            if last_close > penult_close:
                return TREND_UP
            elif last_close < penult_close:
                return TREND_DOWN
            else:
                return TREND_NEUTRAL
                
        except (KeyError, AttributeError, TypeError, IndexError) as e:
            print(f"Error getting trend: {e}")
            return TREND_NEUTRAL

    def get_sticks_from_candle(self, candle, last: bool = False):
        """
        Obtiene las mechas y datos de la última vela cerrada
        """
        if candle is None:
            print("Error: candle is None")
            return None, None, False, False, 0, 0, 0, 0, 0, SIGNAL_NONE
            
        try:
            # Para pandas Series, usar bracket notation con nombres capitalizados
            open_price = candle['Open'] if 'Open' in candle else candle.get('open', 0)
            high_price = candle['High'] if 'High' in candle else candle.get('high', 0)
            low_price = candle['Low'] if 'Low' in candle else candle.get('low', 0)
            close_price = candle['Close'] if 'Close' in candle else candle.get('close', 0)
            
            if any(price == 0 for price in [open_price, high_price, low_price, close_price]):
                print(f"Error: Missing price data in candle: {candle}")
                return None, None, False, False, 0, 0, 0, 0, 0, SIGNAL_NONE
                
        except (KeyError, AttributeError, TypeError) as e:
            print(f"Error accessing candle data: {e}")
            print(f"Candle type: {type(candle)}")
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

        info = {
            "ultima_vela": "Última vela:" if last else "Penúltima vela:",
            "upper_wick": upper_wick,
            "lower_wick": lower_wick,
            "has_upper_wick": has_upper_wick,
            "has_lower_wick": has_lower_wick,
            "low_price": low_price,
            "high_price": high_price,
            "close_price": close_price,
            "open_price": open_price,
            "body": body,
            "signal": signal
        }

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
        # AVANZAR LA VELA AHORA
        if self.pos_current_candle >= self.num_candles:
            return "END", "END"

        # Usar las velas actuales
        penultimate_candle = self.get_penultimate_candle()
        last_candle = self.get_last_candle()

        # avanzar a la siguiente para la próxima llamada
        self.pos_current_candle += 1
            
        trend = self.get_trend()

        upper_wick_prev, lower_wick_prev, has_upper_wick_prev, has_lower_wick_prev, low_price_prev, high_price_prev, close_price_prev, open_price_prev, body_prev, signal_prev = self.get_sticks_from_candle(penultimate_candle, False)

        upper_wick, lower_wick, has_upper_wick, has_lower_wick, low_price, high_price, close_price, open_price, body, signal = self.get_sticks_from_candle(last_candle, True)

        print(f"Tendencia: {trend}")
        resume_logger.log({"message": f"Tendencia: {trend}", "type": "info"})
        resume_logger.log({"message": f"\n{'='*50}", "type": "info"})

        # --- Tiene mecha superior e inferior, la diferencia entre mechas es pequeña y se cierra con el mismo precio

        if (has_upper_wick and has_lower_wick and open_price == close_price):
            if (lower_wick < upper_wick):
                print("01")
                return SIGNAL_SHORT, "01"
            elif (lower_wick > upper_wick):
                print("02")
                return SIGNAL_LONG, "02"
            else:
                if (body == 0):
                    print("03A")
                    return SIGNAL_LONG, "03A"
                else:
                    print("03B")
                    return SIGNAL_SHORT, "03B"
        
        # --- Tienen mecha superior e inferior

        elif (has_upper_wick and has_lower_wick):
            if (upper_wick > lower_wick * 2) and trend == TREND_DOWN:
                print("04")
                return SIGNAL_SHORT, "04"
            elif (upper_wick > lower_wick * 2) and trend == TREND_UP:
                print("05")
                return SIGNAL_LONG, "05"
            elif (upper_wick * 2 < lower_wick) and trend == TREND_DOWN:
                print("06")
                return SIGNAL_SHORT, "06"
            elif (upper_wick * 2 < lower_wick) and trend == TREND_UP:
                print("07")
                return SIGNAL_LONG, "07"
            elif (upper_wick > lower_wick) and trend == TREND_UP:
                print("08")
                return SIGNAL_LONG, "08"
            elif (upper_wick < lower_wick) and trend == TREND_DOWN:
                print("09")
                return SIGNAL_SHORT, "09"
            elif (upper_wick > lower_wick) and trend == TREND_DOWN:
                print("10")
                return SIGNAL_SHORT, "10"
            elif (upper_wick < lower_wick) and trend == TREND_UP:
                print("11")
                return SIGNAL_LONG, "11" 
            elif (upper_wick < lower_wick) and trend == TREND_NEUTRAL:
                print("12")
                return SIGNAL_LONG, "12" 
            elif (upper_wick > lower_wick) and trend == TREND_NEUTRAL:
                print("13")
                return SIGNAL_SHORT, "13"
            else:
                print("14")
                return SIGNAL_SHORT, "14"
                
        # --- No tiene mecha superior ni inferior

        elif (not has_upper_wick and not has_lower_wick):
            if lower_wick >= body * 2 and trend == TREND_DOWN:
                print("20")
                return SIGNAL_SHORT, "20"
            elif lower_wick >= body * 2 and trend == TREND_UP:
                print("21")
                return SIGNAL_LONG, "21"
            elif (body > body_prev) and trend == TREND_UP:
                print("22")
                return SIGNAL_SHORT, "22"
            elif (body > body_prev) and trend == TREND_DOWN:
                print("23")
                return SIGNAL_LONG, "23"
            else:
                print(f"24")
                return SIGNAL_SHORT, "24"

        # --- Tienen mecha superior y no mecha inferior

        elif (has_upper_wick and not has_lower_wick):
            if upper_wick >= 0.00010 and trend == TREND_DOWN:
                print("30")
                return SIGNAL_SHORT, "30"
            elif upper_wick >= 0.00010 and trend == TREND_UP:
                print("31")
                return SIGNAL_LONG, "31"
            elif upper_wick == 0.00001 and trend == TREND_DOWN:
                print("32")
                return SIGNAL_SHORT, "32"
            elif upper_wick == 0.00001 and trend == TREND_UP:
                print("33")
                return SIGNAL_LONG, "33"
            elif upper_wick >= body * 2 and trend == TREND_UP:
                print("34")
                return SIGNAL_SHORT, "34"
            elif upper_wick >= body * 2 and trend == TREND_DOWN:
                print("35")
                return SIGNAL_LONG, "35"
            elif (body > body_prev) and trend == TREND_UP:
                print("36")
                return SIGNAL_SHORT, "36"
            elif (body > body_prev) and trend == TREND_DOWN:
                print("37")
                return SIGNAL_LONG, "37"
            else:
                print("38")
                return SIGNAL_SHORT, "38"


        # --- No tiene mecha superior y tienen mecha inferior

        elif (not has_upper_wick and has_lower_wick):
            if lower_wick >= 0.00010 and trend == TREND_DOWN:
                print("40")
                return SIGNAL_LONG, "40"
            elif lower_wick >= 0.00010 and trend == TREND_UP:
                print("41")
                return SIGNAL_SHORT, "41"
            elif lower_wick == 0.00001 and trend == TREND_DOWN:
                print("42")
                return SIGNAL_SHORT, "42"
            elif lower_wick == 0.00001 and trend == TREND_UP:
                print("43")
                return SIGNAL_LONG, "43"
            elif lower_wick >= body * 2 and trend == TREND_UP:
                print("44")
                return SIGNAL_LONG, "44"
            elif lower_wick >= body * 2 and trend == TREND_DOWN:
                print("45")
                return SIGNAL_SHORT, "45"
            elif (body > body_prev) and trend == TREND_UP:
                print("46")
                return SIGNAL_SHORT, "46"
            elif (body > body_prev) and trend == TREND_DOWN:
                print("47")
                return SIGNAL_LONG, "47"
            else:
                print("48")
                return SIGNAL_SHORT, "48"
    
        else:
            print("50")
            return SIGNAL_NONE, "50"
