import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import MetaTrader5 as mt5
from datetime import datetime
import time

class EURUSD1MPredictor:
    def __init__(self):
        self.last_candle_time = None
        
    def get_current_candle_data(self):
        """Obtener datos de la vela actual"""
        try:
            if not mt5.initialize():
                return None, None
                
            rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M1, 0, 2)
            mt5.shutdown()
            
            if rates is None or len(rates) < 2:
                return None, None
                
            current_candle = rates[-1]
            current_time = datetime.fromtimestamp(current_candle['time'])
            
            return current_candle, current_time
            
        except Exception as e:
            return None, None
    
    def check_new_candle(self):
        """Verificar si hay una vela nueva"""
        current_candle, current_time = self.get_current_candle_data()
        
        if current_candle is None or current_time is None:
            return False, None
        
        if self.last_candle_time is None:
            self.last_candle_time = current_time
            return True, current_time
        
        if current_time != self.last_candle_time:
            self.last_candle_time = current_time
            return True, current_time
        
        return False, current_time
    