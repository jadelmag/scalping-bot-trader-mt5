# 🤖 Scalping Bot Trader MT5

**Un bot de trading automatizado para estrategias de scalping en el mercado Forex con simulación avanzada de precios**

## 📋 Descripción

Este proyecto implementa un sistema de trading automatizado especializado en estrategias de scalping para el par EUR/USD. El bot incluye un simulador de precios en tiempo real y dos estrategias principales de trading, diseñado para operar de forma autónoma con gestión de riesgo integrada.

## ✨ Características Principales

- **🎯 Estrategias de Trading Duales**
  - **Single Position**: Análisis de tendencia y apertura de posición única
  - **Dual Position**: Apertura simultánea de posiciones long/short para capturar movimientos

- **📊 Simulador de Mercado Avanzado**
  - Simulación realista de precios EUR/USD
  - Tendencias dinámicas con cambios aleatorios
  - Actualización en tiempo real cada segundo

- **🛡️ Gestión de Riesgo Integrada**
  - Stop Loss automático (200 pips)
  - Take Profit automático (300 pips)
  - Sistema de recuperación de pérdidas
  - Monitoreo continuo de posiciones

- **📈 Sistema de Logging Completo**
  - Registro detallado de todas las operaciones
  - Formato JSON estructurado
  - Seguimiento de rendimiento por estrategia

## 🏗️ Arquitectura del Sistema

```
scalping-bot-trader-mt5/
├── main.py                 # Punto de entrada principal
├── randomizer/
│   └── randomizer.py       # Simulador de precios EUR/USD
├── strategies/
│   ├── single_position.py  # Estrategia de posición única
│   └── dual_position.py    # Estrategia de posición dual
└── resumes/
    └── resumes.py          # Sistema de logging y reportes
```

## 🚀 Instalación y Configuración

### Requisitos del Sistema
- Python 3.7+
- Librerías estándar de Python (time, random, threading, json, os)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/scalping-bot-trader-mt5.git
   cd scalping-bot-trader-mt5
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Agregar .env y sus variables**
   ```bash
   MT5_ACCOUNT=""
   MT5_PASSWORD=""
   MT5_SERVER=""
   ```

4. **Ejecutar el bot**
   ```bash
   python main.py
   ```

## 📖 Uso del Sistema

### Ejecución Básica

El bot se ejecuta de forma continua realizando simulaciones automáticas:

```python
# El bot iniciará automáticamente con metatrader5
python main.py
```

### Ejecución de Simulación

```python
# El bot iniciará automáticamente con la configuración por defecto
python simulation/main.py
```

### Configuración de Estrategias

**Single Position Strategy:**
- Analiza 60 segundos de datos de precio
- Determina tendencia a los 40 segundos
- Abre posición basada en análisis técnico
- Monitorea hasta cierre por profit/loss

**Dual Position Strategy:**
- Abre simultáneamente posiciones long y short
- Evalúa rendimiento a los 40 segundos
- Continúa con la posición ganadora
- Cierra automáticamente por trailing stop

### Parámetros Configurables

```python
# En main.py
volume = 10.0  # Volumen de trading
symbol = "EURUSD"  # Par de divisas

# En las estrategias
sl_pips = 200  # Stop Loss en pips
tp_pips = 300  # Take Profit en pips
```

## 📊 Monitoreo y Reportes

### Logs en Tiempo Real
El sistema genera logs detallados en formato JSON:

```json
{
  "message": "✅ LONG abierto | EURUSD @ 1.15367 | SL: 1.15167 | TP: 1.15667",
  "order": {
    "symbol": "EURUSD",
    "type": "long",
    "price_open": 1.15367,
    "volume": 10.0,
    "profit": 0.0
  }
}
```

### Archivos de Log
- `resumes/single_position/single_position.jsonl`
- `resumes/dual_position/dual_position.jsonl`

## 🔧 Funcionalidades Técnicas

### Análisis de Tendencias
- **Análisis de cambio total**: Compara precio inicial vs final
- **Análisis step-by-step**: Evalúa cada movimiento consecutivo
- **Detección de volatilidad**: Identifica rangos de precio significativos

### Gestión de Posiciones
- **Apertura automática**: Basada en señales técnicas
- **Monitoreo continuo**: Cálculo de P&L en tiempo real
- **Cierre inteligente**: Por trailing stop o stop loss
- **Recuperación de pérdidas**: Sistema de martingala modificado

## ⚠️ Consideraciones Importantes

- **Modo Simulación**: Actualmente opera con datos simulados
- **Gestión de Riesgo**: Siempre utiliza stop loss y take profit
- **Monitoreo Requerido**: Supervisión recomendada durante operación
- **Backtesting**: Prueba exhaustiva antes de implementación real

## 🛠️ Desarrollo y Contribución

### Estructura de Clases Principales

- `EURUSD_Simulator`: Generador de precios simulados
- `SinglePositionSimulator`: Estrategia de posición única
- `DualPositionSimulator`: Estrategia de posición dual
- `SimulatedOrder`: Representación de órdenes de trading
- `SinglePositionLogger`: Sistema de logging especializado

### Extensibilidad

El sistema está diseñado para fácil extensión:
- Agregar nuevas estrategias en `/strategies`
- Implementar nuevos simuladores en `/randomizer`
- Personalizar logging en `/resumes`

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para reportar bugs o solicitar características:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**⚡ Desarrollado para traders que buscan automatización inteligente en estrategias de scalping**