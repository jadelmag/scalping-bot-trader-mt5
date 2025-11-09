import time
from randomizer.randomizer import EURUSD_Simulator
from strategies.single_position import SinglePositionSimulator
from strategies.dual_position import DualPositionSimulator

sim = EURUSD_Simulator()
sim.start()  # Iniciar la simulación de precios

simulation_count = 0

try:
    while True:
        simulation_count += 1
        print(f"\n🚀 === SIMULACIÓN #{simulation_count} === [{time.strftime('%H:%M:%S')}]")
        print(f"EUR/USD inicial: {sim.get_price():.5f}")
        
        # Ejecutar una simulación completa
        SinglePositionSimulator.strategy_single_position(sim, symbol="EURUSD", volume=10.0)
        # DualPositionSimulator.strategy_dual_position(sim, symbol="EURUSD", volume=10.0)
        
        # Pausa breve antes de la siguiente simulación
        print("⏳ Esperando 2 segundos antes de la próxima simulación...")
        time.sleep(2)
        
except KeyboardInterrupt:
    sim.stop()
    print(f"\n✅ Simulación detenida después de {simulation_count} ciclos.")
