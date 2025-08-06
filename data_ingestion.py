import yfinance as yf
import pandas as pd
import logging

def fetch_stock_data(ticker, period='6mo', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
        
        logging.info(f"Fetched data for {ticker}")
        return data
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return None

def fetch_multiple_stocks(tickers, period='6mo', interval='1d'):
    return {ticker: fetch_stock_data(ticker, period, interval) for ticker in tickers}
