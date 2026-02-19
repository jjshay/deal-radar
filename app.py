#!/usr/bin/env python3
"""
DEAL Radar - eBay Deal Finder for Flipping Authenticated Collectibles

A Flask application that searches eBay in real-time to find underpriced
authenticated items (signed memorabilia, vintage vinyl, space collectibles).

Author: John Shay
License: MIT
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import json
import base64
import requests

app = Flask(__name__, template_folder='templates')

# =============================================================================
# Configuration
# =============================================================================

def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

ENV = load_env()

# eBay API Configuration
EBAY_CLIENT_ID = ENV.get('EBAY_CLIENT_ID', '')
EBAY_CLIENT_SECRET = ENV.get('EBAY_CLIENT_SECRET', '')

# Default price range
DEFAULT_MIN_PRICE = 100
DEFAULT_MAX_PRICE = 700

# =============================================================================
# Deal Targets - Categories to search
# =============================================================================

DEAL_TARGETS = [
    # ===================
    # ART - Street Art
    # ===================
    {'query': 'Mr Brainwash signed print', 'min_price': 100, 'max_price': 500, 'category': 'Mr. Brainwash'},
    {'query': 'MBW signed print', 'min_price': 75, 'max_price': 400, 'category': 'Mr. Brainwash'},
    {'query': 'Shepard Fairey signed print', 'min_price': 75, 'max_price': 400, 'category': 'Shepard Fairey'},
    {'query': 'Obey Giant signed', 'min_price': 50, 'max_price': 300, 'category': 'Shepard Fairey'},
    {'query': 'Death NYC signed', 'min_price': 30, 'max_price': 80, 'category': 'Death NYC'},
    {'query': 'Death NYC framed', 'min_price': 40, 'max_price': 100, 'category': 'Death NYC'},
    {'query': 'Banksy signed print', 'min_price': 200, 'max_price': 1000, 'category': 'Banksy'},

    # ===================
    # ART - KAWS
    # ===================
    {'query': 'KAWS signed print', 'min_price': 200, 'max_price': 600, 'category': 'KAWS'},
    {'query': 'KAWS companion figure', 'min_price': 150, 'max_price': 400, 'category': 'KAWS'},
    {'query': 'KAWS limited edition', 'min_price': 200, 'max_price': 500, 'category': 'KAWS'},
    {'query': 'KAWS original fake', 'min_price': 150, 'max_price': 400, 'category': 'KAWS'},

    # ===================
    # BEARBRICK
    # ===================
    {'query': 'Bearbrick 1000%', 'min_price': 300, 'max_price': 700, 'category': 'Bearbrick'},
    {'query': 'Bearbrick 1000 KAWS', 'min_price': 400, 'max_price': 800, 'category': 'Bearbrick'},
    {'query': 'Medicom Bearbrick 1000', 'min_price': 300, 'max_price': 600, 'category': 'Bearbrick'},

    # ===================
    # NASA / SPACE
    # ===================
    {'query': 'Neil Armstrong signed', 'min_price': 500, 'max_price': 5000, 'category': 'NASA'},
    {'query': 'Buzz Aldrin signed photo', 'min_price': 100, 'max_price': 500, 'category': 'NASA'},
    {'query': 'Buzz Aldrin autograph COA', 'min_price': 150, 'max_price': 600, 'category': 'NASA'},
    {'query': 'Michael Collins signed', 'min_price': 200, 'max_price': 800, 'category': 'NASA'},
    {'query': 'Apollo 11 signed', 'min_price': 300, 'max_price': 2000, 'category': 'NASA'},
    {'query': 'Apollo astronaut signed', 'min_price': 100, 'max_price': 500, 'category': 'NASA'},
    {'query': 'NASA astronaut autograph COA', 'min_price': 75, 'max_price': 400, 'category': 'NASA'},
    {'query': 'Space Shuttle signed', 'min_price': 100, 'max_price': 500, 'category': 'NASA'},
    {'query': 'John Glenn signed', 'min_price': 150, 'max_price': 600, 'category': 'NASA'},
    {'query': 'astronaut signed photo JSA', 'min_price': 100, 'max_price': 400, 'category': 'NASA'},
    {'query': 'astronaut signed photo PSA', 'min_price': 100, 'max_price': 400, 'category': 'NASA'},

    # ===================
    # MUSIC - Signed Vinyl
    # ===================
    {'query': 'signed vinyl COA', 'min_price': 75, 'max_price': 300, 'category': 'Vinyl'},
    {'query': 'signed vinyl JSA', 'min_price': 100, 'max_price': 400, 'category': 'Vinyl'},
    {'query': 'signed vinyl BAS', 'min_price': 100, 'max_price': 400, 'category': 'Vinyl'},
    {'query': 'Taylor Swift signed vinyl', 'min_price': 100, 'max_price': 400, 'category': 'Vinyl'},
    {'query': 'Blink 182 signed', 'min_price': 150, 'max_price': 400, 'category': 'Vinyl'},
    {'query': 'Green Day signed', 'min_price': 150, 'max_price': 400, 'category': 'Vinyl'},

    # ===================
    # MUSIC - Pickguards
    # ===================
    {'query': 'signed pickguard COA', 'min_price': 75, 'max_price': 300, 'category': 'Pickguard'},
    {'query': 'autographed pickguard JSA', 'min_price': 100, 'max_price': 400, 'category': 'Pickguard'},
    {'query': 'signed guitar pickguard', 'min_price': 75, 'max_price': 350, 'category': 'Pickguard'},
]

# =============================================================================
# eBay Browse API
# =============================================================================

def get_browse_token():
    """Get client credentials token for eBay Browse API"""
    if not EBAY_CLIENT_ID or not EBAY_CLIENT_SECRET:
        return None

    credentials = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}"
    encoded_creds = base64.b64encode(credentials.encode()).decode()

    response = requests.post(
        'https://api.ebay.com/identity/v1/oauth2/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded_creds}'
        },
        data={
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
    )

    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def search_ebay(query, max_price, min_price=0, limit=20):
    """
    Search eBay for items using Browse API

    Args:
        query: Search keywords
        max_price: Maximum price filter
        min_price: Minimum price filter (helps filter fakes)
        limit: Number of results to return

    Returns:
        List of item dictionaries
    """
    token = get_browse_token()
    if not token:
        return []

    headers = {
        'Authorization': f'Bearer {token}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        'Content-Type': 'application/json'
    }

    # Build price filter
    if min_price > 0:
        price_filter = f'price:[{min_price}..{max_price}]'
    else:
        price_filter = f'price:[..{max_price}]'

    params = {
        'q': query,
        'filter': f'{price_filter},priceCurrency:USD,buyingOptions:{{FIXED_PRICE|AUCTION}}',
        'sort': 'price',
        'limit': limit
    }

    try:
        response = requests.get(
            'https://api.ebay.com/buy/browse/v1/item_summary/search',
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            return []

        data = response.json()
        items = data.get('itemSummaries', [])

        # Transform to simplified format
        deals = []
        for item in items:
            price_info = item.get('price', {})
            price = float(price_info.get('value', 0))

            if price <= 0 or price > max_price:
                continue

            deals.append({
                'id': item.get('itemId', ''),
                'title': item.get('title', 'Unknown'),
                'price': price,
                'image': item.get('image', {}).get('imageUrl', ''),
                'url': item.get('itemWebUrl', ''),
                'condition': item.get('condition', 'Unknown'),
                'seller': item.get('seller', {}).get('username', 'Unknown'),
                'buying_option': item.get('buyingOptions', [''])[0] if item.get('buyingOptions') else '',
                'location': item.get('itemLocation', {}).get('country', '')
            })

        return deals

    except Exception as e:
        print(f"Search error: {e}")
        return []

# =============================================================================
# Watchlist Management
# =============================================================================

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), 'watchlist.json')


def load_watchlist():
    """Load watchlist from JSON file"""
    try:
        if os.path.exists(WATCHLIST_FILE):
            with open(WATCHLIST_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_watchlist(items):
    """Save watchlist to JSON file"""
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(items, f, indent=2)

# =============================================================================
# Flask Routes
# =============================================================================

@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """Get deal target statistics"""
    return jsonify({
        'targets': len(DEAL_TARGETS),
        'categories': len(set(t['category'] for t in DEAL_TARGETS))
    })


@app.route('/api/search')
def search():
    """
    Search eBay with custom query and price filters

    Query params:
        q: Search query (required)
        min_price: Minimum price (default: 100)
        max_price: Maximum price (default: 700)
    """
    query = request.args.get('q', '')
    min_price = float(request.args.get('min_price', DEFAULT_MIN_PRICE))
    max_price = float(request.args.get('max_price', DEFAULT_MAX_PRICE))

    if not query:
        return jsonify([])

    deals = search_ebay(query, max_price, min_price, limit=20)
    return jsonify(deals)


@app.route('/api/comps')
def get_comps():
    """Get deals organized by category from all targets"""
    results = {}

    # Group targets by category
    by_category = {}
    for target in DEAL_TARGETS:
        cat = target['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(target)

    # Search each category
    for cat, targets in by_category.items():
        results[cat] = []
        for target in targets[:2]:  # Limit searches per category
            min_price = target.get('min_price', 0)
            max_price = target.get('max_price', 500)
            deals = search_ebay(target['query'], max_price, min_price, limit=3)

            for deal in deals:
                deal['search_query'] = target['query']
                deal['min_deal_price'] = min_price
                deal['max_deal_price'] = max_price
                results[cat].append(deal)

    return jsonify(results)


@app.route('/api/watchlist')
def get_watchlist():
    """Get all watchlist items"""
    items = load_watchlist()
    return jsonify(items)


@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add item to watchlist"""
    data = request.get_json()

    item = {
        'id': data.get('id', str(datetime.now().timestamp())),
        'title': data.get('title', ''),
        'price': data.get('price', 0),
        'url': data.get('url', ''),
        'image': data.get('image', ''),
        'notes': data.get('notes', ''),
        'added': datetime.now().isoformat(),
        'status': 'watching'
    }

    items = load_watchlist()

    # Check for duplicates
    if not any(i['id'] == item['id'] for i in items):
        items.append(item)
        save_watchlist(items)

    return jsonify({'success': True, 'count': len(items)})


@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """Remove item from watchlist"""
    data = request.get_json()
    item_id = data.get('id', '')

    items = load_watchlist()
    items = [i for i in items if i['id'] != item_id]
    save_watchlist(items)

    return jsonify({'success': True, 'count': len(items)})


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'app': 'deal-radar'})

# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5051)
