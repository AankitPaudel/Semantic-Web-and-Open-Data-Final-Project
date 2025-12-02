# Premier League Home Advantage Analysis
## Using Semantic Web Technologies and Statistical Analysis
  
**Institution:** University of Idaho  
**Course:** CS4625/5625 - Semantic Web & Ontology  
**Date:** December 2024  
**Status:** Complete

---

## Overview

This project investigates whether Premier League football teams demonstrate a statistically significant home advantage by analyzing 1,520 matches from the 2020-2024 seasons. Using Semantic Web technologies (SPARQL queries to DBpedia and Wikidata) combined with statistical analysis in Python, we provide empirical evidence for the home advantage phenomenon in professional football.

### Research Questions

**Question 1:** Do Premier League teams demonstrate a statistically significant home advantage?

**Question 2:** Which specific teams benefit most from playing at home?

### Key Findings

- Home teams win 43.82% of matches versus 33.82% for away teams
- 10 percentage point advantage (chi-square = 105.04, p < 0.000001)
- Wide team variation: Tottenham (+23.68%) to Watford (-10.53%)
- Mean home advantage: 9.06% across 26 teams analyzed

---

## Technology Stack

**Data Collection:**
- SPARQL 1.1 query language
- DBpedia SPARQL endpoint
- Wikidata Query Service
- Python SPARQLWrapper library
- football-data.co.uk (CSV fallback)

**Data Processing:**
- Python 3.8+
- pandas library for data manipulation
- numpy for numerical operations

**Statistical Analysis:**
- scipy.stats module
- Chi-square test for independence
- Paired sample t-test

**Visualization:**
- matplotlib library
- seaborn for statistical graphics

**Documentation:**
- Markdown
- Microsoft Word

---

## Project Structure

```
premier-league-home-advantage/
│
├── data/
│   ├── raw/
│   │   ├── premier_league_teams.csv          (197 teams)
│   │   ├── match_results.csv                 (1,520 matches)
│   │   └── team_stats.csv                    (team statistics)
│   │
│   └── processed/
│       ├── team_performance_analysis.csv     (analysis results)
│       └── summary_statistics.json           (statistical tests)
│
├── queries/
│   ├── query1_teams.rq                       (DBpedia teams query)
│   ├── query2_matches.rq                     (Wikidata matches query)
│   └── query3_teamstats.rq                   (DBpedia statistics query)
│
├── analysis/
│   ├── collect_data.py                       (SPARQL data collection)
│   ├── analyze_data.py                       (statistical analysis)
│   └── make_charts.py                        (visualization generation)
│
├── visualizations/
│   ├── overall_advantage.png                 (match outcomes chart)
│   └── team_variance.png                     (team rankings chart)
│
├── documentation/
│   ├── section1_sparql_exploration.md        (SPARQL documentation)
│   ├── ROADMAP.md                            (project timeline)
│   └── README.md                             (this file)
│
└── submission/
    ├── SWOP_2020_Assignment4a.docx    (written report)
    └── SWOP_2020_Assignment4b.pptx    (presentation)
```

---

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Required Packages

```bash
pip install sparqlwrapper pandas numpy scipy matplotlib seaborn
```

### Verify Installation

```bash
python --version
pip list | grep sparqlwrapper
```

---

## Running the Project

### Step 1: Collect Data from SPARQL Endpoints

```bash
python analysis/collect_data.py
```

**What this does:**
- Queries DBpedia for Premier League team metadata
- Attempts to query Wikidata for match results
- Falls back to football-data.co.uk CSV if Wikidata returns insufficient data
- Normalizes all data into consistent format
- Saves CSV files to data/raw/

**Expected output:**
- data/raw/premier_league_teams.csv (197 teams)
- data/raw/match_results.csv (1,520 matches)
- data/raw/team_stats.csv (statistics)

### Step 2: Perform Statistical Analysis

```bash
python analysis/analyze_data.py
```

**What this does:**
- Loads collected match data
- Removes duplicates and validates dates
- Calculates overall home/away/draw percentages
- Performs chi-square test for overall home advantage
- Calculates home advantage score for each team
- Performs paired t-test for team-level analysis
- Saves results to data/processed/

**Expected output:**
- data/processed/team_performance_analysis.csv
- data/processed/summary_statistics.json
- Console output with statistical test results

### Step 3: Generate Visualizations

```bash
python analysis/make_charts.py
```

**What this does:**
- Loads analysis results
- Creates bar chart of overall match outcomes
- Creates horizontal bar chart of team rankings
- Saves charts as high-resolution PNG files (300 DPI)

**Expected output:**
- visualizations/overall_advantage.png
- visualizations/team_variance.png

---

## Methodology

### Data Collection Approach

**SPARQL Query 1: Premier League Teams (DBpedia)**

```sparql
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
```

**Result:** 197 unique Premier League team entities

**SPARQL Query 2: Match Results (Wikidata)**

```sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?match ?date ?homeTeam ?homeTeamLabel ?awayTeam ?awayTeamLabel 
       ?homeGoals ?awayGoals
WHERE {
  VALUES ?season { 
    wd:Q116198950  # 2023-24 season
    wd:Q111963073  # 2022-23 season
    wd:Q106624599  # 2021-22 season
    wd:Q94051381   # 2020-21 season
  }
  ?match wdt:P2453 ?season .
  ?match wdt:P6112 ?homeTeam ;
         wdt:P6113 ?awayTeam ;
         wdt:P585  ?date ;
         wdt:P1350 ?homeGoals ;
         wdt:P1351 ?awayGoals .
  
  ?homeTeam rdfs:label ?homeTeamLabel .
  ?awayTeam rdfs:label ?awayTeamLabel .
  
  FILTER (lang(?homeTeamLabel) = "en")
  FILTER (lang(?awayTeamLabel) = "en")
}
ORDER BY DESC(?date)
LIMIT 2000
```

**Hybrid Approach:**

When Wikidata returned fewer than 50 matches, the system automatically:
1. Downloads CSV files from football-data.co.uk for seasons 2020-2024
2. Normalizes CSV data to match SPARQL schema
3. Combines with any available SPARQL results

**Final Result:** 1,520 complete match records

---

### Statistical Analysis Methods

**Data Preprocessing:**

1. Duplicate Removal
   - Checked for repeated date-team combinations
   - Removed approximately 3% duplicate records

2. Data Validation
   - Verified all dates fall within 2020-2024 range
   - Ensured goal values are numeric and non-negative
   - Filtered for complete records only

3. Sample Size Requirements
   - Teams must have minimum 10 home matches
   - Teams must have minimum 10 away matches
   - Result: 26 teams met criteria for analysis

**Overall Analysis (Research Question 1):**

Metrics Calculated:
- Home win percentage: 43.82%
- Away win percentage: 33.82%
- Draw percentage: 22.37%

Statistical Test: Chi-Square Test for Independence
- Null Hypothesis: Match outcomes are equally distributed
- Test Statistic: χ² = 105.0368
- P-value: < 0.000001
- Result: STATISTICALLY SIGNIFICANT
- Conclusion: Home advantage exists at league level

**Team-Level Analysis (Research Question 2):**

Metrics Calculated:
- Home advantage score = Home Win Percentage - Away Win Percentage
- Calculated for each of 26 teams

Statistical Test: Paired Sample T-Test
- Null Hypothesis: Home Win Percentage equals Away Win Percentage
- Test Statistic: t = 6.4876
- P-value: 0.000001
- Result: STATISTICALLY SIGNIFICANT
- Conclusion: Teams systematically perform better at home

Descriptive Statistics:
- Mean home advantage: 9.06%
- Median: 8.99%
- Standard deviation: 7.12%
- Range: -10.53% to +23.68%

---

### Visualization Approach

**Chart 1: Overall Match Outcomes**

Type: Bar chart
Data: Home wins (43.82%), Away wins (33.82%), Draws (22.37%)
Colors: Green for home wins, red for away wins, gray for draws
Format: 300 DPI PNG
Key Feature: Annotation highlighting 10% home advantage gap

**Chart 2: Team-Level Home Advantage**

Type: Horizontal bar chart
Data: Home advantage scores for 26 teams
Colors: Green for positive advantage, red for negative advantage
Format: 300 DPI PNG
Key Features:
- Teams ranked from highest to lowest advantage
- League average reference line at +9.06%
- Annotation highlighting Watford anomaly

---

## Results

### Overall Statistics

| Metric | Value |
|--------|-------|
| Total Matches Analyzed | 1,520 |
| Home Wins | 666 (43.82%) |
| Away Wins | 514 (33.82%) |
| Draws | 340 (22.37%) |
| Home Advantage | 10.0 percentage points |

### Statistical Significance Tests

| Test | Statistic | P-value | Result |
|------|-----------|---------|--------|
| Chi-Square Test | χ² = 105.04 | < 0.000001 | Statistically Significant |
| Paired T-Test | t = 6.49 | < 0.000001 | Statistically Significant |

### Top 5 Teams by Home Advantage

| Rank | Team | Home Win % | Away Win % | Home Advantage |
|------|------|------------|------------|----------------|
| 1 | Tottenham | 63.16% | 39.47% | +23.68% |
| 2 | Nottingham Forest | 63.16% | 42.11% | +21.05% |
| 3 | Liverpool | 69.74% | 50.00% | +19.74% |
| 4 | Newcastle | 55.26% | 39.47% | +15.79% |
| 5 | Wolves | 44.74% | 30.26% | +14.47% |

### Bottom 5 Teams by Home Advantage

| Rank | Team | Home Win % | Away Win % | Home Advantage |
|------|------|------------|------------|----------------|
| 22 | Brighton | 35.53% | 31.58% | +3.95% |
| 23 | Chelsea | 44.74% | 43.42% | +1.32% |
| 24 | Leeds | 18.42% | 18.42% | 0.00% |
| 25 | Burnley | 15.79% | 15.79% | 0.00% |
| 26 | Watford | 15.79% | 26.32% | -10.53% |

---

## Key Insights

### Technical Insights

**Linked Data Coverage:**
- DBpedia provides excellent metadata for football teams
- Wikidata has good structure but incomplete match coverage
- Hybrid approach (SPARQL + CSV) necessary for comprehensive analysis
- OPTIONAL clauses essential for handling missing properties

**Data Quality:**
- Approximately 3% of data were duplicates
- Date validation prevented temporal analysis errors
- Sample size requirements ensure reliable percentage calculations
- Cross-validation with external sources confirmed accuracy

**Statistical Significance:**
- P-values < 0.000001 indicate extremely strong effects
- Large sample size (1,520 matches) provides high confidence
- Multiple tests strengthen conclusions
- Effect size (10 percentage points) is substantial

### Domain Insights

**Home Advantage Reality:**
- 10 percentage point gap is substantial and consistent
- Effect persists across multiple seasons (2020-2024)
- Not attributable to random chance (p < 0.000001)
- Consistent with existing sports science literature

**Team Variation:**
- Wide range from -10.53% to +23.68%
- Top teams (Tottenham, Liverpool) show 20%+ advantages
- Some teams show zero or negative home advantage
- Watford anomaly (-10.53%) warrants further investigation

**Practical Applications:**
- Predictive models should include team-specific home advantage factors
- Betting strategies can leverage variation across teams
- Team managers can benchmark performance against league average
- Sports analysts can identify unusual patterns for investigation

---

## Assignment Requirements

### Section 1: Investigation Goal and Data Collection (15%)

**Section 1.1: Research Goal (5%)**
- Requirement: 5-6 sentences
- Delivered: 6 sentences
- Status: Complete

**Section 1.2: SPARQL Exploration (10%)**
- Requirement: 9-10 sentences
- Delivered: 11 sentences
- Status: Complete

### Section 2: Data Analysis (10%)

**Section 2.1: Research Questions and Analysis Design (5%)**
- Requirement: 5-6 sentences
- Delivered: 6 sentences
- Status: Complete

**Section 2.2: Programming Tools and Validation (5%)**
- Requirement: 5-6 sentences
- Delivered: 6 sentences
- Status: Complete

### Section 3: Visualization (10%)

**Section 3.1: Visualization Descriptions (5%)**
- Requirement: 5-6 sentences
- Delivered: 6 sentences
- Status: Complete

**Section 3.2: Visualization Value (5%)**
- Requirement: 5-6 sentences
- Delivered: 7 sentences
- Status: Complete

### Section 4: Presentation (10%)

**Final Presentation:**
- 15 slides, 15-20 minutes

---

## Deliverables

### Written Report
- Filename: SWOP_2020_Assignment4a.docx
- Format: Microsoft Word document
- Contents:
  - Section 1: Investigation Goal and Data Collection
  - Section 2: Data Analysis
  - Section 3: Visualization
  - Key Findings and Conclusions
  - References

### Presentation
- Filename: SWOP_2020_Assignment4b.pptx
- Format: Microsoft PowerPoint
- Duration: 15-20 minutes
- Contents:
  - Project overview
  - SPARQL queries and data collection
  - Statistical analysis methods
  - Visualizations and results
  - Conclusions and implications

---

## References

### Data Sources

DBpedia SPARQL Endpoint  
URL: https://dbpedia.org/sparql  
Access Date: December 2024

Wikidata Query Service  
URL: https://query.wikidata.org/  
Access Date: December 2024

Football-Data.co.uk  
URL: https://www.football-data.co.uk/  
Access Date: December 2024

### Technical Documentation

SPARQL 1.1 Query Language  
W3C Recommendation  
URL: https://www.w3.org/TR/sparql11-query/

DBpedia Ontology  
URL: http://dbpedia.org/ontology/

Python pandas Documentation  
URL: https://pandas.pydata.org/

scipy.stats Module  
URL: https://docs.scipy.org/doc/scipy/reference/stats.html

matplotlib Documentation  
URL: https://matplotlib.org/

### Statistical Methods

Chi-Square Test for Independence  
Used for testing overall home advantage significance

Paired Sample T-Test  
Used for testing team-level home versus away performance

Descriptive Statistics  
Mean, median, standard deviation, range

---

## Future Work

### Temporal Analysis
- Track home advantage trends over multiple seasons
- Analyze COVID-19 impact on home advantage (empty stadiums)
- Study seasonal variations within single seasons

### Additional Variables
- Incorporate crowd attendance data
- Analyze referee decision patterns (cards, penalties)
- Consider travel distance effects
- Study weather condition impacts

### Expanded Scope
- Compare across multiple leagues (La Liga, Serie A, Bundesliga)
- Analyze other sports (basketball, hockey, baseball)
- Study playoff versus regular season differences
- International competitions analysis

---

## Author Information

**Name:** Group Project  
**Institution:** University of Idaho  
**Expected Graduation:** December 2025  
**Course:** CS4625/5625 - Semantic Web and Ontology  

---

## License

This project was created as coursework for CS4625/5625 at the University of Idaho. All rights reserved.

---

## Acknowledgments

Course Instructor  
For guidance on Semantic Web technologies and project requirements

DBpedia and Wikidata Communities  
For maintaining comprehensive Linked Data endpoints

Football-Data.co.uk  
For providing accessible and comprehensive match data

Python Open Source Community  
For developing excellent data science libraries

---

## Project Statistics

**Code:**
- Lines of Python Code:
- SPARQL Queries Written: 3
- Functions Implemented: 15+

**Data:**
- Data Points Collected: 1,520 matches
- Teams Analyzed: 26 teams
- Time Period: 4 seasons (2020-2024)

**Documentation:**
- Report Pages: 10-12
- Presentation Slides: 15-20
- Total Sentences Written: 50+

**Time Investment:**
- Total Project Duration: 2 weeks
- Data Collection: 3 days
- Analysis: 2 days
- Visualization: 2 days
- Documentation: 3 days

**Results:**
- Statistical Significance: p < 0.000001
- Effect Size: 10 percentage points

---

END OF README