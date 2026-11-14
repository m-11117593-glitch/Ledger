"""
shadcn/ui Zinc Theme (Dark Mode)
Exact design system tokens from shadcn/ui (75k+ GitHub stars):
- Background: #09090b (Zinc 950)
- Card: #18181b (Zinc 900)
- Border / Input: #27272a (Zinc 800)
- Foreground: #fafafa (Zinc 50)
- Muted Foreground: #a1a1aa (Zinc 400)
- Primary Accent Button: #fafafa text #18181b (High contrast crisp white on dark)
- Secondary / Badge: #27272a text #e4e4e7
- Typography: Inter, -apple-system, system-ui, sans-serif
"""

SHADCN_ZINC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ---------------- Global Reset & Typography ---------------- */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background-color: #09090b !important;
    color: #fafafa !important;
    -webkit-font-smoothing: antialiased;
}

/* Page container */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1180px !important;
}

/* ---------------- Navbar / Top Header (shadcn style) ---------------- */
.shadcn-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 20px;
    background-color: #09090b;
    border-bottom: 1px solid #27272a;
    margin-bottom: 24px;
}

.shadcn-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.shadcn-logo {
    width: 28px;
    height: 28px;
    background: #fafafa;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #09090b;
    font-weight: 700;
    font-size: 14px;
}

.shadcn-title {
    font-size: 16px;
    font-weight: 600;
    color: #fafafa;
    letter-spacing: -0.02em;
    margin: 0;
}

.shadcn-subtitle {
    font-size: 12px;
    color: #a1a1aa;
    margin: 0;
}

.shadcn-badge {
    font-size: 11px;
    font-weight: 500;
    background-color: #18181b;
    color: #a1a1aa;
    border: 1px solid #27272a;
    padding: 3px 8px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.shadcn-badge-income {
    font-size: 11px;
    font-weight: 600;
    background-color: rgba(16, 185, 129, 0.12);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 2px 8px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
}

.text-emerald {
    color: #10b981 !important;
}

.text-rose {
    color: #f43f5e !important;
}

/* ---------------- Auth & Login Card ---------------- */
.shadcn-login-card {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 36px 32px;
    max-width: 440px;
    margin: 40px auto;
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.35);
    text-align: center;
}

.shadcn-user-badge {
    background-color: #18181b;
    border: 1px solid #27272a;
    color: #e4e4e7;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.shadcn-google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    background-color: #fafafa;
    color: #18181b !important;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: -0.01em;
    border: 1px solid #e4e4e7;
    border-radius: 8px;
    padding: 12px 20px;
    width: 100%;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    transition: background-color 0.15s ease, transform 0.1s ease;
    margin-top: 16px;
    box-sizing: border-box;
}

.shadcn-google-btn:hover {
    background-color: #f4f4f5;
    color: #09090b !important;
    transform: translateY(-1px);
}

/* ---------------- Metric Cards (shadcn Dashboard Card) ---------------- */
.shadcn-card {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 20px 22px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.2);
}

.shadcn-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.shadcn-card-title {
    font-size: 12px;
    font-weight: 500;
    color: #a1a1aa;
    letter-spacing: -0.01em;
    margin: 0;
}

.shadcn-card-icon {
    font-size: 14px;
    color: #71717a;
}

.shadcn-card-value {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fafafa;
    margin: 0;
}

.shadcn-card-desc {
    font-size: 12px;
    color: #71717a;
    margin-top: 4px;
    margin-bottom: 0;
}

/* ---------------- Alert Callout (shadcn Alert) ---------------- */
.shadcn-alert {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 14px 18px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 24px;
}

.shadcn-alert-icon {
    color: #fafafa;
    font-size: 16px;
    margin-top: 1px;
}

.shadcn-alert-title {
    font-size: 13px;
    font-weight: 600;
    color: #fafafa;
    margin: 0 0 2px 0;
}

.shadcn-alert-desc {
    font-size: 13px;
    color: #a1a1aa;
    margin: 0;
    line-height: 1.4;
}

.shadcn-alert-highlight {
    color: #fafafa;
    font-weight: 600;
}

/* ---------------- Form Inputs & Buttons (shadcn styled) ---------------- */
/* Inputs */
.stTextInput input, .stNumberInput input, .stDateInput input {
    background-color: #09090b !important;
    border: 1px solid #27272a !important;
    border-radius: 6px !important;
    color: #fafafa !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
    border-color: #52525b !important;
    box-shadow: 0 0 0 1px #52525b !important;
    outline: none !important;
}

/* Selectbox dropdown */
div[data-baseweb="select"] {
    background-color: #09090b !important;
    border-radius: 6px !important;
}

div[data-baseweb="select"] > div {
    background-color: #09090b !important;
    border: 1px solid #27272a !important;
    border-radius: 6px !important;
    color: #fafafa !important;
}

/* Primary Button (White on Dark - signature shadcn/ui) */
div.stButton > button {
    background-color: #fafafa !important;
    color: #18181b !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: -0.01em !important;
    border: 1px solid #fafafa !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.15) !important;
    transition: background-color 0.15s ease, opacity 0.15s ease !important;
}

div.stButton > button:hover {
    background-color: #e4e4e7 !important;
    border-color: #e4e4e7 !important;
    color: #09090b !important;
}

/* Download button */
div.stDownloadButton > button {
    background-color: #18181b !important;
    color: #fafafa !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    border: 1px solid #27272a !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    transition: background-color 0.15s ease !important;
}

div.stDownloadButton > button:hover {
    background-color: #27272a !important;
    border-color: #3f3f46 !important;
}

/* Radio Pill Group (shadcn Segmented Control / Tabs) */
div[role="radiogroup"] {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    padding: 3px !important;
    border-radius: 8px !important;
    gap: 4px !important;
}

div[role="radiogroup"] label {
    padding: 4px 12px !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #a1a1aa !important;
}

/* Streamlit Tabs */
button[data-baseweb="tab"] {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #a1a1aa !important;
    border-bottom: 2px solid transparent !important;
    padding-bottom: 8px !important;
}

button[aria-selected="true"] {
    color: #fafafa !important;
    border-bottom: 2px solid #fafafa !important;
    font-weight: 600 !important;
}

/* Dataframe & Tables */
.dataframe {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}

/* Section Header */
.shadcn-section-header {
    font-size: 15px;
    font-weight: 600;
    color: #fafafa;
    letter-spacing: -0.01em;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* AI prediction chip */
.shadcn-ai-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 500;
    color: #a1a1aa;
    background-color: #18181b;
    border: 1px solid #27272a;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 10px;
}

.shadcn-ai-chip strong {
    color: #fafafa;
}
</style>
"""

# shadcn / Tremor Modern Chart Palette
# Neutral zinc with crisp data accents (Emerald, Blue, Amber, Violet, Rose, Cyan)
CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#a1a1aa",
    "grid_color": "#27272a",
    "color_palette": [
        "#10b981", # Emerald 500
        "#3b82f6", # Blue 500
        "#f59e0b", # Amber 500
        "#8b5cf6", # Violet 500
        "#ec4899", # Pink 500
        "#06b6d4", # Cyan 500
        "#64748b", # Slate 500
        "#84cc16", # Lime 500
        "#f97316", # Orange 500
        "#14b8a6", # Teal 500
        "#a855f7", # Purple 500
        "#0284c7", # Sky 600
        "#e11d48", # Rose 600
        "#d97706", # Amber 600
        "#4f46e5", # Indigo 600
        "#059669", # Emerald 600
        "#71717a", # Zinc 500
    ]
}

# Alias for backwards compatibility
EMERALD_THEME_CSS = SHADCN_ZINC_CSS

