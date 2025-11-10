import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import MetaTrader5 as mt5
from datetime import datetime
import time

class EURUSD1MPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_trained = False
        self.last_candle_time = None
        
    def get_historical_data(self, bars=1000):
        """Obtener datos históricos"""
        try:
            if not mt5.initialize():
                return None
                
            rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M1, 0, bars)
            mt5.shutdown()
            
            if rates is None:
                return None
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
            
        except Exception as e:
            return None
    
    def calculate_indicators(self, df):
        """Calcular indicadores"""
        if df is None or len(df) == 0:
            return None
            
        df = df.copy()
        close = df['close']
        high = df['high'] 
        low = df['low']
        open_price = df['open']
        
        # Indicadores básicos
        df['sma_5'] = close.rolling(window=5, min_periods=1).mean()
        df['sma_10'] = close.rolling(window=10, min_periods=1).mean()
        df['ema_8'] = close.ewm(span=8, min_periods=1).mean()
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=6, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=6, min_periods=1).mean()
        rs = gain / (loss + 1e-10)
        df['rsi_6'] = 100 - (100 / (1 + rs))
        
        # Retornos y momentum
        df['return_1'] = close.pct_change(1)
        df['return_3'] = close.pct_change(3)
        df['momentum_3'] = close - close.shift(3)
        
        # Volatilidad
        df['range'] = high - low
        df['atr_5'] = df['range'].rolling(window=5, min_periods=1).mean()
        df['volatility'] = df['range'] / (df['atr_5'] + 1e-10)
        
        # Posición relativa
        df['price_vs_sma5'] = close / (df['sma_5'] + 1e-10)
        df['price_vs_sma10'] = close / (df['sma_10'] + 1e-10)
        
        # Características de velas
        df['body_size'] = abs(close - open_price)
        df['body_ratio'] = df['body_size'] / (df['range'] + 1e-10)
        df['is_bullish'] = (close > open_price).astype(int)
        
        # Tendencias
        df['higher_high'] = (high > high.shift(1)).astype(int)
        df['higher_low'] = (low > low.shift(1)).astype(int)
        
        # Temporales
        df['hour'] = df['time'].dt.hour
        df['minute'] = df['time'].dt.minute
        df['is_london'] = ((df['hour'] >= 7) & (df['hour'] < 16)).astype(int)
        df['is_ny'] = ((df['hour'] >= 13) & (df['hour'] < 22)).astype(int)
        
        return df
    
    def prepare_target(self, df):
        """Preparar variable objetivo - solo SHORT y LONG"""
        if df is None:
            return None
            
        df = df.copy()
        next_close = df['close'].shift(-1)
        next_open = df['open'].shift(-1)
        next_body_pct = (next_close - next_open) / next_open
        
        # Umbral más estricto para solo tener SHORT y LONG
        threshold = 0.0001  # 1 pip para EURUSD
        
        # Solo dos clases: SHORT y LONG
        conditions = [
            next_body_pct > threshold,   # LONG
            next_body_pct <= threshold   # SHORT
        ]
        choices = ['LONG', 'SHORT']
        
        df['target'] = np.select(conditions, choices, default='SHORT')
        return df
    
    def create_balanced_dataset(self, X, y):
        """Balancear dataset para solo 2 clases"""
        from collections import Counter
        
        class_counts = Counter(y)
        max_count = max(class_counts.values())
        
        balanced_X = []
        balanced_y = []
        
        for class_name in class_counts:
            class_indices = np.where(y == class_name)[0]
            current_count = len(class_indices)
            
            if current_count < max_count:
                needed = max_count - current_count
                additional_indices = np.random.choice(class_indices, needed, replace=True)
                
                balanced_X.append(X[class_indices])
                balanced_X.append(X[additional_indices])
                balanced_y.extend([class_name] * (current_count + needed))
            else:
                balanced_X.append(X[class_indices])
                balanced_y.extend([class_name] * current_count)
        
        if balanced_X:
            balanced_X = np.vstack(balanced_X)
            balanced_y = np.array(balanced_y)
            shuffle_idx = np.random.permutation(len(balanced_y))
            return balanced_X[shuffle_idx], balanced_y[shuffle_idx]
        
        return X, y
    
    def train_model(self):
        """Entrenar modelo para solo SHORT/LONG"""
        if self.model_trained:
            return True
            
        print("🚀 ENTRENANDO MODELO (SHORT/LONG ONLY)...")
        
        df = self.get_historical_data(1500)
        if df is None:
            return False
        
        df = self.calculate_indicators(df)
        if df is None:
            return False
        
        df = self.prepare_target(df)
        if df is None:
            return False
        
        self.feature_names = [
            'sma_5', 'sma_10', 'ema_8', 'rsi_6', 
            'return_1', 'return_3', 'momentum_3',
            'volatility', 'price_vs_sma5', 'price_vs_sma10',
            'body_size', 'body_ratio', 'is_bullish',
            'higher_high', 'higher_low', 'hour',
            'is_london', 'is_ny'
        ]
        
        # Verificar características
        missing_features = [f for f in self.feature_names if f not in df.columns]
        if missing_features:
            return False
        
        valid_mask = ~df[self.feature_names + ['target']].isna().any(axis=1)
        df_valid = df[valid_mask]
        
        if len(df_valid) < 500:
            return False
        
        X = df_valid[self.feature_names].values
        y = df_valid['target'].values
        
        X_balanced, y_balanced = self.create_balanced_dataset(X, y)
        
        split_idx = int(len(X_balanced) * 0.8)
        X_train, X_test = X_balanced[:split_idx], X_balanced[split_idx:]
        y_train, y_test = y_balanced[:split_idx], y_balanced[split_idx:]
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = RandomForestClassifier(
            n_estimators=80,
            max_depth=12,
            min_samples_split=15,
            min_samples_leaf=8,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluación
        y_pred = self.model.predict(X_test_scaled)
        accuracy = np.mean(y_pred == y_test)
        
        print(f"✅ Modelo entrenado - Accuracy: {accuracy:.3f}")
        print(f"📊 Distribución: {pd.Series(y_test).value_counts().to_dict()}")
        
        self.model_trained = True
        return True
    
    def get_current_candle_data(self):
        """Obtener datos de la vela actual"""
        try:
            if not mt5.initialize():
                return None, None
                
            rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M1, 0, 2)
            mt5.shutdown()
            
            if rates is None or len(rates) < 2:
                return None, None
                
            current_candle = rates[-1]
            current_time = datetime.fromtimestamp(current_candle['time'])
            
            return current_candle, current_time
            
        except Exception as e:
            return None, None
    
    def check_new_candle(self):
        """Verificar si hay una vela nueva"""
        current_candle, current_time = self.get_current_candle_data()
        
        if current_candle is None or current_time is None:
            return False, None
        
        if self.last_candle_time is None:
            self.last_candle_time = current_time
            return True, current_time
        
        if current_time != self.last_candle_time:
            self.last_candle_time = current_time
            return True, current_time
        
        return False, current_time
    
    def get_prediction_features(self):
        """Obtener características para predicción"""
        df = self.get_historical_data(100)
        if df is None:
            return None
        
        df = self.calculate_indicators(df)
        if df is None or len(df) == 0:
            return None
        
        current_features = df[self.feature_names].iloc[-1:].values
        
        if np.isnan(current_features).any():
            return None
            
        return current_features
    
    def predict_next_candle(self):
        """Predecir siguiente vela - solo retorna SHORT o LONG"""
        if not self.model_trained:
            if not self.train_model():
                return None
        
        current_features = self.get_prediction_features()
        if current_features is None:
            return None
        
        current_scaled = self.scaler.transform(current_features)
        prediction = self.model.predict(current_scaled)[0]
        probabilities = self.model.predict_proba(current_scaled)[0]
        confidence = max(probabilities)
        
        # Solo retornar si la confianza es alta
        if confidence > 0.65:
            return {
                'prediction': prediction,  # Solo será SHORT o LONG
                'confidence': confidence,
                'probabilities': dict(zip(self.model.classes_, probabilities)),
                'timestamp': datetime.now()
            }
        else:
            return None

