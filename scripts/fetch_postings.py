# /// script
# requires-python = ">=3.10"
# dependencies = ["python-jobspy", "pandas"]
# ///
"""Fetch a small seed sample of real job postings into data/jobs_sample.csv.

LOCAL ONLY. Postings scraped from Indeed are not ours to republish (Indeed's
Terms of Service forbid redistribution), so the CSV is gitignored and never
leaves this machine. Only the aggregate KPI computed from it is published.

python-jobspy needs Python >= 3.10, newer than macOS's built-in 3.9, so run
this one script through uv, which fetches the right Python and dependencies
for this run only (the inline block above tells it what to install):

    pip3 install --user uv
    python3 -m uv run scripts/fetch_postings.py           # 15 postings
    python3 -m uv run scripts/fetch_postings.py 20        # or another number
"""
import os
import sys

import pandas as pd
from jobspy import scrape_jobs

N_WANTED = int(sys.argv[1]) if len(sys.argv) > 1 else 15
# Three neighbouring data roles, so the sample is not a single job title
SEARCH_TERMS = ["data engineer", "data scientist", "data analyst"]
MIN_DESCRIPTION_CHARS = 300   # drop postings whose description was not scraped


def main():
    frames = []
    per_term = N_WANTED // len(SEARCH_TERMS) + 4   # ask for a few extra, some get filtered
    for term in SEARCH_TERMS:
        print(f"Searching Indeed France for {term!r}...")
        try:
            jobs = scrape_jobs(
                site_name=["indeed"],
                search_term=term,
                location="France",
                country_indeed="France",
                results_wanted=per_term,
                description_format="markdown",
            )
        except Exception as e:  # one failed search should not lose the others
            print(f"  failed: {e}")
            continue
        print(f"  got {len(jobs)} postings")
        frames.append(jobs)

    if not frames:
        raise SystemExit("No postings fetched -- check your internet connection and retry.")

    df = pd.concat(frames, ignore_index=True)
    df = df[["title", "company", "description"]]
    df["description"] = df["description"].fillna("").astype(str).str.strip()
    df = df[df["description"].str.len() >= MIN_DESCRIPTION_CHARS]
    df = df.drop_duplicates(subset=["title", "company"])
    # interleave the three roles instead of taking all engineers first
    df = df.sample(frac=1, random_state=42).head(N_WANTED)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/jobs_sample.csv", index=False)
    print(f"\nWrote data/jobs_sample.csv ({len(df)} postings, local only -- gitignored)")
    if len(df) < 12:
        print("Warning: fewer than 12 postings, the TD asks for 12-15. Run it again to top up.")


if __name__ == "__main__":
    main()
