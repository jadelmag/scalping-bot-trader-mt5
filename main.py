import MetaTrader5 as mt5
import sys
import os
import time
import threading
from datetime import datetime
from bot_console.strategies.single_position import SinglePositionSimulator
from bot_console.predict_candle.predict_candle import EURUSD1MPredictor

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_console.login.login import LoginMT5
from bot_console.metatrader5.metatrader5 import MetaTrader5

# Configuración desde variables de entorno
symbol = os.getenv("SYMBOL", "EURUSD")
volume = os.getenv("VOLUME", "0.01")
timeframe_map = {
    "1": mt5.TIMEFRAME_M1,
    "5": mt5.TIMEFRAME_M5,
    "15": mt5.TIMEFRAME_M15,
    "30": mt5.TIMEFRAME_M30,
    "60": mt5.TIMEFRAME_H1,
    "240": mt5.TIMEFRAME_H4,
    "1440": mt5.TIMEFRAME_D1
}
default_timeframe = os.getenv("TIMEFRAME", "1")
timeframe = timeframe_map.get(default_timeframe, mt5.TIMEFRAME_M1)

# Tu código principal modificado
def main():
    """Función principal optimizada"""
    try:
        print("🚀 Iniciando Bot de Trading EURUSD 1M")
        print("🎯 Modo: Solo señales SHORT/LONG con alta confianza")
        
        login = LoginMT5()
        connected = login.login()
        
        if not connected:
            print("❌ No se pudo conectar a MetaTrader 5.")
            return
        
        print("✅ Conectado a MetaTrader 5")
        
        mt5_client = MetaTrader5()
        mt5_client.getGlobalInfo()

        # Inicializar modelo
        print("🔄 Inicializando modelo...")
        predictor = EURUSD1MPredictor()

        while True:            
            new_candle, candle_time = predictor.check_new_candle()
            
            if new_candle:
                print(f"\n{'='*50}")
                print(f"🕯️ Vela: {candle_time.strftime('%H:%M:%S')}")

                # Ejecutar estrategia
                SinglePositionSimulator.strategy_single_position(
                    symbol=symbol, 
                    volume=volume,
                )
                
                print(f"{'='*50}")
            
            time.sleep(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔴 Bot finalizado")

if __name__ == "__main__":
    main()
