"""Skill-name normalization shared by check_quality.py and compute_kpi.py.

The LLM extracts skills call by call, independently, so the same real skill comes
back written in different ways ("Python" in one posting, "python" in another,
"Power BI" vs "PowerBI", "GCP" vs "Google Cloud"). Counted as-is, one real skill
is split into several entries and every count is wrong. Normalizing BEFORE
counting is a data-quality step, not a cosmetic one.

Rules, in order:
1. trim spaces, collapse inner whitespace, lower-case -> the comparison key;
2. map known variants to one canonical key (ALIASES below, built from the
   variants actually seen in extracted.json -- extend it when check_quality.py
   reports a new one);
3. display with a canonical spelling (DISPLAY), or the most frequent original
   spelling when there is none.
"""
import re

ALIASES = {
    # languages
    "python3": "python", "python 3": "python", "python (pandas)": "python",
    "r language": "r", "langage r": "r",
    "sql server": "sql server", "ms sql": "sql server", "mssql": "sql server",
    "postgres": "postgresql", "postgre sql": "postgresql",
    "javascript": "javascript", "js": "javascript", "node": "node.js", "nodejs": "node.js",
    # BI
    "powerbi": "power bi", "microsoft power bi": "power bi", "power-bi": "power bi",
    "ms excel": "excel", "microsoft excel": "excel",
    # cloud
    "amazon web services": "aws", "amazon aws": "aws",
    "microsoft azure": "azure", "azure cloud": "azure",
    "google cloud": "gcp", "google cloud platform": "gcp",
    # data / ML
    "machine learning": "machine learning", "ml": "machine learning",
    "apprentissage automatique": "machine learning",
    "deep learning": "deep learning", "dl": "deep learning",
    "computer vision": "computer vision", "vision par ordinateur": "computer vision",
    "scikit learn": "scikit-learn", "sklearn": "scikit-learn",
    "pyspark": "spark", "apache spark": "spark",
    "apache airflow": "airflow",
    "apache kafka": "kafka",
    "k8s": "kubernetes",
    "github": "git", "gitlab": "git",
    "ci/cd": "ci/cd", "ci cd": "ci/cd", "cicd": "ci/cd",
}

DISPLAY = {
    "python": "Python", "r": "R", "sql": "SQL", "sql server": "SQL Server",
    "postgresql": "PostgreSQL", "javascript": "JavaScript", "node.js": "Node.js",
    "power bi": "Power BI", "excel": "Excel", "tableau": "Tableau",
    "aws": "AWS", "azure": "Azure", "gcp": "GCP",
    "machine learning": "Machine learning", "deep learning": "Deep learning",
    "computer vision": "Computer vision", "nlp": "NLP",
    "scikit-learn": "scikit-learn", "pytorch": "PyTorch", "tensorflow": "TensorFlow",
    "spark": "Spark", "airflow": "Airflow", "kafka": "Kafka", "dbt": "dbt",
    "docker": "Docker", "kubernetes": "Kubernetes", "git": "Git", "ci/cd": "CI/CD",
    "snowflake": "Snowflake", "databricks": "Databricks", "linux": "Linux",
}

# Entries the prompt asked the model NOT to return (soft skills, spoken
# languages, job titles). They are reported by check_quality.py and left out of
# every count, otherwise "communication" would rank as a top technical skill.
NOT_A_SKILL = {
    "communication", "teamwork", "team work", "travail en équipe", "autonomie",
    "autonomy", "rigueur", "curiosité", "curiosity", "leadership", "esprit d'équipe",
    "problem solving", "anglais", "english", "français", "french",
    "data engineer", "data scientist", "data analyst", "stage", "internship",
}

# Cloud providers, for the second KPI
CLOUD_PROVIDERS = {"aws", "azure", "gcp"}


def skill_key(raw):
    """Comparison key for one extracted skill string."""
    k = re.sub(r"\s+", " ", str(raw)).strip().lower()
    return ALIASES.get(k, k)


def display_name(key, seen_spellings=None):
    if key in DISPLAY:
        return DISPLAY[key]
    if seen_spellings:
        return max(seen_spellings, key=seen_spellings.get)
    return key


def posting_keys(posting):
    """Set of normalized skills for one posting: a skill counts once per posting,
    even if the model listed it twice ("Python", "python")."""
    keys = {skill_key(s) for s in posting.get("required_skills", []) if str(s).strip()}
    return keys - NOT_A_SKILL
