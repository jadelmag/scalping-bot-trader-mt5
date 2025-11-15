import MetaTrader5 as mt5
import sys
import os
import time
import threading
from datetime import datetime
from bot_console.candle_stick_strategy import CandleStickStrategy
from bot_console.logger import Logger
from bot_console.market_order import MarketSimulator
from offline.candle import CandleGeneratorOffline
from offline.candle_stick import CandleStickOffline

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_console.login import LoginMT5

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

logger = Logger()

def strategy_sticks(candle_generator, candle_stick_strategy, last_processed_candle):
    """
    Estrategia sticks.
    """
    last_prediction = None  # guarda la última predicción y su hora

    while True:
        logger.color_text(f"\n{'='*50}", "blue")
        logger.color_text(f"🕯️ NUEVA VELA INICIADA: ", "cyan")
        
        # Obtener el tiempo actual usando datetime
        candle_time = datetime.now()

        # Si teníamos una predicción anterior, verificar si fue correcta
        if last_prediction is not None:
            prev_signal, prev_time = last_prediction

            # Obtener la dirección real de la vela cerrada (la previa)
            real_signal = candle_generator.get_next_candle()

            # Comparar
            if real_signal == prev_signal:
                logger.color_text(f"✅ La señal anterior fue correcta para vela {prev_time.strftime('%H:%M:%S')} → {real_signal}", "green")
            else:
                if (real_signal == "NEUTRAL" or prev_signal == "NEUTRAL"):
                    logger.color_text(f"⚠️ Operación no realizada para vela {prev_time.strftime('%H:%M:%S')} → real={real_signal}, pred={prev_signal}", "yellow")
                else:
                    logger.color_text(f"❌ Señal incorrecta para vela {prev_time.strftime('%H:%M:%S')} → real={real_signal}, pred={prev_signal}", "red")

        # Obtener la señal para la nueva vela
        predicted_signal, num_operation = candle_stick_strategy.get_signal_for_new_candle()
        
        # Verificar si hemos llegado al final de los datos o hay un error
        if num_operation == "END":
            logger.color_text("✅ Se han procesado todas las velas del CSV", "green")
            break
        elif num_operation == "ERROR":
            logger.color_text("❌ Error al procesar las velas", "red")
            break
            
        logger.color_text(f"🔮Operacion: {num_operation} | Señal predicha para vela {candle_time.strftime('%H:%M:%S')}: {predicted_signal}", "yellow")

        # Guardar la predicción actual para comparar en la próxima iteración
        last_prediction = (predicted_signal, candle_time)

        # # Evitar procesar la misma vela múltiples veces
        # if last_processed_candle != candle_time:
        #     last_processed_candle = candle_time
        #     MarketSimulator.strategy_success_order(symbol=symbol, volume=VOLUME, signal=predicted_signal.upper())    
        # else:
        #     logger.color_text("⚠️ Vela ya procesada, evitando duplicado", "yellow")
        #     resume_logger.log({"message": "⚠️ Vela ya procesada, evitando duplicado", "type": "info"})

        time.sleep(60)

# Tu código principal modificado
VOLUME = 0.5
def main():
    """Función principal optimizada"""
    try:
        logger.color_text("🚀 Iniciando Bot de Trading EURUSD 1M", "blue")
        logger.color_text("🎯 Estrategia: Operar al inicio de nueva vela basado en patrón de vela cerrada", "blue")
        
        logger.color_text("✅ Trabajando offline", "green")

        # Inicializar modelo
        logger.color_text("🔄 Inicializando modelo...", "blue")
        candle_generator = CandleGeneratorOffline()
        candle_stick_strategy = CandleStickOffline()
        
        # Variable para controlar la última vela procesada
        last_processed_candle = None
        strategy_sticks(candle_generator, candle_stick_strategy, last_processed_candle)

    except Exception as e:
        logger.color_text(f"❌ Error: {e}", "red")

if __name__ == "__main__":
    main()
