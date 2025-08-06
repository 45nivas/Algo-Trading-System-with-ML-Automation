import pandas as pd
import numpy as np
import logging

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    exp1 = data['Close'].ewm(span=fast).mean()
    exp2 = data['Close'].ewm(span=slow).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_moving_averages(data, short=20, long=50):
    ma_short = data['Close'].rolling(window=short).mean()
    ma_long = data['Close'].rolling(window=long).mean()
    return ma_short, ma_long

def calculate_bollinger_bands(data, period=20, std_dev=2):
    ma = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    upper_band = ma + (std * std_dev)
    lower_band = ma - (std * std_dev)
    return upper_band, ma, lower_band

def add_technical_indicators(data):
    data['RSI'] = calculate_rsi(data)
    data['MACD'], data['MACD_Signal'], data['MACD_Histogram'] = calculate_macd(data)
    data['MA20'], data['MA50'] = calculate_moving_averages(data)
    data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = calculate_bollinger_bands(data)
    return data

def calculate_returns(data):
    return data['Close'].pct_change()

def calculate_volatility(data, period=30):
    returns = calculate_returns(data)
    return returns.rolling(window=period).std() * np.sqrt(252)

def normalize_data(data):
    return (data - data.mean()) / data.std()
