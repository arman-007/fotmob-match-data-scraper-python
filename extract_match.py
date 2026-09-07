"""
FotMob Match Details Scraper & API Wrapper (Python)
---------------------------------------------------
A clean Python wrapper and CLI utility to extract deep FotMob match statistics,
lineups, xG breakdown, player ratings, and timeline events via the Apify Actor:
`incognito_mode/fotmob-match-details-scraper`.

Author: Arman Hosen
License: MIT
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional
import pandas as pd
from apify_client import ApifyClient

ACTOR_ID = "incognito_mode/fotmob-match-details-scraper"


class FotMobExtractor:
    """Wrapper to query the FotMob Match Details Scraper on Apify."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the extractor.
        :param api_token: Apify API token. If None, reads from APIFY_API_TOKEN env var.
        """
        self.api_token = api_token or os.environ.get("APIFY_API_TOKEN")
        if self.api_token:
            self.client = ApifyClient(self.api_token)
        else:
            self.client = None

    def fetch_match(
        self,
        match_url: Optional[str] = None,
        match_id: Optional[str] = None,
        proxy_configuration: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run the Apify actor for a given match URL or match ID.
        :param match_url: Full FotMob match URL.
        :param match_id: FotMob match ID (e.g. '4506541').
        :param proxy_configuration: Optional custom proxy settings.
        :return: List of extracted match dataset records.
        """
        if not self.client:
            raise ValueError(
                "ApifyClient requires an API token. "
                "Pass api_token or set the APIFY_API_TOKEN environment variable."
            )

        run_input: Dict[str, Any] = {}
        if match_url:
            run_input["matchUrls"] = [match_url]
        elif match_id:
            run_input["matchIds"] = [match_id]
        else:
            raise ValueError("Either match_url or match_id must be provided.")

        if proxy_configuration:
            run_input["proxyConfiguration"] = proxy_configuration
        else:
            run_input["proxyConfiguration"] = {"useApifyProxy": True}

        print(f"[*] Calling actor {ACTOR_ID} on Apify...")
        run = self.client.actor(ACTOR_ID).call(run_input=run_input)
        dataset = self.client.dataset(run["defaultDatasetId"])
        items = list(dataset.iterate_items())
        print(f"[+] Retrieved {len(items)} match record(s).")
        return items

    @staticmethod
    def player_stats_to_df(match_record: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert the nested `playerStats` array from a match record into a tabular Pandas DataFrame.
        """
        players = match_record.get("playerStats", [])
        if not players:
            return pd.DataFrame()
        df = pd.DataFrame(players)
        return df

    @staticmethod
    def events_to_df(match_record: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert the unified `events` timeline from a match record into a tabular Pandas DataFrame.
        """
        events = match_record.get("events", [])
        if not events:
            return pd.DataFrame()
        df = pd.DataFrame(events)
        return df


def load_sample_data() -> Dict[str, Any]:
    """Load bundled sample match dataset for demonstration/testing."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(current_dir, "data", "sample_match_data.json")
    with open(sample_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Extract deep match stats from FotMob into JSON/CSV."
    )
    parser.add_argument("--url", help="FotMob match URL", type=str)
    parser.add_argument("--id", help="FotMob match ID", type=str)
    parser.add_argument(
        "--token",
        help="Apify API Token (defaults to APIFY_API_TOKEN env var)",
        type=str,
    )
    parser.add_argument(
        "--output",
        help="Output file path (.json or .csv)",
        default="match_stats.json",
        type=str,
    )
    parser.add_argument(
        "--use-sample",
        action="store_true",
        help="Use bundled sample data instead of calling live Apify API",
    )

    args = parser.parse_args()

    if args.use_sample:
        print("[*] Loading sample dataset...")
        data = load_sample_data()
        records = [data]
    else:
        if not args.url and not args.id:
            print(
                "[!] Error: Please specify --url, --id, or --use-sample.\n"
                "Example: python extract_match.py --use-sample --output sample_players.csv"
            )
            sys.exit(1)

        extractor = FotMobExtractor(api_token=args.token)
        records = extractor.fetch_match(match_url=args.url, match_id=args.id)

    if not records:
        print("[!] No records returned.")
        return

    first_record = records[0]

    # Save output based on extension
    if args.output.endswith(".csv"):
        df_players = FotMobExtractor.player_stats_to_df(first_record)
        df_players.to_csv(args.output, index=False)
        print(f"[+] Successfully saved {len(df_players)} player stats to {args.output}")
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        print(f"[+] Successfully saved {len(records)} record(s) to {args.output}")


if __name__ == "__main__":
    main()
