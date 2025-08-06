import requests
import logging
from datetime import datetime
import config

class TelegramBot:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message):
        try:
            if self.bot_token == 'YOUR_TELEGRAM_BOT_TOKEN' or self.chat_id == 'YOUR_CHAT_ID':
                logging.info(f"Mock Telegram message: {message}")
                return True
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                logging.info("Telegram message sent successfully")
                return True
            else:
                logging.error(f"Failed to send Telegram message: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_trade_signal(self, signal, ticker):
        emoji = "🟢" if signal['signal'] == 'BUY' else "🔴"
        
        message = f"""
{emoji} <b>Trading Signal Alert</b> {emoji}

<b>Ticker:</b> {ticker}
<b>Signal:</b> {signal['signal']}
<b>Price:</b> ₹{signal['price']:.2f}
<b>RSI:</b> {signal['rsi']:.2f}
<b>MA20:</b> ₹{signal['ma20']:.2f}
<b>MA50:</b> ₹{signal['ma50']:.2f}
<b>Time:</b> {signal['date'].strftime('%Y-%m-%d %H:%M:%S')}

<i>Algo Trading System</i>
        """
        
        return self.send_message(message.strip())
    
    def send_trade_executed(self, trade):
        emoji = "✅" if trade['pnl'] > 0 else "❌"
        
        message = f"""
{emoji} <b>Trade Executed</b> {emoji}

<b>Ticker:</b> {trade['ticker']}
<b>Entry:</b> ₹{trade['entry_price']:.2f} on {trade['entry_date'].strftime('%Y-%m-%d')}
<b>Exit:</b> ₹{trade['exit_price']:.2f} on {trade['exit_date'].strftime('%Y-%m-%d')}
<b>Quantity:</b> {trade['quantity']}
<b>P&L:</b> ₹{trade['pnl']:.2f}
<b>Return:</b> {trade['return_pct']:.2f}%

<i>Algo Trading System</i>
        """
        
        return self.send_message(message.strip())
    
    def send_ml_prediction(self, prediction, ticker):
        direction = "📈 UP" if prediction['prediction'] == 1 else "📉 DOWN"
        confidence_emoji = "🔥" if prediction['confidence'] > 0.7 else "⚡"
        
        message = f"""
{confidence_emoji} <b>ML Prediction</b> {confidence_emoji}

<b>Ticker:</b> {ticker}
<b>Prediction:</b> {direction}
<b>Confidence:</b> {prediction['confidence']:.2%}
<b>Prob Up:</b> {prediction['probability_up']:.2%}
<b>Prob Down:</b> {prediction['probability_down']:.2%}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>AI-Powered Trading System</i>
        """
        
        return self.send_message(message.strip())
    
    def send_daily_summary(self, metrics):
        win_rate_emoji = "🎯" if metrics['win_rate'] > 60 else "📊"
        pnl_emoji = "💰" if metrics['total_pnl'] > 0 else "💸"
        
        message = f"""
{win_rate_emoji} <b>Daily Trading Summary</b> {win_rate_emoji}

<b>Total Trades:</b> {metrics['total_trades']}
<b>Win Rate:</b> {metrics['win_rate']:.1f}%
<b>Winning Trades:</b> {metrics['winning_trades']}
<b>Losing Trades:</b> {metrics['losing_trades']}

{pnl_emoji} <b>Financial Performance:</b>
<b>Total P&L:</b> ₹{metrics['total_pnl']:.2f}
<b>Avg Return:</b> {metrics['avg_return']:.2f}%
<b>Max Drawdown:</b> {metrics['max_drawdown']:.2f}%

<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}
<i>Algo Trading System</i>
        """
        
        return self.send_message(message.strip())
    
    def send_error_alert(self, error_message, module_name):
        message = f"""
🚨 <b>System Error Alert</b> 🚨

<b>Module:</b> {module_name}
<b>Error:</b> {error_message}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>Please check the system logs</i>
        """
        
        return self.send_message(message.strip())
    
    def send_system_startup(self):
        message = f"""
🚀 <b>Algo Trading System Started</b> 🚀

<b>Status:</b> Online
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
<b>Monitoring:</b> {', '.join(config.NIFTY_STOCKS)}

<i>Ready for trading signals!</i>
        """
        
        return self.send_message(message.strip())

class MockTelegramBot:
    def __init__(self, *args, **kwargs):
        logging.info("Using mock Telegram bot (token not configured)")
    
    def send_message(self, message):
        logging.info(f"Mock Telegram: {message[:100]}...")
        return True
    
    def send_trade_signal(self, signal, ticker):
        logging.info(f"Mock Telegram: {signal['signal']} signal for {ticker}")
        return True
    
    def send_trade_executed(self, trade):
        logging.info(f"Mock Telegram: Trade executed for {trade['ticker']}")
        return True
    
    def send_ml_prediction(self, prediction, ticker):
        logging.info(f"Mock Telegram: ML prediction for {ticker}")
        return True
    
    def send_daily_summary(self, metrics):
        logging.info("Mock Telegram: Daily summary sent")
        return True
    
    def send_error_alert(self, error_message, module_name):
        logging.info(f"Mock Telegram: Error in {module_name}")
        return True
    
    def send_system_startup(self):
        logging.info("Mock Telegram: System startup notification")
        return True
