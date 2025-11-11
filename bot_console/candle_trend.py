import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timedelta

class CandleTrend:
    def __init__(self, symbol, timeframe):
        """
        candles: lista de diccionarios, cada uno con 'open', 'high', 'low', 'close'
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.candles = mt5.copy_rates_from_pos(symbol, timeframe, 0, 10)

    def calculate_trend(self, num_candles):
        """
        Determines the market trend (uptrend, downtrend, or sideways)
        based solely on the closing prices of the last candles.
        """
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, num_candles)
        if rates is None or len(rates) < num_candles:
            print("Failed to retrieve candles")
            return None

        closing_prices = np.array([candle['close'] for candle in rates])
        x = np.arange(len(closing_prices))
        slope = np.polyfit(x, closing_prices, 1)[0]

        # Adaptive threshold (0.01% of average price)
        avg_price = np.mean(closing_prices)
        threshold = avg_price * 0.00001  # 0.001% of average price

        if slope > threshold:
            trend = "uptrend"
        elif slope < -threshold:
            trend = "downtrend"
        else:
            trend = "sideways"

        print(f"closes: {closing_prices}")
        return trend

    # ------------------- DETECCIÓN PRINCIPAL MEJORADA -------------------

    def get_trend_with_new_candle(self):
        """
        Devuelve la tendencia basada en el patrón de la vela más reciente.
        
        Returns:
            str: "uptrend" | "downtrend" | "sideways"
        """
        trend = self.calculate_trend(num_candles=4)
        return trend