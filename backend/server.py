from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import asyncio
from data_aggregator import CS2DataAggregator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Player(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    team: str
    avg_kills: float
    avg_headshots: float
    recent_form: float  # Last 5 games multiplier
    map_stats: Dict[str, Dict[str, float]] = {}  # Map-specific stats

class DFSLine(BaseModel):
    model_config = ConfigDict(extra="ignore")
    platform: str  # "prizepicks" or "underdog"
    stat_type: str  # "kills" or "headshots"
    line: float
    maps: str  # "Map1+Map2"

class Match(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team1: str
    team2: str
    tournament: str
    start_time: datetime
    map1: str
    map2: str
    status: str = "upcoming"  # upcoming, live, completed

class Projection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    match_id: str
    player_name: str
    team: str
    stat_type: str  # "kills" or "headshots"
    projected_value: float
    confidence: float  # 0-100
    dfs_lines: List[DFSLine] = []
    value_opportunity: bool = False
    difference: float = 0.0  # Projection vs best DFS line

class MatchWithProjections(BaseModel):
    match: Match
    projections: List[Projection]
    last_updated: datetime

# In-memory cache for demo (in production, use Redis or similar)
data_cache = {
    "matches": [],
    "last_refresh": None
}

# Data aggregator for fetching real data
aggregator = CS2DataAggregator()

# Data fetching function
async def fetch_real_data():
    """Fetch real CS2 data from scrapers"""
    try:
        logger.info("Fetching real data from scrapers...")
        matches_data, projections_data = await aggregator.fetch_all_data()
        
        if matches_data and projections_data:
            # Convert to proper model format
            from pydantic import ValidationError
            
            matches = []
            for m in matches_data:
                try:
                    matches.append(Match(**m))
                except ValidationError as e:
                    logger.error(f"Validation error for match: {e}")
            
            projections = []
            for p in projections_data:
                try:
                    projections.append(Projection(**p))
                except ValidationError as e:
                    logger.error(f"Validation error for projection: {e}")
            
            # Store in cache and database
            data_cache["matches"] = matches
            data_cache["projections"] = projections
            data_cache["last_refresh"] = datetime.now(timezone.utc)
            
            # Store in MongoDB
            if matches:
                await db.matches.delete_many({})
                await db.matches.insert_many([m.model_dump() for m in matches])
            
            if projections:
                await db.projections.delete_many({})
                await db.projections.insert_many([p.model_dump() for p in projections])
            
            logger.info(f"Fetched {len(matches)} matches and {len(projections)} projections")
            return matches, projections
        else:
            logger.warning("No real data available, falling back to mock data")
            return await generate_mock_data()
            
    except Exception as e:
        logger.error(f"Error fetching real data: {e}")
        logger.info("Falling back to mock data")
        return await generate_mock_data()

# Mock data generator (fallback)
async def generate_mock_data():
    """Generate realistic mock data for CS2 matches and projections (fallback)"""
    from random import uniform, choice, randint
    
    teams = ["Navi", "FaZe Clan", "G2 Esports", "Vitality", "Liquid", "MOUZ", "Heroic", "Astralis"]
    tournaments = ["IEM Katowice 2025", "BLAST Premier", "ESL Pro League", "PGL Major"]
    maps = ["Mirage", "Dust2", "Inferno", "Nuke", "Ancient", "Anubis", "Overpass"]
    players_by_team = {
        "Navi": ["s1mple", "electronic", "b1t", "Aleksib", "iM"],
        "FaZe Clan": ["rain", "karrigan", "ropz", "frozen", "broky"],
        "G2 Esports": ["NiKo", "huNter", "m0NESY", "HooXi", "jks"],
        "Vitality": ["ZywOo", "apEX", "Magisk", "Spinx", "flameZ"],
        "Liquid": ["EliGE", "NAF", "Twistzz", "nitr0", "oSee"],
        "MOUZ": ["frozen", "ropz", "JDC", "torzsi", "xertioN"],
        "Heroic": ["cadiaN", "stavn", "TeSeS", "sjuush", "jabbi"],
        "Astralis": ["BlameF", "k0nfig", "device", "Xyp9x", "br0"]
    }
    
    matches = []
    all_projections = []
    
    # Generate 6 upcoming matches
    for i in range(6):
        team1, team2 = choice(teams), choice(teams)
        while team1 == team2:
            team2 = choice(teams)
        
        match = Match(
            id=str(uuid.uuid4()),
            team1=team1,
            team2=team2,
            tournament=choice(tournaments),
            start_time=datetime.now(timezone.utc) + timedelta(hours=randint(1, 72)),
            map1=choice(maps),
            map2=choice([m for m in maps if m != choice(maps)]),
            status="upcoming"
        )
        matches.append(match)
        
        # Generate projections for all players in both teams
        for team in [team1, team2]:
            if team in players_by_team:
                for player in players_by_team[team]:
                    # Kills projection
                    base_kills = uniform(30, 55)
                    kills_projection = Projection(
                        match_id=match.id,
                        player_name=player,
                        team=team,
                        stat_type="kills",
                        projected_value=round(base_kills, 1),
                        confidence=round(uniform(65, 95), 1),
                        dfs_lines=[
                            DFSLine(
                                platform="prizepicks",
                                stat_type="kills",
                                line=round(base_kills + uniform(-3, 3), 1),
                                maps="Map1+Map2"
                            ),
                            DFSLine(
                                platform="underdog",
                                stat_type="kills",
                                line=round(base_kills + uniform(-3, 3), 1),
                                maps="Map1+Map2"
                            )
                        ]
                    )
                    
                    # Calculate value opportunity
                    avg_dfs_line = sum([line.line for line in kills_projection.dfs_lines]) / len(kills_projection.dfs_lines)
                    kills_projection.difference = round(kills_projection.projected_value - avg_dfs_line, 1)
                    kills_projection.value_opportunity = abs(kills_projection.difference) > 3.0
                    
                    all_projections.append(kills_projection)
                    
                    # Headshots projection
                    base_hs = uniform(12, 25)
                    hs_projection = Projection(
                        match_id=match.id,
                        player_name=player,
                        team=team,
                        stat_type="headshots",
                        projected_value=round(base_hs, 1),
                        confidence=round(uniform(65, 95), 1),
                        dfs_lines=[
                            DFSLine(
                                platform="prizepicks",
                                stat_type="headshots",
                                line=round(base_hs + uniform(-2, 2), 1),
                                maps="Map1+Map2"
                            ),
                            DFSLine(
                                platform="underdog",
                                stat_type="headshots",
                                line=round(base_hs + uniform(-2, 2), 1),
                                maps="Map1+Map2"
                            )
                        ]
                    )
                    
                    avg_dfs_line = sum([line.line for line in hs_projection.dfs_lines]) / len(hs_projection.dfs_lines)
                    hs_projection.difference = round(hs_projection.projected_value - avg_dfs_line, 1)
                    hs_projection.value_opportunity = abs(hs_projection.difference) > 2.0
                    
                    all_projections.append(hs_projection)
    
    # Store in cache and database
    data_cache["matches"] = matches
    data_cache["projections"] = all_projections
    data_cache["last_refresh"] = datetime.now(timezone.utc)
    
    # Store in MongoDB
    if matches:
        await db.matches.delete_many({})  # Clear old data
        await db.matches.insert_many([m.model_dump() for m in matches])
    
    if all_projections:
        await db.projections.delete_many({})
        await db.projections.insert_many([p.model_dump() for p in all_projections])
    
    return matches, all_projections

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "CS2 Pro Projection API", "status": "operational"}

@api_router.get("/matches", response_model=List[MatchWithProjections])
async def get_matches():
    """Get all matches with their projections"""
    # If no cached data, fetch it
    if not data_cache.get("matches"):
        await fetch_real_data()
    
    matches = data_cache.get("matches", [])
    projections = data_cache.get("projections", [])
    last_updated = data_cache.get("last_refresh", datetime.now(timezone.utc))
    
    # Group projections by match
    result = []
    for match in matches:
        match_projections = [p for p in projections if p.match_id == match.id]
        result.append(MatchWithProjections(
            match=match,
            projections=match_projections,
            last_updated=last_updated
        ))
    
    return result

@api_router.get("/matches/{match_id}")
async def get_match_detail(match_id: str):
    """Get detailed view of a specific match"""
    matches = data_cache.get("matches", [])
    projections = data_cache.get("projections", [])
    
    match = next((m for m in matches if m.id == match_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match_projections = [p for p in projections if p.match_id == match_id]
    
    return MatchWithProjections(
        match=match,
        projections=match_projections,
        last_updated=data_cache.get("last_refresh", datetime.now(timezone.utc))
    )

@api_router.post("/refresh")
async def refresh_data():
    """Manually trigger data refresh"""
    try:
        matches, projections = await fetch_real_data()
        return {
            "status": "success",
            "matches_count": len(matches),
            "projections_count": len(projections),
            "last_updated": data_cache.get("last_refresh").isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats")
async def get_stats():
    """Get overall statistics"""
    projections = data_cache.get("projections", [])
    matches = data_cache.get("matches", [])
    value_opportunities = [p for p in projections if p.value_opportunity]
    
    # Count matches with and without props
    try:
        matches_with_props = len([m for m in matches if (hasattr(m, 'has_props') and getattr(m, 'has_props', True)) or not hasattr(m, 'has_props')])
        matches_without_props = len(matches) - matches_with_props
    except:
        matches_with_props = len(matches)
        matches_without_props = 0
    
    return {
        "total_matches": len(matches),
        "matches_with_props": matches_with_props,
        "matches_without_props": matches_without_props,
        "total_projections": len(projections),
        "value_opportunities": len(value_opportunities),
        "avg_confidence": round(sum([p.confidence for p in projections]) / len(projections), 1) if projections else 0,
        "last_refresh": data_cache.get("last_refresh").isoformat() if data_cache.get("last_refresh") else None
    }

@api_router.get("/scraping-status")
async def get_scraping_status():
    """Get status of data scraping from various sources"""
    return {
        "status": aggregator.get_scraping_status(),
        "data_mode": "mock" if not any(s['success'] for s in aggregator.get_scraping_status().values()) else "mixed",
        "note": "PrizePicks and HLTV have anti-scraping protection. Real data requires API keys or manual input."
    }

@api_router.get("/model-info")
async def get_model_info():
    """Get projection model information and configuration"""
    return aggregator.projection_model.get_model_info()

@api_router.get("/line-movements")
async def get_line_movements():
    """Get all detected line movements"""
    movements = aggregator.line_tracker.get_all_movements()
    return {
        "movements": list(movements.values()),
        "total_movements": len(movements),
        "tracker_stats": aggregator.line_tracker.get_tracker_stats()
    }

@api_router.get("/line-movements/significant")
async def get_significant_line_movements():
    """Get only significant line movements"""
    significant = aggregator.line_tracker.get_significant_movements()
    return {
        "significant_movements": significant,
        "count": len(significant)
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    logger.info("Starting CS2 Pro Projection API...")
    await fetch_real_data()
    logger.info("Data fetched successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()