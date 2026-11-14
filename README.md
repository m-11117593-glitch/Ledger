# Ledger 💳

A modern expense tracking and cash flow intelligence application with machine learning categorization, persistent SQLite storage, and shadcn/ui analytics.

## Features
- **Machine Learning Auto-Categorization**: Powered by a Scikit-Learn TF-IDF + Logistic Regression pipeline (`model.joblib`) trained on 68,000+ real-world transactions across 17 categories.
- **Model Checkpoint**: Active pipeline loaded from `model.joblib`.
- **Smart Category Override**: AI auto-detects merchant category with confidence percentage, with 1-click manual dropdown override before recording.
- **Zero Data Loss Persistence**: Backed by a local SQLite database (`expenses.db`), preserving all transactions across page refreshes and browser restarts.
- **Concentration Spotlight & Analytics**:
  - Live Donut chart breakdown by category with Plotly interactivity.
  - Spending trajectory timeline across days.
  - Automatic executive spotlight calculating which category absorbed the most funds and its exact percentage.
- **Time Horizon Filter**: Switch between **This Week**, **This Month**, and **All Time**.
- **Audit Ledger**: Searchable, filterable transaction history with single-click record deletion and CSV export.
- **Bespoke Theme**: High-end Emerald & Gold Forest Finance styling for a realistic banking dashboard experience.

---

## Quickstart (Local)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the web application**:
   ```bash
   streamlit run app.py
   ```

3. Open your browser at `http://localhost:8501`.

---

## Easy Free Cloud Hosting (Streamlit Community Cloud)

1. Push this directory to a GitHub repository (`model.joblib`, `app.py`, `database.py`, `model_utils.py`, `styles.py`, `requirements.txt`).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub repository and select `app.py` as the main file.
4. Click **Deploy**!
