#!/usr/bin/env python3
"""
DATARADAR - Daily Deal Scanner
Scans eBay for deals based on watchlist and target categories
"""

import os
import json
import base64
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EBAY_CLIENT_ID = os.getenv('EBAY_CLIENT_ID')
EBAY_CLIENT_SECRET = os.getenv('EBAY_CLIENT_SECRET')

# Base directory for file operations
BASE_DIR = Path(__file__).parent


def get_ebay_token():
    """Get eBay Browse API token"""
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
    return response.json().get('access_token')


def load_watchlist():
    """Load watchlist items from JSON file"""
    watchlist_path = BASE_DIR / 'watchlist.json'
    if watchlist_path.exists():
        with open(watchlist_path, 'r') as f:
            return json.load(f)
    return []


def get_default_targets():
    """Default deal targets with COA requirements"""
    return [
        # Space memorabilia - signed with COA
        {'query': 'Neil Armstrong signed photo COA', 'min_price': 500, 'max_price': 5000, 'category': 'Space'},
        {'query': 'Buzz Aldrin signed photo COA', 'min_price': 100, 'max_price': 800, 'category': 'Space'},
        {'query': 'Michael Collins signed photo COA', 'min_price': 200, 'max_price': 1000, 'category': 'Space'},

        # Street Art
        {'query': 'Death NYC signed print', 'min_price': 50, 'max_price': 200, 'category': 'Street Art'},
        {'query': 'Shepard Fairey signed print', 'min_price': 100, 'max_price': 500, 'category': 'Street Art'},
        {'query': 'Mr Brainwash signed print', 'min_price': 100, 'max_price': 400, 'category': 'Street Art'},

        # Signed Pickguards with COA
        {'query': 'signed pickguard COA', 'min_price': 75, 'max_price': 500, 'category': 'Pickguard'},

        # Vinyl Records - signed with COA
        {'query': 'signed vinyl COA authenticated', 'min_price': 75, 'max_price': 500, 'category': 'Vinyl'},
        {'query': 'Fred Again signed vinyl COA', 'min_price': 100, 'max_price': 400, 'category': 'Vinyl'},

        # Celebrity autographs with COA
        {'query': 'Taylor Swift signed COA', 'min_price': 100, 'max_price': 700, 'category': 'Celebrity'},
        {'query': 'Hunter S Thompson signed COA', 'min_price': 100, 'max_price': 500, 'category': 'Celebrity'},
    ]


def search_ebay_deals(query, max_price=500, limit=10):
    """Search eBay for deals"""
    token = get_ebay_token()

    if not token:
        print("Failed to get eBay token")
        return []

    headers = {
        'Authorization': f'Bearer {token}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        'Content-Type': 'application/json'
    }

    params = {
        'q': query,
        'filter': f'price:[..{max_price}],priceCurrency:USD',
        'sort': 'newlyListed',
        'limit': limit
    }

    try:
        resp = requests.get(
            'https://api.ebay.com/buy/browse/v1/item_summary/search',
            headers=headers,
            params=params
        )

        if resp.status_code != 200:
            print(f"eBay API error: {resp.status_code}")
            return []

        data = resp.json()
        items = data.get('itemSummaries', [])

        deals = []
        for item in items:
            price_info = item.get('price', {})
            price = float(price_info.get('value', 0))

            if price <= 0:
                continue

            image = None
            if item.get('thumbnailImages'):
                image = item['thumbnailImages'][0].get('imageUrl')
            elif item.get('image'):
                image = item['image'].get('imageUrl')

            deals.append({
                'id': item.get('itemId', ''),
                'title': item.get('title', 'Unknown'),
                'price': price,
                'url': item.get('itemWebUrl', ''),
                'image': image,
                'condition': item.get('condition', 'Unknown'),
                'seller': item.get('seller', {}).get('username', 'Unknown'),
                'listed_date': item.get('itemCreationDate', '')
            })

        return deals
    except Exception as e:
        print(f"Search error for {query}: {e}")
        return []


def run_daily_scan():
    """Main daily scan function"""
    print("=" * 60)
    print(f"DATARADAR - Daily Deal Scanner")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Load watchlist
    watchlist = load_watchlist()
    print(f"\nWatchlist items: {len(watchlist)}")

    # Get default targets
    targets = get_default_targets()
    print(f"Target categories: {len(targets)}")

    # Combine watchlist and targets
    search_queries = []

    # Add watchlist items
    for item in watchlist:
        search_queries.append({
            'query': item['title'],
            'max_price': item.get('price', 500),
            'source': 'watchlist'
        })

    # Add default targets
    for target in targets:
        search_queries.append({
            'query': target['query'],
            'max_price': target.get('max_price', 500),
            'source': target.get('category', 'default')
        })

    # Deduplicate by query
    seen = set()
    unique_queries = []
    for q in search_queries:
        if q['query'] not in seen:
            seen.add(q['query'])
            unique_queries.append(q)

    print(f"Unique searches: {len(unique_queries)}")

    # Scan for deals
    all_deals = []

    for query_info in unique_queries[:25]:  # Limit to 25 searches per scan
        query = query_info['query']
        max_price = query_info['max_price']
        print(f"\nScanning: {query} (max ${max_price})...")

        deals = search_ebay_deals(query, max_price=max_price, limit=5)

        for deal in deals:
            deal['search_query'] = query
            deal['source'] = query_info['source']
            all_deals.append(deal)

        if deals:
            print(f"  Found {len(deals)} items")

    # Sort by price
    all_deals.sort(key=lambda x: x['price'])

    # Save results
    results = {
        'scan_date': datetime.now().isoformat(),
        'searches': len(unique_queries),
        'deals_found': len(all_deals),
        'deals': all_deals
    }

    results_file = BASE_DIR / f"scan_results_{datetime.now().strftime('%Y%m%d')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"SCAN COMPLETE")
    print(f"{'=' * 60}")
    print(f"Searches: {len(unique_queries)}")
    print(f"Deals found: {len(all_deals)}")
    print(f"Results saved: {results_file}")

    # Show top deals
    if all_deals:
        print(f"\nTOP 10 DEALS:")
        print("-" * 60)
        for deal in all_deals[:10]:
            print(f"  ${deal['price']:>7.2f} | {deal['title'][:50]}")
            print(f"           {deal['url']}")

    return results


if __name__ == "__main__":
    run_daily_scan()
