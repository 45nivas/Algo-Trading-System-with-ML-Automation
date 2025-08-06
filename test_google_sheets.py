"""
test_google_sheets.py
Simple test script for Google Sheets Logger functionality
"""
import sys
import logging
from datetime import datetime
from google_sheets_logger import GoogleSheetsLogger, MockGoogleSheetsLogger

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_google_sheets_logger():
    """Test the Google Sheets Logger with sample data."""
    print("🔧 Testing Google Sheets Logger...")
    print("="*50)
    
    # Initialize logger (will use mock if credentials not available)
    try:
        logger = GoogleSheetsLogger()
        is_mock = False
        print("✅ Google Sheets Logger initialized successfully!")
    except Exception as e:
        print(f"⚠️  Using mock logger due to: {e}")
        logger = MockGoogleSheetsLogger()
        is_mock = True
    
    # Sample trade data
    sample_trades = [
        {
            'ticker': 'TCS.NS',
            'entry_date': datetime(2025, 8, 1),
            'exit_date': datetime(2025, 8, 5),
            'entry_price': 3500.0,
            'exit_price': 3650.0,
            'quantity': 10,
            'pnl': 1500.0,
            'return_pct': 4.29
        },
        {
            'ticker': 'INFY.NS',
            'entry_date': datetime(2025, 8, 2),
            'exit_date': datetime(2025, 8, 6),
            'entry_price': 1800.0,
            'exit_price': 1750.0,
            'quantity': 20,
            'pnl': -1000.0,
            'return_pct': -2.78
        }
    ]
    
    # Sample signal data
    sample_signals = [
        {
            'date': datetime(2025, 8, 6, 9, 30),
            'signal': 'BUY',
            'price': 3600.0,
            'rsi': 35.5,
            'ma20': 3580.0,
            'ma50': 3520.0
        },
        {
            'date': datetime(2025, 8, 6, 14, 30),
            'signal': 'SELL',
            'price': 1755.0,
            'rsi': 68.2,
            'ma20': 1760.0,
            'ma50': 1740.0
        }
    ]
    
    # Sample metrics
    sample_metrics = {
        'total_trades': 2,
        'win_rate': 50.0,
        'total_pnl': 500.0,
        'avg_return': 0.76,
        'max_drawdown': 2.78,
        'winning_trades': 1,
        'losing_trades': 1
    }
    
    # Sample ML predictions
    sample_predictions = [
        {
            'ticker': 'TCS.NS',
            'prediction': 1,
            'confidence': 0.78,
            'probability_up': 0.78,
            'probability_down': 0.22
        },
        {
            'ticker': 'INFY.NS',
            'prediction': 0,
            'confidence': 0.65,
            'probability_up': 0.35,
            'probability_down': 0.65
        }
    ]
    
    print(f"\n📊 Testing with sample data:")
    print(f"   - {len(sample_trades)} trades")
    print(f"   - {len(sample_signals)} signals")
    print(f"   - {len(sample_predictions)} ML predictions")
    
    # Test logging functions
    print(f"\n🔄 Running logging tests...")
    
    try:
        print("   ✓ Logging trades...")
        logger.log_trades(sample_trades)
        
        print("   ✓ Logging signals...")
        logger.log_signals(sample_signals)
        
        print("   ✓ Logging summary...")
        logger.log_summary(sample_metrics)
        
        print("   ✓ Logging ML predictions...")
        logger.log_ml_predictions(sample_predictions)
        
        print(f"\n✅ All tests completed successfully!")
        
        if not is_mock:
            print(f"📊 Data has been logged to Google Sheets!")
            print(f"🔗 Check your Google Sheet: 'Algo_Trading_Logs'")
        else:
            print(f"📝 Mock mode: Check console logs above for simulated output")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

def show_setup_instructions():
    """Show setup instructions for Google Sheets integration."""
    print(f"\n📋 GOOGLE SHEETS SETUP INSTRUCTIONS:")
    print("="*50)
    print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
    print("2. Create a new project or select existing one")
    print("3. Enable APIs:")
    print("   - Google Sheets API")
    print("   - Google Drive API")
    print("4. Create Service Account:")
    print("   - Go to 'Credentials' → 'Create Credentials' → 'Service Account'")
    print("   - Download the JSON key file")
    print("   - Rename to 'credentials.json' and place in project folder")
    print("5. Create Google Sheet:")
    print("   - Create new sheet named 'Algo_Trading_Logs'")
    print("   - Share with service account email (from credentials.json)")
    print("   - Give 'Editor' permissions")
    print(f"\n🔧 Once setup is complete, run this script again to test real logging!")

def main():
    """Main function."""
    print("🚀 Google Sheets Logger Test")
    print("="*50)
    
    # Run the test
    success = test_google_sheets_logger()
    
    if success:
        show_setup_instructions()
    
    print(f"\n📝 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
