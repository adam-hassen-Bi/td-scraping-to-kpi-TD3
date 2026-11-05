#!/bin/bash
# Run the whole TD3 pipeline on this Mac, in order. Needs Ollama running with qwen3:8b.
#   ./run_all.sh            fetch 15 postings, extract, check, compute
#   ./run_all.sh --no-fetch reuse the existing data/jobs_sample.csv
set -e
cd "$(dirname "$0")"

curl -s --noproxy '*' http://127.0.0.1:11434/api/version >/dev/null \
  || { echo "Ollama is not running -- open the Ollama app first."; exit 1; }

python3 -m pip install --user -q requests beautifulsoup4 uv 2>/dev/null

if [ "$1" != "--no-fetch" ]; then
  echo "== 1. Fetch postings (local only) =="
  python3 -m uv run scripts/fetch_postings.py 15
fi

echo; echo "== 2. Extract skills with the local LLM =="
python3 -W ignore scripts/extract_skills.py 15

echo; echo "== 3. Data quality =="
python3 scripts/check_quality.py

echo; echo "== 4. KPIs =="
python3 scripts/compute_kpi.py

echo; echo "== Check: scraped data must NOT be tracked by git =="
git status --short --ignored data/ docs/data/
