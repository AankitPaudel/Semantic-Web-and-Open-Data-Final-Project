"""
collect_data.py
Member 2 – Data Engineering & Cleaning Lead
CS4625/5625 Final Project

This script implements the data collection pipeline:
1. Connects to DBpedia to fetch Premier League team metadata.
2. Connects to Wikidata to fetch match results (2020-2024).
   * FALLBACK: If SPARQL fails or returns < 50 matches, downloads official CSVs from football-data.co.uk.
3. Connects to DBpedia for aggregate team statistics.
4. Cleans, normalizes, and saves data to CSV format.
"""

import sys
import time
import json
import urllib.request
import io
from pathlib import Path
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# =============================================================================
# CONFIGURATION
# =============================================================================

# Determine paths dynamically
BASE_DIR = Path(__file__).resolve().parent.parent if "analysis" in Path(__file__).name else Path(__file__).resolve().parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"

# Create directories if they don't exist
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

# SPARQL Endpoints
DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

# User Agent to be polite to Wikipedia/DBpedia servers
USER_AGENT = "CS4625-Student-Project/1.0 (contact@example.university.edu)"

# =============================================================================
# SPARQL QUERIES
# =============================================================================

# Query 1: Get Teams (DBpedia)
QUERY_TEAMS = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?team ?teamName ?stadium ?founded WHERE {
  ?team dbo:league dbr:Premier_League .
  ?team rdfs:label ?teamName .
  OPTIONAL { ?team dbo:ground ?stadium . }
  OPTIONAL { ?team dbo:foundingDate ?founded . }
  FILTER (lang(?teamName) = 'en')
}
ORDER BY ?teamName
LIMIT 200
"""

# Query 2: Get Matches (Wikidata) - Optimized for specific PL seasons
QUERY_MATCHES = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?match ?matchLabel ?date ?homeTeam ?homeTeamLabel ?awayTeam ?awayTeamLabel ?homeGoals ?awayGoals
WHERE {
  # VALUES: Look for specific PL seasons (2020-2024)
  VALUES ?season { 
    wd:Q116198950 # 2023-24
    wd:Q111963073 # 2022-23
    wd:Q106624599 # 2021-22
    wd:Q94051381  # 2020-21
  }
  ?match wdt:P2453 ?season .
  
  ?match wdt:P6112 ?homeTeam ;         # Home team
         wdt:P6113 ?awayTeam ;         # Away team
         wdt:P585  ?date ;             # Date
         wdt:P1350 ?homeGoals ;        # Home goals
         wdt:P1351 ?awayGoals .        # Away goals

  ?homeTeam rdfs:label ?homeTeamLabel .
  ?awayTeam rdfs:label ?awayTeamLabel .

  FILTER (lang(?homeTeamLabel) = "en")
  FILTER (lang(?awayTeamLabel) = "en")
}
ORDER BY DESC(?date)
LIMIT 2000
"""

# Query 3: Team Stats (DBpedia)
QUERY_STATS = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?team ?teamName ?wins ?losses ?draws ?goalsFor ?goalsAgainst WHERE {
  ?team dbo:league dbr:Premier_League .
  ?team rdfs:label ?teamName .
  
  OPTIONAL { ?team dbo:numberOfWins ?wins . }
  OPTIONAL { ?team dbo:numberOfGoals ?goalsFor . }
  
  FILTER (lang(?teamName) = 'en')
}
LIMIT 100
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def execute_query(endpoint, query, description):
    """Executes SPARQL query with retry logic."""
    print(f"\n⏳ {description}...")
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.addCustomHttpHeader("User-Agent", USER_AGENT)

    retries = 3
    for i in range(retries):
        try:
            return sparql.query().convert()
        except Exception as e:
            print(f"   ⚠️ Attempt {i+1} failed: {e}")
            time.sleep(2)
    
    print(f"   ❌ Failed to retrieve data for {description}")
    return None

def fetch_fallback_data():
    """Downloads CSV data from football-data.co.uk if SPARQL fails."""
    print("\n🌍 SPARQL returned insufficient data. Switching to Backup Source (football-data.co.uk)...")
    
    # URLs for Premier League Seasons: 23/24, 22/23, 21/22, 20/21
    urls = [
        "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2122/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2021/E0.csv"
    ]
    
    all_matches = []
    
    for url in urls:
        try:
            print(f"   ⬇️ Downloading: {url}...")
            # Use pandas directly to read CSV from URL
            # encoding='latin1' is often needed for football-data.co.uk files
            df = pd.read_csv(url, encoding='latin1')
            
            # Keep only relevant columns
            if {'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'}.issubset(df.columns):
                df_clean = df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].copy()
                df_clean.rename(columns={
                    'Date': 'date',
                    'HomeTeam': 'home_team',
                    'AwayTeam': 'away_team',
                    'FTHG': 'home_goals',
                    'FTAG': 'away_goals'
                }, inplace=True)
                
                # Standardize date format (football-data uses DD/MM/YYYY)
                df_clean['date'] = pd.to_datetime(df_clean['date'], dayfirst=True, errors='coerce')
                
                # Create a fake URI for consistency with SPARQL results
                df_clean['match_uri'] = df_clean.apply(
                    lambda x: f"http://football-data.co.uk/match/{x['home_team'].replace(' ', '_')}_vs_{x['away_team'].replace(' ', '_')}_{x['date'].strftime('%Y%m%d')}", 
                    axis=1
                )
                
                all_matches.append(df_clean)
        except Exception as e:
            print(f"   ⚠️ Failed to download {url}: {e}")

    if all_matches:
        full_df = pd.concat(all_matches, ignore_index=True)
        print(f"   ✅ Backup Source Successful: {len(full_df)} matches loaded.")
        return full_df
    else:
        print("   ❌ Backup Source Failed.")
        return pd.DataFrame()

def save_csv(df, filename):
    """Saves DataFrame to CSV and logs it."""
    filepath = DATA_RAW_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"   💾 Saved: {filepath}")

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline():
    print("="*60)
    print("DATA ENGINEERING PIPELINE STARTED")
    print("="*60)

    # ---------------------------------------------------------
    # 1. FETCH TEAMS
    # ---------------------------------------------------------
    data = execute_query(DBPEDIA_ENDPOINT, QUERY_TEAMS, "Fetching Premier League Teams")
    
    if data:
        teams_list = []
        for item in data['results']['bindings']:
            teams_list.append({
                'team_uri': item.get('team', {}).get('value'),
                'team_name': item.get('teamName', {}).get('value'),
                'stadium': item.get('stadium', {}).get('value', 'Unknown'),
                'founded': item.get('founded', {}).get('value', 'Unknown')
            })
        
        df_teams = pd.DataFrame(teams_list)
        if not df_teams.empty:
            df_teams.drop_duplicates(subset=['team_uri'], inplace=True)
            df_teams['team_name'] = df_teams['team_name'].str.strip()
            print(f"   ✅ Retrieved {len(df_teams)} unique teams")
            save_csv(df_teams, 'premier_league_teams.csv')
        else:
            print("   ⚠️ No team data found.")

    # ---------------------------------------------------------
    # 2. FETCH MATCHES (With Fallback)
    # ---------------------------------------------------------
    data = execute_query(WIKIDATA_ENDPOINT, QUERY_MATCHES, "Fetching Match Results (2020-2024)")
    df_matches = pd.DataFrame()
    
    # Try processing SPARQL results first
    if data and "results" in data and "bindings" in data["results"] and len(data["results"]["bindings"]) > 0:
        matches_list = []
        for item in data["results"]["bindings"]:
            matches_list.append({
                'match_uri': item.get('match', {}).get('value'),
                'date': item.get('date', {}).get('value'),
                'home_team': item.get('homeTeamLabel', {}).get('value'),
                'away_team': item.get('awayTeamLabel', {}).get('value'),
                'home_goals': item.get('homeGoals', {}).get('value'),
                'away_goals': item.get('awayGoals', {}).get('value')
            })
        df_matches = pd.DataFrame(matches_list)
        
        # Clean SPARQL data
        df_matches['date'] = pd.to_datetime(df_matches['date'], errors='coerce')
        df_matches['home_goals'] = pd.to_numeric(df_matches['home_goals'], errors='coerce')
        df_matches['away_goals'] = pd.to_numeric(df_matches['away_goals'], errors='coerce')
        df_matches.dropna(subset=['home_goals', 'away_goals', 'date'], inplace=True)

    # If SPARQL result is too small (< 50 matches), use Fallback
    if len(df_matches) < 50:
        if len(df_matches) > 0:
            print(f"   ⚠️ SPARQL only returned {len(df_matches)} matches. Fetching more data...")
        df_fallback = fetch_fallback_data()
        
        # Merge if we have fallback data
        if not df_fallback.empty:
            df_matches = pd.concat([df_matches, df_fallback], ignore_index=True)
            # Drop duplicates if any overlap
            df_matches.drop_duplicates(subset=['date', 'home_team', 'away_team'], inplace=True)
    
    # Save final Matches CSV
    if not df_matches.empty:
        print(f"   ✅ Final Dataset: {len(df_matches)} matches ready for analysis.")
        save_csv(df_matches, 'match_results.csv')
    else:
        print("   ❌ CRITICAL: No match data found from either SPARQL or Fallback.")

    # ---------------------------------------------------------
    # 3. FETCH STATS (Validation)
    # ---------------------------------------------------------
    data = execute_query(DBPEDIA_ENDPOINT, QUERY_STATS, "Fetching Team Statistics")
    if data:
        stats_list = []
        for item in data['results']['bindings']:
            stats_list.append({
                'team_name': item.get('teamName', {}).get('value'),
                'wins': item.get('wins', {}).get('value', 0),
                'goals_for': item.get('goalsFor', {}).get('value', 0)
            })
        df_stats = pd.DataFrame(stats_list)
        if not df_stats.empty:
            save_csv(df_stats, 'team_stats.csv')

    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print(f"Data available in: {DATA_RAW_DIR}")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()