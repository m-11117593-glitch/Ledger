import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import re

import database
import model_utils
import styles
import auth_utils

from database import init_db, add_expense, delete_expense, get_expenses, get_summary_stats
from model_utils import predict_category, get_categories
from styles import SHADCN_ZINC_CSS, CHART_THEME
from auth_utils import get_google_auth_url, exchange_code_for_user


def clear_query_params():
    """Safely clear query params across Streamlit versions."""
    try:
        st.query_params.clear()
    except Exception:
        for key in list(st.query_params.keys()):
            del st.query_params[key]


def parse_expenses_from_text(text: str) -> list[dict]:
    """
    Parse a free-text essay and extract potential expense transactions.

    Finds all dollar amounts and captures surrounding words as descriptions.
    Handles multiple amounts per sentence by assigning surrounding text to each.
    """
    if not text or not text.strip():
        return []

    sentences = re.split(r'[.!?\n]+', text)
    transactions = []

    amount_pattern = re.compile(
        r'\$?(\d{1,3}(?:,\d{3})*\.\d{2}|\d+\.\d{2}|\d{1,3}(?:,\d{3})*|\d+)'
    )

    strip_prefixes = re.compile(
        r'^(I\s+)?(spent|paid|cost|was|for|at|on|in|of|to|bought|purchased)\s+',
        re.IGNORECASE
    )

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        matches = list(amount_pattern.finditer(sentence))
        if not matches:
            continue

        prev_end = 0
        for i, match in enumerate(matches):
            amount_str = match.group(1)
            try:
                amount = float(amount_str.replace(',', ''))
            except ValueError:
                prev_end = match.end()
                continue

            if amount <= 0 or amount > 1_000_000:
                prev_end = match.end()
                continue

            # Text before this amount (from prev match end to this match start)
            before = sentence[prev_end:match.start()].strip()

            # Text after this amount (up to next match or end of sentence)
            after_end = matches[i + 1].start() if i + 1 < len(matches) else len(sentence)
            after = sentence[match.end():after_end].strip()

            desc = ' '.join(filter(None, [before, after]))

            # Clean up description
            desc = re.sub(r'[,:;–—\-]+$', '', desc).strip()
            desc = strip_prefixes.sub('', desc).strip()
            desc = re.sub(r'\b(dollars?|usd|cad|eur|gbp)\b$', '', desc, flags=re.IGNORECASE).strip()

            if not desc:
                desc = "Imported from text"

            transactions.append({
                "description": desc[:120],
                "amount": round(amount, 2),
            })

            prev_end = match.end()

    return transactions


# ----------------- Page Configuration -----------------
st.set_page_config(
    page_title="Ledger — Cash Flow & Expense Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply shadcn/ui Zinc Theme
st.markdown(SHADCN_ZINC_CSS, unsafe_allow_html=True)

# Initialize Persistent SQLite Database
init_db()

all_categories = get_categories()

# ----------------- Session State -----------------
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_picture" not in st.session_state:
    st.session_state.user_picture = None

# ----------------- Handle Incoming Google OAuth Callback -----------------
if "code" in st.query_params:
    auth_code = st.query_params["code"]
    with st.spinner("Verifying Google account..."):
        user_info = exchange_code_for_user(auth_code)
        if user_info["success"]:
            st.session_state.current_user = user_info["email"]
            st.session_state.user_name = user_info.get("name", user_info["email"])
            st.session_state.user_picture = user_info.get("picture", "")
            clear_query_params()
            st.rerun()
        else:
            st.error(f"Google Authentication failed: {user_info.get('error')}")
            clear_query_params()

# ----------------- Login Screen (If Not Signed In) -----------------
if not st.session_state.current_user:
    col_l1, col_center, col_l2 = st.columns([1, 1.2, 1])
    
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="shadcn-login-card">
            <div style="display: flex; justify-content: center; margin-bottom: 14px;">
                <div class="shadcn-logo" style="width: 38px; height: 38px; font-size: 19px;">L</div>
            </div>
            <h2 style="font-size: 22px; font-weight: 700; color: #fafafa; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                Welcome to Ledger
            </h2>
            <p style="font-size: 13px; color: #a1a1aa; margin: 0 0 20px 0; line-height: 1.4;">
                Sign in with your verified Google account to access your personal expense dashboard.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Google OAuth Button
        google_url = get_google_auth_url()
        
        if google_url:
            st.markdown(f"""
            <a href="{google_url}" target="_self" class="shadcn-google-btn">
                <svg width="18" height="18" viewBox="0 0 18 18">
                    <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.616z"/>
                    <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
                    <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707 0-.59.102-1.167.282-1.707V4.961H.957C.347 6.175 0 7.55 0 9s.347 2.825.957 4.039l3.007-2.332z"/>
                    <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z"/>
                </svg>
                Continue with Google
            </a>
            """, unsafe_allow_html=True)
        else:
            st.warning("Google OAuth credentials missing in .streamlit/secrets.toml")
            
        st.markdown("""
        <div style="text-align: center; margin-top: 32px; font-size: 11px; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;">
            Or quick demo bypass:
        </div>
        """, unsafe_allow_html=True)
        
        c_demo1, c_demo2 = st.columns(2)
        with c_demo1:
            if st.button("Demo Account", use_container_width=True):
                st.session_state.current_user = "demo@ledger.app"
                st.session_state.user_name = "Demo Tester"
                st.rerun()
        with c_demo2:
            if st.button("Guest Workspace", use_container_width=True):
                st.session_state.current_user = "guest@ledger.app"
                st.session_state.user_name = "Guest User"
                st.rerun()
                
    st.stop()

# ----------------- Top Navbar (Signed In) -----------------
current_user = st.session_state.current_user
user_name = st.session_state.get("user_name", current_user)
user_pic = st.session_state.get("user_picture")

nav_col_left, nav_col_mid, nav_col_right = st.columns([1.5, 1, 0.8])

with nav_col_left:
    pic_html = f'<img src="{user_pic}" style="width:20px; height:20px; border-radius:50%; vertical-align:middle; margin-right:4px;" />' if user_pic else "👤 "
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <div class="shadcn-logo">L</div>
        <div>
            <div class="shadcn-title">Ledger</div>
            <div class="shadcn-subtitle">Income & Expense Intelligence</div>
        </div>
        <div style="margin-left: 8px;">
            <span class="shadcn-user-badge">{pic_html}{current_user}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with nav_col_mid:
    selected_period = st.radio(
        "Time Horizon",
        ["This Week", "This Month", "All Time"],
        index=1,
        horizontal=True,
        label_visibility="collapsed"
    )

with nav_col_right:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.user_name = None
        st.session_state.user_picture = None
        clear_query_params()
        st.rerun()

st.markdown("<hr style='border: none; border-top: 1px solid #27272a; margin: 8px 0 20px 0;'>", unsafe_allow_html=True)

# ----------------- Data Retrieval & Calculations -----------------
df_current = get_expenses(selected_period, user_email=current_user)
stats = get_summary_stats(df_current)

total_income = stats.get("total_income", 0.0)
total_spent = stats.get("total_spent", 0.0)
net_val = stats.get("net_savings", 0.0)
expense_count = stats.get("expense_count", 0)
top_category = stats.get("top_category", "None")
top_category_amount = stats.get("top_category_amount", 0.0)
top_category_pct = stats.get("top_category_pct", 0.0)

# ----------------- Metric Cards Grid (shadcn Cards) -----------------
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown(f"""
    <div class="shadcn-card">
        <div class="shadcn-card-header">
            <span class="shadcn-card-title">Total Income (Inflow)</span>
            <span class="shadcn-card-icon" style="color: #10b981;">↓</span>
        </div>
        <div class="shadcn-card-value text-emerald">+${total_income:,.2f}</div>
        <div class="shadcn-card-desc">Gained in {selected_period.lower()}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="shadcn-card">
        <div class="shadcn-card-header">
            <span class="shadcn-card-title">Total Expenses (Outflow)</span>
            <span class="shadcn-card-icon" style="color: #f43f5e;">↑</span>
        </div>
        <div class="shadcn-card-value">${total_spent:,.2f}</div>
        <div class="shadcn-card-desc">Across {expense_count} purchases</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    net_sign = "+" if net_val >= 0 else "-"
    net_color_class = "text-emerald" if net_val >= 0 else "text-rose"
    st.markdown(f"""
    <div class="shadcn-card">
        <div class="shadcn-card-header">
            <span class="shadcn-card-title">Net Cash Flow</span>
            <span class="shadcn-card-icon">⚡</span>
        </div>
        <div class="shadcn-card-value {net_color_class}">{net_sign}${abs(net_val):,.2f}</div>
        <div class="shadcn-card-desc">Income minus expenses</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    top_cat_display = top_category if top_category != "None" else "No Expenses"
    top_cat_desc = f"${top_category_amount:,.2f} ({top_category_pct}% of spend)" if top_category != "None" else "0 expenses logged"
    st.markdown(f"""
    <div class="shadcn-card">
        <div class="shadcn-card-header">
            <span class="shadcn-card-title">Top Expense Category</span>
            <span class="shadcn-card-icon">↗</span>
        </div>
        <div class="shadcn-card-value" style="font-size: 20px; line-height: 1.4;">{top_cat_display}</div>
        <div class="shadcn-card-desc">{top_cat_desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- Spending Concentration Alert (shadcn Alert) -----------------
if top_category != "None" and top_category_amount > 0:
    st.markdown(f"""
    <div class="shadcn-alert">
        <div class="shadcn-alert-icon">ℹ</div>
        <div>
            <div class="shadcn-alert-title">Expense Concentration Summary</div>
            <div class="shadcn-alert-desc">
                Excluding income, most of your spending in <span class="shadcn-alert-highlight">{selected_period.lower()}</span> went towards 
                <span class="shadcn-alert-highlight">{top_category}</span> 
                (<span class="shadcn-alert-highlight">${top_category_amount:,.2f}</span>), 
                accounting for <span class="shadcn-alert-highlight">{top_category_pct}%</span> of your total outflow.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- Main Workspace Columns -----------------
col_form, col_charts = st.columns([1, 1.4], gap="large")

# ========== Left Column: Transaction Input ==========
with col_form:
    st.markdown('<div class="shadcn-section-header">Record Transaction</div>', unsafe_allow_html=True)
    
    with st.container():
        desc = st.text_input(
            "Description",
            placeholder="e.g. Payroll direct deposit, Starbucks, Shell gas station",
            key="input_desc"
        )
        
        # Real-time AI prediction
        pred = predict_category(desc)
        suggested_cat = pred["predicted_category"]
        conf = pred["confidence"]
        
        cat_index = 0
        if suggested_cat in all_categories:
            cat_index = all_categories.index(suggested_cat)
            
        if desc.strip():
            conf_str = f"({int(conf * 100)}% match)" if conf else ""
            st.markdown(f"""
            <div class="shadcn-ai-chip">
                <span>AI Predicted:</span> <strong>{suggested_cat}</strong> {conf_str}
            </div>
            """, unsafe_allow_html=True)
            
        chosen_cat = st.selectbox(
            "Category",
            options=all_categories,
            index=cat_index,
            help="Select 'Income' for money earned/received, or any expense category for money spent."
        )
        
        # Highlight if income vs expense
        is_income = (chosen_cat.strip().lower() == "income")
        if is_income:
            st.markdown("""
            <div style="font-size: 12px; color: #10b981; font-weight: 500; margin-bottom: 8px;">
                ✓ Categorized as <strong>Income (Money Inflow)</strong>
            </div>
            """, unsafe_allow_html=True)
        
        c_amt, c_date = st.columns(2)
        with c_amt:
            amount = st.number_input(
                "Amount ($)",
                min_value=0.01,
                max_value=1000000.0,
                value=25.00,
                step=1.00,
                format="%.2f"
            )
        with c_date:
            exp_date = st.date_input(
                "Date",
                value=date.today(),
                max_value=date.today()
            )
            
        button_label = "Save Income (+)" if is_income else "Save Expense (-)"
        submit_btn = st.button(button_label, use_container_width=True)
        
        if submit_btn:
            if not desc.strip():
                st.error("Please enter a transaction description.")
            else:
                date_str = exp_date.strftime("%Y-%m-%d")
                add_expense(date_str, desc, amount, chosen_cat, user_email=current_user)
                if is_income:
                    st.success(f"Recorded +${amount:,.2f} as Income")
                else:
                    st.success(f"Recorded -${amount:,.2f} under {chosen_cat}")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------- Bulk Import from Text -----------------
    st.markdown('<div class="shadcn-section-header">Bulk Import from Text</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size: 12px; color: #a1a1aa; margin-bottom: 10px;">Paste a long essay or paragraph describing your spending. '
        'I will extract every dollar amount, guess the description, and auto-categorize each transaction.</p>',
        unsafe_allow_html=True
    )

    bulk_text = st.text_area(
        "Paste your spending story",
        placeholder="e.g. I spent $4.50 on coffee this morning, then $12.00 for lunch at the deli. "
                    "Later I paid $85.00 for my electric bill and $3.75 for a snack.",
        height=140,
        key="bulk_text_input",
        label_visibility="collapsed"
    )

    c_parse, c_import = st.columns([1, 1])
    with c_parse:
        parse_btn = st.button("Parse Text", use_container_width=True)
    with c_import:
        import_btn = st.button("Import All Parsed", use_container_width=True, type="primary")

    if parse_btn and bulk_text.strip():
        parsed = parse_expenses_from_text(bulk_text)
        st.session_state.bulk_parsed = parsed

    if "bulk_parsed" in st.session_state and st.session_state.bulk_parsed:
        parsed = st.session_state.bulk_parsed
        st.markdown(f"**Found {len(parsed)} transaction(s):**")

        # Show each parsed transaction with category prediction and checkbox
        selected_indices = []
        for i, txn in enumerate(parsed):
            pred = predict_category(txn["description"])
            suggested_cat = pred["predicted_category"] if pred["success"] else "Shopping & Retail"
            conf = pred["confidence"] if pred["success"] else 0.0

            cat_index = 0
            if suggested_cat in all_categories:
                cat_index = all_categories.index(suggested_cat)

            cols = st.columns([0.05, 0.35, 0.2, 0.2, 0.2])
            with cols[0]:
                checked = st.checkbox("", key=f"bulk_select_{i}")
                if checked:
                    selected_indices.append(i)
            with cols[1]:
                st.markdown(f"**{txn['description']}**")
            with cols[2]:
                st.markdown(f"${txn['amount']:,.2f}")
            with cols[3]:
                cat_choice = st.selectbox(
                    "Category",
                    options=all_categories,
                    index=cat_index,
                    key=f"bulk_cat_{i}",
                    label_visibility="collapsed"
                )
            with cols[4]:
                conf_str = f"{int(conf * 100)}%" if conf else "—"
                st.markdown(f"<div style='text-align: right; font-size: 11px; color: #a1a1aa;'>{conf_str}</div>", unsafe_allow_html=True)

        if import_btn and selected_indices:
            date_str = date.today().strftime("%Y-%m-%d")
            imported = 0
            for i in selected_indices:
                txn = parsed[i]
                cat = st.session_state.get(f"bulk_cat_{i}", "Shopping & Retail")
                add_expense(date_str, txn["description"], txn["amount"], cat, user_email=current_user)
                imported += 1
            st.success(f"Imported {imported} transaction(s) successfully!")
            del st.session_state.bulk_parsed
            st.rerun()
        elif import_btn and not selected_indices:
            st.warning("Please select at least one transaction to import.")

# ========== Right Column: Visualizations ==========
with col_charts:
    st.markdown(f'<div class="shadcn-section-header">Visual Analytics — {selected_period}</div>', unsafe_allow_html=True)
    
    if df_current.empty:
        st.markdown("""
        <div style="background-color: #18181b; border: 1px dashed #27272a; border-radius: 8px; padding: 48px 24px; text-align: center; color: #71717a;">
            <div style="font-size: 14px; font-weight: 500; color: #fafafa; margin-bottom: 4px;">No Transactions For This Account</div>
            <div style="font-size: 13px;">Add your first expense or income on the left to start viewing your personal metrics.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        tab_dist, tab_cashflow = st.tabs(["Expense Breakdown", "Cash Flow Timeline"])
        
        # Donut Chart (Expenses Only, Excluding Income)
        with tab_dist:
            cat_df = stats.get("category_summary", pd.DataFrame())
            if cat_df.empty or total_spent == 0:
                st.markdown("<div style='color: #71717a; padding: 20px 0; font-size: 13px;'>No outflow/expenses logged in this period (only income recorded).</div>", unsafe_allow_html=True)
            else:
                fig_donut = go.Figure(data=[go.Pie(
                    labels=cat_df["category"],
                    values=cat_df["amount"],
                    hole=0.68,
                    textinfo="percent",
                    hoverinfo="label+value+percent",
                    marker=dict(
                        colors=CHART_THEME["color_palette"],
                        line=dict(color="#18181b", width=2)
                    ),
                    hovertemplate="<b>%{label}</b><br>Spent: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
                )])
                
                fig_donut.update_layout(
                    paper_bgcolor=CHART_THEME["paper_bgcolor"],
                    plot_bgcolor=CHART_THEME["plot_bgcolor"],
                    font=dict(color=CHART_THEME["font_color"], family="Inter, sans-serif", size=12),
                    margin=dict(t=15, b=15, l=15, r=15),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.25,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=11, color="#a1a1aa")
                    ),
                    annotations=[dict(
                        text=f"<span style='font-size:10px;color:#71717a;'>TOTAL EXPENSES</span><br><b style='font-size:17px;color:#fafafa;'>${total_spent:,.0f}</b>",
                        x=0.5, y=0.5,
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig_donut, use_container_width=True)
                
        # Cash Flow Timeline Chart (Income vs Expenses side by side)
        with tab_cashflow:
            time_df = stats.get("timeline_summary", pd.DataFrame())
            fig_bar = go.Figure()
            
            # Income Bars (Emerald)
            fig_bar.add_trace(go.Bar(
                x=time_df["date"],
                y=time_df["income"],
                name="Income (+)",
                marker_color="#10b981", # Emerald 500
                hovertemplate="<b>%{x}</b><br>Income: +$%{y:,.2f}<extra></extra>"
            ))
            
            # Expense Bars (Rose/Slate)
            fig_bar.add_trace(go.Bar(
                x=time_df["date"],
                y=time_df["expenses"],
                name="Expenses (-)",
                marker_color="#f43f5e", # Rose 500
                hovertemplate="<b>%{x}</b><br>Expenses: -$%{y:,.2f}<extra></extra>"
            ))
            
            fig_bar.update_layout(
                barmode="group",
                paper_bgcolor=CHART_THEME["paper_bgcolor"],
                plot_bgcolor=CHART_THEME["plot_bgcolor"],
                font=dict(color=CHART_THEME["font_color"], family="Inter, sans-serif", size=12),
                margin=dict(t=15, b=15, l=15, r=15),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, color="#a1a1aa")
                ),
                xaxis=dict(
                    gridcolor=CHART_THEME["grid_color"],
                    linecolor=CHART_THEME["grid_color"],
                    tickformat="%b %d"
                ),
                yaxis=dict(
                    gridcolor=CHART_THEME["grid_color"],
                    linecolor=CHART_THEME["grid_color"],
                    tickprefix="$"
                )
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- Bottom Section: Transaction Ledger -----------------
st.markdown("<br><hr style='border: none; border-top: 1px solid #27272a; margin: 16px 0 20px 0;'>", unsafe_allow_html=True)
st.markdown(f'<div class="shadcn-section-header">Transactions Ledger — {current_user}</div>', unsafe_allow_html=True)

df_all = get_expenses("All Time", user_email=current_user)

if df_all.empty:
    st.markdown("<div style='color: #71717a; font-size: 13px;'>No transactions recorded for this account yet.</div>", unsafe_allow_html=True)
else:
    c_search, c_delete, c_exp = st.columns([2, 1.5, 0.8])
    
    with c_search:
        search_query = st.text_input(
            "Search Transactions",
            placeholder="Filter by merchant or category...",
            label_visibility="collapsed"
        )
        
    display_df = df_all.copy()
    if search_query.strip():
        q = search_query.strip().lower()
        display_df = display_df[
            display_df["description"].str.lower().str.contains(q) |
            display_df["category"].str.lower().str.contains(q)
        ]
        
    with c_delete:
        if not display_df.empty:
            del_id = st.selectbox(
                "Delete",
                options=display_df["id"].tolist(),
                format_func=lambda x: f"#{x} · {display_df[display_df['id']==x]['description'].values[0][:18]} (${display_df[display_df['id']==x]['amount'].values[0]:,.2f})",
                label_visibility="collapsed"
            )
            if st.button("Delete Selected", use_container_width=True):
                delete_expense(del_id, user_email=current_user)
                st.rerun()

    with c_exp:
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export CSV",
            data=csv_data,
            file_name=f"ledger_{current_user.split('@')[0]}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Format table with signs
    table_view = display_df[["id", "date", "description", "category", "amount"]].copy()
    table_view["Type"] = table_view["category"].apply(lambda c: "Inflow (+)" if c.strip().lower() == "income" else "Outflow (-)")
    table_view["Formatted Amount"] = table_view.apply(
        lambda row: f"+${row['amount']:,.2f}" if row["category"].strip().lower() == "income" else f"-${row['amount']:,.2f}",
        axis=1
    )
    
    final_table = table_view[["id", "date", "description", "category", "Type", "Formatted Amount"]].copy()
    final_table.columns = ["ID", "Date", "Description", "Category", "Flow Type", "Amount"]
    
    st.dataframe(
        final_table,
        use_container_width=True,
        hide_index=True,
        height=260
    )
