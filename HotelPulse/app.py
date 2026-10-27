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
    page_title="HotelPulse AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Night Blue, White Text, and Electric Blue Buttons
st.markdown(
    """
    <style>
    /* Global App Background */
    .stApp {
        background-color: #0B132B !important;
        color: #FFFFFF !important;
    }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #060913 !important;
    }
    
    /* Global Text Elements */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #FFFFFF;
    }
    
    /* Electric Blue Buttons */
    div.stButton > button:first-child {
        background-color: #0066FF !important;
        color: #FFFFFF !important;
        border: 1px solid #0066FF !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #00E5FF !important;
        border-color: #00E5FF !important;
        color: #0B132B !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.6) !important;
    }

    /* Adjust Streamlit inputs/select boxes for Dark Theme */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #151e32 !important;
        color: white !important;
        border-color: #2d3748 !important;
    }
    
    /* Layout Adjustments */
    .block-container { padding-top: 2rem; padding-bottom: 2.5rem; }
    
    /* Custom KPI Cards */
    .kpi-card {
        background-color: #151E32;
        border: 1px solid #2D3748;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card-alert {
        background-color: #1A1118;
        border: 1px solid #4A1525;
        border-left: 6px solid #E11D48;
        border-radius: 8px;
        padding: 16px 20px;
        height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #94A3B8; }
    .kpi-value { font-size: 1.7rem; font-weight: 700; color: #FFFFFF; line-height: 1.2; }
    .kpi-subtext-positive { font-size: 0.8rem; font-weight: 600; color: #10B981; }
    .kpi-subtext-neutral { font-size: 0.8rem; font-weight: 500; color: #94A3B8; }
    .kpi-alert-value { font-size: 1.0rem; font-weight: 700; color: #F43F5E; line-height: 1.3; }
    .kpi-alert-subtext { font-size: 0.78rem; font-weight: 500; color: #FDA4AF; }

    /* Custom Action Cards */
    .action-card {
        background-color: #151E32;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 12px;
        border: 1px solid #2D3748;
    }
    .action-high { border-left: 6px solid #EF4444; }
    .action-medium { border-left: 6px solid #F59E0B; }
    .action-low { border-left: 6px solid #10B981; }
    .action-addressed { border-left: 6px solid #475569; opacity: 0.6; }

    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 8px;
    }
    .badge-high { background-color: #451a1a; color: #fca5a5; }
    .badge-medium { background-color: #452a0a; color: #fcd34d; }
    .badge-low { background-color: #064e3b; color: #6ee7b7; }
    .badge-dept { background-color: #172554; color: #93c5fd; border: 1px solid #1e3a8a; }
    
    .action-headline { font-size: 1.05rem; font-weight: 600; color: #F8FAFC; margin: 10px 0 6px 0; }
    .action-meta { font-size: 0.85rem; color: #CBD5E1; }
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
    {"name": "Hotel Novotel Paris les Halles", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8606, "lon": 2.3461, "color": [16, 185, 129]},
    {"name": "Novotel Paris Centre Tour Eiffel", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8507, "lon": 2.2825, "color": [16, 185, 129]},
    {"name": "Novotel Paris Vaugirard Montparnasse", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8385, "lon": 2.3045, "color": [16, 185, 129]},
    {"name": "Hotel Mercure Paris Centre Tour Eiffel", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8542, "lon": 2.2941, "color": [245, 158, 11]},
    {"name": "Mercure Paris Opera Garnier", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8751, "lon": 2.3262, "color": [245, 158, 11]},
    {"name": "Mercure Paris Montmartre Sacre-Coeur", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8858, "lon": 2.3312, "color": [245, 158, 11]},
    {"name": "Hotel ibis Paris Tour Eiffel Cambronne", "brand": "ibis", "group": "Accor Economy", "stars": 3, "lat": 48.8465, "lon": 2.3032, "color": [239, 68, 68]},
    {"name": "ibis Paris Bastille Opera", "brand": "ibis", "group": "Accor Economy", "stars": 3, "lat": 48.8553, "lon": 2.3689, "color": [239, 68, 68]},
    {"name": "ibis Styles Paris Republique", "brand": "ibis Styles", "group": "Accor Economy", "stars": 3, "lat": 48.8672, "lon": 2.3644, "color": [239, 68, 68]},
])

# Initialize Session State
if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = "Pullman Paris Tour Eiffel"

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
    languages = ["English", "French", "German", "Spanish"]
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

def get_hotel_actions(hotel_name: str, filtered_df: pd.DataFrame):
    lang_counts = filtered_df["Language"].value_counts().to_dict()
    en_cnt = lang_counts.get("English", 8)
    fr_cnt = lang_counts.get("French", 6)
    
    return [
        {
            "id": "card_1",
            "priority": "High Priority",
            "priority_level": "high",
            "department": "Front Desk",
            "dept_head": "Alexandre de Saint-Germain",
            "recommendation": "Add secondary service team during peak hours to mitigate wait times.",
            "impact": "Estimated +0.25 overall lift | Root Aspect: Queue Management",
            "languages_affected": f"English ({en_cnt}), French ({fr_cnt})",
        },
        {
            "id": "card_2",
            "priority": "Medium Priority",
            "priority_level": "medium",
            "department": "F&B",
            "dept_head": "Chef Jerome Charles",
            "recommendation": "Extend late-night room service menu options to support late arrivals.",
            "impact": "Estimated +0.14 overall lift | Root Aspect: Dining Variety",
            "languages_affected": f"English ({en_cnt-2}), French ({fr_cnt})",
        },
        {
            "id": "card_3",
            "priority": "Low Priority",
            "priority_level": "low",
            "department": "Housekeeping",
            "dept_head": "Marie-Therese Blanc",
            "recommendation": "Review standardization for room amenity restocks.",
            "impact": "Estimated +0.05 overall lift | Root Aspect: Room Comfort",
            "languages_affected": f"French ({fr_cnt}), English ({en_cnt})",
        },
    ]

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("## HotelPulse AI")
    st.markdown("<hr style='border-color: #2D3748;'>", unsafe_allow_html=True)

    st.markdown("### Property Filters")
    
    selected_stars = st.multiselect(
        "Filter by Star Rating",
        options=[3, 4, 5],
        default=[3, 4, 5],
        format_func=lambda x: f"{x} Stars",
    )

    available_brands = HOTELS_METADATA["brand"].unique().tolist()
    selected_brands = st.multiselect(
        "Filter by Brand Family",
        options=available_brands,
        default=available_brands,
    )

    filtered_hotels_df = HOTELS_METADATA[
        (HOTELS_METADATA["stars"].isin(selected_stars)) &
        (HOTELS_METADATA["brand"].isin(selected_brands))
    ]

    if filtered_hotels_df.empty:
        st.error("No properties match your filters.")
        st.stop()

    hotel_names_list = filtered_hotels_df["name"].tolist()
    
    # Ensure current selected hotel is valid based on filters
    if st.session_state.selected_hotel not in hotel_names_list:
        st.session_state.selected_hotel = hotel_names_list[0]

    # By using the session_state 'key' directly here, we bind this UI element to the State variable.
    # This prevents the UI from overriding our map selection on reload!
    st.selectbox(
        "Select Property Details",
        options=hotel_names_list,
        key="selected_hotel"
    )

    st.markdown("<hr style='border-color: #2D3748;'>", unsafe_allow_html=True)

    selected_date_range = st.selectbox(
        "Date Range Window",
        options=["Last 30 Days", "Q3 2026", "Full Year 2026"],
        index=0,
    )

    today = datetime(2026, 10, 27).date()
    if selected_date_range == "Last 30 Days":
        start_date = today - timedelta(days=30)
        end_date = today
    elif selected_date_range == "Q3 2026":
        start_date = datetime(2026, 7, 1).date()
        end_date = datetime(2026, 9, 30).date()
    else:
        start_date = datetime(2026, 1, 1).date()
        end_date = today

# ==========================================
# DATA PROCESSING
# ==========================================
selected_hotel = st.session_state.selected_hotel
raw_df = generate_synthetic_review_dataset(selected_hotel)
filtered_df = raw_df[
    (raw_df["Date"] >= start_date) & (raw_df["Date"] <= end_date)
]

total_reviews_count = len(filtered_df)
avg_score = filtered_df["Rating"].mean() if total_reviews_count > 0 else 0.0
negative_alerts_count = len(filtered_df[filtered_df["Sentiment"] == "Negative"])
actions = get_hotel_actions(selected_hotel, filtered_df)

# ==========================================
# MAIN LAYOUT
# ==========================================
st.title("HotelPulse AI: Operations & Sentiment Engine")
st.markdown(
    f"<span style='color:#94A3B8;'>Selected Property:</span> <strong>{selected_hotel}</strong> &nbsp;|&nbsp; "
    f"<span style='color:#94A3B8;'>Window:</span> <strong>{start_date} to {end_date}</strong>",
    unsafe_allow_html=True
)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.15, 0.85])

# ------------------------------------------
# LEFT COLUMN: KPI CARDS & DASHBOARD
# ------------------------------------------
with col_left:
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

    with kpi_col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Satisfaction Score</div>
                <div class="kpi-value">{avg_score:.2f} / 5.0</div>
                <div class="kpi-subtext-positive">Trend Positive</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Review Volume</div>
                <div class="kpi-value">{total_reviews_count}</div>
                <div class="kpi-subtext-neutral">Total captured records</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class="kpi-card-alert">
                <div class="kpi-title" style="color: #FDA4AF;">Urgent Alerts</div>
                <div class="kpi-alert-value">{negative_alerts_count} Negative Mentions</div>
                <div class="kpi-alert-subtext">Action Required</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Action Matrix", "Department Ratings"])

    with tab1:
        st.subheader("Priority Actions")
        hotel_states = st.session_state.action_states[selected_hotel]
        
        for idx, item in enumerate(actions):
            card_id = item["id"]
            current_state = hotel_states[card_id]["status"]
            assigned_person = hotel_states[card_id]["assigned_to"]

            border_class = "action-addressed" if current_state == "Addressed" else f"action-{item['priority_level']}"
            priority_badge_class = f"badge-{item['priority_level']}"
            
            status_text = "Completed" if current_state == "Addressed" else ("Assigned" if assigned_person else "Open")

            st.markdown(
                f"""
                <div class="action-card {border_class}">
                    <div>
                        <span class="badge {priority_badge_class}">{item["priority"]}</span>
                        <span class="badge badge-dept">{item["department"]}</span>
                        <span style="font-size: 0.8rem; color: #94A3B8; float: right;">Status: {status_text}</span>
                    </div>
                    <div class="action-headline">Action {idx + 1}: {item["recommendation"]}</div>
                    <div class="action-meta">
                        <strong>Impact:</strong> {item["impact"]} <br/>
                        <strong>Languages Affected:</strong> {item["languages_affected"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_col1, btn_col2, _ = st.columns([1.5, 2.0, 3])
            with btn_col1:
                is_done = current_state == "Addressed"
                if st.button(
                    "Revert Status" if is_done else "Mark Addressed",
                    key=f"btn_done_{selected_hotel}_{card_id}",
                    use_container_width=True,
                ):
                    st.session_state.action_states[selected_hotel][card_id]["status"] = "Open" if is_done else "Addressed"
                    st.rerun()

            with btn_col2:
                if st.button(
                    "Assign Lead",
                    key=f"btn_assign_{selected_hotel}_{card_id}",
                    use_container_width=True,
                    disabled=(current_state == "Addressed"),
                ):
                    st.session_state.action_states[selected_hotel][card_id]["assigned_to"] = item["dept_head"]
                    st.rerun()

            st.markdown("<hr style='border-color: #1E293B;'>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Departmental Aspect Scores")
        if total_reviews_count > 0:
            aspect_df = filtered_df.groupby("Aspect")["Rating"].agg(["mean"]).reset_index()
            aspect_df.columns = ["Aspect", "Score"]
            aspect_df = aspect_df.sort_values(by="Score", ascending=True)

            fig_aspects = px.bar(
                aspect_df, x="Score", y="Aspect", orientation="h", text=aspect_df["Score"].round(2),
                color="Score",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                title="Computed Aspect Ratings (1-5 Scale)"
            )
            fig_aspects.update_layout(
                xaxis=dict(range=[0, 5.5]), 
                height=350, 
                margin=dict(l=10, r=10, t=35, b=10),
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_aspects, use_container_width=True)

# ------------------------------------------
# RIGHT COLUMN: MAP PIN CLICK LOADS HOTEL REVIEWS PAGE
# ------------------------------------------
with col_right:
    st.subheader("Interactive Map Switcher")
    st.caption("Select any hotel pin to analyze its operational dashboard.")

    # Distinct rendering for active selection vs secondary pins
    map_hotels_df = filtered_hotels_df.copy()
    map_hotels_df["is_selected"] = map_hotels_df["name"] == selected_hotel
    map_hotels_df["radius"] = map_hotels_df["is_selected"].apply(lambda s: 450 if s else 200)
    map_hotels_df["render_color"] = map_hotels_df.apply(
        lambda r: [0, 229, 255] if r["is_selected"] else [71, 85, 105], axis=1 # Cyan for selected, Gray for unselected
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        map_hotels_df,
        id="hotel_pins",
        get_position=["lon", "lat"],
        get_color="render_color",
        get_radius="radius",
        pickable=True,
        opacity=0.9,
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
        get_line_color=[255, 255, 255],
        radius_min_pixels=8,
        radius_max_pixels=18,
    )

    selected_row = map_hotels_df[map_hotels_df["name"] == selected_hotel].iloc[0]
    view_state = pdk.ViewState(
        latitude=float(selected_row["lat"]),
        longitude=float(selected_row["lon"]),
        zoom=12.2,
        pitch=30,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Click to Load:\n{name}\nBrand: {brand} | {stars} Stars"},
        map_style="mapbox://styles/mapbox/dark-v11",
    )

    # Enable interactive object selection on click
    map_event = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")

    # Safe extraction of the clicked layer data
    if map_event and map_event.selection and map_event.selection.get("objects"):
        for layer_id, selected_rows in map_event.selection["objects"].items():
            if selected_rows:
                clicked_hotel = selected_rows[0].get("name")
                if clicked_hotel and clicked_hotel != st.session_state.selected_hotel:
                    st.session_state.selected_hotel = clicked_hotel
                    st.rerun()

    # Active Hotel Summary Card
    st.markdown(
        f"""
        <div style="background-color: #151E32; border: 1px solid #0066FF; border-radius: 8px; padding: 18px 20px; margin-top: 15px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Active Analysis Target</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin: 4px 0;">{selected_row['name']}</div>
            <div style="font-size: 0.9rem; color: #CBD5E1;">
                Brand: <strong>{selected_row['brand']}</strong> <br/> 
                Rating: <strong>{selected_row['stars']} Stars</strong> <br/>
                Segment: <strong>{selected_row['group']}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )