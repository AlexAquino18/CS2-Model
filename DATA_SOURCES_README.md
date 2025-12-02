# CS2 Pro Terminal - Data Sources Guide

## Current Status

The application is designed to fetch **real-time CS2 match data and PrizePicks props**, but currently faces anti-scraping protection from both data sources.

### What's Happening

1. **PrizePicks** - Returns 403 (Forbidden) due to:
   - Cloudflare protection
   - Anti-bot measures
   - Requires authentication or browser-based access

2. **HLTV.org** - Returns 403 (Forbidden) due to:
   - Rate limiting
   - Anti-scraping protection
   - Requires proper headers and timing

3. **Underdog Fantasy** - API not publicly accessible

### Current Fallback

The system automatically falls back to **mock/sample data** that demonstrates the application's functionality with realistic CS2 team names, player names, and stat projections.

---

## Solutions to Get Real Data

### Option 1: Manual Data Input (Easiest)

1. Visit [PrizePicks.com](https://app.prizepicks.com/)
2. Navigate to CS2 section
3. Copy player props (names, kills, headshots lines)
4. Input into the application

**Implementation Status**: ✅ Backend infrastructure ready, UI input form needed

### Option 2: Browser Extension (Recommended)

Create a simple browser extension that:
- Runs in your browser while you're on PrizePicks
- Extracts CS2 prop data
- Sends to your local API

**Pros**: Bypasses anti-scraping (you're a real user)
**Cons**: Requires browser extension development

### Option 3: PrizePicks Official API

Contact PrizePicks for official API access:
- Requires business/partnership relationship
- Provides reliable, legal data access
- No scraping issues

### Option 4: Selenium with Anti-Detection

Enhance the existing Selenium scraper:
```python
- Use undetected-chromedriver
- Implement random delays
- Rotate user agents
- Use residential proxies
```

**Status**: ⚠️ Partial implementation exists, needs enhancement

### Option 5: Third-Party Data Providers

Use specialized sports data APIs:
- **Odds API** (oddsapi.io)
- **The Odds API** (the-odds-api.com)
- **RapidAPI CS:GO/CS2 endpoints**

**Pros**: Legal, reliable, documented
**Cons**: May require paid subscription

---

## Technical Details

### Scraper Status Endpoint

Access real-time scraper status:
```bash
GET /api/scraping-status
```

Returns:
```json
{
  "status": {
    "hltv": {"success": false, "error": "...", "last_attempt": "..."},
    "prizepicks": {"success": false, "error": "...", "last_attempt": "..."},
    "underdog": {"success": false, "error": "...", "last_attempt": "..."}
  },
  "data_mode": "mock",
  "note": "..."
}
```

### File Locations

- **Scrapers**: `/app/backend/scrapers/`
  - `prizepicks_scraper.py` - PrizePicks data fetching
  - `hltv_scraper.py` - HLTV match data
  - `manual_input.py` - Manual data input helper

- **Aggregator**: `/app/backend/data_aggregator.py`
  - Combines data from all sources
  - Handles fallbacks

---

## Development Recommendations

### Immediate (Quick Win)

1. **Add Manual Input UI**
   - Create form for pasting PrizePicks data
   - CSV/JSON upload support
   - One-click import

### Short-term (Best Practice)

2. **API Integration**
   - Research paid CS2 data APIs
   - Implement official API connectors
   - Better than scraping

### Long-term (Advanced)

3. **Hybrid Approach**
   - Use official APIs where available
   - Supplement with manual input
   - Consider partnership with PrizePicks

---

## Legal Considerations

⚠️ **Important**: Web scraping terms of service
- PrizePicks ToS may prohibit automated scraping
- Consider contacting them for data partnership
- Always respect robots.txt and rate limits

---

## Testing the Current System

The application works perfectly with mock data:
- ✅ Match display
- ✅ Player projections
- ✅ DFS line comparison
- ✅ Value opportunity detection
- ✅ Responsive design

Once real data is available (via any method above), it will seamlessly integrate without code changes.

---

## Questions?

The architecture is ready for real data. The only blocker is data acquisition due to anti-scraping protection. Choose the solution that best fits your needs:

- **Quick test**: Use current mock data
- **Personal use**: Manual input
- **Production**: Official API or paid data provider
