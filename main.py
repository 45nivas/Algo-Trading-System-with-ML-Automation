import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import schedule
import time
import traceback

from data_ingestion import fetch_multiple_stocks
from strategy import TradingStrategy
from ml_model import MLPredictor
from google_sheets_logger import GoogleSheetsLogger, MockGoogleSheetsLogger
from telegram_bot import TelegramBot, MockTelegramBot
import config

class AlgoTradingSystem:
    def __init__(self):
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler('trading_system.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
        self.strategy = TradingStrategy(
            rsi_oversold=config.RSI_OVERSOLD,
            ma_short=config.MA_SHORT,
            ma_long=config.MA_LONG
        )
        
        self.ml_predictor = MLPredictor(model_type=config.ML_MODEL_TYPE)
        
        try:
            self.sheets_logger = GoogleSheetsLogger()
        except:
            self.logger.warning("Using mock Google Sheets logger")
            self.sheets_logger = MockGoogleSheetsLogger()
        
        try:
            self.telegram_bot = TelegramBot()
        except:
            self.logger.warning("Using mock Telegram bot")
            self.telegram_bot = MockTelegramBot()
        
        self.all_trades = []
        self.all_signals = []
        self.ml_predictions = []
        
        self.logger.info("Algo Trading System initialized successfully")
    
    def fetch_stock_data(self):
        self.logger.info("Fetching stock data...")
        
        try:
            stock_data = fetch_multiple_stocks(
                config.NIFTY_STOCKS,
                period=config.DATA_PERIOD,
                interval=config.DATA_INTERVAL
            )
            
            valid_data = {ticker: data for ticker, data in stock_data.items() if data is not None}
            
            self.logger.info(f"Successfully fetched data for {len(valid_data)} stocks")
            return valid_data
            
        except Exception as e:
            self.logger.error(f"Error fetching stock data: {e}")
            self.telegram_bot.send_error_alert(str(e), "Data Fetching")
            return {}
    
    def run_strategy_analysis(self, stock_data):
        self.logger.info("Running strategy analysis...")
        
        all_trades = []
        all_signals = []
        
        try:
            for ticker, data in stock_data.items():
                if data is None or len(data) < 100:
                    self.logger.warning(f"Insufficient data for {ticker}")
                    continue
                
                self.logger.info(f"Analyzing {ticker}...")
                
                trades, signals = self.strategy.backtest(data, ticker)
                
                all_trades.extend(trades)
                all_signals.extend(signals)
                
                recent_signals = [s for s in signals if s['date'] >= datetime.now() - timedelta(days=1)]
                for signal in recent_signals:
                    self.telegram_bot.send_trade_signal(signal, ticker)
            
            self.all_trades = all_trades
            self.all_signals = all_signals
            
            self.logger.info(f"Strategy analysis completed. {len(all_trades)} trades, {len(all_signals)} signals")
            return all_trades, all_signals
            
        except Exception as e:
            self.logger.error(f"Error in strategy analysis: {e}")
            self.telegram_bot.send_error_alert(str(e), "Strategy Analysis")
            return [], []
    
    def run_ml_analysis(self, stock_data):
        self.logger.info("Running ML analysis...")
        
        predictions = []
        
        try:
            for ticker, data in stock_data.items():
                if data is None or len(data) < 100:
                    continue
                
                self.logger.info(f"Training ML model for {ticker}...")
                
                if self.ml_predictor.train_model(data):
                    prediction = self.ml_predictor.predict(data)
                    
                    if prediction:
                        prediction['ticker'] = ticker
                        predictions.append(prediction)
                        
                        self.telegram_bot.send_ml_prediction(prediction, ticker)
                        
                        self.logger.info(f"ML prediction for {ticker}: "
                                       f"{'UP' if prediction['prediction'] == 1 else 'DOWN'} "
                                       f"(Confidence: {prediction['confidence']:.2%})")
                
                importance = self.ml_predictor.get_feature_importance()
                if importance is not None:
                    self.logger.info(f"Feature importance for {ticker}:\n{importance}")
            
            self.ml_predictions = predictions
            
            if predictions:
                avg_confidence = np.mean([p['confidence'] for p in predictions])
                self.logger.info(f"Average ML prediction confidence: {avg_confidence:.2%}")
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error in ML analysis: {e}")
            self.telegram_bot.send_error_alert(str(e), "ML Analysis")
            return []
    
    def calculate_and_log_metrics(self):
        self.logger.info("Calculating and logging metrics...")
        
        try:
            strategy_metrics = self.strategy.calculate_metrics(self.all_trades)
            
            ml_metrics = None
            if self.ml_predictions:
                ml_metrics = {
                    'accuracy': self.ml_predictor.accuracy,
                    'total_predictions': len(self.ml_predictions),
                    'avg_confidence': np.mean([p['confidence'] for p in self.ml_predictions])
                }
            
            self.sheets_logger.log_trades(self.all_trades)
            self.sheets_logger.log_signals(self.all_signals)
            self.sheets_logger.log_summary(strategy_metrics, ml_metrics)
            self.sheets_logger.log_ml_predictions(self.ml_predictions)
            
            self.telegram_bot.send_daily_summary(strategy_metrics)
            
            self.print_summary(strategy_metrics, ml_metrics)
            
            return strategy_metrics, ml_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            self.telegram_bot.send_error_alert(str(e), "Metrics Calculation")
            return None, None
    
    def print_summary(self, strategy_metrics, ml_metrics):
        print("\n" + "="*60)
        print("ALGO TRADING SYSTEM - COMPREHENSIVE SUMMARY")
        print("="*60)
        
        print(f"\n📊 STRATEGY PERFORMANCE:")
        print(f"  Total Trades: {strategy_metrics['total_trades']}")
        print(f"  Win Rate: {strategy_metrics['win_rate']:.2f}%")
        print(f"  Winning Trades: {strategy_metrics['winning_trades']}")
        print(f"  Losing Trades: {strategy_metrics['losing_trades']}")
        print(f"  Total P&L: ₹{strategy_metrics['total_pnl']:.2f}")
        print(f"  Average Return: {strategy_metrics['avg_return']:.2f}%")
        print(f"  Max Drawdown: {strategy_metrics['max_drawdown']:.2f}%")
        
        if ml_metrics:
            print(f"\n🤖 ML MODEL PERFORMANCE:")
            print(f"  Model Accuracy: {ml_metrics['accuracy']:.4f}")
            print(f"  Total Predictions: {ml_metrics['total_predictions']}")
            print(f"  Average Confidence: {ml_metrics.get('avg_confidence', 0):.2%}")
        
        print(f"\n📈 SIGNALS GENERATED:")
        print(f"  Total Signals: {len(self.all_signals)}")
        buy_signals = len([s for s in self.all_signals if s['signal'] == 'BUY'])
        sell_signals = len([s for s in self.all_signals if s['signal'] == 'SELL'])
        print(f"  Buy Signals: {buy_signals}")
        print(f"  Sell Signals: {sell_signals}")
        
        print(f"\n📱 AUTOMATION STATUS:")
        print(f"  Google Sheets: {'✅ Connected' if isinstance(self.sheets_logger, GoogleSheetsLogger) else '❌ Mock Mode'}")
        print(f"  Telegram Bot: {'✅ Connected' if isinstance(self.telegram_bot, TelegramBot) else '❌ Mock Mode'}")
        
        print(f"\n⏰ LAST UPDATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
    
    def run_full_analysis(self):
        self.logger.info("Starting full analysis pipeline...")
        
        try:
            self.telegram_bot.send_system_startup()
            
            stock_data = self.fetch_stock_data()
            
            if not stock_data:
                self.logger.error("No stock data available")
                return
            
            trades, signals = self.run_strategy_analysis(stock_data)
            
            predictions = self.run_ml_analysis(stock_data)
            
            strategy_metrics, ml_metrics = self.calculate_and_log_metrics()
            
            self.logger.info("Full analysis pipeline completed successfully")
            
            return {
                'strategy_metrics': strategy_metrics,
                'ml_metrics': ml_metrics,
                'trades': trades,
                'signals': signals,
                'predictions': predictions
            }
            
        except Exception as e:
            self.logger.error(f"Error in full analysis: {e}")
            self.logger.error(traceback.format_exc())
            self.telegram_bot.send_error_alert(str(e), "Full Analysis")
            return None
    
    def schedule_analysis(self):
        self.logger.info("Setting up scheduled analysis...")
        
        schedule.every().day.at("09:30").do(self.run_full_analysis)
        
        schedule.every().day.at("15:30").do(self.run_full_analysis)
        
        self.logger.info("Scheduled analysis setup complete")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    print("🚀 Starting Algo Trading System with ML & Automation")
    print("=" * 60)
    
    system = AlgoTradingSystem()
    
    print("\n📊 Running immediate analysis...")
    results = system.run_full_analysis()
    
    if results:
        print("\n✅ Analysis completed successfully!")
        print("📋 Check Google Sheets for detailed logs")
        print("📱 Check Telegram for real-time alerts")
    else:
        print("\n❌ Analysis failed. Check logs for details.")

if __name__ == "__main__":
    main()
