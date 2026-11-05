"""Stage 4 -- turn the extracted skills into two KPIs, and publish ONLY aggregates.

KPI 1 (the TD's): share of postings that mention TARGET_SKILL.
KPI 2 (my own):   share of postings that mention at least one cloud provider
                  (AWS, Azure or GCP) -- "do data jobs now assume cloud skills?"

Both are constructs, not facts: changing TARGET_SKILL, the alias table in
skills.py, or the list of cloud providers changes the number.

Two fixes over the TD's starting version, both data-quality decisions:
- skills are normalized before counting (skills.py), so "Python" and "python"
  are one skill, counted once per posting;
- matching is on the whole normalized skill, not a substring: with
  `target in skill`, "r" would match "docker" and "java" would match "javascript".
  The naive version is still computed and published next to the corrected one,
  so the effect of the correction is visible.

docs/data/kpi.json contains counts and skill names only -- no title, company,
description or per-posting row -- so no posting can be traced back from it.

    python3 scripts/compute_kpi.py                 # tracked skill = python
    python3 scripts/compute_kpi.py --skill sql     # any other skill
"""
import argparse
import json
import time
from collections import Counter, defaultdict

from skills import CLOUD_PROVIDERS, NOT_A_SKILL, display_name, posting_keys, skill_key

TARGET_SKILL = "python"
TOP_N = 15


def load_extracted(path="data/extracted.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def share(n, total):
    return round(n / total, 3) if total else 0.0


def compute_kpi(extracted, target_skill=TARGET_SKILL):
    postings = extracted["postings"]
    n = len(postings)
    keys = [posting_keys(p) for p in postings]
    target = skill_key(target_skill)

    # --- KPI 1: share of postings mentioning the target skill (whole-skill match)
    n_target = sum(1 for k in keys if target in k)
    # same KPI as the TD's first version: substring match on raw strings
    n_target_naive = sum(
        1 for p in postings
        if any(target_skill.lower() in s.lower() for s in p.get("required_skills", []))
    )

    # --- KPI 2: share of postings mentioning at least one cloud provider
    n_cloud = sum(1 for k in keys if k & CLOUD_PROVIDERS)
    cloud_split = {display_name(c): sum(1 for k in keys if c in k) for c in sorted(CLOUD_PROVIDERS)}

    # --- skill frequencies: number of postings mentioning each normalized skill
    postings_per_skill = Counter()
    spellings = defaultdict(Counter)
    raw_strings = set()
    for p, k in zip(postings, keys):
        postings_per_skill.update(k)
        for s in p.get("required_skills", []):
            raw_strings.add(s.strip())
            spellings[skill_key(s)][s.strip()] += 1
    top = [
        {"skill": display_name(s, spellings[s]), "postings": c, "share": share(c, n)}
        for s, c in sorted(postings_per_skill.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_N]
    ]

    per_posting = [len(k) for k in keys]
    dist = Counter(per_posting)

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "audience": "ENSIM curriculum committee",
        "model": extracted.get("model", "unknown"),
        "n_postings_analyzed": n,
        "kpis": [
            {
                "id": "target_skill",
                "label": f"Postings asking for {display_name(target)}",
                "definition": f"Share of postings whose normalized skill list contains '{display_name(target)}' (whole-skill match).",
                "value": share(n_target, n),
                "n_matching": n_target,
                "naive_value": share(n_target_naive, n),
                "naive_definition": f"TD's first version: raw substring match on '{target_skill}'.",
            },
            {
                "id": "any_cloud",
                "label": "Postings asking for a cloud provider",
                "definition": "Share of postings mentioning at least one of AWS, Azure or GCP.",
                "value": share(n_cloud, n),
                "n_matching": n_cloud,
                "split": cloud_split,
            },
        ],
        "top_skills": top,
        "n_distinct_skills": len(postings_per_skill),
        "avg_skills_per_posting": round(sum(per_posting) / n, 2) if n else 0.0,
        "skills_per_posting_distribution": [{"n_skills": k, "postings": dist[k]} for k in sorted(dist)],
        "quality": {
            "n_raw_distinct_strings": len(raw_strings),
            "n_after_normalization": len(postings_per_skill),
            "n_skills_with_several_spellings": sum(1 for v in spellings.values() if len(v) > 1),
            "n_postings_without_skill": sum(1 for k in keys if not k),
            "n_non_skill_mentions_excluded": sum(
                1 for p in postings for s in p.get("required_skills", []) if skill_key(s) in NOT_A_SKILL
            ),
        },
        "extraction": {
            k: extracted[k] for k in ("avg_seconds_per_posting", "max_chars_per_posting") if k in extracted
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", default=TARGET_SKILL, help="skill tracked by KPI 1 (default: python)")
    args = ap.parse_args()

    kpi = compute_kpi(load_extracted(), args.skill)
    k1, k2 = kpi["kpis"]
    print(f"Postings analyzed: {kpi['n_postings_analyzed']}  (model: {kpi['model']})")
    print(f"KPI 1  {k1['label']}: {k1['value']:.0%} ({k1['n_matching']}/{kpi['n_postings_analyzed']})"
          f"   naive substring version: {k1['naive_value']:.0%}")
    print(f"KPI 2  {k2['label']}: {k2['value']:.0%} ({k2['n_matching']}/{kpi['n_postings_analyzed']})  {k2['split']}")
    q = kpi["quality"]
    print(f"Quality: {q['n_raw_distinct_strings']} raw spellings -> {q['n_after_normalization']} skills, "
          f"{q['n_skills_with_several_spellings']} merged, {q['n_postings_without_skill']} posting(s) without skill")
    print("Top skills: " + ", ".join(f"{s['skill']} {s['postings']}" for s in kpi["top_skills"][:10]))

    with open("docs/data/kpi.json", "w", encoding="utf-8") as f:
        json.dump(kpi, f, indent=2, ensure_ascii=False)
    print("\nWrote docs/data/kpi.json (aggregates only)")


if __name__ == "__main__":
    main()
