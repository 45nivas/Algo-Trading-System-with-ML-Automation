import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from utils import add_technical_indicators
import config

class MLPredictor:
    def __init__(self, model_type='DecisionTree'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = ['RSI', 'MACD', 'Volume', 'MA20', 'MA50', 'BB_Upper', 'BB_Lower']
        self.accuracy = 0
        
    def prepare_features(self, data):
        data = add_technical_indicators(data)
        
        data['Next_Day_Return'] = data['Close'].pct_change().shift(-1)
        data['Target'] = (data['Next_Day_Return'] > 0).astype(int)
        
        data['Price_Change'] = data['Close'].pct_change()
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        
        volume_ratio = data['Volume'] / data['Volume_MA']
        data['Volume_Ratio'] = volume_ratio.fillna(1.0)
        
        self.feature_columns = ['RSI', 'MACD', 'Volume_Ratio', 'MA20', 'MA50', 
                               'Price_Change', 'MACD_Histogram']
        
        return data
    
    def train_model(self, data):
        try:
            data = self.prepare_features(data)
            
            clean_data = data[self.feature_columns + ['Target']].dropna()
            
            if len(clean_data) < 50:
                logging.warning("Insufficient data for training")
                return False
            
            X = clean_data[self.feature_columns]
            y = clean_data['Target']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            if self.model_type == 'DecisionTree':
                self.model = DecisionTreeClassifier(
                    max_depth=10, min_samples_split=5, random_state=42
                )
            elif self.model_type == 'LogisticRegression':
                self.model = LogisticRegression(random_state=42, max_iter=1000)
            elif self.model_type == 'RandomForest':
                self.model = RandomForestClassifier(
                    n_estimators=100, max_depth=10, random_state=42
                )
            
            if self.model_type == 'LogisticRegression':
                self.model.fit(X_train_scaled, y_train)
                y_pred = self.model.predict(X_test_scaled)
            else:
                self.model.fit(X_train, y_train)
                y_pred = self.model.predict(X_test)
            
            self.accuracy = accuracy_score(y_test, y_pred)
            
            logging.info(f"Model trained successfully. Accuracy: {self.accuracy:.4f}")
            logging.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error training model: {e}")
            return False
    
    def predict(self, data):
        try:
            if self.model is None:
                logging.error("Model not trained")
                return None
            
            data = self.prepare_features(data)
            latest_data = data[self.feature_columns].iloc[-1:].dropna()
            
            if len(latest_data) == 0:
                logging.warning("No valid data for prediction")
                return None
            
            if self.model_type == 'LogisticRegression':
                latest_scaled = self.scaler.transform(latest_data)
                prediction = self.model.predict(latest_scaled)[0]
                probability = self.model.predict_proba(latest_scaled)[0]
            else:
                prediction = self.model.predict(latest_data)[0]
                probability = self.model.predict_proba(latest_data)[0]
            
            return {
                'prediction': prediction,
                'probability_down': probability[0],
                'probability_up': probability[1],
                'confidence': max(probability)
            }
            
        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            return None
    
    def get_feature_importance(self):
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            return None
        
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def evaluate_model(self, data):
        try:
            data = self.prepare_features(data)
            clean_data = data[self.feature_columns + ['Target']].dropna()
            
            if len(clean_data) < 30:
                return None
            
            X = clean_data[self.feature_columns]
            y = clean_data['Target']
            
            if self.model_type == 'LogisticRegression':
                X_scaled = self.scaler.transform(X)
                predictions = self.model.predict(X_scaled)
            else:
                predictions = self.model.predict(X)
            
            accuracy = accuracy_score(y, predictions)
            
            return {
                'accuracy': accuracy,
                'total_predictions': len(predictions),
                'correct_predictions': sum(predictions == y)
            }
            
        except Exception as e:
            logging.error(f"Error evaluating model: {e}")
            return None
