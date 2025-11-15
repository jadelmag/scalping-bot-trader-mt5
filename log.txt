# 🤖 Scalping Bot Trader MT5

**Bot de trading automatizado profesional para MetaTrader 5 con estrategia de análisis de velas japonesas en tiempo real**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![MetaTrader5](https://img.shields.io/badge/MetaTrader5-5.0.5260-green.svg)](https://www.metatrader5.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

Bot de trading automatizado de consola que se conecta a MetaTrader 5 para ejecutar operaciones en tiempo real basadas en el análisis técnico de patrones de velas japonesas. El sistema monitorea continuamente el mercado EURUSD en timeframe M1, predice la dirección de nuevas velas y valida sus predicciones con resultados reales.

## ✨ Características Principales

### 🎯 **Estrategia de Trading Avanzada**
- **Análisis de Patrones de Velas**: Evaluación detallada de mechas superiores e inferiores
- **Predicción en Tiempo Real**: Genera señales LONG/SHORT/NEUTRAL para cada nueva vela
- **Validación Automática**: Compara predicciones con resultados reales de velas cerradas
- **Timeframes Configurables**: Soporte para M1, M5, M15, M30, H1, H4, D1

### 📊 **Integración con MetaTrader 5**
- **Conexión Segura**: Autenticación mediante variables de entorno
- **Ejecución de Órdenes Reales**: Apertura automática de posiciones LONG/SHORT
- **Gestión de Riesgo**: Stop Loss (200 pips) y Take Profit (300 pips) automáticos
- **Monitoreo en Tiempo Real**: Seguimiento continuo de P&L de posiciones abiertas

### 🛡️ **Sistema de Gestión de Posiciones**
- **Apertura Inteligente**: Basada en análisis de 14 patrones de velas diferentes
- **Cierre Automático**: Por tiempo (58 segundos) o por SL/TP
- **Cálculo de Profit**: Actualización en tiempo real del beneficio/pérdida
- **Prevención de Duplicados**: Control de velas ya procesadas

### 📈 **Logging y Reportes Completos**
- **Logs en Consola**: Salida colorizada con emojis para fácil seguimiento
- **Archivos JSONL**: Registro estructurado de todas las operaciones
- **Timestamps Precisos**: Seguimiento temporal de cada evento
- **Métricas de Rendimiento**: Validación de señales correctas/incorrectas

## 🏗️ Arquitectura del Sistema

```
scalping-bot-trader-mt5/
├── main.py                              # Punto de entrada principal
├── bot_console/
│   ├── __init__.py                      # Inicializador del módulo
│   ├── login.py                         # Autenticación MT5
│   ├── metatrader5.py                   # Wrapper de MT5
│   ├── predict_candle.py                # Generador y detector de velas
│   ├── candle_stick_strategy.py         # Estrategia de análisis de velas
│   ├── market_order.py                  # Gestión de órdenes y posiciones
│   ├── logger.py                        # Sistema de logging colorizado
│   └── resumes.py                       # Exportación de logs JSONL
├── old_code/                            # Versiones anteriores
├── .env                                 # Variables de entorno (credenciales)
├── requirements.txt                     # Dependencias del proyecto
└── README.md                            # Documentación
```

## 🚀 Instalación y Configuración

### Requisitos del Sistema

- **Python**: 3.7 o superior
- **MetaTrader 5**: Instalado y configurado
- **Sistema Operativo**: Windows (recomendado para MT5)
- **Conexión a Internet**: Para datos de mercado en tiempo real

### Dependencias

```txt
MetaTrader5==5.0.5260
pandas>=2.3.2
numpy>=2.2.6
python-dotenv>=1.0.0
scipy>=1.11.0
```

### Instalación Paso a Paso

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/jadelmag/scalping-bot-trader-mt5.git
   cd scalping-bot-trader-mt5
   ```

2. **Crear entorno virtual (recomendado | opcional)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Crear archivo `.env` en la raíz del proyecto:
   ```env
   # Credenciales de MetaTrader 5
   MT5_ACCOUNT=12345678
   MT5_PASSWORD=tu_contraseña_segura
   MT5_SERVER=nombre_del_servidor
   
   # Configuración de trading (opcional)
   SYMBOL=EURUSD
   TIMEFRAME=1
   ```

5. **Verificar instalación de MetaTrader 5**
   ```bash
   python -c "import MetaTrader5 as mt5; print('MT5 Version:', mt5.version())"
   ```

## 📖 Uso del Sistema

### Ejecución Básica

```bash
python main.py
```

### Flujo de Operación

1. **Inicialización**
   - Conexión a MetaTrader 5 con credenciales del `.env`
   - Verificación de cuenta y balance
   - Inicialización de generadores de velas y estrategia

2. **Monitoreo Continuo**
   - Detección de nuevas velas cada segundo
   - Análisis de la última vela cerrada
   - Generación de señal predictiva (LONG/SHORT/NEUTRAL)

3. **Validación de Predicciones**
   - Comparación de señal predicha vs resultado real
   - Registro de aciertos/errores en logs
   - Actualización de métricas de rendimiento

4. **Ejecución de Operaciones** (actualmente comentado)
   - Apertura de posición según señal
   - Configuración automática de SL/TP
   - Monitoreo de P&L en tiempo real

### Salida de Consola

```
🚀 Iniciando Bot de Trading EURUSD 1M
🎯 Estrategia: Operar al inicio de nueva vela basado en patrón de vela cerrada
🔗 Inicializando MetaTrader 5...
✅ Conexión a MetaTrader 5 establecida correctamente
   👤 Cuenta: 12345678
   💼 Broker: XM Global Limited
   🌐 Servidor: XMGlobal-MT5
   💰 Balance: $10000.00
🔄 Inicializando modelo...

==================================================
🕯️ NUEVA VELA INICIADA: 14:23:00
✅ Señal correcta para vela 14:22:00 → LONG
🕯 Precio de cierre: Close: 1.08456
⬆ Mecha superior: 0.00012 (Sí)
⬇ Mecha inferior: 0.00008 (Sí)
🔮 Señal predicha para vela 14:23:00: SHORT
```

## 🔧 Componentes Técnicos

### 1. **LoginMT5** (`login.py`)

Gestiona la autenticación y conexión con MetaTrader 5.

**Métodos principales:**
- `login()`: Establece conexión con MT5
- `get_connection_info()`: Obtiene información de la cuenta
- `logout()`: Cierra la conexión
- `test_connection()`: Verifica conectividad

### 2. **CandleGenerator** (`predict_candle.py`)

Detecta nuevas velas y obtiene datos históricos.

**Métodos principales:**
- `check_new_candle()`: Detecta inicio de nueva vela
- `get_candles(n)`: Obtiene últimas n velas
- `get_signal_for_last_candle()`: Determina dirección de vela cerrada

### 3. **CandleStickStrategy** (`candle_stick_strategy.py`)

Analiza patrones de velas para generar señales de trading.

### 4. **MarketSimulator** (`market_order.py`)

Gestiona la apertura, cierre y monitoreo de posiciones.

**Métodos principales:**
- `open_long(symbol, volume, sl_pips, tp_pips)`: Abre posición de compra
- `open_short(symbol, volume, sl_pips, tp_pips)`: Abre posición de venta
- `close_position(order)`: Cierra posición abierta
- `monitor_positions(symbol)`

## Modo Offline

El modo offline permite ejecutar el bot sin conexión a MetaTrader 5, utilizando datos históricos para simular operaciones.

### Ejecución en Modo Offline

```bash
python mainoff.py
```

### Exportar logs a fichero TXT

```bash
python mainoff.py | Out-File -FilePath "resultado.txt" -Encoding UTF8
```