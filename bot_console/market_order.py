import time
import pandas as pd
import MetaTrader5 as mt5
from bot_console.resumes import ResumeJsonL
from bot_console.logger import Logger
from datetime import datetime

LONG = "LONG"
SHORT = "SHORT"
NEUTRAL = "NEUTRAL"

logger = Logger()
resume_logger = ResumeJsonL(f"strategy_single_position_{datetime.now().strftime('%Y%m%d_%H%M%S')}")


class MarketOrder:
    """Representa una operación abierta (simulada)."""
    def __init__(self, symbol, order_type, price_open, volume, sl_price, tp_price, position_id):
        self.symbol = symbol
        self.type = order_type  # "long" o "short"
        self.price_open = price_open
        self.volume = volume
        self.sl = sl_price      # Precio de stop loss
        self.tp = tp_price      # Precio de take profit
        self.open_time = time.time()
        self.closed = False
        self.price_close = None
        self.profit = 0.0
        self.position_id = position_id

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "type": self.type,
            "price_open": self.price_open,
            "volume": self.volume,
            "sl": self.sl,
            "tp": self.tp,
            "open_time": self.open_time,
            "closed": self.closed,
            "price_close": self.price_close,
            "profit": self.profit,
            "position_id": self.position_id
        }


class MarketSimulator:
    """
    Estrategia de posición simulada
    """
    open_positions = []

    @staticmethod
    def strategy_success_order(symbol: str="EURUSD", volume: float=0.01, signal: str="NEUTRAL"):
        """
        Ejecuta la estrategia de posición simulada.
        """
        logger.color_text(f"🚀 Ejecutando operación {signal.upper()}...", "green")
        resume_logger.log({"message": f"🚀 Ejecutando operación {signal.upper()}...", "type": "info"})
        
        if signal == LONG:
            MarketSimulator.open_long(symbol, volume)
        elif signal == SHORT:
            MarketSimulator.open_short(symbol, volume)
        else:
            logger.color_text(f"Señal: {signal} | No se abre operación", "yellow")
            resume_logger.log({"message": f"Señal: {signal} | No se abre operación", "type": "info"})
            return
        
        MarketSimulator.monitor_positions(symbol)

    # ------------------- Funciones short, long and close -------------------

    @staticmethod
    def open_long(symbol, volume, sl_pips=200, tp_pips=300):
        """Abre una operación real de compra (LONG) en MT5."""
        try:
            # Obtener información actual del símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.color_text(f"❌ No se pudo obtener información para {symbol}", "red")
                resume_logger.log({"message": f"❌ No se pudo obtener información para {symbol}", "type": "error"})
                return False
            
            # Verificar si el símbolo está disponible para trading
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    logger.color_text(f"❌ No se puede seleccionar {symbol}", "red")
                    resume_logger.log({"message": f"❌ No se puede seleccionar {symbol}", "type": "error"})
                    return False
            
            # Obtener el precio actual
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.color_text(f"❌ No se pudo obtener el tick para {symbol}", "red")
                resume_logger.log({"message": f"❌ No se pudo obtener el tick para {symbol}", "type": "error"})
                return False
            
            # Calcular SL y TP
            point = symbol_info.point
            price_open = tick.ask  # Para compras usamos el precio ASK
            
            sl_price = price_open - sl_pips * point
            tp_price = price_open + tp_pips * point
            
            # Preparar la orden
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price_open,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 12345,
                "comment": "Bot LONG",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            # Enviar la orden
            result = mt5.order_send(request)

            if result is None:
                last_error = mt5.last_error()
                logger.color_text(f"❌ Error: No se pudo enviar la orden. MT5 Error: {last_error}", "red")
                resume_logger.log({"message": f"❌ Error: No se pudo enviar la orden. MT5 Error: {last_error}", "type": "error"})
                return False

            order = MarketOrder(symbol, "long", price_open, volume, sl_price, tp_price, position_id=result.order)
            MarketSimulator.open_positions.append(order)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.color_text(f"❌ Error al abrir LONG: {result.retcode} | msj: {result.comment}", "red")
                resume_logger.log({"message": f"❌ Error al abrir LONG: {result.retcode} | msj: {result.comment}", "type": "error"})
                return False
            else:
                logger.color_text(f"✅ LONG abierto | Ticket: {result.order} | {symbol} @ {price_open:.5f}", "green")
                resume_logger.log({"message": f"✅ LONG abierto | Ticket: {result.order} | {symbol} @ {price_open:.5f}", "type": "success"})
                logger.color_text(f"✅ SL: {sl_price:.5f} | TP: {tp_price:.5f} | Volumen: {volume}", "green")
                resume_logger.log({"message": f"✅ SL: {sl_price:.5f} | TP: {tp_price:.5f} | Volumen: {volume}", "type": "success"})
                return True
                
        except Exception as e:
            logger.color_text(f"❌ Error en open_long: {e}", "red")
            resume_logger.log({"message": f"❌ Error en open_long: {e}", "type": "error"})
            return False

    @staticmethod
    def open_short(symbol, volume, sl_pips=200, tp_pips=300):
        """Abre una operación real de venta (SHORT) en MT5."""
        try:
            # Obtener información actual del símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.color_text(f"❌ No se pudo obtener información para {symbol}", "red")
                resume_logger.log({"message": f"❌ No se pudo obtener información para {symbol}", "type": "error"})
                return False
            
            # Verificar si el símbolo está disponible para trading
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    logger.color_text(f"❌ No se puede seleccionar {symbol}", "red")
                    resume_logger.log({"message": f"❌ No se puede seleccionar {symbol}", "type": "error"})
                    return False
            
            # Obtener el precio actual usando el módulo mt5 directamente
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.color_text(f"❌ No se pudo obtener el tick para {symbol}", "red")
                resume_logger.log({"message": f"❌ No se pudo obtener el tick para {symbol}", "type": "error"})
                return False
            
            # Calcular SL y TP
            point = symbol_info.point
            price_open = tick.bid  # Para ventas usamos el precio BID
            
            sl_price = price_open + sl_pips * point
            tp_price = price_open - tp_pips * point
            
            # Preparar la orden
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": price_open,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 12345,
                "comment": "Bot SHORT",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            # Enviar la orden
            result = mt5.order_send(request)
            
            if result is None:
                last_error = mt5.last_error()
                logger.color_text(f"❌ Error: No se pudo enviar la orden. MT5 Error: {last_error}", "red")
                resume_logger.log({"message": f"❌ Error: No se pudo enviar la orden. MT5 Error: {last_error}", "type": "error"})
                return False
                
            order = MarketOrder(symbol, "short", price_open, volume, sl_price, tp_price, position_id=result.order)
            MarketSimulator.open_positions.append(order)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.color_text(f"❌ Error al abrir SHORT: {result.retcode} | msj: {result.comment}", "red")
                resume_logger.log({"message": f"❌ Error al abrir SHORT: {result.retcode} | msj: {result.comment}", "type": "error"})
                return False
            else:
                logger.color_text(f"✅ SHORT abierto | Ticket: {result.order} | {symbol} @ {price_open:.5f}", "green")
                resume_logger.log({"message": f"✅ SHORT abierto | Ticket: {result.order} | {symbol} @ {price_open:.5f}", "type": "success"})
                logger.color_text(f"✅ SL: {sl_price:.5f} | TP: {tp_price:.5f} | Volumen: {volume}", "green")
                resume_logger.log({"message": f"✅ SL: {sl_price:.5f} | TP: {tp_price:.5f} | Volumen: {volume}", "type": "success"})
                return True
                
        except Exception as e:
            logger.color_text(f"❌ Error en open_short: {e}", "red")
            resume_logger.log({"message": f"❌ Error en open_short: {e}", "type": "error"})
            return False

    @staticmethod
    def close_position(order):
        """Cierra una operación en MetaTrader 5."""
        # Primero, cierra la posición en MT5
        symbol = order.symbol
        close_price = mt5.symbol_info_tick(symbol).ask if order.type.upper() == "LONG" else mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_SELL if order.type.upper() == "LONG" else mt5.ORDER_TYPE_BUY

        # Crear la solicitud de cierre
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": order.position_id,
            "symbol": symbol,
            "volume": order.volume,
            "type": type,
            "price": close_price,
            "deviation": 20,
            "magic": order.magic if hasattr(order, 'magic') else 100,
            "comment": "Cierre posición",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Enviar la solicitud de cierre
        result = mt5.order_send(close_request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.color_text(f"❌ Error al cerrar posición: {result.retcode} | {result.comment}", "red")
            resume_logger.log({"message": f"❌ Error al cerrar posición: {result.retcode} | {result.comment}", "type": "error"})
            return False

        order.closed = True
        order.price_close = close_price
        order.close_time = mt5.symbol_info_tick(symbol).time if mt5.symbol_info_tick(symbol) else None

        logger.color_text(f"✅ Cierre REAL {order.type.upper()} @ {close_price:.5f} | Profit: {order.profit:.2f} USD", "green")
        resume_logger.log({"message": f"✅ Cierre REAL {order.type.upper()} @ {close_price:.5f} | Profit: {order.profit:.2f} USD", "type": "success"})
        return True

    @staticmethod
    def clear_positions():
        """Limpia las posiciones abiertas."""
        # Limpiar posiciones cerradas y retornar para nueva simulación
        MarketSimulator.open_positions = [pos for pos in MarketSimulator.open_positions if not pos.closed]
        
        logger.color_text("🔄 Preparando nueva simulación...\n", "blue")
        resume_logger.log({"message": "🔄 Preparando nueva simulación...\n", "type": "info"})

    # ------------------- Monitoring -------------------

    @staticmethod
    def monitor_positions(symbol):
        """Monitorea las posiciones abiertas en tiempo real."""
        print("📈 Monitoreando operaciones... (presiona Ctrl+C para detener)")
        
        seconds = 1

        try:
            while True:
                # Obtener el precio actual del mercado
                tick = mt5.symbol_info_tick(symbol)  # O usar el símbolo de la orden
                if tick is None:
                    logger.color_text("❌ No se pudo obtener el precio actual", "red")
                    resume_logger.log({"message": "❌ No se pudo obtener el precio actual", "type": "error"})
                    time.sleep(1)
                    continue
                    
                # Para posiciones largas usamos el bid, para cortas el ask
                current_bid = tick.bid
                current_ask = tick.ask

                for order in MarketSimulator.open_positions:
                    if order.closed:
                        continue
                        
                    # Usar el precio apropiado según el tipo de orden
                    current_price = current_bid if order.type == "long" else current_ask
                    
                    # Calcular ganancias/pérdidas
                    if order.type == "long":
                        order.profit = (current_price - order.price_open) * 100000 * order.volume
                    elif order.type == "short":
                        order.profit = (order.price_open - current_price) * 100000 * order.volume
    
                    logger.color_text(f"💰 {order.symbol} | {order.type.upper()} | Entrada: {order.price_open:.5f} | Actual: {current_price:.5f} | Profit: {order.profit:.4f} USD", "blue")
                    resume_logger.log({"message": f"💰 {order.symbol} | {order.type.upper()} | Entrada: {order.price_open:.5f} | Actual: {current_price:.5f} | Profit: {order.profit:.4f} USD", "type": "info"})

                    if seconds > 58:
                        MarketSimulator.close_position(order)
                        MarketSimulator.clear_positions()
                        return;
 
                seconds += 1
                time.sleep(1)

        except KeyboardInterrupt:
            logger.color_text("\n🛑 Simulación detenida por el usuario.", "red")
            resume_logger.log({"message": "\n🛑 Simulación detenida por el usuario.", "type": "info"})
            return
