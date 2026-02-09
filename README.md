# DATARADAR Deals

eBay Deal Finder for Flipping Authenticated Collectibles

Find underpriced signed memorabilia, vintage vinyl, space collectibles, and art prints on eBay using real-time Browse API searches.

## Features

- **Real-time eBay searches** via Browse API
- **Pre-configured deal targets** for art, space, music collectibles
- **Price filtering** to find deals below market value
- **Watchlist** to track potential purchases
- **Category organization** for easy browsing
- **Web dashboard** for monitoring deals

## Deal Categories

### Art Prints
| Artist | Search Terms | Price Range |
|--------|-------------|-------------|
| Mr. Brainwash | "Mr Brainwash signed print", "MBW signed print" | $75 - $500 |
| Shepard Fairey | "Shepard Fairey signed print", "Obey Giant signed" | $50 - $400 |

### Space Memorabilia
| Category | Search Terms | Price Range |
|----------|-------------|-------------|
| Neil Armstrong | "Neil Armstrong signed photo COA" | $500 - $5,000 |
| Buzz Aldrin | "Buzz Aldrin signed photo COA" | $100 - $800 |
| Astronauts | "astronaut signed COA authenticated" | $100 - $1,000 |

### Music Collectibles
| Category | Search Terms | Price Range |
|----------|-------------|-------------|
| Pickguards | "signed pickguard COA", "autographed pickguard COA" | $75 - $500 |
| Vinyl | "signed vinyl COA authenticated", "Taylor Swift signed vinyl COA" | $75 - $600 |

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/jjshay/DATARADAR-Deals.git
cd DATARADAR-Deals
pip install -r requirements.txt
```

### 2. Configure eBay API
Create a `.env` file:
```env
EBAY_CLIENT_ID=your_client_id_here
EBAY_CLIENT_SECRET=your_client_secret_here
```

Get your eBay API credentials at [developer.ebay.com](https://developer.ebay.com)

### 3. Run
```bash
python app.py
```

Open http://localhost:5051

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/api/search?q=...&min_price=...&max_price=...` | GET | Custom search |
| `/api/comps` | GET | Get deals by category |
| `/api/stats` | GET | Target statistics |
| `/api/watchlist` | GET | Get watchlist |
| `/api/watchlist/add` | POST | Add to watchlist |
| `/api/watchlist/remove` | POST | Remove from watchlist |
| `/health` | GET | Health check |

## Search API

### Parameters
| Param | Default | Description |
|-------|---------|-------------|
| `q` | required | Search query |
| `min_price` | 100 | Minimum price (filters fakes) |
| `max_price` | 700 | Maximum price ceiling |

### Example
```bash
curl "http://localhost:5051/api/search?q=Shepard+Fairey+signed&min_price=50&max_price=300"
```

### Response
```json
[
  {
    "id": "v1|123456789|0",
    "title": "Shepard Fairey HOPE Signed Print",
    "price": 275.00,
    "image": "https://i.ebayimg.com/...",
    "url": "https://www.ebay.com/itm/...",
    "condition": "New",
    "seller": "art_dealer_123",
    "buying_option": "FIXED_PRICE",
    "location": "US"
  }
]
```

## Watchlist

Track items you're considering purchasing:

### Add Item
```bash
curl -X POST http://localhost:5051/api/watchlist/add \
  -H "Content-Type: application/json" \
  -d '{"id": "123", "title": "Art Print", "price": 200, "url": "https://..."}'
```

### Watchlist Item Schema
```json
{
  "id": "v1|123456789|0",
  "title": "Item title",
  "price": 200.00,
  "url": "https://ebay.com/...",
  "image": "https://i.ebayimg.com/...",
  "notes": "Good deal, check COA",
  "added": "2025-02-09T01:30:00",
  "status": "watching"
}
```

## Project Structure

```
DATARADAR-Deals/
├── app.py              # Flask application
├── daily_scanner.py    # Scheduled deal scanner
├── ebay_oauth.py       # eBay authentication helper
├── health_check.py     # Health monitoring
├── requirements.txt    # Python dependencies
├── watchlist.json      # Saved watchlist items
├── templates/
│   └── index.html      # Web dashboard
└── .env                # API credentials (not in repo)
```

## Why Minimum Price Filters?

Setting a minimum price ($50-100) helps filter out:
- Fake/counterfeit prints
- Unsigned reproductions
- Poster reprints without COA
- Suspicious deals that are too good to be true

Authentic signed collectibles rarely sell for under $50-75.

## Adding New Deal Targets

Edit `DEAL_TARGETS` in `app.py`:

```python
DEAL_TARGETS = [
    {
        'query': 'KAWS signed print',
        'min_price': 200,
        'max_price': 1000,
        'category': 'KAWS'
    },
    # ... more targets
]
```

## Deployment

### PythonAnywhere
1. Upload files to PythonAnywhere
2. Set up virtual environment
3. Configure WSGI to point to `app.py`
4. Add environment variables in web app settings

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5051
CMD ["python", "app.py"]
```

## Related Projects

- [DATARADAR](https://github.com/jjshay/DATARADAR) - Main inventory management
- [DATARADAR-Listings](https://github.com/jjshay/DATARADAR-Listings) - eBay listing automation

## License

MIT

## Author

JJ Shay - Art dealer specializing in authenticated collectibles
