# Scalping Bot Trader MT5

<div align="center">

**Bot de trading automatizado profesional para MetaTrader 5 con estrategia avanzada de análisis de patrones de velas japonesas**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg?style=for-the-badge)](https://www.python.org/)
[![MetaTrader5](https://img.shields.io/badge/MetaTrader5-5.0.5260-green.svg?style=for-the-badge)](https://www.metatrader5.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg?style=for-the-badge)](#)

</div>

---

## Descripción

**Scalping Bot Trader MT5** es un sistema de trading automatizado de última generación que combina análisis técnico avanzado con inteligencia artificial para operar en los mercados financieros. El bot utiliza **19 patrones de velas japonesas** optimizados para timeframes de 1 minuto, ofreciendo tanto **modo en tiempo real** como **modo offline** para backtesting y análisis histórico.

### Características Destacadas

- ⚡ **Análisis en Tiempo Real**: Procesamiento instantáneo de nuevas velas
- 🧠 **19 Patrones de Velas**: Sistema completo de reconocimiento de patrones
- 📊 **Dual Mode**: Operación en vivo y análisis offline
- 🎨 **Interfaz Colorizada**: Logs visuales con emojis y colores
- 📈 **Métricas Avanzadas**: Estadísticas detalladas de rendimiento
- 🔒 **Gestión de Riesgo**: SL/TP automáticos y control de posiciones

## Funcionalidades Principales

### Sistema de Análisis Avanzado

- **🕯️ 19 Patrones de Velas Japonesas**:
  - Hammer, Hanging Man, Shooting Star
  - Doji, Spinning Tops, Marubozu
  - Engulfing Patterns (Bullish/Bearish)
  - Morning/Evening Star, Three White Soldiers
  - Dark Cloud Cover, Piercing Pattern
  - Tweezer Tops/Bottoms, Triple Formations
  - Y muchos más...

- **📊 Predicción Inteligente**: Señales LONG/SHORT/NEUTRAL basadas en análisis multi-patrón
- **✅ Validación Automática**: Comparación en tiempo real de predicciones vs resultados
- **⏱️ Timeframes Flexibles**: M1, M5, M15, M30, H1, H4, D1

### Modos de Operación

#### 🔴 Modo En Vivo (main.py)
- Conexión directa a MetaTrader 5
- Ejecución de órdenes reales
- Monitoreo continuo del mercado
- Gestión automática de posiciones

#### 📊 Modo Offline (mainoff.py)
- Análisis de datos históricos CSV
- Backtesting completo de estrategias
- Estadísticas detalladas de rendimiento
- Sin riesgo financiero

### Gestión de Riesgo Profesional

- **Stop Loss Automático**: Protección de capital configurable
- **Take Profit Inteligente**: Maximización de ganancias
- **Control de Volumen**: Gestión precisa del tamaño de posición
- **Prevención de Duplicados**: Evita operaciones múltiples en la misma vela

### Sistema de Logging Avanzado

- **🎨 Consola Colorizada**: Salida visual con códigos de color y emojis
- **📄 Logs JSONL**: Registro estructurado para análisis posterior
- **📊 Métricas en Tiempo Real**: Contadores de éxito/fallo/neutral
- **⏰ Timestamps Precisos**: Seguimiento temporal de cada evento

## 🏗️ Arquitectura del Sistema

```
scalping-bot-trader-mt5/
├── 📄 main.py                           # Modo en vivo - Conexión MT5
├── 📄 mainoff.py                        # Modo offline - Análisis histórico
├── 📁 bot_console/                      # Módulo principal del bot
│   ├── __init__.py                      # Inicializador del módulo
│   ├── 🔐 login.py                      # Autenticación MT5
│   ├── 🔗 metatrader5.py                # Wrapper de MT5
│   ├── 🕯️ predict_candle.py             # Generador y detector de velas
│   ├── 📊 candle_stick_strategy.py      # Estrategia de análisis de velas
│   ├── 🧠 candle_patterns.py            # 19 patrones de velas japonesas
│   ├── 💰 market_order.py               # Gestión de órdenes y posiciones
│   ├── 🎨 logger.py                     # Sistema de logging colorizado
│   ├── 📝 resumes.py                    # Exportación de logs JSONL
│   └── 📁 oldcode/                      # Versiones anteriores bot_console
│       └── candle_stick_strategy.py     # Estrategia anterior
├── 📁 offline/                          # Módulo de análisis offline
│   ├── 🕯️ candle.py                     # Generador de velas offline
│   ├── 📊 candle_stick.py               # Estrategia offline
│   ├── 📁 csv/                          # Datos CSV de prueba
│   │   └── chart.csv                    # Datos de ejemplo
│   ├── 📁 csv_years/                    # Datos históricos anuales
│   │   └── DATA_M1_2024.csv             # Datos completos 2024
│   └── 📁 oldcode/                      # Versiones anteriores offline
│       ├── candle_stick.py              # Estrategia offline v1
│       ├── candle_stick_v1.py           # Estrategia offline v1
│       └── candle_stick_v2.py           # Estrategia offline v2
├── 🔧 .env                              # Variables de entorno (credenciales)
├── 📦 requirements.txt                  # Dependencias del proyecto
├── 📖 README.md                         # Documentación
├── 📄 LICENSE                           # Licencia MIT
├── 📄 log.txt                           # Archivo de logs generado
└── 🗂️ .gitignore                        # Archivos ignorados por Git
```

### 🧩 Módulos Principales

#### **🤖 Bot Console** (`bot_console/`)
Módulo principal que contiene toda la lógica de trading en tiempo real:

- **`candle_patterns.py`** - Sistema avanzado de 19 patrones de velas japonesas
- **`candle_stick_strategy.py`** - Lógica de estrategia y toma de decisiones
- **`predict_candle.py`** - Detección y análisis de nuevas velas
- **`market_order.py`** - Gestión de órdenes y posiciones
- **`logger.py`** - Sistema de logging colorizado con emojis
- **`resumes.py`** - Exportación de logs en formato JSONL
- **`oldcode/`** - Versiones anteriores del módulo bot_console

#### **📊 Offline** (`offline/`)
Módulo especializado para análisis histórico y backtesting:

- **`candle.py`** - Procesamiento de datos CSV históricos
- **`candle_stick.py`** - Análisis de patrones en modo offline
- **`csv/`** - Datos CSV de prueba y ejemplos
- **`csv_years/`** - Base de datos de velas históricas por año
- **`oldcode/`** - Evolución del sistema offline (v1, v2, etc.)

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