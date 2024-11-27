from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Portfolio storage (in-memory for MVP)
portfolio = []

# API keys loaded from .env file
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')

print (ALPHA_VANTAGE_API_KEY)
print (COINGECKO_API_KEY)
# API URLs
ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


def get_stock_price(symbol):
    """Fetch current stock price using a free API (e.g., Yahoo Finance API via RapidAPI)."""
    url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}'
    response = requests.get(url).json()
    try:
        return float(response['quoteResponse']['result'][0]['regularMarketPrice'])
    except (KeyError, IndexError):
        return None

def get_crypto_price(symbol):
    """Fetch current cryptocurrency price using CoinGecko API."""
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
    response = requests.get(url).json()
    return response.get(symbol, {}).get('usd', None)

@app.route('/')
def index():
    """Homepage with input form."""
    return render_template('index.html')

@app.route('/add_asset', methods=['POST'])
def add_asset():
    """Add an asset to the portfolio."""
    asset = request.form.to_dict()
    asset['purchase_date'] = datetime.strptime(asset['purchase_date'], '%Y-%m-%d').date()
    portfolio.append(asset)
    return jsonify({"message": "Asset added successfully!", "portfolio": portfolio})

@app.route('/portfolio', methods=['GET'])
def view_portfolio():
    """Calculate and display portfolio performance."""
    total_value = 0
    details = []

    for asset in portfolio:
        symbol = asset['symbol']
        asset_type = asset['asset_type']
        purchase_price = float(asset['purchase_price'])
        units = float(asset['units'])
        current_price = None

        if asset_type == 'stock':
            current_price = get_stock_price(symbol)
        elif asset_type == 'crypto':
            current_price = get_crypto_price(symbol)

        if current_price:
            current_value = units * current_price
            total_value += current_value
            absolute_change = current_value - (units * purchase_price)
            percentage_change = (absolute_change / (units * purchase_price)) * 100
            details.append({
                "symbol": symbol,
                "current_value": current_value,
                "absolute_change": absolute_change,
                "percentage_change": percentage_change
            })

    return render_template('portfolio.html', details=details, total_value=total_value)

if __name__ == '__main__':
    app.run(debug=True)
