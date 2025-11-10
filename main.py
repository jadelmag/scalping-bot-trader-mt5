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


# Instancia global
predictor = EURUSD1MPredictor()

def predict_signal():
    """Función de predicción optimizada"""
    signal = predictor.predict_next_candle()
    
    if signal:
        print(f"\n🎯 NUEVA PREDICCIÓN:")
        print(f"   Señal: {signal['prediction'].upper()}")
        print(f"   Confianza: {signal['confidence']:.1%}")
        print(f"   Acción: {signal['action']}")
        print(f"   Probabilidades:")
        for cls, prob in signal['probabilities'].items():
            print(f"     {cls}: {prob:.1%}")
        
        return signal['prediction']
    else:
        print("❌ No se pudo obtener predicción")
        return 'neutral'


# Variables globales para control

# Tu código principal modificado
def main():
    """Función principal optimizada"""
    try:
        print("🚀 Iniciando Bot de Trading...")
        login = LoginMT5()
        connected = login.login()
        
        if not connected:
            print("❌ No se pudo conectar a MetaTrader 5.")
            return
        
        print("✅ Conectado a MetaTrader 5 correctamente.")
        
        mt5_client = MetaTrader5()
        mt5_client.getGlobalInfo()

        # Inicializar modelo
        print("🔄 Inicializando modelo de predicción...")
        if not predictor.train_model():
            print("❌ No se pudo entrenar el modelo")
            return

        print("✅ Modelo listo. Monitoreando velas en tiempo real...")
        print("⏰ Esperando nuevas velas...")
        
        while True:            
            # Verificar nueva vela con nuestro método optimizado
            new_candle, candle_time = predictor.check_new_candle()
            
            if new_candle:
                print(f"\n{'='*60}")
                print(f"🕯️ NUEVA VELA DETECTADA: {candle_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                
                # Pequeña pausa para asegurar que la vela está completa
                time.sleep(1)
                
                # Predecir señal
                signal = predict_signal()
                
                if signal == 'neutral':
                    print("🟡 No se abre operación (neutral).")
                    continue
                else:
                    # Ejecutar estrategia
                    SinglePositionSimulator.strategy_single_position(
                        symbol="EURUSD", 
                        volume=0.01, 
                        signal=signal
                    )
                
                print(f"\n⏳ Esperando siguiente vela...")
            else:
                # Verificación más frecuente pero con mensaje solo ocasional
                if int(time.time()) % 30 == 0:  # Mostrar cada 30 segundos
                    current_candle, current_time = predictor.get_current_candle_data()
                    if current_time:
                        print(f"⏰ Vela actual: {current_time.strftime('%H:%M:%S')} - Esperando nueva vela...", end='\r')
                
                time.sleep(1)  # Verificar cada segundo
        
    except Exception as e:
        print(f"❌ Error en la aplicación: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    finally:
        print("🔴 Bot finalizado")

if __name__ == "__main__":
    main()