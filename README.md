# FotMob Match Data Scraper & Python API Wrapper ⚽📊

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![Apify Actor](https://img.shields.io/badge/Apify-Actor-00A65A.svg?style=flat&logo=apify&logoColor=white)](https://apify.com/incognito_mode/fotmob-match-details-scraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/arman-007/fotmob-match-data-scraper-python?style=social)](https://github.com/arman-007/fotmob-match-data-scraper-python)

> **The easiest way to extract deep FotMob match stats, expected goals (xG), player ratings, tactical lineups, and minute-by-minute timeline events into clean JSON and Pandas DataFrames.**

---

## 🔍 Why This Exists: The FotMob API Problem

[FotMob](https://www.fotmob.com/) provides some of the richest match-day analytics in world football—including expected goals (xG), shot maps, individual player ratings, passing accuracy, and tactical formations.

However, football data analysts, sports scientists, and Fantasy Premier League (FPL) managers face a major roadblock:
1. **No Public API**: FotMob does not offer an official developer API.
2. **Anti-Scraping Protection**: FotMob's internal endpoints are protected by dynamic signatures (`x-mas` headers) and Cloudflare rate-limiting that break custom BeautifulSoup or Puppeteer scripts.
3. **Enterprise Feeds are Unaffordable**: Official feeds like Opta or StatsBomb cost thousands of dollars per month and gatekeep raw xG data behind enterprise tiers.

This repository provides a reliable **Python client and CLI** backed by the cloud-hosted [FotMob Match Details Scraper on Apify](https://apify.com/incognito_mode/fotmob-match-details-scraper), giving you fully automated access to granular match records without managing browser infrastructure or proxy rotation.

---

## ⚡ Quickstart (Python)

### 1. Installation

```bash
git clone https://github.com/arman-007/fotmob-match-data-scraper-python.git
cd fotmob-match-data-scraper-python
pip install -r requirements.txt
```

### 2. Extract Match Data into Pandas

Set your [Apify API token](https://console.apify.com/account/integrations) (free tier includes ~500 matches/month—enough for an entire Premier League season):

```python
import os
import pandas as pd
from apify_client import ApifyClient

# Initialize client
client = ApifyClient(os.environ.get("APIFY_API_TOKEN") or "YOUR_APIFY_TOKEN")

# Run scraper for any FotMob match URL or match ID
run_input = {
    "matchUrls": [
        "https://www.fotmob.com/matches/aston-villa-vs-manchester-united/2d1h42#4506541"
    ]
}

# Run the actor and fetch results
run = client.actor("incognito_mode/fotmob-match-details-scraper").call(run_input=run_input)
dataset = client.dataset(run["defaultDatasetId"])
matches = list(dataset.iterate_items())

# Flatten player stats directly into a Pandas DataFrame
first_match = matches[0]
df_players = pd.DataFrame(first_match["playerStats"])

print(df_players[["name", "team", "position", "rating", "minutes", "xG", "passAccuracyPct"]].head())
```

---

## 💻 CLI Usage

Extract match data directly from the terminal without writing code:

```bash
# Export player ratings and xG directly to CSV
python extract_match.py --url "https://www.fotmob.com/matches/arsenal-vs-chelsea/..." --output chelsea_arsenal.csv

# Or inspect bundled sample dataset immediately without an API token
python extract_match.py --use-sample --output sample_players.csv
```

---

## 📊 Google Sheets One-Liner (No Code)

You can pull live FotMob match statistics directly into Google Sheets for spreadsheet modeling or FPL tracking:

```excel
=IMPORTDATA("https://api.apify.com/v2/datasets/<DATASET_ID>/items?format=csv")
```

---

## 📋 Data Schema

Each scraped record is normalized into flat, analysis-ready JSON objects:

### `matchGeneral`
| Field | Type | Description |
| :--- | :--- | :--- |
| `matchId` | `string` | Unique FotMob match identifier (e.g. `"4506541"`) |
| `league` | `string` | Competition name (e.g. `"Premier League"`) |
| `round` | `string` | Gameweek or cup round |
| `venue` | `string` | Stadium name |
| `referee` | `string` | Match official |
| `homeTeam` / `awayTeam` | `object` | Team ID, team name, and final score |

### `playerStats` (Per-Player Granular Stats)
| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | Player display name |
| `team` | `string` | Club name |
| `position` | `string` | Tactical position (Goalkeeper, Defender, Midfielder, Forward) |
| `role` | `string` | `starter` or `bench` |
| `rating` | `float` | FotMob post-match rating (1.0 - 10.0 scale) |
| `minutes` | `int` | Exact minutes played |
| `xG` | `float` | Individual Expected Goals |
| `xA` | `float` | Individual Expected Assists |
| `passesTotal` | `int` | Total passes attempted |
| `passAccuracyPct` | `float` | Passing accuracy percentage |
| `tacklesWon` | `int` | Successful tackles |
| `duelsWon` | `int` | Ground and aerial duels won |

### `events` (Unified Timeline)
| Field | Type | Description |
| :--- | :--- | :--- |
| `minute` | `int` | Minute event occurred |
| `type` | `string` | `goal`, `yellowCard`, `redCard`, `substitution`, `var` |
| `player` | `string` | Primary player involved |
| `assistPlayer` | `string` | Assisting player (if applicable) |
| `subIn` / `subOut` | `string` | Substitution participants |

---

## 📈 Jupyter Notebook Example

A complete analysis notebook is included in [`notebooks/fotmob_match_analysis.ipynb`](notebooks/fotmob_match_analysis.ipynb):

1. **Team xG Comparison**: Compare underlying expected goals against the actual scoreline.
2. **Player Performance Visuals**: Horizontal bar chart comparing player ratings and xG contributions.
3. **Timeline Event Breakdown**: Map match momentum shifts across substitutions and bookings.

To run the notebook:
```bash
jupyter notebook notebooks/fotmob_match_analysis.ipynb
```

---

## 📖 Deep Dives & Articles

For complete architecture walkthroughs, proxy strategies, and data modeling guides:

- 🚀 **Apify Actor**: [FotMob Match Details Scraper](https://apify.com/incognito_mode/fotmob-match-details-scraper)
- 📝 **Hashnode**: [Extracting FotMob Match Data: Lineups, xG, Player Ratings, and Match Events](https://armanhosen.hashnode.dev/extracting-fotmob-match-data-lineups-xg-player-ratings-and-match-events-into-json)
- 📝 **DEV.to**: [How to Turn FotMob Matches into Clean JSON: Lineups, Per-Player Stats, Events Timeline & xG](https://dev.to/arman_007/how-to-turn-fotmob-matches-into-clean-json-lineups-per-player-stats-events-timeline-xg-4lln)
- 📝 **Substack**: [Extracting FotMob Match Data into JSON](https://armanhosen.substack.com/p/extracting-fotmob-match-data-lineups)
- 🐦 **X (Twitter)**: [Technical Thread Breakdown on #FootballData](https://x.com/armanirfan007/status/2097027820597969115)

---

## ⚖️ Disclaimer & License

This project is intended for educational and personal research purposes (e.g., non-commercial sports analytics and Fantasy Premier League modeling). Please respect FotMob's Terms of Service and robot policies.

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
