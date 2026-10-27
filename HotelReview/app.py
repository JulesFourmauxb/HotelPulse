import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from datetime import datetime, timedelta

# ==========================================
# PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="HotelPulse AI | Accor Paris Multi-Property & Map Engine",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.8rem; padding-bottom: 2.5rem; }
    
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        height: 135px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card-alert {
        background-color: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 6px solid #e11d48;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 6px rgba(225, 29, 72, 0.06);
        height: 135px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title { font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: #64748b; }
    .kpi-value { font-size: 1.9rem; font-weight: 700; color: #0f172a; line-height: 1.2; }
    .kpi-subtext-positive { font-size: 0.85rem; font-weight: 600; color: #16a34a; }
    .kpi-subtext-neutral { font-size: 0.85rem; font-weight: 500; color: #475569; }
    .kpi-alert-value { font-size: 1.05rem; font-weight: 700; color: #be123c; line-height: 1.3; }
    .kpi-alert-subtext { font-size: 0.82rem; font-weight: 500; color: #9f1239; }

    .action-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 3px 8px rgba(15, 23, 42, 0.04);
    }
    .action-high { border-left: 7px solid #ef4444; }
    .action-medium { border-left: 7px solid #f59e0b; }
    .action-low { border-left: 7px solid #10b981; }
    .action-addressed { border-left: 7px solid #64748b; background-color: #f8fafc; opacity: 0.88; }

    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 8px;
    }
    .badge-high { background-color: #fee2e2; color: #b91c1c; }
    .badge-medium { background-color: #fef3c7; color: #b45309; }
    .badge-low { background-color: #d1fae5; color: #047857; }
    .badge-dept { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .badge-status-open { background-color: #f1f5f9; color: #475569; }
    .badge-status-assigned { background-color: #e0e7ff; color: #4338ca; }
    .badge-status-done { background-color: #dcfce7; color: #15803d; }

    .action-headline { font-size: 1.1rem; font-weight: 600; color: #0f172a; margin: 10px 0 6px 0; }
    .action-meta { font-size: 0.86rem; color: #64748b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 15 ACCOR PARIS HOTELS MASTER METADATA
# ==========================================
HOTELS_METADATA = pd.DataFrame([
    {"name": "Le Royal Monceau - Raffles Paris", "brand": "Raffles", "group": "Accor Luxury", "stars": 5, "lat": 48.8763, "lon": 2.3004, "color": [147, 51, 234]},
    {"name": "Sofitel Paris Le Faubourg", "brand": "Sofitel", "group": "Accor Luxury", "stars": 5, "lat": 48.8687, "lon": 2.3218, "color": [147, 51, 234]},
    {"name": "Sofitel Paris Baltimore Tour Eiffel", "brand": "Sofitel", "group": "Accor Luxury", "stars": 5, "lat": 48.8654, "lon": 2.2902, "color": [147, 51, 234]},
    {"name": "Pullman Paris Tour Eiffel", "brand": "Pullman", "group": "Accor Premium", "stars": 4, "lat": 48.8554, "lon": 2.2929, "color": [37, 99, 235]},
    {"name": "Pullman Paris Montparnasse", "brand": "Pullman", "group": "Accor Premium", "stars": 4, "lat": 48.8396, "lon": 2.3228, "color": [37, 99, 235]},
    {"name": "Pullman Paris Bercy", "brand": "Pullman", "group": "Accor Premium", "stars": 4, "lat": 48.8315, "lon": 2.3862, "color": [37, 99, 235]},
    {"name": "Hôtel Novotel Paris les Halles", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8606, "lon": 2.3461, "color": [16, 185, 129]},
    {"name": "Novotel Paris Centre Tour Eiffel", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8507, "lon": 2.2825, "color": [16, 185, 129]},
    {"name": "Novotel Paris Vaugirard Montparnasse", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8385, "lon": 2.3045, "color": [16, 185, 129]},
    {"name": "Hôtel Mercure Paris Centre Tour Eiffel", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8542, "lon": 2.2941, "color": [245, 158, 11]},
    {"name": "Mercure Paris Opéra Garnier", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8751, "lon": 2.3262, "color": [245, 158, 11]},
    {"name": "Mercure Paris Montmartre Sacré-Cœur", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8858, "lon": 2.3312, "color": [245, 158, 11]},
    {"name": "Hôtel ibis Paris Tour Eiffel Cambronne", "brand": "ibis", "group": "Accor Economy", "stars": 3, "lat": 48.8465, "lon": 2.3032, "color": [239, 68, 68]},
    {"name": "ibis Paris Bastille Opéra", "brand": "ibis", "group": "Accor Economy", "stars": 3, "lat": 48.8553, "lon": 2.3689, "color": [239, 68, 68]},
    {"name": "ibis Styles Paris République", "brand": "ibis Styles", "group": "Accor Economy", "stars": 3, "lat": 48.8672, "lon": 2.3644, "color": [239, 68, 68]},
])

# Initialize Session State
if "action_states" not in st.session_state:
    st.session_state.action_states = {
        hotel: {
            "card_1": {"status": "Open", "assigned_to": None},
            "card_2": {"status": "Open", "assigned_to": None},
            "card_3": {"status": "Open", "assigned_to": None},
        }
        for hotel in HOTELS_METADATA["name"]
    }


# ==========================================
# SYNTHETIC DATA GENERATOR
# ==========================================
@st.cache_data
def generate_synthetic_review_dataset(hotel_name: str):
    np.random.seed(abs(hash(hotel_name)) % (2**32))
    today = datetime(2026, 10, 27)

    platforms = ["Google Reviews", "TripAdvisor", "Booking.com"]
    languages = ["English 🇬🇧", "French 🇫🇷", "German 🇩🇪", "Spanish 🇪🇸"]
    dept_aspects = {
        "Front Desk": ["Check-in Speed", "Staff Politeness", "Arrival Flow"],
        "Housekeeping": ["Room Cleanliness", "Bedding Comfort", "Bathroom Space"],
        "Maintenance": ["Wi-Fi Speed", "Air Conditioning", "Elevator Delay"],
        "F&B": ["Breakfast Variety", "Coffee Quality", "Room Service Speed"],
    }

    records = []
    for _ in range(120):
        review_date = (today - timedelta(days=int(np.random.randint(0, 300)))).date()
        dept = np.random.choice(list(dept_aspects.keys()))
        aspect = np.random.choice(dept_aspects[dept])
        platform = np.random.choice(platforms)
        lang = np.random.choice(languages, p=[0.4, 0.3, 0.15, 0.15])

        rating_val = np.random.choice([5, 4, 3, 2, 1], p=[0.50, 0.25, 0.15, 0.07, 0.03])
        sentiment = "Positive" if rating_val >= 4 else ("Neutral" if rating_val == 3 else "Negative")

        records.append({
            "Date": review_date,
            "Rating": rating_val,
            "Platform": platform,
            "Language": lang,
            "Department": dept,
            "Aspect": aspect,
            "Sentiment": sentiment,
            "Original Text": f"Sample feedback regarding {aspect.lower()} at {hotel_name}.",
        })

    return pd.DataFrame(records)


def get_hotel_actions(hotel_name: str):
    return [
        {
            "id": "card_1",
            "priority": "High Priority",
            "priority_level": "high",
            "department": "Front Desk",
            "dept_head": "Claire Moreau (Front Office Lead)",
            "recommendation": "Deploy express check-in desk for ALL Accor Loyalty members during 3 PM peak.",
            "impact": "Estimated +0.22 score lift | Root Aspect: Check-in Speed",
            "languages_affected": "English (14), French (10), German (5)",
        },
        {
            "id": "card_2",
            "priority": "Medium Priority",
            "priority_level": "medium",
            "department": "Maintenance",
            "dept_head": "Marc Dubois (Chief Engineer)",
            "recommendation": "Calibrate HVAC cooling relays & replace hallway door hydraulic closers.",
            "impact": "Estimated +0.15 score lift | Root Aspect: Noise & Air Conditioning",
            "languages_affected": "German (8), French (6)",
        },
        {
            "id": "card_3",
            "priority": "Low Priority",
            "priority_level": "low",
            "department": "F&B",
            "dept_head": "Chef Jérôme Charles (F&B Director)",
            "recommendation": "Add organic plant-based milk and gluten-free pastries to breakfast buffet.",
            "impact": "Estimated +0.06 score lift | Root Aspect: Breakfast Variety",
            "languages_affected": "English (5), Spanish (3)",
        },
    ]


# ==========================================
# SIDEBAR CONTROLS & MAP FILTERS
# ==========================================
with st.sidebar:
    st.markdown("## 🏨 HotelPulse AI")
    st.caption("Accor Paris Multi-Property Dashboard")
    st.markdown("---")

    st.markdown("### 🔍 Property Filters")
    
    # 1. Star Rating Filter
    selected_stars = st.multiselect(
        "🌟 Filter by Star Rating",
        options=[3, 4, 5],
        default=[3, 4, 5],
        format_func=lambda x: f"{x} Stars",
    )

    # 2. Brand Family Filter
    available_brands = HOTELS_METADATA["brand"].unique().tolist()
    selected_brands = st.multiselect(
        "🏷️ Filter by Brand Family",
        options=available_brands,
        default=available_brands,
    )

    # Filter Hotels Table based on selection
    filtered_hotels_df = HOTELS_METADATA[
        (HOTELS_METADATA["stars"].isin(selected_stars)) &
        (HOTELS_METADATA["brand"].isin(selected_brands))
    ]

    if filtered_hotels_df.empty:
        st.error("No properties match your star/brand filters.")
        st.stop()

    # 3. Selected Property Dropdown
    selected_hotel = st.selectbox(
        "📍 Select Property Details",
        options=filtered_hotels_df["name"].tolist(),
        index=0,
    )

    st.markdown("---")

    selected_date_range = st.selectbox(
        "📅 Date Range Window",
        options=["Last 30 Days", "Q3 2026", "Full Year 2026", "Custom Range"],
        index=0,
    )

    today = datetime(2026, 10, 27).date()
    if selected_date_range == "Last 30 Days":
        start_date = today - timedelta(days=30)
        end_date = today
    elif selected_date_range == "Q3 2026":
        start_date = datetime(2026, 7, 1).date()
        end_date = datetime(2026, 9, 30).date()
    elif selected_date_range == "Full Year 2026":
        start_date = datetime(2026, 1, 1).date()
        end_date = today
    else:
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("Start", today - timedelta(days=60))
        with col_d2: end_date = st.date_input("End", today)

    st.markdown("---")
    plat_google = st.checkbox("Google Reviews", value=True)
    plat_tripadvisor = st.checkbox("TripAdvisor", value=True)
    plat_booking = st.checkbox("Booking.com", value=True)

    selected_platforms = []
    if plat_google: selected_platforms.append("Google Reviews")
    if plat_tripadvisor: selected_platforms.append("TripAdvisor")
    if plat_booking: selected_platforms.append("Booking.com")


# ==========================================
# DATA PROCESSING & COMPUTATION
# ==========================================
raw_df = generate_synthetic_review_dataset(selected_hotel)
filtered_df = raw_df[
    (raw_df["Date"] >= start_date) &
    (raw_df["Date"] <= end_date) &
    (raw_df["Platform"].isin(selected_platforms))
]

total_reviews_count = len(filtered_df)
avg_score = filtered_df["Rating"].mean() if total_reviews_count > 0 else 0.0
negative_alerts_count = len(filtered_df[filtered_df["Sentiment"] == "Negative"])
actions = get_hotel_actions(selected_hotel)


# ==========================================
# INTERACTIVE MAP SECTION
# ==========================================
st.subheader("🗺️ Accor Paris Interactive Property Map")
st.caption("Displaying properties based on star rating and brand filters. Hover over pins for hotel info.")

# PyDeck 3D Map View
layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_hotels_df,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius=250,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_min_pixels=8,
    radius_max_pixels=15,
)

view_state = pdk.ViewState(
    latitude=48.8566,
    longitude=2.3428,
    zoom=11.5,
    pitch=35,
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}\nBrand: {brand} | Category: {stars}★\nGroup: {group}"},
    map_style="mapbox://styles/mapbox/light-v10",
)

st.pydeck_chart(r)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


# ==========================================
# HEADER & TOP METRICS KPI CARDS
# ==========================================
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.title("HotelPulse AI: Accor Guest Sentiment & Action Engine")
    st.markdown(
        f"**Selected Property:** `{selected_hotel}` &nbsp;|&nbsp; "
        f"**Window:** `{start_date}` to `{end_date}` &nbsp;|&nbsp; "
        f"**Sources:** `{', '.join(selected_platforms)}`"
    )
with head_col2:
    st.markdown("<div style='text-align: right; padding-top: 18px;'>", unsafe_allow_html=True)
    st.button(
        "📥 Export Executive PDF",
        type="secondary",
        use_container_width=True,
        on_click=lambda: st.toast("Executive Brief queued for PDF export!", icon="📄"),
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# Top KPI Cards
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Calculated Guest Satisfaction Score</div>
            <div class="kpi-value">⭐ {avg_score:.2f} / 5.0</div>
            <div class="kpi-subtext-positive">▲ Computed from {total_reviews_count} reviews</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Analyzed Review Volume</div>
            <div class="kpi-value">{total_reviews_count} Reviews</div>
            <div class="kpi-subtext-neutral">🌍 Across 4 languages (EN, FR, DE, ES)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col3:
    st.markdown(
        f"""
        <div class="kpi-card-alert">
            <div class="kpi-title" style="color: #9f1239;">Urgent Operational Alerts</div>
            <div class="kpi-alert-value">⚠️ {negative_alerts_count} Negative Feedback Mentions</div>
            <div class="kpi-alert-subtext">Requires immediate resolution by dept leads</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


# ==========================================
# MAIN NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(
    [
        "🔥 Priority Action Matrix",
        "🏢 Departmental Deep-Dive & Ratings",
        "🌍 Multilingual Feed & Auto-Translation",
    ]
)


# ------------------------------------------
# TAB 1: PRIORITY ACTION MATRIX
# ------------------------------------------
with tab1:
    st.subheader("Weekly Priority Action Matrix")
    st.markdown("AI-synthesized operational recommendations generated by clustering guest feedback.")

    hotel_states = st.session_state.action_states[selected_hotel]
    completed_count = sum(1 for v in hotel_states.values() if v["status"] == "Addressed")
    st.progress(
        completed_count / len(actions),
        text=f"Resolution Progress: {completed_count} of {len(actions)} actions addressed",
    )

    for idx, item in enumerate(actions):
        card_id = item["id"]
        current_state = hotel_states[card_id]["status"]
        assigned_person = hotel_states[card_id]["assigned_to"]

        border_class = "action-addressed" if current_state == "Addressed" else f"action-{item['priority_level']}"
        priority_badge_class = f"badge-{item['priority_level']}"

        if current_state == "Addressed":
            status_badge = '<span class="badge badge-status-done">✓ Addressed</span>'
        elif assigned_person:
            status_badge = f'<span class="badge badge-status-assigned">👤 Assigned: {assigned_person}</span>'
        else:
            status_badge = '<span class="badge badge-status-open">● Pending Action</span>'

        st.markdown(
            f"""
            <div class="action-card {border_class}">
                <div>
                    <span class="badge {priority_badge_class}">{item["priority"]}</span>
                    <span class="badge badge-dept">🏢 {item["department"]}</span>
                    {status_badge}
                </div>
                <div class="action-headline">Action {idx + 1}: "{item["recommendation"]}"</div>
                <div class="action-meta">
                    <strong>📊 Impact:</strong> {item["impact"]} &nbsp;|&nbsp;
                    <strong>🗣️ Mentioned in:</strong> {item["languages_affected"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn_col1, btn_col2, _ = st.columns([1.3, 1.8, 4])
        with btn_col1:
            is_done = current_state == "Addressed"
            if st.button(
                "✓ Mark as Addressed" if not is_done else "↺ Reopen Action",
                key=f"btn_done_{selected_hotel}_{card_id}",
                type="primary" if not is_done else "secondary",
                use_container_width=True,
            ):
                new_status = "Open" if is_done else "Addressed"
                st.session_state.action_states[selected_hotel][card_id]["status"] = new_status
                st.rerun()

        with btn_col2:
            if st.button(
                f"📋 Assign to {item['dept_head'].split(' ')[0]}",
                key=f"btn_assign_{selected_hotel}_{card_id}",
                use_container_width=True,
                disabled=(current_state == "Addressed"),
            ):
                st.session_state.action_states[selected_hotel][card_id]["assigned_to"] = item["dept_head"]
                st.toast(f"Assigned to {item['dept_head']}", icon="📨")
                st.rerun()

        st.markdown("<hr style='margin: 12px 0 18px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)


# ------------------------------------------
# TAB 2: DEPARTMENTAL DEEP-DIVE & RATINGS
# ------------------------------------------
with tab2:
    st.subheader("Departmental Deep-Dive & Exact Aspect Ratings")

    if total_reviews_count == 0:
        st.warning("No reviews available for the selected filters.")
    else:
        chart_col1, chart_col2 = st.columns([1.4, 1])

        with chart_col1:
            dept_sentiment = filtered_df.groupby(["Department", "Sentiment"]).size().unstack(fill_value=0)
            for col in ["Positive", "Neutral", "Negative"]:
                if col not in dept_sentiment.columns: dept_sentiment[col] = 0

            dept_pct = (dept_sentiment.div(dept_sentiment.sum(axis=1), axis=0) * 100).reset_index().melt(
                id_vars="Department", value_name="Percentage", var_name="Sentiment"
            )

            fig_dept = px.bar(
                dept_pct,
                x="Percentage",
                y="Department",
                color="Sentiment",
                orientation="h",
                title="Sentiment Share by Department (%)",
                color_discrete_map={"Positive": "#10b981", "Neutral": "#94a3b8", "Negative": "#ef4444"},
            )
            fig_dept.update_layout(barmode="stack", height=350, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_dept, use_container_width=True)

        with chart_col2:
            lang_counts = filtered_df["Language"].value_counts().reset_index()
            lang_counts.columns = ["Language", "Count"]

            fig_lang = px.pie(lang_counts, names="Language", values="Count", hole=0.5, title="Review Volume by Language")
            fig_lang.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_lang, use_container_width=True)

        st.markdown("---")

        aspect_df = filtered_df.groupby("Aspect")["Rating"].agg(["mean", "count"]).reset_index()
        aspect_df.columns = ["Aspect", "Score", "Count"]
        aspect_df = aspect_df.sort_values(by="Score", ascending=True)

        aspect_df["Tier"] = aspect_df["Score"].apply(
            lambda v: "Healthy (≥ 4.0)" if v >= 4.0 else ("At Risk (3.5 - 3.9)" if v >= 3.5 else "Critical (< 3.5)")
        )

        fig_aspects = px.bar(
            aspect_df,
            x="Score",
            y="Aspect",
            orientation="h",
            text=aspect_df["Score"].round(2),
            color="Tier",
            color_discrete_map={
                "Healthy (≥ 4.0)": "#10b981",
                "At Risk (3.5 - 3.9)": "#f59e0b",
                "Critical (< 3.5)": "#ef4444",
            },
            title="Computed Aspect Ratings (1-5 Scale)",
        )
        fig_aspects.add_vline(x=4.0, line_dash="dash", line_color="#ef4444", annotation_text="Benchmark Target (4.0)")
        fig_aspects.update_layout(xaxis=dict(range=[0, 5.5]), height=380, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_aspects, use_container_width=True)


# ------------------------------------------
# TAB 3: MULTILINGUAL FEED & AUTO-TRANSLATION
# ------------------------------------------
with tab3:
    st.subheader("Filtered Live Review Feed")

    if total_reviews_count == 0:
        st.info("No reviews match the current filters.")
    else:
        f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
        with f_col1: sent_f = st.selectbox("Filter Sentiment", ["All", "Positive", "Neutral", "Negative"])
        with f_col2: dept_f = st.selectbox("Filter Department", ["All", "Front Desk", "Housekeeping", "Maintenance", "F&B"])
        with f_col3: search_q = st.text_input("🔍 Search Keyword", placeholder="e.g. Wi-Fi, elevator...")

        display_df = filtered_df.copy()
        if sent_f != "All": display_df = display_df[display_df["Sentiment"] == sent_f]
        if dept_f != "All": display_df = display_df[display_df["Department"] == dept_f]
        if search_q: display_df = display_df[display_df["Original Text"].str.contains(search_q, case=False)]

        st.caption(f"Showing {len(display_df)} matching reviews:")

        for _, r in display_df.head(15).iterrows():
            sentiment_color = "#10b981" if r["Sentiment"] == "Positive" else ("#f59e0b" if r["Sentiment"] == "Neutral" else "#ef4444")
            st.markdown(
                f"""
                <div style="background-color: #ffffff; border-radius: 10px; padding: 14px 18px; border: 1px solid #e2e8f0; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div>
                            <strong>{r['Platform']}</strong> &nbsp;|&nbsp; {r['Language']} &nbsp;|&nbsp; <span style="color: #64748b;">{r['Date']}</span>
                        </div>
                        <div>
                            <span style="background-color: {sentiment_color}22; color: {sentiment_color}; font-weight: 700; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem;">
                                ⭐ {r['Rating']}/5 - {r['Sentiment']}
                            </span>
                        </div>
                    </div>
                    <div style="font-size: 0.95rem; color: #1e293b; margin-bottom: 6px;">
                        <em>"{r['Original Text']}"</em>
                    </div>
                    <div>
                        <span class="badge badge-dept">🏢 {r['Department']}</span>
                        <span style="font-size: 0.8rem; background-color: #f1f5f9; color: #334155; padding: 3px 8px; border-radius: 6px;">
                            🏷️ Aspect: {r['Aspect']}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )