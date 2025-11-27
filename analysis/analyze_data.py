"""
analyze_data.py
Member 3 – Aarav (Analysis & Modeling Lead)
CS4625/5625 Final Project

This script performs statistical analysis on Premier League match data to investigate home advantage.

Research Questions:
Q1: Do Premier League teams demonstrate a statistically significant home advantage?
Q2: Which teams benefit most from playing at home?

Analysis Methods:
- Descriptive statistics (win percentages)
- Chi-square test for overall home advantage
- Paired t-test for team-level significance
- Home advantage score calculation (home_win% - away_win%)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import json
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================

# Determine paths dynamically
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Create output directory if it doesn't exist
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# STEP 1: LOAD DATA
# =============================================================================

print("=" * 80)
print("PREMIER LEAGUE HOME ADVANTAGE ANALYSIS")
print("Member 3: Aarav (Analysis & Modeling Lead)")
print("=" * 80)

print("\n STEP 1: Loading Data...")

try:
    # Load match results
    matches_df = pd.read_csv(DATA_RAW_DIR / 'match_results.csv')
    print(f" Loaded {len(matches_df)} matches from match_results.csv")
    
    # Load teams (for reference)
    teams_df = pd.read_csv(DATA_RAW_DIR / 'premier_league_teams.csv')
    print(f" Loaded {len(teams_df)} teams from premier_league_teams.csv")
    
except FileNotFoundError as e:
    print(f" ERROR: Could not find data files!")
    print(f"   Make sure these files exist in {DATA_RAW_DIR}:")
    print(f"   - match_results.csv")
    print(f"   - premier_league_teams.csv")
    sys.exit(1)

# =============================================================================
# STEP 2: DATA PREPROCESSING & VALIDATION
# =============================================================================

print("\n🔧 STEP 2: Data Preprocessing & Validation...")

# Convert date to datetime
matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')

# Remove rows with missing data
initial_count = len(matches_df)
matches_df = matches_df.dropna(subset=['date', 'home_team', 'away_team', 'home_goals', 'away_goals'])
print(f"   Removed {initial_count - len(matches_df)} rows with missing data")

# Remove duplicates
initial_count = len(matches_df)
matches_df = matches_df.drop_duplicates(subset=['date', 'home_team', 'away_team'])
print(f"   Removed {initial_count - len(matches_df)} duplicate matches")

# Ensure goals are numeric
matches_df['home_goals'] = pd.to_numeric(matches_df['home_goals'], errors='coerce')
matches_df['away_goals'] = pd.to_numeric(matches_df['away_goals'], errors='coerce')

# Remove any rows where goals couldn't be converted
matches_df = matches_df.dropna(subset=['home_goals', 'away_goals'])

# Sort by date
matches_df = matches_df.sort_values('date')

print(f" Final dataset: {len(matches_df)} valid matches")
print(f"   Date range: {matches_df['date'].min().date()} to {matches_df['date'].max().date()}")

# =============================================================================
# STEP 3: CALCULATE MATCH OUTCOMES
# =============================================================================

print("\n STEP 3: Calculating Match Outcomes...")

# Determine match outcome
matches_df['home_win'] = (matches_df['home_goals'] > matches_df['away_goals']).astype(int)
matches_df['away_win'] = (matches_df['home_goals'] < matches_df['away_goals']).astype(int)
matches_df['draw'] = (matches_df['home_goals'] == matches_df['away_goals']).astype(int)

# Calculate goal difference
matches_df['goal_difference'] = matches_df['home_goals'] - matches_df['away_goals']

print(f" Match outcomes calculated")

# =============================================================================
# ANALYSIS 1: OVERALL HOME ADVANTAGE
# =============================================================================

print("\n" + "=" * 80)
print("ANALYSIS 1: OVERALL HOME ADVANTAGE (Answers Research Question 1)")
print("=" * 80)

total_matches = len(matches_df)
home_wins = matches_df['home_win'].sum()
away_wins = matches_df['away_win'].sum()
draws = matches_df['draw'].sum()

home_win_pct = (home_wins / total_matches) * 100
away_win_pct = (away_wins / total_matches) * 100
draw_pct = (draws / total_matches) * 100

print(f"\n Overall Match Statistics:")
print(f"   Total Matches Analyzed: {total_matches}")
print(f"   Home Wins: {home_wins} ({home_win_pct:.2f}%)")
print(f"   Away Wins: {away_wins} ({away_win_pct:.2f}%)")
print(f"   Draws: {draws} ({draw_pct:.2f}%)")
print(f"   Home Advantage: {home_win_pct - away_win_pct:.2f} percentage points")

# Statistical Test: Chi-square test for independence
print(f"\n Statistical Test: Chi-Square Test")
print(f"   Hypothesis: Match outcomes are NOT equally distributed")

observed = [home_wins, away_wins, draws]
expected_equal = [total_matches/3, total_matches/3, total_matches/3]

chi_stat, p_value = stats.chisquare(observed, expected_equal)

print(f"   Chi-Square Statistic: {chi_stat:.4f}")
print(f"   P-value: {p_value:.6f}")

if p_value < 0.05:
    print(f"    RESULT: STATISTICALLY SIGNIFICANT (p < 0.05)")
    print(f"   CONCLUSION: Home advantage EXISTS!")
else:
    print(f"    RESULT: NOT statistically significant (p >= 0.05)")
    print(f"   CONCLUSION: No evidence of home advantage")

# =============================================================================
# ANALYSIS 2: TEAM-BY-TEAM HOME ADVANTAGE
# =============================================================================

print("\n" + "=" * 80)
print("ANALYSIS 2: TEAM-BY-TEAM HOME ADVANTAGE (Answers Research Question 2)")
print("=" * 80)

# Get unique teams from match data
all_teams = pd.concat([
    matches_df['home_team'],
    matches_df['away_team']
]).unique()

print(f"\n  Analyzing {len(all_teams)} teams...")

team_stats_list = []

for team in all_teams:
    # HOME MATCHES
    home_matches = matches_df[matches_df['home_team'] == team]
    home_total = len(home_matches)
    home_wins_count = home_matches['home_win'].sum()
    home_draws_count = home_matches['draw'].sum()
    home_losses_count = home_matches['away_win'].sum()
    home_goals_scored = home_matches['home_goals'].sum()
    home_goals_conceded = home_matches['away_goals'].sum()
    home_win_rate = (home_wins_count / home_total * 100) if home_total > 0 else 0
    
    # AWAY MATCHES
    away_matches = matches_df[matches_df['away_team'] == team]
    away_total = len(away_matches)
    away_wins_count = away_matches['away_win'].sum()
    away_draws_count = away_matches['draw'].sum()
    away_losses_count = away_matches['home_win'].sum()
    away_goals_scored = away_matches['away_goals'].sum()
    away_goals_conceded = away_matches['home_goals'].sum()
    away_win_rate = (away_wins_count / away_total * 100) if away_total > 0 else 0
    
    # HOME ADVANTAGE SCORE
    home_advantage = home_win_rate - away_win_rate
    
    team_stats_list.append({
        'team_name': team,
        'home_matches': home_total,
        'home_wins': home_wins_count,
        'home_draws': home_draws_count,
        'home_losses': home_losses_count,
        'home_goals_scored': int(home_goals_scored),
        'home_goals_conceded': int(home_goals_conceded),
        'home_win_pct': round(home_win_rate, 2),
        'away_matches': away_total,
        'away_wins': away_wins_count,
        'away_draws': away_draws_count,
        'away_losses': away_losses_count,
        'away_goals_scored': int(away_goals_scored),
        'away_goals_conceded': int(away_goals_conceded),
        'away_win_pct': round(away_win_rate, 2),
        'home_advantage': round(home_advantage, 2),
        'total_matches': home_total + away_total
    })

team_performance = pd.DataFrame(team_stats_list)

# Filter teams with sufficient data (at least 10 home and 10 away matches)
team_performance_filtered = team_performance[
    (team_performance['home_matches'] >= 10) & 
    (team_performance['away_matches'] >= 10)
].copy()

print(f" Analysis complete for {len(team_performance_filtered)} teams with sufficient data (10+ home & away matches)")

# Sort by home advantage
team_performance_filtered = team_performance_filtered.sort_values('home_advantage', ascending=False)

# Display top 10 teams with strongest home advantage
print(f"\n TOP 10 Teams with Strongest Home Advantage:")
print(team_performance_filtered[['team_name', 'home_win_pct', 'away_win_pct', 'home_advantage']].head(10).to_string(index=False))

# Display bottom 5 teams with weakest home advantage
print(f"\n BOTTOM 5 Teams with Weakest Home Advantage:")
print(team_performance_filtered[['team_name', 'home_win_pct', 'away_win_pct', 'home_advantage']].tail(5).to_string(index=False))

# Statistical Test: Paired T-Test
print(f"\n Statistical Test: Paired T-Test (Home vs Away Win %)")
print(f"   Hypothesis: Teams win more at home than away")

home_percentages = team_performance_filtered['home_win_pct'].values
away_percentages = team_performance_filtered['away_win_pct'].values

t_stat, p_value_paired = stats.ttest_rel(home_percentages, away_percentages)

print(f"   T-Statistic: {t_stat:.4f}")
print(f"   P-value: {p_value_paired:.6f}")

if p_value_paired < 0.05:
    print(f"    RESULT: STATISTICALLY SIGNIFICANT (p < 0.05)")
    print(f"   CONCLUSION: Teams perform significantly better at home!")
else:
    print(f"    RESULT: NOT statistically significant (p >= 0.05)")

# =============================================================================
# ANALYSIS 3: DESCRIPTIVE STATISTICS
# =============================================================================

print("\n" + "=" * 80)
print("ANALYSIS 3: DESCRIPTIVE STATISTICS")
print("=" * 80)

print(f"\n Home Advantage Distribution:")
print(f"   Mean Home Advantage: {team_performance_filtered['home_advantage'].mean():.2f}%")
print(f"   Median Home Advantage: {team_performance_filtered['home_advantage'].median():.2f}%")
print(f"   Std Deviation: {team_performance_filtered['home_advantage'].std():.2f}%")
print(f"   Min Home Advantage: {team_performance_filtered['home_advantage'].min():.2f}%")
print(f"   Max Home Advantage: {team_performance_filtered['home_advantage'].max():.2f}%")

# =============================================================================
# STEP 4: SAVE RESULTS
# =============================================================================

print("\n" + "=" * 80)
print("STEP 4: SAVING RESULTS")
print("=" * 80)

# Save 1: Team Performance Analysis (CSV)
output_csv = DATA_PROCESSED_DIR / 'team_performance_analysis.csv'
team_performance.to_csv(output_csv, index=False)
print(f" Saved: {output_csv}")
print(f"   Contains performance data for {len(team_performance)} teams")

# Save 2: Summary Statistics (JSON)
summary_stats = {
    'dataset_info': {
        'total_matches': int(total_matches),
        'date_range_start': str(matches_df['date'].min().date()),
        'date_range_end': str(matches_df['date'].max().date()),
        'unique_teams': len(all_teams),
        'teams_analyzed': len(team_performance_filtered)
    },
    'overall_results': {
        'home_wins': int(home_wins),
        'away_wins': int(away_wins),
        'draws': int(draws),
        'home_win_pct': float(round(home_win_pct, 2)),
        'away_win_pct': float(round(away_win_pct, 2)),
        'draw_pct': float(round(draw_pct, 2)),
        'home_advantage_pct_points': float(round(home_win_pct - away_win_pct, 2))
    },
    'statistical_tests': {
        'chi_square': {
            'test_name': 'Chi-Square Test for Independence',
            'statistic': float(round(chi_stat, 4)),
            'p_value': float(round(p_value, 6)),
            'significant': bool(p_value < 0.05),
            'alpha': 0.05
        },
        'paired_t_test': {
            'test_name': 'Paired T-Test (Home vs Away Win %)',
            't_statistic': float(round(t_stat, 4)),
            'p_value': float(round(p_value_paired, 6)),
            'significant': bool(p_value_paired < 0.05),
            'alpha': 0.05
        }
    },
    'team_level_analysis': {
        'mean_home_advantage': float(round(team_performance_filtered['home_advantage'].mean(), 2)),
        'median_home_advantage': float(round(team_performance_filtered['home_advantage'].median(), 2)),
        'std_home_advantage': float(round(team_performance_filtered['home_advantage'].std(), 2)),
        'min_home_advantage': float(round(team_performance_filtered['home_advantage'].min(), 2)),
        'max_home_advantage': float(round(team_performance_filtered['home_advantage'].max(), 2))
    },
    'top_5_teams': team_performance_filtered.head(5)[['team_name', 'home_advantage']].to_dict('records'),
    'bottom_5_teams': team_performance_filtered.tail(5)[['team_name', 'home_advantage']].to_dict('records')
}

output_json = DATA_PROCESSED_DIR / 'summary_statistics.json'
with open(output_json, 'w') as f:
    json.dump(summary_stats, f, indent=4)
print(f" Saved: {output_json}")
print(f"   Contains summary statistics and test results")

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print(" ANALYSIS COMPLETE!")
print("=" * 80)

print(f"\n KEY FINDINGS:")
print(f"   1. Home teams win {home_win_pct:.2f}% of matches")
print(f"   2. Away teams win {away_win_pct:.2f}% of matches")
print(f"   3. Home advantage: {home_win_pct - away_win_pct:.2f} percentage points")
print(f"   4. Statistical significance: {'YES ' if p_value < 0.05 else 'NO '} (p = {p_value:.6f})")
print(f"   5. Team-level significance: {'YES ' if p_value_paired < 0.05 else 'NO '} (p = {p_value_paired:.6f})")
print(f"   6. Average team home advantage: {team_performance_filtered['home_advantage'].mean():.2f}%")

print(f"\n OUTPUT FILES:")
print(f"   - {output_csv}")
print(f"   - {output_json}")

print(f"\n Ready for Member 4 (Visualization Lead) to create plots!")
print("=" * 80)