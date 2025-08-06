# Sample Google Sheets Setup Instructions

## Create Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Algo Trading System"
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create credentials:
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Name: "algo-trading-service"
   - Download the JSON key file
   - Rename it to `credentials.json` and place in project root

## Create Google Sheet

1. Create a new Google Sheet named: "Algo_Trading_Logs"
2. Share the sheet with the service account email (from credentials.json)
3. Give "Editor" permissions

## Sample Credentials File Structure

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "algo-trading-service@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/algo-trading-service%40your-project.iam.gserviceaccount.com"
}
```

## Telegram Bot Setup

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose bot name: "Algo Trading Bot"
4. Choose username: "your_algo_trading_bot"
5. Copy the bot token
6. Get your chat ID by messaging @userinfobot
7. Update config.py with both values

## Testing the Setup

Run this command to test Google Sheets connection:
```bash
python -c "from google_sheets_logger import GoogleSheetsLogger; logger = GoogleSheetsLogger(); print('✅ Google Sheets connected!')"
```

Run this command to test Telegram:
```bash
python -c "from telegram_bot import TelegramBot; bot = TelegramBot(); bot.send_message('Test message from algo trading system!')"
```
