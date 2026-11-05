# Reflections — TD3 Scraping to KPI

> Figures marked **(pilot)** come from my first real run on 21 October 2026: 3
> postings, `qwen3:8b` on my MacBook Pro M1 Pro. Lines marked **TODO** are updated
> after the full 15-posting run (`./run_all.sh`).

## 1. Why a silent robots.txt failure is worse than a loud one (CM3)

`robots.txt` is the provenance gate of the whole pipeline: it is the moment we check
that we are allowed to collect the data at all. If `rp.read()` fails behind a proxy it
does not crash, it quietly answers "disallow everything", and nothing in the output
says the check never really ran. A crash stops the pipeline and forces someone to look; a
silent wrong answer produces a run that *looks* compliant, so the record of "we
checked the rules" is false. That is why the script fetches the file with `requests`
and hands the text to `rp.parse()`: if the fetch fails, `raise_for_status()` fails
loudly.

## 2. France Travail vs. the jobspy sample — and does public/private matter?

France Travail's API is government open data under an explicit reuse licence: I can
store it, transform it and republish it with attribution. The jobspy sample is
scraped from Indeed, whose terms forbid automated collection and redistribution, so
the content is not mine to publish at all — the risk is legal and contractual, not
technical. A private repository reduces who can see the files, but it is still a
copy hosted on a third party's servers, shared with every collaborator and kept in
the git history forever. So I do not treat "private" as a licence: the scraped files
stay out of git in both cases (`.gitignore` before any data existed), and only the
aggregate is pushed — which matters even more here because the repository is public
for GitHub Pages.

## 3. Why free text → skills is an LLM task and application tracking is not (CM5)

Turning a recruiter's paragraph ("maîtrise de l'écosystème Python, idéalement
PySpark…") into `["Python", "Spark"]` is interpretation of unstructured, variable
language — exactly what rules or regular expressions do badly and an LLM does well,
and an occasional error is caught by the quality step and the critique pass. A record
of which applications I sent, or my real skill level, is a fact about my own
actions: there is nothing to interpret, a plain table records it exactly, and an LLM
could only add the risk of a plausible but invented entry. CM5's distinction is
between a stage where judgement on messy input adds value and a stage where the
system of record must be exact.

## 4. Predicted formatting inconsistency — and did I find one?

I expected the same skill to come back with different capitalisation or spacing
across independent calls (`Python` / `python`, `Power BI` / `PowerBI`), and
abbreviations next to full names (`ML` / `Machine learning`). **(pilot)** I did find
one in my own `extracted.json`: posting 1 returned `'Python'` and posting 2 returned
`'python'`. Counted as-is, Python would have appeared twice in the top skills with 1
posting each instead of once with 2 — the TD's first `kpi.json` shows exactly that
split. With only 3 postings this mostly says that the risk is real, not how frequent
it is. **TODO** after the full run: number of variants reported by
`check_quality.py` (section 1).

## 5. The critique pass — why it is human-in-the-loop (CM5)

A classmate reading the original posting next to the model's list is an independent
check of the model's output against the source, by someone who did not write the
prompt — the definition of a human in the loop: a person validates the automated
step before its result is used. It has to happen on `extracted.json` because that
is the last place where each skill is still tied to the posting it came from; in
`kpi.json` an invented or missing skill has already been added into a count and
cannot be traced back to the posting that caused it.

**TODO (Adam):** error found by my classmate in my extraction: …
**TODO (Adam):** error I found in my classmate's extraction: …

## 6. My own TARGET_SKILL, argued before seeing its value (CM2)

Written before running it: I would track **SQL**. Python is already taught
everywhere, while SQL is what every one of the three roles (engineer, scientist,
analyst) shares, and it is the skill an ENSIM graduate is most often tested on in
interviews without a dedicated course. **(pilot)** On the 3-posting run both values
are identical: Python 67 % (2/3) and SQL 67 % (2/3), with a 95 % interval of
21–94 % — so neither can tell the committee anything yet. Even with 15 postings I
would not trust either number alone: the interval stays around ±25 points, and "most
mentioned" is not "most missing from the curriculum". I would use it to rank skills
and compare with what is taught, not as a target. **TODO** after the full run: the
two values and intervals.

## 7. What can be reconstructed from kpi.json alone (CM3 / CM6)

From `kpi.json` a classmate sees how many postings mention each skill, the two KPIs,
quality counters and the model name — not which postings were scraped, nor any
company. That is a design choice in `compute_kpi()`, not luck: the function only
outputs counts; it drops `title`, `company` and every per-posting list, and counts
each skill once per posting so no row of the output corresponds to one posting. The
residual risk is a rare skill with a count of 1 in a small sample, which could hint
at one specific posting to someone who knows the market; with a larger sample I would
publish only skills mentioned at least twice.

## 8. Who this dashboard is really for (CM1)

The TD's page said "Scraping to KPI lab — see `data/extracted.json` and
`compute_kpi.py`": written for me, checking my own work, and it pointed a reader to a
file that is deliberately not published. The real audience in Stage 4 is the
curriculum committee, so the page now says it: "For ENSIM's curriculum committee —
Which skills do data job postings actually ask for?", with the sample size and its
limits on screen, since a committee cannot open my laptop to check them.

## 9. My second KPI, and which one I trust more

Second KPI: **share of postings asking for at least one cloud provider** (AWS,
Azure or GCP). **(pilot)** 33 % (1 of 3, AWS only). I trust it more for a curriculum
decision than the single-skill KPI, because it answers a broader, decision-shaped
question ("do data jobs now assume cloud skills?") and is less sensitive to which
provider a given company happens to use; the single-skill share depends heavily on
which skill someone picked. Both share the same weakness, the sample size, so the
dashboard shows the confidence interval under each. **TODO** after the full run: the
value and its AWS / Azure / GCP split.
