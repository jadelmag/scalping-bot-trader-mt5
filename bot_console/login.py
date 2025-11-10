import MetaTrader5 as mt5
import os
from dotenv import load_dotenv
from typing import Optional

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class LoginMT5:
    def __init__(self, account: Optional[int] = None, password: Optional[str] = None, server: Optional[str] = None):
        """
        Inicializa la conexión a MetaTrader 5.
        Las credenciales se pueden pasar directamente o se leerán desde variables de entorno.
        
        Args:
            account: Número de cuenta (opcional)
            password: Contraseña (opcional)
            server: Servidor (opcional)
        """
        self.account = int(account) if account else int(os.getenv("MT5_ACCOUNT", "0"))
        self.password = password if password else os.getenv("MT5_PASSWORD", "")
        self.server = server if server else os.getenv("MT5_SERVER", "")
        
    def login(self) -> bool:
        """
        Establece conexión con MetaTrader 5.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Verificar que tenemos todas las credenciales
            if not self.account or not self.password or not self.server:
                print("❌ Error: Faltan credenciales. Proporciónelas al conectar o en el archivo .env.")
                return False
            
            # Inicializar MetaTrader 5
            print("🔗 Inicializando MetaTrader 5...")
            if not mt5.initialize():
                error = mt5.last_error()
                print(f"❌ Error al inicializar MetaTrader 5: {error}")
                return False
            
            # Realizar login
            print(f"🔗 Conectando a la cuenta {self.account} en {self.server}...")
            connected = mt5.login(self.account, self.password, self.server)
            
            if connected:
                print("✅ Conexión a MetaTrader 5 establecida correctamente")
                
                # Mostrar información de la cuenta conectada
                account_info = mt5.account_info()
                if account_info:
                    print(f"   👤 Cuenta: {account_info.login}")
                    print(f"   💼 Broker: {account_info.company}")
                    print(f"   🌐 Servidor: {account_info.server}")
                    print(f"   💰 Balance: ${account_info.balance:.2f}")
                
                return True
            else:
                error = mt5.last_error()
                print(f"❌ Error al conectar con MetaTrader 5: {error}")
                return False
                
        except Exception as e:
            print(f"❌ Excepción durante la conexión: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """
        Obtiene información de la conexión actual.
        
        Returns:
            Diccionario con información de conexión
        """
        try:
            account_info = mt5.account_info()
            return {
                "connected": mt5.initialize(),
                "account_number": account_info.login if account_info else None,
                "broker": account_info.company if account_info else None,
                "server": account_info.server if account_info else None,
                "balance": account_info.balance if account_info else None,
                "last_error": mt5.last_error(),
                "version": mt5.version()
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    def logout(self) -> bool:
        """
        Cierra la conexión con MetaTrader 5.
        
        Returns:
            True si se cerró correctamente
        """
        try:
            mt5.shutdown()
            print("🔒 Conexión con MetaTrader 5 cerrada")
            return True
        except Exception as e:
            print(f"❌ Error al cerrar conexión: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con MetaTrader 5 sin mostrar mucha información.
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            if not mt5.initialize():
                return False
            return mt5.login(self.account, self.password, self.server)
        except:
            return False