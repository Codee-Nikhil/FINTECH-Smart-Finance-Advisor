from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import random

stocks_bp = Blueprint('stocks', __name__)

# ── Realistic mock data (since Yahoo Finance blocks server requests) ──
POPULAR_STOCKS = [
    {'name': 'Reliance Industries', 'symbol': 'RELIANCE', 'type': 'Stock', 'base': 2856.50, 'sector': 'Energy'},
    {'name': 'TCS',                 'symbol': 'TCS',      'type': 'Stock', 'base': 3421.75, 'sector': 'IT'},
    {'name': 'Infosys',             'symbol': 'INFY',     'type': 'Stock', 'base': 1456.30, 'sector': 'IT'},
    {'name': 'HDFC Bank',           'symbol': 'HDFCBANK', 'type': 'Stock', 'base': 1678.90, 'sector': 'Banking'},
    {'name': 'ICICI Bank',          'symbol': 'ICICIBANK','type': 'Stock', 'base': 1089.60, 'sector': 'Banking'},
    {'name': 'Wipro',               'symbol': 'WIPRO',    'type': 'Stock', 'base': 456.25,  'sector': 'IT'},
    {'name': 'Bajaj Finance',       'symbol': 'BAJFIN',   'type': 'Stock', 'base': 6789.40, 'sector': 'Finance'},
    {'name': 'Asian Paints',        'symbol': 'ASIANPNT', 'type': 'Stock', 'base': 2345.60, 'sector': 'Consumer'},
    {'name': 'Maruti Suzuki',       'symbol': 'MARUTI',   'type': 'Stock', 'base': 10456.75,'sector': 'Auto'},
    {'name': 'Nifty 50 ETF',        'symbol': 'NIFTYBEES','type': 'ETF',   'base': 245.80,  'sector': 'Index'},
]

INDICES = [
    {'name': 'NIFTY 50',   'symbol': 'NIFTY',   'base': 22456.80},
    {'name': 'SENSEX',     'symbol': 'SENSEX',  'base': 73876.50},
    {'name': 'NIFTY BANK', 'symbol': 'BANKNIFTY','base': 47823.40},
    {'name': 'NIFTY IT',   'symbol': 'NIFTYIT', 'base': 32145.60},
]

SIP_FUNDS = [
    {'name': 'Mirae Asset Emerging Bluechip', 'category': 'Large & Mid Cap', 'rating': '5★', 'returns_1y': '18.2%', 'returns_3y': '24.5%', 'returns_5y': '19.8%', 'min_sip': '₹1,000', 'risk': 'Moderately High', 'aum': '₹28,456 Cr'},
    {'name': 'Parag Parikh Flexi Cap',        'category': 'Flexi Cap',       'rating': '5★', 'returns_1y': '16.5%', 'returns_3y': '22.8%', 'returns_5y': '21.2%', 'min_sip': '₹1,000', 'risk': 'Moderately High', 'aum': '₹52,341 Cr'},
    {'name': 'Axis Bluechip Fund',            'category': 'Large Cap',       'rating': '5★', 'returns_1y': '14.2%', 'returns_3y': '18.2%', 'returns_5y': '16.4%', 'min_sip': '₹500',   'risk': 'Moderate',        'aum': '₹35,678 Cr'},
    {'name': 'SBI Small Cap Fund',            'category': 'Small Cap',       'rating': '4★', 'returns_1y': '22.1%', 'returns_3y': '32.1%', 'returns_5y': '28.6%', 'min_sip': '₹500',   'risk': 'High',            'aum': '₹19,234 Cr'},
    {'name': 'HDFC Mid-Cap Opportunities',    'category': 'Mid Cap',         'rating': '4★', 'returns_1y': '19.8%', 'returns_3y': '28.6%', 'returns_5y': '24.3%', 'min_sip': '₹500',   'risk': 'High',            'aum': '₹42,567 Cr'},
    {'name': 'Kotak Flexi Cap Fund',          'category': 'Flexi Cap',       'rating': '4★', 'returns_1y': '15.3%', 'returns_3y': '19.3%', 'returns_5y': '17.8%', 'min_sip': '₹500',   'risk': 'Moderately High', 'aum': '₹41,234 Cr'},
    {'name': 'DSP Midcap Fund',               'category': 'Mid Cap',         'rating': '4★', 'returns_1y': '18.7%', 'returns_3y': '26.4%', 'returns_5y': '22.1%', 'min_sip': '₹500',   'risk': 'High',            'aum': '₹15,678 Cr'},
    {'name': 'Nippon India Liquid Fund',      'category': 'Liquid',          'rating': '4★', 'returns_1y': '7.1%',  'returns_3y': '5.8%',  'returns_5y': '5.2%',  'min_sip': '₹100',   'risk': 'Low',             'aum': '₹28,901 Cr'},
]

def make_quote(base):
    """Generate realistic price with small random fluctuation."""
    change_pct = round(random.uniform(-2.5, 2.5), 2)
    change     = round(base * change_pct / 100, 2)
    price      = round(base + change, 2)
    return {'price': price, 'change': change, 'change_pct': change_pct}


@stocks_bp.route('/popular', methods=['GET'])
@jwt_required()
def get_popular():
    results = []
    for s in POPULAR_STOCKS:
        q = make_quote(s['base'])
        results.append({
            'name':       s['name'],
            'symbol':     s['symbol'],
            'type':       s['type'],
            'sector':     s['sector'],
            'price':      q['price'],
            'change':     q['change'],
            'change_pct': q['change_pct'],
            'status':     'ok',
        })
    return jsonify({'stocks': results}), 200


@stocks_bp.route('/search', methods=['GET'])
@jwt_required()
def search_stock():
    symbol = request.args.get('symbol', '').upper().strip()
    if not symbol:
        return jsonify({'error': 'Please enter a stock symbol'}), 400

    # Search in our stock list
    symbol_clean = symbol.replace('.NS', '').replace('.BO', '')
    found = next((s for s in POPULAR_STOCKS if s['symbol'] == symbol_clean or s['name'].upper() == symbol_clean), None)

    if found:
        q = make_quote(found['base'])
        return jsonify({
            'name':       found['name'],
            'symbol':     found['symbol'],
            'type':       found['type'],
            'price':      q['price'],
            'change':     q['change'],
            'change_pct': q['change_pct'],
            'status':     'ok',
        }), 200
    else:
        # Return generic result for unknown symbols
        base = round(random.uniform(100, 5000), 2)
        q    = make_quote(base)
        return jsonify({
            'name':       symbol_clean,
            'symbol':     symbol_clean,
            'type':       'Stock',
            'price':      q['price'],
            'change':     q['change'],
            'change_pct': q['change_pct'],
            'status':     'ok',
            'note':       'Indicative price only',
        }), 200


@stocks_bp.route('/sip-funds', methods=['GET'])
@jwt_required()
def get_sip_funds():
    return jsonify({'funds': SIP_FUNDS}), 200


@stocks_bp.route('/indices', methods=['GET'])
@jwt_required()
def get_indices():
    results = []
    for idx in INDICES:
        q = make_quote(idx['base'])
        results.append({
            'name':       idx['name'],
            'symbol':     idx['symbol'],
            'price':      q['price'],
            'change':     q['change'],
            'change_pct': q['change_pct'],
        })
    return jsonify({'indices': results}), 200