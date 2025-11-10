import time
from randomizer.randomizer import EURUSD_Simulator


class SimulatedOrder:
    """Representa una operación abierta (simulada)."""
    def __init__(self, symbol, order_type, price_open, volume, sl_price, tp_price):
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
        }


class DualPositionSimulator:
    """
    Estrategia de posición dual simulada (sin MT5)
    """
    open_positions = []
    userVolume = 0.01

    @staticmethod
    def strategy_dual_position(sim, symbol="EURUSD", volume=0.01):
        """
        Estrategia principal de simulación.
        """
        print("🔄 Iniciando estrategia Dual Position...")
        userVolume = volume
        price = sim.get_price()
        DualPositionSimulator.open_long(symbol, price, 0.01)
        DualPositionSimulator.open_short(symbol, price, 0.01)

        DualPositionSimulator.monitor_positions(sim)

    @staticmethod
    def open_long(symbol, price_open, volume):
        """Simula una operación de compra (long)."""
        point = 0.0001
        sl_pips = 200
        tp_pips = 300

        sl_price = price_open - sl_pips * point
        tp_price = price_open + tp_pips * point

        order = SimulatedOrder(symbol, "long", price_open, volume, sl_price, tp_price)
        DualPositionSimulator.open_positions.append(order)

        print(f"✅ LONG abierto | {symbol} @ {price_open:.5f} | SL: {sl_price:.5f} | TP: {tp_price:.5f}")

    @staticmethod
    def open_short(symbol, price_open, volume):
        """Simula una operación de venta (short)."""
        point = 0.0001
        sl_pips = 200
        tp_pips = 300

        sl_price = price_open + sl_pips * point
        tp_price = price_open - tp_pips * point

        order = SimulatedOrder(symbol, "short", price_open, volume, sl_price, tp_price)
        DualPositionSimulator.open_positions.append(order)

        print(f"✅ SHORT abierto | {symbol} @ {price_open:.5f} | SL: {sl_price:.5f} | TP: {tp_price:.5f}")

    @staticmethod
    def monitor_positions(sim):
        """Simula la evolución del mercado y calcula el beneficio/pérdida."""
        print("📈 Monitoreando operaciones... (presiona Ctrl+C para detener)")

        winnerType = "neutral"
        profits = []
        try:
            for sec in range(1, 61):
                price = sim.get_price()

                for order in DualPositionSimulator.open_positions:
                    if order.closed:
                        continue

                    if order.type == "long":
                        order.profit = (price - order.price_open) * 100000 * order.volume

                    elif order.type == "short":
                        order.profit = (order.price_open - price) * 100000 * order.volume
    
                    print(f"[{sec:02d}s]💰 {order.symbol} | {order.type.upper()} | Precio actual: {price:.5f} | Profit: {order.profit:.2f} USD")

                    if (sec == 40):
                        if (order.profit > 0):
                            DualPositionSimulator.close_position(order, price)
                            winnerType = order.type
                            DualPositionSimulator.createWinnerOperation(sim, order.symbol, order, winnerType)
                            print(f"✅ SEÑAL GANADORA: {winnerType.upper()}")    
                        elif (order.profit < 0):
                            print("✅ SEÑAL PERDEDORA")
                            DualPositionSimulator.close_position(order, price)
                            winnerType = order.type
                            DualPositionSimulator.createWinnerOperation(sim, order.symbol, order, winnerType)
                            print(f"✅ SEÑAL GANADORA: {winnerType.upper()}")   
                            return
                        else:
                            print("✅ SEÑAL EMPATADA")
                            DualPositionSimulator.clear_positions()
                            return
  
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Simulación detenida por el usuario.")
            
    @staticmethod
    def createWinnerOperation(sim, symbol, order, winnerType):
        if winnerType == "long":
            DualPositionSimulator.open_long(symbol, order.price_open, DualPositionSimulator.userVolume)
        elif winnerType == "short":
            DualPositionSimulator.open_short(symbol, order.price_open, DualPositionSimulator.userVolume)

        DualPositionSimulator.monitor_winner_position(sim)

    @staticmethod
    def monitor_winner_position(sim):
        """Simula la evolución del mercado y calcula el beneficio/pérdida."""
        print("📈 Monitoreando operacion ganadora...")

        profits = []
        try:
            while True:
                price = sim.get_price()

                for order in DualPositionSimulator.open_positions:
                    if order.closed:
                        continue

                    if order.type == "long":
                        order.profit = (price - order.price_open) * 100000 * order.volume

                    elif order.type == "short":
                        order.profit = (order.price_open - price) * 100000 * order.volume
    
                    print(f"💰 {order.symbol} | {order.type.upper()} | Precio actual: {price:.5f} | Profit: {order.profit:.2f} USD")

                    if (order.profit > 0):
                        profits.append(order.profit)
                        maxProfit = max(profits)
                        if (len(profits) >= 2 and order.profit < maxProfit):  
                            DualPositionSimulator.close_winner_position(order, price)
                            return  # Retorna para permitir nueva simulación
                    elif (order.profit < 0):
                        DualPositionSimulator.close_winner_position(order, price)  
  
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Simulación detenida por el usuario.")
            
    @staticmethod
    def close_position(order, price_close):
        """Cierra una operación simulada."""
        order.closed = True
        order.price_close = price_close

        print(f"✅ Cierre {order.type.upper()} @ {price_close:.5f} | Profit: {order.profit:.2f} USD")

    @staticmethod
    def close_winner_position(order, price_close):
        """Cierra una operación simulada."""
        order.closed = True
        order.price_close = price_close

        print(f"✅ Cierre {order.type.upper()} @ {price_close:.5f} | Profit: {order.profit:.2f} USD")
        DualPositionSimulator.clear_positions()

    @staticmethod
    def clear_positions():
        """Limpia las posiciones abiertas."""
        # Limpiar posiciones cerradas y retornar para nueva simulación
        DualPositionSimulator.open_positions = [pos for pos in DualPositionSimulator.open_positions if not pos.closed]
        
        print("🔄 Preparando nueva simulación...\n")











