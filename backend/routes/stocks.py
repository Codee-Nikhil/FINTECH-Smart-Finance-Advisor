from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import urllib.request
import json

stocks_bp = Blueprint('stocks', __name__)

# Top Indian Mutual Funds & ETFs with their Yahoo Finance symbols
POPULAR_FUNDS = [
    {'name': 'Nifty 50 ETF (Nippon)',        'symbol': 'NIFTYBEES.NS',  'type': 'ETF'},
    {'name': 'SBI Nifty Index Fund',          'symbol': 'SETFNIF50.NS', 'type': 'ETF'},
    {'name': 'Mirae Asset Large Cap',         'symbol': 'MIRAEASSET.NS','type': 'MF'},
    {'name': 'HDFC Top 100 Fund',             'symbol': 'HDFCTOP100.NS','type': 'MF'},
    {'name': 'Reliance Industries',           'symbol': 'RELIANCE.NS',  'type': 'Stock'},
    {'name': 'TCS',                           'symbol': 'TCS.NS',       'type': 'Stock'},
    {'name': 'Infosys',                       'symbol': 'INFY.NS',      'type': 'Stock'},
    {'name': 'HDFC Bank',                     'symbol': 'HDFCBANK.NS',  'type': 'Stock'},
    {'name': 'Wipro',                         'symbol': 'WIPRO.NS',     'type': 'Stock'},
    {'name': 'ICICI Bank',                    'symbol': 'ICICIBANK.NS', 'type': 'Stock'},
]

def fetch_quote(symbol):
    """Fetch stock quote from Yahoo Finance API."""
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d'
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read())
        meta   = data['chart']['result'][0]['meta']
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        current = meta.get('regularMarketPrice', closes[-1] if closes else 0)
        prev    = closes[-2] if len(closes) >= 2 else current
        change  = current - prev
        pct     = (change / prev * 100) if prev else 0
        return {
            'symbol':   symbol,
            'price':    round(current, 2),
            'change':   round(change, 2),
            'change_pct': round(pct, 2),
            'currency': meta.get('currency', 'INR'),
            'status':   'ok',
        }
    except Exception as e:
        return {'symbol': symbol, 'status': 'error', 'error': str(e)}


@stocks_bp.route('/popular', methods=['GET'])
@jwt_required()
def get_popular():
    """Return list of popular Indian stocks/funds with live prices."""
    results = []
    for fund in POPULAR_FUNDS:
        quote = fetch_quote(fund['symbol'])
        results.append({**fund, **quote})
    return jsonify({'stocks': results}), 200


@stocks_bp.route('/search', methods=['GET'])
@jwt_required()
def search_stock():
    """Search for any stock by symbol e.g. RELIANCE.NS"""
    symbol = request.args.get('symbol', '').upper().strip()
    if not symbol:
        return jsonify({'error': 'Symbol is required e.g. RELIANCE.NS'}), 400
    if '.NS' not in symbol and '.BO' not in symbol:
        symbol = symbol + '.NS'
    quote = fetch_quote(symbol)
    return jsonify(quote), 200


@stocks_bp.route('/sip-funds', methods=['GET'])
@jwt_required()
def get_sip_funds():
    """Return curated list of top SIP fund recommendations."""
    funds = [
        {'name': 'Mirae Asset Emerging Bluechip', 'category': 'Large & Mid Cap', 'rating': '5★', 'returns_3y': '24.5%', 'min_sip': '₹1,000', 'risk': 'Moderately High'},
        {'name': 'Axis Bluechip Fund',             'category': 'Large Cap',       'rating': '5★', 'returns_3y': '18.2%', 'min_sip': '₹500',   'risk': 'Moderate'},
        {'name': 'Parag Parikh Flexi Cap',         'category': 'Flexi Cap',       'rating': '5★', 'returns_3y': '22.8%', 'min_sip': '₹1,000', 'risk': 'Moderately High'},
        {'name': 'SBI Small Cap Fund',             'category': 'Small Cap',       'rating': '4★', 'returns_3y': '32.1%', 'min_sip': '₹500',   'risk': 'High'},
        {'name': 'HDFC Mid-Cap Opportunities',     'category': 'Mid Cap',         'rating': '4★', 'returns_3y': '28.6%', 'min_sip': '₹500',   'risk': 'High'},
        {'name': 'Nippon India Liquid Fund',       'category': 'Liquid',          'rating': '4★', 'returns_3y': '5.8%',  'min_sip': '₹100',   'risk': 'Low'},
    ]
    return jsonify({'funds': funds}), 200
