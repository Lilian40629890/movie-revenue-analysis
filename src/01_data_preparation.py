"""Build an analytics-ready movie dataset from the TMDB 5000 files.

Steps: load the movies and credits files, parse JSON columns, merge on movie_id,
engineer features, and convert budget, revenue, and profit to constant 2024 USD.

The main steps are taken from the project's final presentation. The helper
functions marked [RECONSTRUCTED] were referenced in the presentation but not
shown, so they were rewritten from their names and documented purpose.

Inputs (not included in this repository):
    data/tmdb_5000_movies.csv
    data/tmdb_5000_credits.csv
    data/CPIAUCSL.csv
Output:
    data/final_integrated_dataset.csv
"""

import json

import numpy as np
import pandas as pd

DATA_DIR = "data"


# --- Helper functions [RECONSTRUCTED] --------------------------------------

def safe_load_json(value):
    """Parse a JSON string into a list; return an empty list if parsing fails."""
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError):
        return []


def extract_director(crew):
    """Return the name of the first crew member whose job is Director."""
    for member in crew:
        if member.get("job") == "Director":
            return member.get("name")
    return None


def extract_top_cast(cast, n=3):
    """Return the names of the first n billed cast members."""
    ordered = sorted(cast, key=lambda member: member.get("order", 0))
    return [member.get("name") for member in ordered[:n]]


def determine_season(release_date):
    """Map a release date to Winter, Spring, Summer, or Fall."""
    if pd.isna(release_date):
        return None
    month = release_date.month
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Fall"


def extract_primary_genre(genres):
    """Use the first listed genre as the movie's primary genre."""
    return genres[0].get("name") if genres else None


# --- 1. Data loading ----------------------------------------------------------

movies = pd.read_csv(f"{DATA_DIR}/tmdb_5000_movies.csv")
credits = pd.read_csv(f"{DATA_DIR}/tmdb_5000_credits.csv")

print("Movies shape:", movies.shape)
print("Credits shape:", credits.shape)

# --- 2. JSON parsing and merge ------------------------------------------------

movies["genres_parsed"] = movies["genres"].apply(safe_load_json)
movies["keywords_parsed"] = movies["keywords"].apply(safe_load_json)
credits["cast_parsed"] = credits["cast"].apply(safe_load_json)
credits["crew_parsed"] = credits["crew"].apply(safe_load_json)
credits["director"] = credits["crew_parsed"].apply(extract_director)
credits["num_cast"] = credits["cast_parsed"].apply(lambda x: len(x) if isinstance(x, list) else 0)
credits["top_3_cast"] = credits["cast_parsed"].apply(lambda x: extract_top_cast(x, n=3))
movies = movies.rename(columns={"id": "movie_id"})
df = movies.merge(credits, on="movie_id", how="left")

# --- 3. Feature engineering ---------------------------------------------------

df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df["release_year"] = df["release_date"].dt.year
df["release_season"] = df["release_date"].apply(determine_season)
df["primary_genre"] = df["genres_parsed"].apply(extract_primary_genre)
df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
df["profit"] = df["revenue"] - df["budget"]
df["roi"] = df["profit"] / df["budget"].replace(0, np.nan)
df["num_genres"] = df["genres_parsed"].apply(lambda x: len(x) if isinstance(x, list) else 0)

# --- 4. Inflation adjustment (constant 2024 USD) ---------------------------
# In the original project this step re-read the exported dataset; here it runs
# on the same DataFrame before export.

cpi = pd.read_csv(f"{DATA_DIR}/CPIAUCSL.csv")
cpi["observation_date"] = pd.to_datetime(cpi["observation_date"])
cpi["year"] = cpi["observation_date"].dt.year
cpi_year = cpi.groupby("year")["CPIAUCSL"].mean().reset_index()

df = df.merge(cpi_year, left_on="release_year", right_on="year", how="left")

cpi_2024 = cpi_year.loc[cpi_year["year"] == 2024, "CPIAUCSL"].values[0]

df["budget_constant_2024"] = df["budget"] * (cpi_2024 / df["CPIAUCSL"])
df["revenue_constant_2024"] = df["revenue"] * (cpi_2024 / df["CPIAUCSL"])
df["profit_constant_2024"] = df["profit"] * (cpi_2024 / df["CPIAUCSL"])

# --- 5. Export ----------------------------------------------------------------

df.to_csv(f"{DATA_DIR}/final_integrated_dataset.csv", index=False)
print("Final dataset shape:", df.shape)
