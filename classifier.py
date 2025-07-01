# classifier.py
# ─────────────────────────────────────────────────────────────
"""
Adds these columns to the DataFrame returned by collector.collect():

    primary_app        (single label)
    secondary_app      (semicolon-separated list)
    species_group      (one of the 42 UI buckets)
"""
import yaml, pandas as pd, difflib, re

# ── 1.  Load vocabularies ────────────────────────────────────
cfg  = yaml.safe_load(open("product_terms.yml"))
SPECIES_MAP = yaml.safe_load(open("species_map.yml"))["species_map"]

PRIMARY   = cfg["applications_primary"]      # dict[label] -> keywords
SECONDARY = cfg["applications_secondary"]    # dict[label] -> keywords


# ── 2.  Helper functions ─────────────────────────────────────
def _match_keywords(text: str, kw_dict: dict, take_first: bool = False) -> str:
    """Return first hit (if take_first) or '; '-joined list of all hits."""
    hits = [label
            for label, keywords in kw_dict.items()
            if any(k.lower() in text for k in keywords)]
    return (hits[0] if (hits and take_first) else "; ".join(hits)) or "Other"


def _species_group(row: pd.Series) -> str:
    """
    Decide which species bucket a paper belongs to.

    Priority:
      1) ≥2 species in metadata → 'Multiple'
      2) Exact Latin/common name match in species_map.yml
      3) Fuzzy substring match (case-insensitive, punctuation stripped)
      4) Fallback → 'Other'
    """
    latin_names = []

    # Europe PMC usually stores a list of dicts under 'speciesList'
    if isinstance(row.get("speciesList"), list) and row["speciesList"]:
        latin_names = [d.get("scientificName", "") for d in row["speciesList"]]
    elif row.get("species"):                # sometimes only a common name
        latin_names = [row["species"]]

    if len(latin_names) > 1:
        return "Multiple"
    if not latin_names:
        return "Other"

    latin = latin_names[0]
    latin_clean = re.sub(r"\W", "", latin.lower())   # strip punctuation

    # 2) Exact match
    for group, latin_list in SPECIES_MAP.items():
        if latin in latin_list:
            return group

    # 3) Fuzzy / substring match
    for group, latin_list in SPECIES_MAP.items():
        for ref in latin_list:
            ref_clean = re.sub(r"\W", "", ref.lower())
            if latin_clean in ref_clean or ref_clean in latin_clean:
                return group

    return "Other"


# ── 3.  Public entry point ───────────────────────────────────
def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds primary_app, secondary_app, species_group columns and
    returns the augmented DataFrame.
    """
    if df.empty:
        return df

    # single lowercase blob = faster keyword scans
    blob = (df["title"].fillna("") + " " + df["abstract"].fillna("")).str.lower()

    df = df.copy()  # avoid SettingWithCopy warnings
    df["primary_app"]   = blob.apply(lambda t: _match_keywords(t, PRIMARY, take_first=True))
    df["secondary_app"] = blob.apply(lambda t: _match_keywords(t, SECONDARY))
    df["species_group"] = df.apply(_species_group, axis=1)

    return df
