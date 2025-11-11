import MetaTrader5 as mt5
import sys
import os
import time
import threading
from datetime import datetime
from bot_console.single_position import SinglePositionSimulator
from bot_console.predict_candle import CandleGenerator
from bot_console.candle_stick import CandleStick
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

# Tu código principal modificado
VOLUME = 0.5
def main():
    """Función principal optimizada"""
    try:
        logger.color_text("🚀 Iniciando Bot de Trading EURUSD 1M", "blue")
        resume_logger.log("🚀 Iniciando Bot de Trading EURUSD 1M")
        logger.color_text("🎯 Modo: Solo señales SHORT/LONG con alta confianza", "blue")
        resume_logger.log("🎯 Modo: Solo señales SHORT/LONG con alta confianza")
        
        login = LoginMT5()
        connected = login.login()
        
        if not connected:
            logger.color_text("❌ No se pudo conectar a MetaTrader 5.", "red")
            resume_logger.log("❌ No se pudo conectar a MetaTrader 5.")
            return
        
        logger.color_text("✅ Conectado a MetaTrader 5", "green")
        resume_logger.log("✅ Conectado a MetaTrader 5")
        
        mt5_client = MetaTrader5()
        mt5_client.getGlobalInfo()

        # Inicializar modelo
        logger.color_text("🔄 Inicializando modelo...", "blue")
        resume_logger.log("🔄 Inicializando modelo...")
        candle_generator = CandleGenerator(symbol=symbol)
        candle_stick = CandleStick(symbol=symbol)

        while True:            
            # luego en el loop
            new_candle, candle_time = candle_generator.check_new_candle()

            if new_candle:
                signal, pattern = candle_stick.get_type_signal_when_candle_finish()
                logger.color_text(f"🕯️ Vela anterior -> SEÑAL: {signal} -> PATRÓN: {pattern}", "blue")
                resume_logger.log(f"🕯️ Vela anterior -> SEÑAL: {signal} -> PATRÓN: {pattern}")

                logger.color_text(f"\n{'='*50}", "blue")
                resume_logger.log(f"\n{'='*50}")
                logger.color_text(f"🕯️ Vela: {candle_time.strftime('%H:%M:%S')}", "blue")
                resume_logger.log(f"🕯️ Vela: {candle_time.strftime('%H:%M:%S')}")
                
                signal = candle_stick.predict_short_or_long_candle()
                logger.color_text(f"Signal: {signal}", "blue")
                resume_logger.log(f"Signal: {signal}")
                # Ejecutar estrategia
                # SinglePositionSimulator.strategy_single_position(symbol=symbol, volume=VOLUME, signal=signal)
                
                logger.color_text(f"{'='*50}", "blue")
                resume_logger.log(f"{'='*50}")
            
            time.sleep(1)
        
    except Exception as e:
        logger.color_text(f"❌ Error: {e}", "red")
        resume_logger.log(f"❌ Error: {e}")
    finally:
        logger.color_text("🔴 Bot finalizado", "red")
        resume_logger.log("🔴 Bot finalizado")

if __name__ == "__main__":
    main()
