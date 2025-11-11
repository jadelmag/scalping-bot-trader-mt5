import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

class CandleStick:
    def __init__(self, symbol, timeframe):
        """
        candles: lista de diccionarios, cada uno con 'open', 'high', 'low', 'close'
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.candles = mt5.copy_rates_from_pos(symbol, timeframe, 0, 10)
    
    def is_bullish_harami(self, i):
        """Detecta patrón bullish harami en la vela i y la anterior (i-1)."""
        if i == 0:
            return False  # No hay vela anterior
        
        prev = self.candles[i-1]
        curr = self.candles[i]
        
        # 1) Primera vela grande bajista
        if not (prev['open'] > prev['close']):
            return False
        
        # 2) Segunda vela pequeña alcista dentro del cuerpo de la anterior
        if not (curr['close'] > curr['open']):
            return False
        
        # Verificamos que la segunda vela esté contenida dentro del cuerpo de la primera
        high_body = max(prev['open'], prev['close'])
        low_body = min(prev['open'], prev['close'])
        
        if (curr['open'] >= low_body and curr['open'] <= high_body and
            curr['close'] >= low_body and curr['close'] <= high_body):
            return True
        
        return False
    
    def is_bearish_harami(self, i):
        """Detecta patrón bearish harami en la vela i y la anterior (i-1)."""
        if i == 0:
            return False
        
        prev = self.candles[i-1]
        curr = self.candles[i]
        
        # 1) Primera vela grande alcista
        if not (prev['close'] > prev['open']):
            return False
        
        # 2) Segunda vela pequeña bajista dentro del cuerpo de la anterior
        if not (curr['open'] > curr['close']):
            return False
        
        high_body = max(prev['open'], prev['close'])
        low_body = min(prev['open'], prev['close'])
        
        if (curr['open'] >= low_body and curr['open'] <= high_body and
            curr['close'] >= low_body and curr['close'] <= high_body):
            return True
        
        return False

    def update(self, candles=10):
        """Actualiza los datos de las velas desde MetaTrader 5"""
        try:
            rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, candles)
            if rates is not None and len(rates) > 0:
                self.candles = rates
                return True
            else:
                return False
        except Exception as e:
            return False

    # ------------------- DETECCIÓN PRINCIPAL MEJORADA -------------------

    def get_signal_for_new_candle(self):
        """
        Devuelve la señal basada en el patrón de la vela más reciente.
        
        Returns:
            str: "long" si es bullish_harami, "short" si es bearish_harami, "neutral" si no es ninguno
        """
        # 1. Actualizar datos de las velas desde MetaTrader 5
        if not self.update():
            return "neutral"  # Si no se pueden obtener datos, retornar neutral
        
        # 2. Verificar que tenemos suficientes velas para analizar
        if len(self.candles) < 2:
            return "neutral"
        
        # Analizar la vela más reciente (última posición del array)
        last_index = len(self.candles) - 1
        
        # 3. Comprobar si es bullish_harami
        if self.is_bullish_harami(last_index):
            return "long"
        
        # 4. Comprobar si es bearish_harami
        if self.is_bearish_harami(last_index):
            return "short"
        
        # 5. Si no es ninguno de los dos, devolver neutral
        return "neutral"