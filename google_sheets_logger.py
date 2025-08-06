import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import logging
from datetime import datetime
import config

class GoogleSheetsLogger:
    def __init__(self, credentials_file=None, sheet_name=None):
        self.credentials_file = credentials_file or config.GOOGLE_CREDENTIALS_FILE
        self.sheet_name = sheet_name or config.GOOGLE_SHEET_NAME
        self.gc = None
        self.workbook = None
        self.setup_connection()
    
    def setup_connection(self):
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, scope
            )
            
            self.gc = gspread.authorize(creds)
            
            try:
                self.workbook = self.gc.open(self.sheet_name)
            except gspread.SpreadsheetNotFound:
                self.workbook = self.gc.create(self.sheet_name)
                logging.info(f"Created new spreadsheet: {self.sheet_name}")
            
            logging.info("Google Sheets connection established successfully")
            return True
            
        except FileNotFoundError:
            logging.error(f"Credentials file not found: {self.credentials_file}")
            logging.info("Please download credentials.json from Google Cloud Console")
            return False
        except Exception as e:
            logging.error(f"Error setting up Google Sheets connection: {e}")
            return False
    
    def create_or_get_worksheet(self, worksheet_name):
        try:
            worksheet = self.workbook.worksheet(worksheet_name)
            return worksheet
        except gspread.WorksheetNotFound:
            worksheet = self.workbook.add_worksheet(
                title=worksheet_name, rows="1000", cols="20"
            )
            logging.info(f"Created new worksheet: {worksheet_name}")
            return worksheet
    
    def log_trades(self, trades):
        if not trades:
            logging.info("No trades to log")
            return
        
        try:
            worksheet = self.create_or_get_worksheet("Trades")
            
            worksheet.clear()
            
            headers = ['Ticker', 'Entry Date', 'Exit Date', 'Entry Price', 
                      'Exit Price', 'Quantity', 'P&L', 'Return %']
            
            data = [headers]
            for trade in trades:
                data.append([
                    trade['ticker'],
                    trade['entry_date'].strftime('%Y-%m-%d') if hasattr(trade['entry_date'], 'strftime') else str(trade['entry_date']),
                    trade['exit_date'].strftime('%Y-%m-%d') if hasattr(trade['exit_date'], 'strftime') else str(trade['exit_date']),
                    f"{trade['entry_price']:.2f}",
                    f"{trade['exit_price']:.2f}",
                    trade['quantity'],
                    f"{trade['pnl']:.2f}",
                    f"{trade['return_pct']:.2f}%"
                ])
            
            worksheet.update('A1', data)
            logging.info(f"Logged {len(trades)} trades to Google Sheets")
            
        except Exception as e:
            logging.error(f"Error logging trades: {e}")
    
    def log_signals(self, signals):
        if not signals:
            logging.info("No signals to log")
            return
        
        try:
            worksheet = self.create_or_get_worksheet("Signals")
            
            worksheet.clear()
            
            headers = ['Date', 'Signal', 'Price', 'RSI', 'MA20', 'MA50']
            
            data = [headers]
            for signal in signals:
                data.append([
                    signal['date'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(signal['date'], 'strftime') else str(signal['date']),
                    signal['signal'],
                    f"{signal['price']:.2f}",
                    f"{signal['rsi']:.2f}" if signal['rsi'] else 'N/A',
                    f"{signal['ma20']:.2f}" if signal['ma20'] else 'N/A',
                    f"{signal['ma50']:.2f}" if signal['ma50'] else 'N/A'
                ])
            
            worksheet.update('A1', data)
            logging.info(f"Logged {len(signals)} signals to Google Sheets")
            
        except Exception as e:
            logging.error(f"Error logging signals: {e}")
    
    def log_summary(self, metrics, ml_metrics=None):
        try:
            worksheet = self.create_or_get_worksheet("Summary")
            
            worksheet.clear()
            
            data = [
                ['Metric', 'Value'],
                ['Total Trades', metrics.get('total_trades', 0)],
                ['Win Rate (%)', f"{metrics.get('win_rate', 0):.2f}"],
                ['Total P&L', f"{metrics.get('total_pnl', 0):.2f}"],
                ['Average Return (%)', f"{metrics.get('avg_return', 0):.2f}"],
                ['Max Drawdown (%)', f"{metrics.get('max_drawdown', 0):.2f}"],
                ['Winning Trades', metrics.get('winning_trades', 0)],
                ['Losing Trades', metrics.get('losing_trades', 0)],
                ['', ''],
                ['ML Model Metrics', ''],
            ]
            
            if ml_metrics:
                data.extend([
                    ['Model Accuracy', f"{ml_metrics.get('accuracy', 0):.4f}"],
                    ['Total Predictions', ml_metrics.get('total_predictions', 0)],
                    ['Correct Predictions', ml_metrics.get('correct_predictions', 0)]
                ])
            
            data.extend([
                ['', ''],
                ['Last Updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ])
            
            worksheet.update('A1', data)
            logging.info("Logged summary metrics to Google Sheets")
            
        except Exception as e:
            logging.error(f"Error logging summary: {e}")
    
    def log_ml_predictions(self, predictions):
        if not predictions:
            logging.info("No ML predictions to log")
            return
        
        try:
            worksheet = self.create_or_get_worksheet("ML_Predictions")
            
            try:
                existing_data = worksheet.get_all_values()
                if not existing_data or len(existing_data) == 0:
                    headers = ['Date', 'Ticker', 'Prediction', 'Confidence', 'Prob_Up', 'Prob_Down']
                    worksheet.update('A1', [headers])
                    next_row = 2
                else:
                    next_row = len(existing_data) + 1
            except:
                headers = ['Date', 'Ticker', 'Prediction', 'Confidence', 'Prob_Up', 'Prob_Down']
                worksheet.update('A1', [headers])
                next_row = 2
            
            new_data = []
            for pred in predictions:
                new_data.append([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    pred.get('ticker', 'N/A'),
                    'UP' if pred.get('prediction', 0) == 1 else 'DOWN',
                    f"{pred.get('confidence', 0):.4f}",
                    f"{pred.get('probability_up', 0):.4f}",
                    f"{pred.get('probability_down', 0):.4f}"
                ])
            
            if new_data:
                worksheet.update(f'A{next_row}', new_data)
                logging.info(f"Logged {len(new_data)} ML predictions to Google Sheets")
            
        except Exception as e:
            logging.error(f"Error logging ML predictions: {e}")

class MockGoogleSheetsLogger:
    def __init__(self, *args, **kwargs):
        logging.info("Using mock Google Sheets logger (credentials not available)")
    
    def log_trades(self, trades):
        logging.info(f"Mock: Would log {len(trades) if trades else 0} trades")
    
    def log_signals(self, signals):
        logging.info(f"Mock: Would log {len(signals) if signals else 0} signals")
    
    def log_summary(self, metrics, ml_metrics=None):
        logging.info("Mock: Would log summary metrics")
    
    def log_ml_predictions(self, predictions):
        logging.info(f"Mock: Would log {len(predictions) if predictions else 0} predictions")
