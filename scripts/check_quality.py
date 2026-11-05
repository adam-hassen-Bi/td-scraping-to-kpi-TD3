"""Stage 3 -- check what the model actually gave us, before counting anything.

Reads data/extracted.json (local only) and prints:
  1. spelling variants of the same skill ("Python" / "python", "PowerBI" / "Power BI")
     that would be counted as two different skills without normalization;
  2. postings where the model found no skill at all;
  3. suspicious "skills" -- soft skills, languages spoken, job titles -- that the
     prompt asked the model NOT to return.

Output is console only and never names a company: it is a working tool for the
critique pass, not something to publish.

    python3 scripts/check_quality.py
"""
import json
from collections import Counter, defaultdict

from skills import NOT_A_SKILL, skill_key


def main(path="data/extracted.json"):
    with open(path, encoding="utf-8") as f:
        postings = json.load(f)["postings"]

    raw = Counter()
    spellings = defaultdict(Counter)
    for p in postings:
        for s in p.get("required_skills", []):
            raw[s] += 1
            spellings[skill_key(s)][s.strip()] += 1

    print(f"{len(postings)} postings, {sum(raw.values())} extracted skill mentions, "
          f"{len(raw)} distinct raw strings -> {len(spellings)} after normalization\n")

    print("1. Same skill, several spellings (merged by normalization):")
    variants = {k: v for k, v in spellings.items() if len(v) > 1}
    if not variants:
        print("   none found")
    for k, v in sorted(variants.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"   {k!r:24} <- " + ", ".join(f"{s!r} x{n}" for s, n in v.most_common()))

    print("\n2. Postings with no skill extracted:")
    empty = [i for i, p in enumerate(postings, 1) if not p.get("required_skills")]
    print("   none" if not empty else "   posting #" + ", #".join(map(str, empty)))

    print("\n3. Not hard skills (soft skill / spoken language / job title) -- excluded from the KPI:")
    sus = Counter({k: sum(v.values()) for k, v in spellings.items() if k in NOT_A_SKILL})
    print("   none" if not sus else "   " + ", ".join(f"{k!r} x{n}" for k, n in sus.most_common()))

    per_posting = [len(p.get("required_skills", [])) for p in postings]
    print(f"\nSkills per posting: min {min(per_posting)}, max {max(per_posting)}, "
          f"mean {sum(per_posting) / len(per_posting):.1f}")


if __name__ == "__main__":
    main()
