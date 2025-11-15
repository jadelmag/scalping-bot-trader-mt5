import MetaTrader5 as mt5
import sys
import os
import io
import time
import threading
from datetime import datetime
from bot_console.candle_stick_strategy import CandleStickStrategy
from bot_console.logger import Logger
from bot_console.market_order import MarketSimulator
from offline.candle import CandleGeneratorOffline
from offline.candle_stick import CandleStickOffline
from bot_console.login import LoginMT5

# Configurar stdout para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
file_path_chart = "offline/csv/chart.csv"
file_path_chart_year = "offline/csv_years/DATA_M1_2024.csv"


logger = Logger()

def strategy_sticks(candle_generator, candle_stick_strategy, last_processed_candle):
    """
    Estrategia sticks.
    """
    last_prediction = None  # guarda la última predicción y su hora

    num_success = 0
    num_fails = 0
    num_neutral = 0

    while True:
        print(f"\n=== ITERACIÓN DEL BUCLE - {datetime.now()} ===")
        sys.stdout.flush()
        
        logger.color_text(f"\n{'='*50}", "blue")
        logger.color_text(f"🕯️ NUEVA VELA INICIADA: ", "cyan")
        
        # Obtener el tiempo actual usando datetime
        candle_time = datetime.now()
        print(f"Tiempo de vela: {candle_time}")
        sys.stdout.flush()

        # Si teníamos una predicción anterior, verificar si fue correcta
        if last_prediction is not None:
            prev_signal, prev_time = last_prediction

            # Obtener la dirección real de la vela cerrada (la previa)
            real_signal = candle_generator.get_next_candle()

            # Comparar
            if real_signal == prev_signal:
                logger.color_text(f"✅ La señal anterior fue correcta para vela {prev_time.strftime('%H:%M:%S')} → {real_signal}", "green")
                num_success += 1
            else:
                if (real_signal == "NEUTRAL" or prev_signal == "NEUTRAL"):
                    logger.color_text(f"⚠️ Operación no realizada para vela {prev_time.strftime('%H:%M:%S')} → real={real_signal}, pred={prev_signal}", "yellow")
                    num_neutral += 1
                else:
                    logger.color_text(f"❌ Señal incorrecta para vela {prev_time.strftime('%H:%M:%S')} → real={real_signal}, pred={prev_signal}", "red")
                    num_fails += 1

        # Obtener la señal para la nueva vela
        predicted_signal, num_operation = candle_stick_strategy.get_signal_for_new_candle()
        
        # Verificar si hemos llegado al final de los datos o hay un error
        if num_operation == "END":
            logger.color_text("✅ Se han procesado todas las velas del CSV", "green")
            logger.color_text(f"================== RESUMEN ============================", "blue")
            logger.color_text(f"✅ Operaciones Correctas: {num_success} ", "green")
            logger.color_text(f"❌ Operaciones Incorrectas: {num_fails} ", "red")
            logger.color_text(f"⚠️ Operaciones No Realizadas: {num_neutral} ", "yellow")
            logger.color_text(f"=======================================================", "blue")
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

        time.sleep(5)

# Tu código principal modificado
VOLUME = 0.5
def main():
    """Función principal optimizada"""
    print("=== INICIANDO MAINOFF.PY ===")
    sys.stdout.flush()
    
    try:
        print("Antes de logger.color_text")
        logger.color_text("🚀 Iniciando Bot de Trading EURUSD 1M", "blue")
        logger.color_text("🎯 Estrategia: Operar al inicio de nueva vela basado en patrón de vela cerrada", "blue")
        
        logger.color_text("✅ Trabajando offline", "green")
        print("Después de mensajes iniciales")
        sys.stdout.flush()

        # Inicializar modelo
        logger.color_text("🔄 Inicializando modelo...", "blue")
        print(f"Cargando archivo: {file_path_chart}")
        sys.stdout.flush()
        
        candle_generator = CandleGeneratorOffline(file_path_chart)
        print("CandleGeneratorOffline creado")
        sys.stdout.flush()
        
        candle_stick_strategy = CandleStickOffline(file_path_chart)
        print("CandleStickOffline creado")
        sys.stdout.flush()
        
        # Variable para controlar la última vela procesada
        last_processed_candle = None
        print("Iniciando strategy_sticks...")
        sys.stdout.flush()
        
        strategy_sticks(candle_generator, candle_stick_strategy, last_processed_candle)

    except Exception as e:
        print(f"ERROR EN MAIN: {e}")
        import traceback
        traceback.print_exc()
        logger.color_text(f"❌ Error: {e}", "red")

if __name__ == "__main__":
    main()
