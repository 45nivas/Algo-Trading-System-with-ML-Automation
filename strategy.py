import pandas as pd
import numpy as np
import logging
from datetime import datetime
from utils import add_technical_indicators
import config

class TradingStrategy:
    def __init__(self, rsi_oversold=30, ma_short=20, ma_long=50):
        self.rsi_oversold = rsi_oversold
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.trades = []
        self.portfolio_value = 100000
        self.position = None
        
    def generate_signals(self, data):
        data = add_technical_indicators(data)
        signals = []
        
        for i in range(1, len(data)):
            if (data['RSI'].iloc[i] < self.rsi_oversold and 
                data['MA20'].iloc[i] > data['MA50'].iloc[i] and
                data['MA20'].iloc[i-1] <= data['MA50'].iloc[i-1] and
                not pd.isna(data['RSI'].iloc[i]) and
                not pd.isna(data['MA20'].iloc[i]) and
                not pd.isna(data['MA50'].iloc[i])):
                
                signals.append({
                    'date': data.index[i],
                    'signal': 'BUY',
                    'price': data['Close'].iloc[i],
                    'rsi': data['RSI'].iloc[i],
                    'ma20': data['MA20'].iloc[i],
                    'ma50': data['MA50'].iloc[i]
                })
                
            elif (data['RSI'].iloc[i] > 70 and 
                  not pd.isna(data['RSI'].iloc[i])):
                
                signals.append({
                    'date': data.index[i],
                    'signal': 'SELL',
                    'price': data['Close'].iloc[i],
                    'rsi': data['RSI'].iloc[i],
                    'ma20': data['MA20'].iloc[i],
                    'ma50': data['MA50'].iloc[i]
                })
                
        return signals
    
    def backtest(self, data, ticker):
        signals = self.generate_signals(data)
        trades = []
        current_position = None
        
        for signal in signals:
            if signal['signal'] == 'BUY' and current_position is None:
                current_position = {
                    'entry_date': signal['date'],
                    'entry_price': signal['price'],
                    'ticker': ticker,
                    'quantity': self.portfolio_value // signal['price']
                }
                
            elif signal['signal'] == 'SELL' and current_position is not None:
                exit_price = signal['price']
                pnl = (exit_price - current_position['entry_price']) * current_position['quantity']
                
                trades.append({
                    'ticker': ticker,
                    'entry_date': current_position['entry_date'],
                    'exit_date': signal['date'],
                    'entry_price': current_position['entry_price'],
                    'exit_price': exit_price,
                    'quantity': current_position['quantity'],
                    'pnl': pnl,
                    'return_pct': (exit_price - current_position['entry_price']) / current_position['entry_price'] * 100
                })
                
                self.portfolio_value += pnl
                current_position = None
        
        logging.info(f"Backtest completed for {ticker}. Generated {len(trades)} trades.")
        return trades, signals
    
    def calculate_metrics(self, trades):
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_return': 0,
                'max_drawdown': 0
            }
            
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        total_pnl = sum([t['pnl'] for t in trades])
        avg_return = np.mean([t['return_pct'] for t in trades])
        
        cumulative_returns = np.cumsum([t['pnl'] for t in trades])
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / peak * 100
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_return': avg_return,
            'max_drawdown': max_drawdown,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades
        }
