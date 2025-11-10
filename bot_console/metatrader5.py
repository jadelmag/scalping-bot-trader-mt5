import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import os

class MetaTrader5:
    def __init__(self):
        """
        Inicializa la conexión a MetaTrader 5.
        Maneja errores de conexión y inicialización.
        """
        # Verificar que MT5 esté inicializado
        if not mt5.initialize():
            print(f"❌ Error al inicializar MetaTrader 5: {mt5.last_error()}")
            raise ConnectionError(f"No se pudo inicializar MetaTrader 5. Error: {mt5.last_error()}")
        
        self.last_candle_time = None
        # Obtener información de la cuenta con manejo de errores
        self._initialize_account_info()
    
    def _initialize_account_info(self):
        """Inicializa la información de la cuenta con manejo de errores."""
        try:
            self.account = mt5.account_info()
            if self.account is None:
                raise ConnectionError("No se pudo obtener información de la cuenta")
            
            # Inicializar atributos con valores por defecto
            self.balance = self.account.balance
            self.equity = self.account.equity
            self.margin = self.account.margin
            self.profit = self.account.profit
            self.leverage = self.account.leverage
            self.positions = mt5.positions_get() or []
            
        except Exception as e:
            print(f"⚠️ Error al obtener información inicial: {e}")
            # Valores por defecto en caso de error
            self.balance = 0.0
            self.equity = 0.0
            self.margin = 0.0
            self.profit = 0.0
            self.leverage = 1
            self.positions = []

    def display_account_info(self) -> None:
        """
        Muestra la información de la cuenta en un diseño ASCII bonito.
        """
        # Limpiar pantalla (opcional)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Actualizar información
        self._update_account_info()
        
        # Calcular métricas adicionales
        free_margin = self.equity - self.margin if self.equity and self.margin else 0
        margin_level = (self.equity / self.margin * 100) if self.margin else 0
        margin_used_percent = (self.margin / self.equity * 100) if self.equity else 0
        
        # Determinar color basado en profit
        profit_color = "🟢" if self.profit >= 0 else "🔴"
        equity_color = "🟢" if self.equity >= self.balance else "🔴"
        
        print("\n" + "="*50)
        print("           📊 INFO CUENTA TRADING")
        print("="*50)
        
        # Información básica de la cuenta
        print(f"┌{'─'*48}┐")
        print(f"│ {'🏦 INFORMACIÓN BÁSICA':<46} │")
        print(f"├{'─'*48}┤")
        print(f"│ ▪ Cuenta: {self.account.login if self.account else 'N/A':<34} │")
        print(f"│ ▪ Compañía: {self.account.company if self.account else 'N/A':<31} │")
        print(f"│ ▪ Servidor: {self.account.server if self.account else 'N/A':<31} │")
        print(f"│ ▪ Moneda: {self.account.currency if self.account else 'N/A':<33} │")
        print(f"│ ▪ Apalancamiento: 1:{self.leverage:<26} │")
        print(f"└{'─'*48}┘")
        
        # Estado financiero
        print(f"┌{'─'*48}┐")
        print(f"│ {'💰 ESTADO FINANCIERO':<46} │")
        print(f"├{'─'*48}┤")
        print(f"│ ▪ Balance: ${self.balance:>12.2f} {'':<20} │")
        print(f"│ ▪ Equity:  ${self.equity:>12.2f} {equity_color:<2} {'':<18} │")
        print(f"│ ▪ Profit:  ${self.profit:>12.2f} {profit_color:<2} {'':<18} │")
        print(f"│ ▪ Margen:  ${self.margin:>12.2f} {'':<20} │")
        print(f"│ ▪ Margen Libre: ${free_margin:>9.2f} {'':<20} │")
        print(f"└{'─'*48}┘")
        
        # Niveles de margen
        print(f"┌{'─'*48}┐")
        print(f"│ {'📈 NIVELES DE MARGEN':<46} │")
        print(f"├{'─'*48}┤")
        print(f"│ ▪ Nivel de Margen: {margin_level:>7.1f}% {'':<20} │")
        print(f"│ ▪ Margen Usado:    {margin_used_percent:>7.1f}% {'':<20} │")
        
        # Indicador visual de nivel de margen
        margin_bar = self._create_margin_bar(margin_level)
        print(f"│ ▪ Estado: {margin_bar:<35} │")
        print(f"└{'─'*48}┘")
        
        # Posiciones abiertas
        print(f"┌{'─'*48}┐")
        print(f"│ {'📊 POSICIONES ABIERTAS':<46} │")
        print(f"├{'─'*48}┤")
        if self.positions:
            for i, position in enumerate(self.positions[:5]):
                pos_type = "LONG 📈" if position.type == 0 else "SHORT 📉"
                profit_color_pos = "🟢" if position.profit >= 0 else "🔴"
                print(f"│ {i+1}. {position.symbol:<8} {pos_type:<12} ${position.profit:>8.2f} {profit_color_pos:<2} │")
            
            if len(self.positions) > 5:
                print(f"│ ... y {len(self.positions) - 5} posiciones más {'':<12} │")
        else:
            print(f"│ {'No hay posiciones abiertas':<44} │")
        print(f"└{'─'*48}┘")
        
        print("="*50)
        print("           💡 Actualizado en tiempo real")
        print("="*50)

    def _create_margin_bar(self, margin_level: float) -> str:
        """Crea una barra visual para el nivel de margen."""
        if margin_level >= 500:
            return "🟢🟢🟢🟢🟢 EXCELENTE"
        elif margin_level >= 300:
            return "🟢🟢🟢🟢⚪ BUENO"
        elif margin_level >= 200:
            return "🟡🟡🟡⚪⚪ NORMAL"
        elif margin_level >= 100:
            return "🟠🟠⚪⚪⚪ ALERTA"
        else:
            return "🔴⚪⚪⚪⚪ PELIGRO"

    def getGlobalInfo(self) -> Dict[str, Any]:
        """
        Obtiene información global de la cuenta y la muestra en formato bonito.
        """
        try:
            self._update_account_info()
            
            globalInfo = {
                "account": self.account._asdict() if self.account else {},
                "balance": self.balance,
                "equity": self.equity,
                "margin": self.margin,
                "profit": self.profit,
                "leverage": self.leverage,
                "positions": [pos._asdict() for pos in self.positions] if self.positions else [],
                "positions_count": len(self.positions)
            }
            
            # Mostrar la información en formato bonito
            self.display_account_info()
            
            return globalInfo
        except Exception as e:
            print(f"❌ Error en getGlobalInfo: {e}")
            return {}

    def _update_account_info(self) -> None:
        """Actualiza toda la información de la cuenta."""
        try:
            self.account = mt5.account_info()
            if self.account:
                self.balance = self.account.balance
                self.equity = self.account.equity
                self.margin = self.account.margin
                self.profit = self.account.profit
                self.leverage = self.account.leverage
            self.positions = mt5.positions_get() or []
        except Exception as e:
            print(f"⚠️ Error al actualizar información de cuenta: {e}")

    def close(self) -> None:
        """Cierra la conexión con MetaTrader 5."""
        try:
            mt5.shutdown()
            print("🔒 Conexión con MetaTrader 5 cerrada correctamente")
        except Exception as e:
            print(f"❌ Error al cerrar conexión: {e}")
