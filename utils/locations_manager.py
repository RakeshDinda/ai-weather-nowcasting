"""
Locations Manager:
Loads and manages 790+ Indian locations from data/india_locations.csv.
Provides fast lookups and state-to-climate-region mapping.
"""
import os
import pandas as pd
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "india_locations.csv")

# Comprehensive State to Region mapping for climatological realism
STATE_REGION_MAP = {
    # North
    "Delhi": "North",
    "Haryana": "North",
    "Punjab": "North",
    "Himachal Pradesh": "North",
    "Jammu and Kashmir": "North",
    "Ladakh": "North",
    "Chandigarh": "North",
    "Uttarakhand": "North",
    "Uttar Pradesh": "North",
    # West
    "Rajasthan": "West",
    "Gujarat": "West",
    "Maharashtra": "West",
    "Goa": "West",
    "Dadra and Nagar Haveli and Daman and Diu": "West",
    # South
    "Karnataka": "South",
    "Kerala": "South",
    "Tamil Nadu": "South",
    "Andhra Pradesh": "South",
    "Telangana": "South",
    "Puducherry": "South",
    "Lakshadweep": "South",
    # East
    "Bihar": "East",
    "Jharkhand": "East",
    "Odisha": "East",
    "West Bengal": "East",
    "Andaman and Nicobar Islands": "East",
    # Central
    "Madhya Pradesh": "Central",
    "Chhattisgarh": "Central",
    # Northeast
    "Assam": "Northeast",
    "Arunachal Pradesh": "Northeast",
    "Manipur": "Northeast",
    "Meghalaya": "Northeast",
    "Mizoram": "Northeast",
    "Nagaland": "Northeast",
    "Tripura": "Northeast",
    "Sikkim": "Northeast"
}

_LOCATIONS_CACHE: Optional[List[Dict[str, Any]]] = None

def get_india_locations() -> List[Dict[str, Any]]:
    """
    Loads and returns all locations from data/india_locations.csv.
    Caches in memory on first read.
    """
    global _LOCATIONS_CACHE
    if _LOCATIONS_CACHE is not None:
        return _LOCATIONS_CACHE
        
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"India locations CSV not found at: {CSV_PATH}")
        
    df = pd.read_csv(CSV_PATH)
    locations = []
    for _, row in df.iterrows():
        st = str(row.get("state", "India"))
        loc = {
            "city": str(row["city"]),
            "state": st,
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "region": STATE_REGION_MAP.get(st, "North")
        }
        locations.append(loc)
        
    _LOCATIONS_CACHE = locations
    return _LOCATIONS_CACHE

def find_location_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Fast case-insensitive search by city name."""
    query = name.strip().lower()
    for loc in get_india_locations():
        if loc["city"].lower() == query:
            return loc
    # Substring match fallback
    for loc in get_india_locations():
        if query in loc["city"].lower():
            return loc
    return None


def get_sampled_locations(limit: int = 200, state: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns a balanced, stratified sample of Indian locations.
    Guarantees every State and UT (especially North-East) is represented,
    limiting to 100-200 cities per request for optimal performance.
    """
    all_locs = get_india_locations()
    if state:
        st_lower = state.strip().lower()
        matched = [loc for loc in all_locs if loc["state"].lower() == st_lower]
        return matched[:limit]
        
    if limit >= len(all_locs):
        return all_locs
        
    # Stratified sampling across all states/UTs
    by_state: Dict[str, List[Dict[str, Any]]] = {}
    for loc in all_locs:
        by_state.setdefault(loc["state"], []).append(loc)
        
    total_states = len(by_state)
    target_per_state = max(2, limit // total_states)
    
    sampled: List[Dict[str, Any]] = []
    
    # First pass: collect up to target_per_state from every state
    for st, loc_list in by_state.items():
        n = min(len(loc_list), target_per_state)
        # Select representative entries (evenly spaced)
        step = max(1, len(loc_list) // n)
        for i in range(0, len(loc_list), step):
            if len(sampled) < limit:
                sampled.append(loc_list[i])
            if len([x for x in sampled if x["state"] == st]) >= n:
                break
                
    # If we have remaining quota up to limit, fill with remaining items from larger states
    if len(sampled) < limit:
        sampled_keys = set((x["city"], x["state"]) for x in sampled)
        for loc in all_locs:
            key = (loc["city"], loc["state"])
            if key not in sampled_keys:
                sampled.append(loc)
                sampled_keys.add(key)
                if len(sampled) >= limit:
                    break
                    
    return sampled[:limit]

