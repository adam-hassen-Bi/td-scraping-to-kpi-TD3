# TD3 — Scraping to KPI

Pipeline: scrape/acquire → structure (local LLM via Ollama) → data quality → KPI → publish aggregate only.

```
python scripts/scrape_demo.py          # optional: robots.txt check + one extraction
python scripts/extract_skills.py 12    # needs data/jobs_sample.csv (local only) + Ollama running
python scripts/compute_kpi.py          # writes docs/data/kpi.json (aggregate only)
```

`data/jobs_sample.csv` and `data/extracted.json` are gitignored: scraped postings are never published.
Dashboard: `docs/index.html` (GitHub Pages, `main` / `/docs`).
