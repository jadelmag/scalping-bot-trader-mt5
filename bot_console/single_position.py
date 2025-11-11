import time
import pandas as pd
import MetaTrader5 as mt5
from bot_console.resumes import ResumeJsonL
from bot_console.logger import Logger

LONG = "LONG"
SHORT = "SHORT"
NEUTRAL = "NEUTRAL"

class SimulatedOrder:
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


class SinglePositionSimulator:
    """
    Estrategia de posición simulada
    """
    logger = Logger()
    open_positions = []
    resume_logger = ResumeJsonL("strategy_single_position")

    @staticmethod
    def strategy_single_position(symbol: str="EURUSD", volume: float=0.01, signal: str="NEUTRAL"):
        """
        Estrategia principal de simulación.
        """
        print(SinglePositionSimulator.color_text("🔄 Iniciando simulación de ticks (60 segundos...)", "blue"))
        SinglePositionSimulator.resume_logger.log_resume("🔄 Iniciando simulación de ticks (60 segundos...)")

        if signal == LONG:
            SinglePositionSimulator.open_long(symbol, volume)
        elif signal == SHORT:
            SinglePositionSimulator.open_short(symbol, volume)
        else:
            SinglePositionSimulator.resume_logger.color_text(f"No se abre operacion por tipo de señal: {signal}", "yellow")
            return

        SinglePositionSimulator.monitor_positions(symbol)

    # ------------------- Funciones short, long and close -------------------

    @staticmethod
    def open_long(symbol, volume, sl_pips=200, tp_pips=300):
        """Abre una operación real de compra (LONG) en MT5."""
        try:
            # Obtener información actual del símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                SinglePositionSimulator.resume_logger.color_text(f"❌ No se pudo obtener información para {symbol}", "red")
                return False
            
            # Verificar si el símbolo está disponible para trading
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    SinglePositionSimulator.resume_logger.color_text(f"❌ No se puede seleccionar {symbol}", "red")
                    return False
            
            # Obtener el precio actual
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                SinglePositionSimulator.resume_logger.color_text(f"❌ No se pudo obtener el tick para {symbol}", "red")
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
            
            SinglePositionSimulator.price = price_open

            if result is None:
                last_error = mt5.last_error()
                SinglePositionSimulator.resume_logger.color_text(f"❌ Error: No se pudo enviar la orden. MT5 Error: {last_error}", "red")
                return False

            order = SimulatedOrder(symbol, "long", price_open, volume, sl_price, tp_price, position_id=result.order)
            SinglePositionSimulator.open_positions.append(order)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                SinglePositionSimulator.resume_logger.color_text(f"❌ Error al abrir LONG: {result.retcode} | msj: {result.comment}", "red")
                return False
            else:
                SinglePositionSimulator.resume_logger.color_text(f"✅ LONG abierto | Ticket: {result.order} | {symbol} @ {price_open:.5f}", "green")
                SinglePositionSimulator.resume_logger.color_text(f"✅ SL: {sl_price:.5f} | TP: {tp_price:.5f} | Volumen: {volume}", "green")
                return True
                
        except Exception as e:
            SinglePositionSimulator.resume_logger.color_text(f"❌ Error en open_long: {e}", "red")
            return False

    @staticmethod
    def open_short(symbol, volume, sl_pips=200, tp_pips=300):
        """Abre una operación real de venta (SHORT) en MT5."""
        try:
            # Obtener información actual del símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                SinglePositionSimulator.resume_logger.color_text(f"❌ No se pudo obtener información para {symbol}", "red")
                return False
            
            # Verificar si el símbolo está disponible para trading
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    SinglePositionSimulator.resume_logger.color_text(f"❌ No se puede seleccionar {symbol}", "red")
                    return False
            
            # Obtener el precio actual usando el módulo mt5 directamente
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                SinglePositionSimulator.resume_logger.color_text(f"❌ No se pudo obtener el tick para {symbol}", "red")
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
            
            SinglePositionSimulator.price = price_open
            
            if result is None:
                last_error = mt5.last_error()
                SinglePositionSimulator.resume_logger.color_text(f"❌ Error: No se pudo enviar la orden. MT5 Error: {last_error}", "red")
                return False
                
            order = SimulatedOrder(symbol, "short", price_open, volume, sl_price, tp_price, position_id=result.order)
            SinglePositionSimulator.open_positions.append(order)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                SinglePositionSimulator.resume_logger.color_text(f"❌ Error al abrir SHORT: {result.retcode} | msj: {result.comment}", "red")
                return False
            else:
                SinglePositionSimulator.resume_logger.color_text(f"✅ SHORT abierto | Ticket: {result.order} | {symbol} @ {price_open:.5f}", "green")
                SinglePositionSimulator.resume_logger.color_text(f"✅ SL: {sl_price:.5f} | TP: {tp_price:.5f} | Volumen: {volume}", "green")
                return True
                
        except Exception as e:
            SinglePositionSimulator.resume_logger.color_text(f"❌ Error en open_short: {e}", "red")
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
            SinglePositionSimulator.resume_logger.color_text(f"❌ Error al cerrar posición: {result.retcode} | {result.comment}", "red")
            return False

        order.closed = True
        order.price_close = close_price
        order.close_time = mt5.symbol_info_tick(symbol).time if mt5.symbol_info_tick(symbol) else None

        SinglePositionSimulator.resume_logger.color_text(f"✅ Cierre REAL {order.type.upper()} @ {close_price:.5f} | Profit: {order.profit:.2f} USD", "green")
        return True

    @staticmethod
    def clear_positions():
        """Limpia las posiciones abiertas."""
        # Limpiar posiciones cerradas y retornar para nueva simulación
        SinglePositionSimulator.open_positions = [pos for pos in SinglePositionSimulator.open_positions if not pos.closed]
        
        SinglePositionSimulator.resume_logger.color_text("🔄 Preparando nueva simulación...\n", "blue")

    # ------------------- Monitoring -------------------

    @staticmethod
    def monitor_positions(symbol):
        """Monitorea las posiciones abiertas en tiempo real."""
        print("📈 Monitoreando operaciones... (presiona Ctrl+C para detener)")
        
        profits = []
        numTimes = 0

        try:
            while True:
                # Obtener el precio actual del mercado
                tick = mt5.symbol_info_tick(symbol)  # O usar el símbolo de la orden
                if tick is None:
                    print(SinglePositionSimulator.color_text("❌ No se pudo obtener el precio actual", "red"))
                    time.sleep(1)
                    continue
                    
                # Para posiciones largas usamos el bid, para cortas el ask
                current_bid = tick.bid
                current_ask = tick.ask

                for order in SinglePositionSimulator.open_positions:
                    if order.closed:
                        continue
                        
                    # Usar el precio apropiado según el tipo de orden
                    current_price = current_bid if order.type == "long" else current_ask
                    
                    # Calcular ganancias/pérdidas
                    if order.type == "long":
                        order.profit = (current_price - order.price_open) * 100000 * order.volume
                    elif order.type == "short":
                        order.profit = (order.price_open - current_price) * 100000 * order.volume
    
                    SinglePositionSimulator.resume_logger.color_text(f"💰 {order.symbol} | {order.type.upper()} | Entrada: {order.price_open:.5f} | Actual: {current_price:.5f} | Profit: {order.profit:.4f} USD", "blue")

                    if order.profit > 0:
                        profits.append(order.profit)
                        if len(profits) >= 2:
                            max_profit = max(profits)
                            close_profit = max_profit * 0.90 # Si el profit baja un 10% del máximo
                            if order.profit < close_profit:  
                                SinglePositionSimulator.close_position(order)
                    elif order.profit < 0:
                        print(f"🔴 Pérdida: {order.profit:.2f} USD")
                        numTimes += 1
                        print(f"🔴 Times: {numTimes}")
                        if numTimes >= 4:
                            print(f"🔴 Times: {numTimes}")
                            SinglePositionSimulator.close_position(order)
                            SinglePositionSimulator.clear_positions()
                            return

                time.sleep(1)

        except KeyboardInterrupt:
            SinglePositionSimulator.resume_logger.color_text("\n🛑 Simulación detenida por el usuario.", "red")
            return
    # ------------------- Funciones recovery profit -------------------

    @staticmethod
    def get_opposite_type(type):
        if type == "long":
            return "short"
        elif type == "short":
            return "long"
        else:
            return "neutral"

    @staticmethod
    def recovery_profit(lostProfit, currentType, order):
        """Recupera el profit perdido."""
        SinglePositionSimulator.resume_logger.color_text(f"🔴 Pérdida: -{lostProfit:.2f} USD", "red")

        oppositeType = SinglePositionSimulator.get_opposite_type(currentType)
        if (oppositeType == "long"):
            SinglePositionSimulator.open_long(order.symbol, order.price_open, order.volume * 2)
        elif (oppositeType == "short"):
            SinglePositionSimulator.open_short(order.symbol, order.price_open, order.volume * 2)


