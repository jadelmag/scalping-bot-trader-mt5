import time
from randomizer.randomizer import EURUSD_Simulator
from resumes.resumes import SinglePositionLogger

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


class SinglePositionSimulator:
    """
    Estrategia de posición simulada (sin MT5)
    """
    open_positions = []
    lostMoney = 0
    recoveryProfit = False

    logger = SinglePositionLogger("single_position")

    @staticmethod
    def strategy_single_position(sim, symbol="EURUSD", volume=0.01):
        """
        Estrategia principal de simulación.
        """
        ticks_price = []
        operation = "neutral"

        print("🔄 Iniciando simulación de ticks (60 segundos)...")
        SinglePositionSimulator.logger.log({"message": "Iniciando simulación de ticks (60 segundos)..."})

        for sec in range(1, 61):
            price = sim.get_price()  # obtiene nuevo tick
            ticks_price.append(price)
    
            SinglePositionSimulator.logger.log({"message": f"[{sec:02d}s] Tick → {price:.5f}"})
            print(f"[{sec:02d}s] Tick → {price:.5f}")

            # A los 40s analizamos la tendencia
            if sec == 40:
                operation = SinglePositionSimulator.determinar_tendencia(ticks_price)
                if operation == "long":
                    SinglePositionSimulator.open_long(symbol, price, volume)
                elif operation == "short":
                    SinglePositionSimulator.open_short(symbol, price, volume)
                else:
                    print("🟡 No se abre operación (neutral).")
                    SinglePositionSimulator.logger.log({"message": "🟡 No se abre operación (neutral)."})
                    break

            time.sleep(1)
            if sec == 40 and (operation == "long" or operation == "short"):
                SinglePositionSimulator.monitor_positions(sim)
                break

    # ------------------- Funciones de deteccion operacion -------------------

    @staticmethod
    def determinar_tendencia(prices, threshold=0.00001):
        """
        Determina la tendencia de una lista de precios.

        Parámetros:
        - prices: lista de floats con los precios en orden cronológico.
        - threshold: mínimo cambio para considerar una tendencia significativa.

        Retorna:
        - "long" si la tendencia es alcista,
        - "short" si la tendencia es bajista,
        - "neutral" si no hay cambio significativo.
        """
        if not prices or len(prices) < 2:
            return "neutral"

        total = prices[-1] - prices[0]

        if total > threshold:
            return "long"
        elif total < -threshold:
            return "short"
        else:
            return "neutral"

    @staticmethod
    def step_trend(prices, threshold=0.00001):
        """
        Analyzes each consecutive step in the price list and determines
        if the majority indicate going up, down, or staying stable.

        Parameters:
        - prices: list of floats with prices in chronological order.
        - threshold: minimum change to consider a significant step.

        Returns:
        - "long" if most steps go up,
        - "short" if most steps go down,
        - "neutral" if no clear majority.
        """
        if not prices or len(prices) < 2:
            return "neutral"

        ups = 0
        downs = 0
        neutrals = 0

        for i in range(len(prices) - 1):
            diff = prices[i+1] - prices[i]
            if diff > threshold:
                ups += 1
            elif diff < -threshold:
                downs += 1
            else:
                neutrals += 1

        decision = "neutral"
        # Decide based on simple majority
        if ups > downs and ups > neutrals:
            decision = "long"
        elif downs > ups and downs > neutrals:
            decision = "short"
        else:
            decision = "neutral"

        print(f"📊 SEÑAL DETECTADA: → {decision.upper()}")
        SinglePositionSimulator.logger.log({"message": f"📊 SEÑAL DETECTADA: → {decision.upper()}", "action": "step_trend"})
        return decision

    @staticmethod
    def detect_operation(ticks_price):
        """Detecta si abrir LONG, SHORT o mantenerse NEUTRAL."""
        if len(ticks_price) < 5:
            return "neutral"

        initial = ticks_price[0]
        final = ticks_price[-1]
        change = final - initial

        max_price = max(ticks_price)
        min_price = min(ticks_price)
        price_range = max_price - min_price

        trend_threshold = 0.00005
        volatility_threshold = 0.00010

        if price_range < volatility_threshold:
            decision = "neutral"
        elif change > trend_threshold:
            decision = "long"
        elif change < -trend_threshold:
            decision = "short"
        else:
            decision = "neutral"

        print(f"📊 Cambio: {change:.5f} | Rango: {price_range:.5f} → {decision.upper()}")
        SinglePositionSimulator.logger.log({"message": f"📊 Cambio: {change:.5f} | Rango: {price_range:.5f} → {decision.upper()}", "decision": decision})

        return decision

    @staticmethod
    def get_opposite_type(type):
        if type == "long":
            return "short"
        elif type == "short":
            return "long"
        else:
            return "neutral"

    # ------------------- Operaciones simuladas -------------------

    @staticmethod
    def open_long(symbol, price_open, volume):
        """Simula una operación de compra (long)."""
        point = 0.0001
        sl_pips = 200
        tp_pips = 300

        sl_price = price_open - sl_pips * point
        tp_price = price_open + tp_pips * point

        order = SimulatedOrder(symbol, "long", price_open, volume, sl_price, tp_price)
        SinglePositionSimulator.open_positions.append(order)

        print(f"✅ LONG abierto | {symbol} @ {price_open:.5f} | SL: {sl_price:.5f} | TP: {tp_price:.5f}")
        SinglePositionSimulator.logger.log({"message": f"✅ LONG abierto | {symbol} @ {price_open:.5f} | SL: {sl_price:.5f} | TP: {tp_price:.5f}", "order": order.to_dict()})

    @staticmethod
    def open_short(symbol, price_open, volume):
        """Simula una operación de venta (short)."""
        point = 0.0001
        sl_pips = 200
        tp_pips = 300

        sl_price = price_open + sl_pips * point
        tp_price = price_open - tp_pips * point

        order = SimulatedOrder(symbol, "short", price_open, volume, sl_price, tp_price)
        SinglePositionSimulator.open_positions.append(order)

        print(f"✅ SHORT abierto | {symbol} @ {price_open:.5f} | SL: {sl_price:.5f} | TP: {tp_price:.5f}")
        SinglePositionSimulator.logger.log({"message": f"✅ SHORT abierto | {symbol} @ {price_open:.5f} | SL: {sl_price:.5f} | TP: {tp_price:.5f}", "order": order.to_dict()})

    @staticmethod
    def monitor_positions(sim):
        """Simula la evolución del mercado y calcula el beneficio/pérdida."""
        print("📈 Monitoreando operaciones... (presiona Ctrl+C para detener)")
        SinglePositionSimulator.logger.log({"message": "📈 Monitoreando operaciones... (presiona Ctrl+C para detener)", "action": "monitor_positions"})

        numTimesitive = 0
        profits = []
        try:
            while True:
                price = sim.get_price()

                for order in SinglePositionSimulator.open_positions:
                    if order.closed:
                        continue

                    if order.type == "long":
                        order.profit = (price - order.price_open) * 100000 * order.volume

                    elif order.type == "short":
                        order.profit = (order.price_open - price) * 100000 * order.volume
    
                    print(f"💰 {order.symbol} | {order.type.upper()} | Precio actual: {price:.5f} | Profit: {order.profit:.2f} USD")
                    SinglePositionSimulator.logger.log({"message": f"💰 {order.symbol} | {order.type.upper()} | Precio actual: {price:.5f} | Profit: {order.profit:.2f} USD", "order": order.to_dict(), "action": "monitor_positions"})

                    if (order.profit > 0):
                        profits.append(order.profit)
                        maxProfit = max(profits)
                        if (len(profits) >= 2 and order.profit < maxProfit):
                            SinglePositionSimulator.close_position(order, price)
                            SinglePositionSimulator.clear_positions()
                            return  # Retorna para permitir nueva simulación
                    elif (order.profit < 0):
                        SinglePositionSimulator.close_position(order, price)
                        lostProfit = abs(order.profit)
                        SinglePositionSimulator.recovery_profit(lostProfit, order.type, order)   

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Simulación detenida por el usuario.")
            SinglePositionSimulator.logger.log({"message": "\n🛑 Simulación detenida por el usuario.", "action": "monitor_positions"})

    @staticmethod
    def recovery_profit(lostProfit, currentType, order):
        """Recupera el profit perdido."""
        print(f"🔴 Pérdida: -{lostProfit:.2f} USD")
        SinglePositionSimulator.logger.log({"message": f"🔴 Pérdida: -{lostProfit:.2f} USD", "action": "recovery_profit", "action": "recovery_profit"})

        SinglePositionSimulator.lostMoney = lostProfit
        SinglePositionSimulator.recoveryProfit = True

        oppositeType = SinglePositionSimulator.get_opposite_type(currentType)
        if (oppositeType == "long"):
            SinglePositionSimulator.open_long(order.symbol, order.price_open, order.volume * 2)
        elif (oppositeType == "short"):
            SinglePositionSimulator.open_short(order.symbol, order.price_open, order.volume * 2)

    @staticmethod
    def close_position(order, price_close):
        """Cierra una operación simulada."""
        order.closed = True
        order.price_close = price_close

        if (SinglePositionSimulator.recoveryProfit):
            lost = SinglePositionSimulator.lostMoney
            total = order.profit - lost

            print(f"✅ Cierre {order.type.upper()} @ {price_close:.5f} | Profit: {order.profit:.2f} USD | Perdido: -{lost:.2f} USD | Total: {total:.2f} USD")
            SinglePositionSimulator.logger.log({"message": f"✅ Cierre {order.type.upper()} @ {price_close:.5f} | Profit: {order.profit:.2f} USD | Perdido: -{lost:.2f} USD | Total: {total:.2f} USD", "action": "close_position"})

            SinglePositionSimulator.recoveryProfit = False
            SinglePositionSimulator.lostMoney = 0
            SinglePositionSimulator.clear_positions()
            return
        else:
            print(f"✅ Cierre {order.type.upper()} @ {price_close:.5f} | Profit: {order.profit:.2f} USD")
            SinglePositionSimulator.logger.log({"message": f"✅ Cierre {order.type.upper()} @ {price_close:.5f} | Profit: {order.profit:.2f} USD", "action": "close_position"})

    @staticmethod
    def clear_positions():
        """Limpia las posiciones abiertas."""
        # Limpiar posiciones cerradas y retornar para nueva simulación
        SinglePositionSimulator.open_positions = [pos for pos in SinglePositionSimulator.open_positions if not pos.closed]
        
        print("🔄 Preparando nueva simulación...\n")
        SinglePositionSimulator.logger.log({"message": "🔄 Preparando nueva simulación...", "action": "clear_positions"})