# 📚 Literature Scout

A Streamlit app that crawls Europe PMC for
publications that relate to specific products, classifies them, and
exports a CSV ready for updating to website.

---

## Key features

* **Time-machine slider** – choose how far back (in days) to search.
* **Guaranteed relevance** – every hit contains “Dovetail Genomics” *and* a specific synonym (Omni-C, Hi-C, HiRise, etc.).
* **Automatic tagging** – adds Species, Primary Application,
  Secondary Application, Product/Service, and Year columns.

---

## How to Use It

**Live app:**  
[https://literature-scout.streamlit.app/](https://literature-scout.streamlit.app/)


**Local use:**
```bash
# clone & enter repo
git clone https://github.com/olioschanz/literature-scout.git
cd literature-scout

# set up virtual-env
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate

# install requirements
pip install -r requirements.txt

# run Streamlit
streamlit run app.py
