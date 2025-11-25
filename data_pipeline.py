"""
Member 2 – Data Engineering & Cleaning
Project: Betting / Bookmakers – Linked Open Data (Wikidata)

This script:
1. Queries Wikidata for bookmaker companies and their attributes.
2. Queries Wikidata for nominal GDP per capita (P2132) for countries.
3. Cleans and normalizes the datasets.
4. Joins them on ISO country codes.
5. Writes intermediate and final CSVs into a `data/` folder.

Note: We originally planned to use the World Bank Linked Data SPARQL endpoint
(http://worldbank.270a.info/sparql), but the host is currently not reachable
from our environment (getaddrinfo failed). Instead, we use Wikidata’s
`nominal GDP per capita` property (P2132), which is sourced from the World Bank.
"""

from pathlib import Path

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# ---------- Configuration ----------

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

# ---------- SPARQL queries ----------

# 1) Bookmakers (same as before)
WIKIDATA_BOOKMAKERS_QUERY = """
PREFIX wd:   <http://www.wikidata.org/entity/>
PREFIX wdt:  <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?company ?companyLabel ?country ?countryLabel ?iso2 ?inception ?employees ?revenue
WHERE {
  ?company wdt:P31 wd:Q664702 .   # bookmaker

  # country: directly or via headquarters
  OPTIONAL { ?company wdt:P17 ?country . }
  OPTIONAL { ?company wdt:P159 ?hq . ?hq wdt:P17 ?country . }

  OPTIONAL { ?country wdt:P297 ?iso2 . }      # ISO 3166-1 alpha-2
  OPTIONAL { ?company wdt:P571 ?inception . } # inception date
  OPTIONAL { ?company wdt:P1128 ?employees . }
  OPTIONAL { ?company wdt:P2139 ?revenue . }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
  }
}
LIMIT 500
"""

# 2) GDP per capita (P2132) for countries with ISO2 codes
#    We fetch all statements and later pick the latest year per country in Python.
WIKIDATA_GDP_PER_CAPITA_QUERY = """
PREFIX wd:   <http://www.wikidata.org/entity/>
PREFIX wdt:  <http://www.wikidata.org/prop/direct/>
PREFIX p:    <http://www.wikidata.org/prop/>
PREFIX ps:   <http://www.wikidata.org/prop/statement/>
PREFIX pq:   <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

SELECT ?country ?countryLabel ?iso2 ?gdpPerCapita ?gdpYear
WHERE {
  # We restrict to things that have an ISO 3166-1 alpha-2 code
  ?country wdt:P297 ?iso2 .

  # nominal GDP per capita statements
  ?country p:P2132 ?gdpStmt .
  ?gdpStmt ps:P2132 ?gdpPerCapita .

  # optional point-in-time
  OPTIONAL { ?gdpStmt pq:P585 ?gdpDate . }
  BIND( IF(BOUND(?gdpDate), YEAR(?gdpDate), 0) AS ?gdpYear )

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
  }
}
LIMIT 5000
"""

# ---------- Helper: run SPARQL and return pandas DataFrame ----------

def run_sparql(endpoint_url: str, query: str) -> pd.DataFrame:
    """Send a SPARQL query and convert JSON bindings to a DataFrame."""
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    rows = []
    for row in results["results"]["bindings"]:
        record = {}
        for var, val in row.items():
            record[var] = val.get("value")
        rows.append(record)

    df = pd.DataFrame(rows)
    return df

# ---------- Step 1: Fetch raw data ----------

def fetch_wikidata_bookmakers() -> pd.DataFrame:
    print("Querying Wikidata for bookmakers...")
    df = run_sparql(WIKIDATA_ENDPOINT, WIKIDATA_BOOKMAKERS_QUERY)
    out_path = DATA_DIR / "wikidata_bookmakers_raw.csv"
    df.to_csv(out_path, index=False)
    print(f"Wikidata bookmakers: {len(df)} rows → {out_path}")
    return df

def fetch_wikidata_gdp_per_capita() -> pd.DataFrame:
    print("Querying Wikidata for nominal GDP per capita (P2132)...")
    df = run_sparql(WIKIDATA_ENDPOINT, WIKIDATA_GDP_PER_CAPITA_QUERY)
    out_path = DATA_DIR / "wikidata_gdp_per_capita_raw.csv"
    df.to_csv(out_path, index=False)
    print(f"Wikidata GDP per capita: {len(df)} rows → {out_path}")
    return df

# ---------- Step 2: Clean and normalize ----------

def clean_wikidata_bookmakers(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning Wikidata bookmakers dataset...")
    df_clean = df.copy()

    # Remove entries without ISO2 country code (can't be joined)
    if "iso2" in df_clean.columns:
        df_clean = df_clean.dropna(subset=["iso2"])
        df_clean["iso2"] = df_clean["iso2"].str.upper()

    # Convert numeric fields
    for col in ["employees", "revenue"]:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Extract year from inception date (YYYY)
    if "inception" in df_clean.columns:
        df_clean["inception_year"] = (
            df_clean["inception"]
            .str.extract(r"(\d{4})")[0]
            .astype("Int64")
        )

    out_path = DATA_DIR / "wikidata_bookmakers_clean.csv"
    df_clean.to_csv(out_path, index=False)
    print(f"Cleaned Wikidata bookmakers: {len(df_clean)} rows → {out_path}")
    return df_clean

def clean_wikidata_gdp(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning Wikidata GDP per capita dataset...")
    df_clean = df.copy()

    # Standardize ISO code to upper case
    if "iso2" in df_clean.columns:
        df_clean["iso2"] = df_clean["iso2"].str.upper()

    # Convert GDP per capita and year to numeric
    if "gdpPerCapita" in df_clean.columns:
        df_clean["gdpPerCapita"] = pd.to_numeric(df_clean["gdpPerCapita"],
                                                 errors="coerce")
    if "gdpYear" in df_clean.columns:
        df_clean["gdpYear"] = pd.to_numeric(df_clean["gdpYear"],
                                            errors="coerce").astype("Int64")

    # Keep only rows with ISO and GDP value
    df_clean = df_clean.dropna(subset=["iso2", "gdpPerCapita"])

    # For each ISO2, keep the latest year (gdpYear); if year=0 (no date), treat as oldest
    df_clean = df_clean.sort_values(["iso2", "gdpYear"])
    df_latest = df_clean.drop_duplicates(subset=["iso2"], keep="last")

    out_path = DATA_DIR / "wikidata_gdp_per_capita_clean.csv"
    df_latest.to_csv(out_path, index=False)
    print(f"Cleaned Wikidata GDP per capita (latest per country): {len(df_latest)} rows → {out_path}")
    return df_latest

# ---------- Step 3: Join datasets ----------

def merge_bookmakers_with_gdp(df_book: pd.DataFrame,
                              df_gdp: pd.DataFrame) -> pd.DataFrame:
    print("Merging bookmakers with GDP per capita on ISO country code...")
    merged = pd.merge(
        df_book,
        df_gdp,
        left_on="iso2",
        right_on="iso2",
        how="left",
        suffixes=("", "_gdp"),
    )

    out_path = DATA_DIR / "bookmakers_with_gdp.csv"
    merged.to_csv(out_path, index=False)
    print(f"Merged dataset: {len(merged)} rows → {out_path}")

    # Quick sanity checks
    n_countries_book = merged["iso2"].nunique()
    n_countries_gdp = df_gdp["iso2"].nunique()
    print(f"Distinct countries in bookmakers dataset: {n_countries_book}")
    print(f"Distinct countries with GDP per capita data: {n_countries_gdp}")

    # Show a small sample
    cols_to_show = ["companyLabel", "countryLabel", "iso2", "gdpPerCapita", "gdpYear"]
    print(merged[cols_to_show].head())

    return merged

# ---------- Main pipeline ----------

def main():
    print("=== MEMBER 2 DATA PIPELINE (WIKIDATA-ONLY) START ===")

    # 1) Fetch raw data
    df_book_raw = fetch_wikidata_bookmakers()
    df_gdp_raw = fetch_wikidata_gdp_per_capita()

    # 2) Clean
    df_book_clean = clean_wikidata_bookmakers(df_book_raw)
    df_gdp_clean = clean_wikidata_gdp(df_gdp_raw)

    # 3) Merge
    _ = merge_bookmakers_with_gdp(df_book_clean, df_gdp_clean)

    print("=== MEMBER 2 DATA PIPELINE FINISHED ===")

if __name__ == "__main__":
    main()
