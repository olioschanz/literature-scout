# collector.py
# ─────────────────────────────────────────────────────────────
"""
Collects publication metadata from Europe PMC and returns a DataFrame that
drives the rest of the pipeline.

Key behaviours
--------------
1.  A paper is kept only if it contains a *Dovetail* synonym **and**
    a kit-specific synonym.  (The ‘Generic Dovetail’ product is the
    one exception—it just looks for the company name.)
2.  Searches are loose:
      · queries are NOT wrapped in quotes, so word order can vary
      · no [TIAB] filter, so all indexed fields are searched
      · multi-word synonyms are AND-joined (“Chicago library” → Chicago AND library)
3.  Duplicates (same DOI or same title) are removed before returning.
"""

# collector.py  –  Dovetail required, verb "dovetail" excluded
# ─────────────────────────────────────────────────────────────
import datetime as dt
import requests
import yaml
import pandas as pd
from tqdm import tqdm

# 1. Company-name synonyms  (NO generic 'Dovetail')
DOVETAIL_SYNS = [
    '"Dovetail Genomics"',   # exact phrase
    '"Dovetail genomic"',     # handles missing “s”
    '"Cantata Bio"',
    '"Dovetail Micro-C"',
    '"Dovetail HiChIP"',
    '"Dovetail"',
    '"LinkPrep"',
    '"Dovetail"',
    '"TopoLink"',
    '"AssemblyLink"'
]
DOVETAIL_OR = " OR ".join(DOVETAIL_SYNS)

# 2. Load vocabularies
terms = yaml.safe_load(open("product_terms.yml"))
PRODUCTS = terms["products"]

# 3. Query builder  (company-name AND kit-term)
def build_queries():
    for prod, meta in PRODUCTS.items():
        for syn in meta["synonyms"]:
            product_term = " AND ".join(syn.split()) if " " in syn else syn
            query = f"({DOVETAIL_OR}) AND ({product_term})"
            yield prod, query

# 4. Fetch helper
def pull_eupmc(q: str, since: str, page_size: int = 1000):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f'{q} AND FIRST_PDATE:[{since} TO {dt.date.today()}]',
        "format": "json",
        "pageSize": page_size,
    }
    try:
        return requests.get(url, params=params, timeout=20).json()\
                       .get("resultList", {}).get("result", [])
    except requests.RequestException as e:
        print("⚠️  Europe PMC error:", e)
        return []

# 5. Public entry
def collect(days_back: int = 365) -> pd.DataFrame:
    since = (dt.date.today() - dt.timedelta(days=days_back)).isoformat()
    rows = []
    for prod, q in tqdm(list(build_queries()), desc="Europe PMC"):
        for rec in pull_eupmc(q, since):
            rows.append({
                "title":    rec.get("title", ""),
                "doi":      rec.get("doi", ""),
                "url":      rec.get("url", ""),
                "abstract": rec.get("abstractText", ""),
                "journal":  rec.get("journal", ""),
                "pubYear":  rec.get("pubYear", ""),
                "species":  rec.get("species", ""),
                "speciesList": rec.get("speciesList", []),
                "product_service": prod
            })
    return pd.DataFrame(rows).drop_duplicates(subset=["doi", "title"])
