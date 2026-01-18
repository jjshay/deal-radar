# DATARADAR Deals

> eBay deal finder for flipping authenticated collectibles

A Flask-based web application that searches eBay in real-time to find underpriced authenticated items (signed memorabilia, vintage vinyl, space collectibles) for resale.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![eBay API](https://img.shields.io/badge/eBay-Browse%20API-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Live eBay Search** - Real-time search with price filtering
- **Category Presets** - Quick search for popular categories
- **Dual Price Slider** - Filter by min/max price range ($100-$700 default)
- **Watchlist** - Track items you're looking for
- **Item Preview** - View details before going to eBay
- **Mobile-First UI** - Clean, responsive iOS-style design

## Categories

- **Art Prints** - Mr. Brainwash, Shepard Fairey (signed)
- **Signed Pickguards** - Authenticated guitar pickguards with COA
- **Signed Vinyl** - Authenticated records with COA
- **Space Memorabilia** - NASA, astronaut autographs with COA

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **API**: eBay Browse API (OAuth 2.0)
- **Storage**: JSON files for watchlist

## Screenshots

### Home Screen
```
┌─────────────────────────────────────┐
│  Deals                              │
│  Find items to flip                 │
├─────────────────────────────────────┤
│  Price ━━━●━━━━━━●━━━  $100 - $700  │
├─────────────────────────────────────┤
│  🎨 MBW    ✊ Fairey    🎸 Pickguards│
│  💿 Vinyl  🚀 Space    ⭐ T Swift   │
├─────────────────────────────────────┤
│  Hot Now                   Refresh  │
│  ┌─────────────────────────────────┐│
│  │ Mr Brainwash signed      $245  ││
│  │ Life is Beautiful print        ││
│  ├─────────────────────────────────┤│
│  │ Shepard Fairey signed    $189  ││
│  │ Obey Giant print               ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
     [Home]  [Search]  [Watchlist]
```

## Installation

### Prerequisites
- Python 3.9+
- eBay Developer Account (for Browse API access)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dataradar-deals.git
cd dataradar-deals
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your eBay API credentials
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://localhost:5051
```

## Configuration

### Environment Variables

```env
# eBay API Credentials (required)
EBAY_CLIENT_ID=your_client_id
EBAY_CLIENT_SECRET=your_client_secret
```

### Deal Targets

Edit the `DEAL_TARGETS` in `app.py` to customize search queries:

```python
DEAL_TARGETS = [
    {
        'query': 'Mr Brainwash signed',
        'min_price': 100,
        'max_price': 500,
        'category': 'Mr. Brainwash'
    },
    # Add more targets...
]
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/search` | GET | Search eBay with filters |
| `/api/stats` | GET | Target statistics |
| `/api/watchlist` | GET | Get watchlist items |
| `/api/watchlist/add` | POST | Add item to watchlist |
| `/api/watchlist/remove` | POST | Remove from watchlist |

### Search Parameters

```
GET /api/search?q=signed+vinyl+COA&min_price=100&max_price=700
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query |
| `min_price` | number | Minimum price filter |
| `max_price` | number | Maximum price filter |

## Project Structure

```
dataradar-deals/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── watchlist.json        # Watchlist storage
├── templates/
│   └── index.html        # Dashboard UI
└── README.md
```

## Key Code Examples

### eBay Browse API Search
```python
def search_ebay(query, min_price=100, max_price=700, limit=20):
    """Search eBay using Browse API with price filters"""
    token = get_browse_token()

    headers = {
        'Authorization': f'Bearer {token}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
    }

    params = {
        'q': query,
        'filter': f'price:[{min_price}..{max_price}],priceCurrency:USD',
        'sort': 'price',
        'limit': limit
    }

    response = requests.get(
        'https://api.ebay.com/buy/browse/v1/item_summary/search',
        headers=headers,
        params=params
    )

    return response.json().get('itemSummaries', [])
```

### Watchlist Management
```python
def add_to_watchlist(item):
    """Add item to JSON watchlist"""
    items = load_watchlist()

    if not any(i['id'] == item['id'] for i in items):
        items.append({
            'id': item['id'],
            'title': item['title'],
            'price': item['price'],
            'notes': item.get('notes', ''),
            'added': datetime.now().isoformat(),
            'status': 'watching'
        })
        save_watchlist(items)

    return True
```

## Mobile-First Design

The UI is built with a mobile-first approach:

- **Dark theme** - Easy on the eyes, modern look
- **Touch-friendly** - Large tap targets (44px minimum)
- **Gesture support** - Pull to refresh, swipe actions
- **Bottom navigation** - Thumb-friendly navigation
- **Responsive** - Works on all screen sizes

## Authentication

The app uses eBay's OAuth 2.0 Client Credentials flow:

```python
def get_browse_token():
    """Get client credentials token for Browse API"""
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    response = requests.post(
        'https://api.ebay.com/identity/v1/oauth2/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded}'
        },
        data={
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
    )

    return response.json().get('access_token')
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**John Shay**
- GitHub: [@johnshay](https://github.com/johnshay)

## Acknowledgments

- eBay Developer Program for API access
- Flask community for excellent documentation
