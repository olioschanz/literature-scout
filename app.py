# app.py  –  Streamlit front-end for Dovetail Literature Scout
# ─────────────────────────────────────────────────────────────
import datetime as dt
import streamlit as st
import pandas as pd

from collector import collect
from classifier import enrich

st.set_page_config(page_title="Dovetail Literature Scout",
                   layout="wide"
                   )

st.title("Dovetail Literature Scout")

# ── Main Page controls ────────────────────────────────────────
# –– Label line
st.markdown("⏳ Set Your Scout’s Time Machine (Days)")

# –– Thin spacer
st.markdown("&nbsp;", unsafe_allow_html=True)

# –– slider, give it a hidden label
days_back = st.slider("Look-back window (days)", 30, 365, 120, step=30,
                      label_visibility="collapsed")   # label text exists, but stays invisible)
run_query = st.button("Fetch publications")

# ── Main action button ──────────────────────────────────────
if run_query:
    with st.spinner(f"Collecting publications from the last {days_back} days…"):
        df = collect(days_back=days_back)

        if df.empty:
            st.warning("No publications found for that window.")
            st.stop()

        df = enrich(df)

        # ── Rename & keep only desired columns ───────────────
        display_cols = {
            "title":            "Title",
            "doi":              "DOI",
            "pubYear":          "Year",
            "species_group":    "Species",
            "primary_app":      "Primary Application",
            "secondary_app":    "Secondary Application",
            "product_service":  "Product/Service",
        }
        df = df.rename(columns=display_cols)[list(display_cols.values())]
        # ─────────────────────────────────────────────────────

        st.success(f"Found {len(df)} publications.")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        date_str = dt.date.today().isoformat()
        st.download_button(
            label=f"Download CSV ({date_str})",
            data=csv_data,
            file_name=f"dovetail_pubs_{date_str}.csv",
            mime="text/csv"
        )
