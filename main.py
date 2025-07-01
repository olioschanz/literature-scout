# main.py
import os, datetime as dt
from collector  import collect
from classifier import enrich

def main():
    # quarterly 120 day search
    df = collect(days_back=120)

    # ── Guard: exit quietly if no papers found ──
    if df.empty:
        print("⚠️  No publications found.  Nothing to export.")
        return

    df = enrich(df)

    cols = [
        "title", "url", "doi", "journal", "pubYear",
        "species_group", "primary_app", "secondary_app", "product_service"
    ]

    out_dir = "exports"
    os.makedirs(out_dir, exist_ok=True)            # creates exports/ if missing
    out_file = os.path.join(out_dir, f"dovetail_pubs_{dt.date.today()}.csv")

    df.to_csv(out_file, index=False, columns=cols, encoding="utf-8")
    print(f"✔  Exported {len(df)} rows → {out_file}")

if __name__ == "__main__":
    main()
