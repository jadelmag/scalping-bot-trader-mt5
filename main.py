import MetaTrader5 as mt5
import sys
import os
import time
import threading
from datetime import datetime
from bot_console.predict_candle import CandleGenerator
from bot_console.candle_stick_strategy import CandleStickStrategy
from bot_console.logger import Logger
from bot_console.resumes import ResumeJsonL

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_console.login import LoginMT5
from bot_console.metatrader5 import MetaTrader5

# Configuración desde variables de entorno
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
symbol = os.getenv("SYMBOL", "EURUSD")
timeframe = timeframe_map.get(default_timeframe, mt5.TIMEFRAME_M1)

resume_logger = ResumeJsonL(f"main_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
logger = Logger()

def strategy_sticks(candle_generator, candle_stick_strategy, last_processed_candle):
    """
    Estrategia sticks.
    """
    while True:
        # Verificar si hay nueva vela
        new_candle, candle_time = candle_generator.check_new_candle()

        if new_candle:
            logger.color_text(f"\n{'='*50}", "blue")
            logger.color_text(f"🕯️ NUEVA VELA INICIADA: {candle_time.strftime('%H:%M:%S')}", "cyan")
            
            # Obtener la señal para la nueva vela
            signal = candle_stick_strategy.get_signal_for_new_candle()
            logger.color_text(f"Signal: {signal}", "blue")

            # Evitar procesar la misma vela múltiples veces
            # if last_processed_candle != candle_time:
            #     last_processed_candle = candle_time

            #     logger.color_text(f"🚀 Ejecutando operación {signal.upper()}...", "green")
            #     resume_logger.log({"message": f"🚀 Ejecutando operación {signal.upper()}...", "type": "info"})
            #     BearishHaramiSimulator.strategy_single_position(symbol=symbol, volume=VOLUME, signal=signal.upper())    
        # else:
        #     logger.color_text("⚠️ Vela ya procesada, evitando duplicado", "yellow")
        #     resume_logger.log({"message": "⚠️ Vela ya procesada, evitando duplicado", "type": "info"})

        time.sleep(1)

# Tu código principal modificado
VOLUME = 0.5
def main():
    """Función principal optimizada"""
    try:
        logger.color_text("🚀 Iniciando Bot de Trading EURUSD 1M", "blue")
        logger.color_text("🎯 Estrategia: Operar al inicio de nueva vela basado en patrón de vela cerrada", "blue")
        
        login = LoginMT5()
        connected = login.login()
        
        if not connected:
            logger.color_text("❌ No se pudo conectar a MetaTrader 5.", "red")
            return
        
        logger.color_text("✅ Conectado a MetaTrader 5", "green")
        
        mt5_client = MetaTrader5()
        # mt5_client.getGlobalInfo()

        # Inicializar modelo
        logger.color_text("🔄 Inicializando modelo...", "blue")
        candle_generator = CandleGenerator(symbol=symbol)
        candle_stick_strategy = CandleStickStrategy(symbol=symbol)
        
        # Variable para controlar la última vela procesada
        last_processed_candle = None
        strategy_sticks(candle_generator, candle_stick_strategy, last_processed_candle)

    except Exception as e:
        logger.color_text(f"❌ Error: {e}", "red")
        resume_logger.log({"message": f"❌ Error: {e}", "type": "error"})
    finally:
        logger.color_text("🔴 Bot finalizado", "red")
        resume_logger.log({"message": "🔴 Bot finalizado", "type": "info"})

if __name__ == "__main__":
    main()
