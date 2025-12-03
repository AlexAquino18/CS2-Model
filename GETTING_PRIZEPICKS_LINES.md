# How to Get PrizePicks CS2 Lines

## The Reality: PrizePicks API is Blocked from Server

**Current Status**:
- ✅ PrizePicks API integration code is ready
- ❌ Server IP is blocked (403 Forbidden / 429 Rate Limited)
- ✅ Works from residential IPs (your computer)

## Solution 1: Run Local Scraper (5 Minutes)

### Step 1: Create Local Script

Save this as `prizepicks_local.py` on YOUR computer:

```python
import requests
import json

def fetch_prizepicks_cs2():
    """Fetch PrizePicks CS2 props from your local machine"""
    
    # Simple headers that work from residential IP
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    })
    
    # Get leagues
    leagues_url = 'https://api.prizepicks.com/leagues'
    response = session.get(leagues_url, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print("Try visiting https://app.prizepicks.com in your browser first")
        return
    
    leagues = response.json()
    
    # Find CS2/CSGO league
    cs2_league_id = None
    for league in leagues.get('data', []):
        name = league.get('attributes', {}).get('name', '').upper()
        league_id = league.get('id')
        print(f"Found: {name} (ID: {league_id})")
        
        if any(term in name for term in ['CS2', 'CS:2', 'COUNTER-STRIKE', 'CSGO']):
            cs2_league_id = league_id
            print(f"✅ CS2 League Found: {name}")
            break
    
    if not cs2_league_id:
        print("❌ No CS2 league found on PrizePicks")
        print("CS2 might not be available right now")
        return
    
    # Fetch CS2 props
    props_url = f'https://api.prizepicks.com/projections?league_id={cs2_league_id}&per_page=500&single_stat=true&game_mode=pickem'
    props_response = session.get(props_url, timeout=15)
    
    if props_response.status_code != 200:
        print(f"❌ Props Error: {props_response.status_code}")
        return
    
    props_data = props_response.json()
    
    # Parse props
    cs2_props = []
    projections = props_data.get('data', [])
    included = props_data.get('included', [])
    
    # Create player lookup
    players = {item['id']: item for item in included if item.get('type') == 'new_player'}
    
    for projection in projections:
        try:
            attrs = projection.get('attributes', {})
            relationships = projection.get('relationships', {})
            
            # Get player name
            player_id = relationships.get('new_player', {}).get('data', {}).get('id')
            player_info = players.get(player_id, {}).get('attributes', {})
            player_name = player_info.get('display_name', 'Unknown')
            
            # Get stat and line
            stat_type = attrs.get('stat_type', '')
            line = attrs.get('line_score')
            
            if line and player_name:
                cs2_props.append({
                    'player_name': player_name,
                    'stat_type': stat_type,
                    'line': float(line),
                    'description': attrs.get('description', '')
                })
        except:
            continue
    
    print(f"\\n✅ Found {len(cs2_props)} CS2 props!")
    
    # Save to file
    with open('prizepicks_cs2_props.json', 'w') as f:
        json.dump(cs2_props, f, indent=2)
    
    print("\\n📝 Saved to: prizepicks_cs2_props.json")
    print("\\nSample props:")
    for prop in cs2_props[:10]:
        print(f"  {prop['player_name']}: {prop['stat_type']} = {prop['line']}")

if __name__ == "__main__":
    print("🎮 PrizePicks CS2 Props Fetcher")
    print("=" * 50)
    fetch_prizepicks_cs2()
```

### Step 2: Run It

```bash
# Install requests
pip install requests

# Run the script
python prizepicks_local.py
```

### Step 3: You'll Get

A file `prizepicks_cs2_props.json` with all CS2 props:
```json
[
  {
    "player_name": "s1mple",
    "stat_type": "Kills",
    "line": 45.5,
    "description": "s1mple - Kills (Map 1 + Map 2)"
  },
  ...
]
```

## Solution 2: Manual Copy from Website (10 Minutes)

### Step 1: Visit PrizePicks
Go to: https://app.prizepicks.com/

### Step 2: Find CS2 Section
Look for "CS2" or "Counter-Strike" in the sports tabs

### Step 3: Copy Props
For each player, note:
- Player name
- Stat type (Kills, Headshots, etc.)
- Line number

### Step 4: Format as JSON
Create a file with this format:
```json
[
  {
    "player_name": "Player1",
    "stat_type": "kills",
    "line": 42.5
  },
  {
    "player_name": "Player2",
    "stat_type": "headshots",
    "line": 18.5
  }
]
```

## Solution 3: Browser Console (Advanced)

### Open PrizePicks in Browser
1. Go to https://app.prizepicks.com/
2. Navigate to CS2 section
3. Open Developer Tools (F12)
4. Go to Network tab
5. Refresh page
6. Look for API calls to `api.prizepicks.com/projections`
7. Copy the response data

## Why CS2 Might Not Be on PrizePicks

**Important**: CS2 props might not always be available because:
1. PrizePicks focuses on major sports
2. CS2 coverage depends on tournament schedules
3. Not all esports are available 24/7

**Check availability**: Visit https://app.prizepicks.com/ and look for CS2/Counter-Strike tab

## Integrating Props into Your App

Once you have the props JSON file:

### Option A: API Endpoint (Future)
We can create an endpoint on your server to receive props:
```bash
curl -X POST https://your-app.com/api/upload-props \
  -H "Content-Type: application/json" \
  -d @prizepicks_cs2_props.json
```

### Option B: Manual Update
1. Get props using local scraper
2. Send to developer
3. Update app database
4. Refresh dashboard

## Current Workaround

Until we get real PrizePicks props, the app:
1. ✅ Shows REAL CS2 matches (from PandaScore)
2. ✅ Generates realistic prop lines
3. ⚠️ Props are simulated based on typical values
4. ✅ Full functionality for demonstration

## Next Steps

1. **Try local scraper** → See if CS2 is available on PrizePicks
2. **If available** → Get props and share the JSON
3. **If not available** → Use app as-is with simulated props
4. **For production** → Consider paid DFS data API (has all platforms)

## Questions?

- **"Why can't server fetch it?"** → Cloudflare blocks data center IPs
- **"Is this legal?"** → Fetching from your own browser/computer is fine
- **"How often update?"** → Run script whenever props change (daily/per tournament)
