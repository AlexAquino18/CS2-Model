"""
LOCAL PRIZEPICKS SCRAPER
Run this script from YOUR LOCAL MACHINE (not server) to fetch PrizePicks CS2 props
and send them to your deployed application.

This works because:
1. Your local machine has a residential IP (not blocked by Cloudflare)
2. You're running it as a real user (not a bot)
3. Can use either API or Selenium approach

SETUP:
pip install httpx requests

USAGE:
python LOCAL_PRIZEPICKS_SCRAPER.py
"""

import httpx
import json
import requests
from datetime import datetime
import uuid

# Your deployed app URL
DEPLOYED_APP_URL = "https://cs2-bet-buddy.preview.emergentagent.com"

def fetch_prizepicks_api_method():
    """
    Method 1: Using PrizePicks API directly (from StackOverflow solution)
    This should work from your local machine
    """
    print("\\n🔍 Attempting to fetch from PrizePicks API...")
    
    headers = {
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Referer': 'https://app.prizepicks.com/',
        'X-Device-ID': str(uuid.uuid4()),
        'sec-ch-ua-platform': '"macOS"'
    }
    
    try:
        # First, get available leagues
        with httpx.Client(http2=True, timeout=15) as client:
            leagues_response = client.get('https://api.prizepicks.com/leagues', headers=headers)
            
            if leagues_response.status_code == 200:
                leagues_data = leagues_response.json()
                print(f"✅ Successfully fetched leagues list")
                
                # Look for CS2/CSGO
                cs2_league_id = None
                for league in leagues_data.get('data', []):
                    name = league.get('attributes', {}).get('name', '').lower()
                    league_id = league.get('id')
                    print(f"   - {league.get('attributes', {}).get('name')}: {league_id}")
                    
                    if any(term in name for term in ['cs2', 'cs:2', 'counter-strike', 'csgo']):
                        cs2_league_id = league_id
                        print(f"\\n🎯 Found CS2 league: {name} (ID: {league_id})")
                
                # Fetch projections for CS2 if found
                if cs2_league_id:
                    props_url = f"https://api.prizepicks.com/projections?league_id={cs2_league_id}&per_page=250&single_stat=true&game_mode=pickem"
                    props_response = client.get(props_url, headers=headers)
                    
                    if props_response.status_code == 200:
                        props_data = props_response.json()
                        print(f"✅ Successfully fetched CS2 props: {len(props_data.get('data', []))} projections")
                        return parse_prizepicks_props(props_data)
                    else:
                        print(f"❌ Props request failed: {props_response.status_code}")
                else:
                    print("⚠️  CS2 league not found. Trying to fetch all leagues...")
                    # Fetch all props and filter
                    all_props_url = "https://api.prizepicks.com/projections?per_page=250&single_stat=true&game_mode=pickem"
                    props_response = client.get(all_props_url, headers=headers)
                    
                    if props_response.status_code == 200:
                        props_data = props_response.json()
                        cs2_props = filter_cs2_props(props_data)
                        if cs2_props:
                            print(f"✅ Found {len(cs2_props)} CS2 props from all leagues")
                            return cs2_props
            else:
                print(f"❌ Leagues request failed: {leagues_response.status_code}")
                if leagues_response.status_code == 403:
                    print("   Cloudflare is blocking the request (403 Forbidden)")
                    print("   This might still happen if you're on a VPN or proxy")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return []

def parse_prizepicks_props(data):
    """Parse PrizePicks API response"""
    props = []
    
    for item in data.get('data', []):
        if item.get('type') == 'projection':
            attrs = item.get('attributes', {})
            
            player_name = attrs.get('name', '')
            if not player_name:
                desc = attrs.get('description', '')
                if desc:
                    player_name = desc.split(' - ')[0].strip()
            
            stat_type = attrs.get('stat_type', '').lower()
            line = attrs.get('line_score')
            
            if player_name and line:
                props.append({
                    'player_name': player_name,
                    'stat_type': 'kills' if 'kill' in stat_type else 'headshots' if 'headshot' in stat_type or 'hs' in stat_type else stat_type,
                    'line': float(line),
                    'platform': 'prizepicks'
                })
    
    return props

def filter_cs2_props(data):
    """Filter CS2 props from all props"""
    cs2_props = []
    
    for item in data.get('data', []):
        desc = item.get('attributes', {}).get('description', '').lower()
        if any(term in desc for term in ['cs2', 'cs:2', 'counter-strike', 'csgo']):
            props = parse_prizepicks_props({'data': [item]})
            cs2_props.extend(props)
    
    return cs2_props

def send_props_to_app(props):
    """Send scraped props to your deployed application"""
    print(f"\\n📤 Sending {len(props)} props to deployed app...")
    
    # You would need an endpoint on your server to receive this data
    # For now, we'll just save to a JSON file that you can manually upload
    
    output_file = 'prizepicks_cs2_props.json'
    with open(output_file, 'w') as f:
        json.dump(props, f, indent=2)
    
    print(f"✅ Saved to {output_file}")
    print(f"\\n📋 Sample props:")
    for prop in props[:5]:
        print(f"   {prop['player_name']}: {prop['stat_type']} = {prop['line']}")
    
    return output_file

def main():
    print("=" * 60)
    print("🎮 PrizePicks CS2 Props Scraper (LOCAL)")
    print("=" * 60)
    print("\\nThis script should work from your local machine")
    print("(residential IP not blocked by Cloudflare)\\n")
    
    # Try API method
    props = fetch_prizepicks_api_method()
    
    if props:
        output_file = send_props_to_app(props)
        print(f"\\n✅ SUCCESS! Data saved to: {output_file}")
        print(f"\\n📝 Next steps:")
        print(f"1. Review the data in {output_file}")
        print(f"2. You can manually upload this to your app")
        print(f"3. Or set up an API endpoint to receive it automatically")
    else:
        print("\\n❌ No CS2 props found or API is blocked")
        print("\\n💡 Possible reasons:")
        print("   1. PrizePicks doesn't have CS2 props available right now")
        print("   2. You're on a VPN/proxy that's being blocked")
        print("   3. CS2 might not be a supported league on PrizePicks")
        print("\\n💡 Try:")
        print("   1. Visit https://app.prizepicks.com/ in your browser")
        print("   2. Check if CS2/Counter-Strike is listed")
        print("   3. Run this script again from a different network")

if __name__ == "__main__":
    main()
