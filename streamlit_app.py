from __future__ import annotations

import base64
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = BASE_DIR / "frontend" / "assets" / "images"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from matcher import find_matches  # noqa: E402
from scraper import scrape_quotes  # noqa: E402


st.set_page_config(
    page_title="B&B Studio | Blush & Buzz",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


PALETTE = {
    "champagne": "#F2E5C6",
    "sand": "#F2D9A0",
    "burgundy": "#75162D",
    "maroon": "#560B18",
    "wine": "#3B010B",
}


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=DM+Sans:wght@400;500;600&display=swap');
    :root { --champagne:#F2E5C6; --sand:#F2D9A0; --burgundy:#75162D; --maroon:#560B18; --wine:#3B010B; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--wine); }
    .stApp { background:var(--champagne); }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stSidebar"] { background:var(--wine); border-right:1px solid var(--sand); }
    [data-testid="stSidebar"] * { color:var(--champagne); }
    [data-testid="stSidebar"] .stRadio label { padding:.35rem .5rem; border-bottom:1px solid rgba(242,217,160,.25); }
    [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child { border-color:var(--sand); }
    .block-container { max-width:1500px; padding-top:2rem; padding-bottom:4rem; }
    h1,h2,h3,.editorial-title,.brand-wordmark { font-family:'Cormorant Garamond',serif !important; font-weight:500 !important; letter-spacing:-.035em; }
    h1 { color:var(--wine) !important; font-size:clamp(3.6rem,7vw,7rem) !important; line-height:.9 !important; }
    h2 { color:var(--wine) !important; font-size:clamp(2.5rem,4.5vw,4.8rem) !important; line-height:.95 !important; }
    h3 { color:var(--wine) !important; }
    .brand-wordmark { color:var(--sand); font-size:2.3rem; line-height:.9; }
    .brand-subtitle,.eyebrow { font:600 .65rem/1.4 'DM Sans',sans-serif; letter-spacing:.18em; text-transform:uppercase; }
    .brand-subtitle { margin-top:.45rem; color:var(--champagne); }
    .eyebrow { margin-bottom:1rem; color:var(--burgundy); }
    .eyebrow-light { color:var(--sand); }
    .page-lede { max-width:46rem; color:var(--maroon); font-size:1.05rem; line-height:1.7; }
    .hero-panel { min-height:31rem; padding:clamp(2rem,5vw,5rem); display:flex; flex-direction:column; justify-content:center; background:var(--sand); border:1px solid var(--burgundy); }
    .hero-panel h1 { margin:.3rem 0 1.4rem; }
    .hero-panel em { font-weight:400; }
    .editorial-band { margin:1.5rem 0 3rem; padding:1.25rem 1.5rem; display:flex; justify-content:space-between; gap:2rem; color:var(--champagne); background:var(--wine); }
    .editorial-band strong { font:italic 1.35rem 'Cormorant Garamond',serif; }
    .section-intro { margin:2.5rem 0 1.5rem; }
    .section-intro p { max-width:43rem; }
    .creator-card { height:100%; overflow:hidden; background:var(--sand); border:1px solid rgba(117,22,45,.45); }
    .creator-card img { width:100%; height:17rem; display:block; object-fit:cover; object-position:center 28%; }
    .creator-body { padding:1rem 1.1rem 1.15rem; }
    .creator-body .meta { display:flex; justify-content:space-between; color:var(--burgundy); font-size:.58rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; }
    .creator-body h3 { margin:.55rem 0 .35rem; font-size:2rem; }
    .creator-body p { margin:0; font-size:.72rem; }
    .disclosure { margin:1.5rem 0; color:var(--burgundy); font-size:.65rem; letter-spacing:.08em; text-transform:uppercase; }
    .metric-card { min-height:9rem; padding:1.2rem; display:flex; flex-direction:column; justify-content:space-between; color:var(--champagne); background:var(--maroon); border:1px solid var(--sand); }
    .metric-card span { color:var(--sand); font-size:.6rem; letter-spacing:.12em; text-transform:uppercase; }
    .metric-card strong { font:500 clamp(2rem,4vw,3.5rem)/1 'Cormorant Garamond',serif; }
    .match-card { margin-bottom:1rem; padding:1.1rem; background:var(--sand); border-left:4px solid var(--burgundy); }
    .match-card h3 { margin:.2rem 0; font-size:2rem; }
    .match-score { color:var(--burgundy); font:600 .65rem 'DM Sans',sans-serif; letter-spacing:.1em; text-transform:uppercase; }
    .pipeline-step { min-height:9rem; padding:1rem; color:var(--champagne); background:var(--burgundy); border-top:2px solid var(--sand); }
    .pipeline-step span { color:var(--sand); font:italic 1.1rem 'Cormorant Garamond',serif; }
    .pipeline-step h3 { margin:.6rem 0; color:var(--champagne) !important; font-size:1.65rem; }
    .pipeline-step p { font-size:.72rem; }
    .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button { color:var(--champagne); background:var(--burgundy); border:1px solid var(--burgundy); border-radius:0; font-weight:600; letter-spacing:.07em; text-transform:uppercase; }
    .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { color:var(--sand); background:var(--wine); border-color:var(--wine); }
    [data-baseweb="select"] > div, .stTextInput input, .stNumberInput input { background:var(--champagne); border-color:rgba(117,22,45,.45); border-radius:0; }
    [data-testid="stExpander"] { background:rgba(242,217,160,.45); border:1px solid rgba(117,22,45,.35); border-radius:0; }
    [data-testid="stDataFrame"] { border:1px solid var(--burgundy); }
    hr { border-color:rgba(117,22,45,.35); }
    @media (max-width:800px) { .block-container{padding-left:1rem;padding-right:1rem}.hero-panel{min-height:0}.creator-card img{height:20rem}.editorial-band{flex-direction:column;gap:.4rem} }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_creators() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "demo" / "beauty_creators.csv")


@st.cache_data
def load_analytics() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "processed" / "instagram_cleaned.csv")
    frame["followers"] = pd.to_numeric(frame["followers"], errors="coerce")
    frame["engagement_rate"] = pd.to_numeric(frame["engagement_rate"], errors="coerce")
    frame["category_1"] = frame["category_1"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    return frame


@st.cache_data
def image_uri(path: str) -> str:
    image_path = Path(path)
    mime = "image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    return f"data:{mime};base64,{base64.b64encode(image_path.read_bytes()).decode()}"


def compact_number(value: float) -> str:
    value = float(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M".replace(".0M", "M")
    if value >= 1_000:
        return f"{value / 1_000:.1f}K".replace(".0K", "K")
    return f"{value:,.0f}"


def creator_card(creator: pd.Series, key_prefix: str) -> None:
    portrait = IMAGE_DIR / str(creator["image"])
    if portrait.exists():
        portrait_html = f'<img src="{image_uri(str(portrait))}" alt="AI-generated fictional portrait of {creator["name"]}">'
    else:
        portrait_html = '<div style="height:17rem;display:grid;place-items:center;background:#560B18;color:#F2D9A0">Portrait unavailable</div>'
    st.markdown(
        f"""
        <article class="creator-card">{portrait_html}<div class="creator-body">
        <div class="meta"><span>{creator['niche']}</span><span>{int(creator['creator_id']):02d}</span></div>
        <h3>{creator['name']}</h3><p>{compact_number(creator['followers'])} followers · {creator['engagement_rate']:.1f}% engagement</p>
        </div></article>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("View profile"):
        st.write(f"**Audience:** {creator['audience']}  ·  **Location:** {creator['location']}")
        st.write(f"**Indicative demo fee:** ₹{int(creator['estimated_fee']):,}")
        st.caption("Fictional persona and demonstration metrics.")
    shortlist = st.session_state.setdefault("shortlist", [])
    creator_id = int(creator["creator_id"])
    label = "Remove from shortlist" if creator_id in shortlist else "Add to shortlist"
    if st.button(label, key=f"{key_prefix}_{creator_id}", width="stretch"):
        if creator_id in shortlist:
            shortlist.remove(creator_id)
        else:
            shortlist.append(creator_id)
        st.rerun()


def set_page(name: str) -> None:
    st.session_state.page_nav = name


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="brand-wordmark">B&amp;B Studio</div><div class="brand-subtitle">Blush &amp; Buzz</div>', unsafe_allow_html=True)
        st.markdown("---")
        selected = st.radio("Studio navigation", ["Home", "Creators", "Matchmaker", "Analytics", "Data Atelier"], key="page_nav", label_visibility="collapsed")
        st.markdown("---")
        shortlist = st.session_state.setdefault("shortlist", [])
        st.markdown(f'<div class="eyebrow eyebrow-light">Shortlist · {len(shortlist)}</div>', unsafe_allow_html=True)
        if shortlist:
            creators = load_creators()
            for creator_id in shortlist:
                row = creators[creators.creator_id == creator_id]
                if not row.empty:
                    st.caption(f"✦ {row.iloc[0]['name']}")
        else:
            st.caption("Save creators while you explore.")
        st.markdown("<br><small>Fictional creator data · Historical analytics clearly labeled</small>", unsafe_allow_html=True)
    return selected


def render_home() -> None:
    left, right = st.columns([1.05, 0.95], gap="small")
    with left:
        st.markdown(
            """<section class="hero-panel"><div class="eyebrow">A new language of beauty influence</div>
            <h1>Where beauty<br><em>meets influence.</em></h1>
            <p class="page-lede">Discover inspiring creators, explore meaningful insights, and find the perfect voice for your next campaign.</p></section>""",
            unsafe_allow_html=True,
        )
        action_one, action_two = st.columns(2)
        action_one.button("Explore creators", on_click=set_page, args=("Creators",), width="stretch")
        action_two.button("Find your match", on_click=set_page, args=("Matchmaker",), width="stretch")
    with right:
        st.image(str(IMAGE_DIR / "hero_beauty_still_life.jpg"), width="stretch")

    st.markdown('<div class="editorial-band"><strong>Beauty is personal.</strong><strong>Influence should feel that way, too.</strong><span>Curated connections, grounded in real insight.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-intro"><div class="eyebrow">Creator spotlight</div><h2>Faces shaping <em>what comes next.</em></h2><p>A considered selection of beauty voices with distinct points of view and genuinely engaged communities.</p></div>', unsafe_allow_html=True)
    creators = load_creators().head(3)
    columns = st.columns(3, gap="medium")
    for column, (_, creator) in zip(columns, creators.iterrows()):
        with column:
            creator_card(creator, "home")
    st.markdown('<p class="disclosure">All creator profiles and portraits shown are fictional and AI-generated.</p>', unsafe_allow_html=True)


def render_creators() -> None:
    st.markdown('<div class="eyebrow">The creator edit</div><h1>Distinct voices.<br><em>Beautiful perspectives.</em></h1><p class="page-lede">Discover beauty creators whose individuality, creativity, and communities make every collaboration meaningful.</p>', unsafe_allow_html=True)
    creators = load_creators()
    search_col, niche_col, sort_col = st.columns([1.4, 1, 1])
    search = search_col.text_input("Search by creator name")
    niches = ["All categories", *sorted(creators.niche.unique())]
    niche = niche_col.selectbox("Beauty category", niches)
    sort = sort_col.selectbox("Sort", ["Featured", "Followers: high to low", "Followers: low to high", "Engagement: high to low"])
    filtered = creators[creators.name.str.contains(search, case=False, na=False)]
    if niche != "All categories":
        filtered = filtered[filtered.niche == niche]
    if sort == "Followers: high to low": filtered = filtered.sort_values("followers", ascending=False)
    if sort == "Followers: low to high": filtered = filtered.sort_values("followers")
    if sort == "Engagement: high to low": filtered = filtered.sort_values("engagement_rate", ascending=False)
    st.markdown(f'<p class="disclosure">{len(filtered)} fictional demonstration profiles</p>', unsafe_allow_html=True)
    if filtered.empty:
        st.info("No creators match those filters. Try another name or category.")
        return
    rows = list(filtered.iterrows())
    for start in range(0, len(rows), 3):
        columns = st.columns(3, gap="medium")
        for column, (_, creator) in zip(columns, rows[start:start + 3]):
            with column:
                creator_card(creator, "directory")


def render_matchmaker() -> None:
    st.markdown('<div class="eyebrow">Campaign matchmaker</div><h1>Find your<br><em>perfect match.</em></h1><p class="page-lede">Tell us about your campaign and discover creators whose style and audience align with your vision.</p>', unsafe_allow_html=True)
    with st.form("campaign_brief"):
        st.subheader("Campaign brief")
        campaign_name = st.text_input("Campaign or product name", placeholder="e.g. Velvet Lip Launch")
        col1, col2 = st.columns(2)
        niche = col1.selectbox("Beauty category", ["Makeup", "Skincare", "Luxury Beauty", "Lifestyle"])
        budget = col2.number_input("Campaign budget (₹)", min_value=1, value=30000, step=1000)
        col3, col4 = st.columns(2)
        audience = col3.selectbox("Target audience", ["18-24", "25-34"])
        location = col4.selectbox("Target location", ["Any location", "India", "UK", "USA", "Singapore"])
        goal = st.selectbox("Campaign goal", ["Awareness", "Engagement", "Conversions"])
        submitted = st.form_submit_button("Find my match", width="stretch")
    st.caption("Rankings use category, audience, engagement, location, and demonstration fee data. Campaign goal is context only and is not scored.")
    if submitted:
        if not campaign_name.strip():
            st.warning("Add a campaign or product name to complete the brief.")
            return
        matches = find_matches(niche=niche, budget=budget, audience=audience, location=None if location == "Any location" else location)
        if not matches:
            st.info("No creators fit this budget. Increase the budget or broaden the brief.")
            return
        st.markdown(f'<div class="section-intro"><div class="eyebrow">Ranked recommendations</div><h2>Strongest connections for <em>{campaign_name}</em>.</h2></div>', unsafe_allow_html=True)
        for match in matches[:5]:
            st.markdown(f'<article class="match-card"><div class="match-score">{match["match_score"]:.0f}% match · {match["niche"]}</div><h3>{match["name"]}</h3><p>{compact_number(match["followers"])} followers · {match["engagement_rate"]:.1f}% engagement</p><p>{" · ".join(match["reasons"])}</p></article>', unsafe_allow_html=True)


def render_analytics() -> None:
    st.markdown('<div class="eyebrow">Analytics studio</div><h1>The Insight <em>Edit.</em></h1><p class="page-lede">Explore influencer trends, audience reach, and engagement patterns through meaningful historical data.</p>', unsafe_allow_html=True)
    frame = load_analytics()
    valid_engagement = frame[frame.engagement_rate.notna() & frame.engagement_rate.between(0, 100)]
    category_counts = frame.category_1.value_counts().head(10)
    metrics = [
        ("Records", f"{len(frame):,}"),
        ("Average followers", compact_number(frame.followers.mean())),
        ("Average engagement", f"{valid_engagement.engagement_rate.mean():.2f}%"),
        ("Leading category", category_counts.index[0]),
    ]
    columns = st.columns(4)
    for column, (label, value) in zip(columns, metrics):
        column.markdown(f'<div class="metric-card"><span>{label}</span><strong>{value}</strong></div>', unsafe_allow_html=True)
    st.markdown("### Category landscape")
    distribution = category_counts.rename_axis("category").reset_index(name="records")
    fig_one = px.bar(distribution, x="category", y="records", color_discrete_sequence=[PALETTE["burgundy"]])
    fig_one.update_layout(paper_bgcolor=PALETTE["champagne"], plot_bgcolor=PALETTE["champagne"], font_color=PALETTE["wine"], xaxis_title="", margin=dict(l=20, r=20, t=20, b=80))
    st.plotly_chart(fig_one, width="stretch")
    left, right = st.columns(2)
    grouped = valid_engagement.groupby("category_1").engagement_rate.agg(["mean", "count"]).query("count >= 3").nlargest(10, "mean").sort_values("mean").reset_index()
    fig_two = px.bar(grouped, x="mean", y="category_1", orientation="h", color_discrete_sequence=[PALETTE["maroon"]], labels={"mean": "Average engagement (%)", "category_1": ""})
    fig_two.update_layout(paper_bgcolor=PALETTE["sand"], plot_bgcolor=PALETTE["sand"], font_color=PALETTE["wine"], margin=dict(l=20, r=20, t=20, b=30))
    left.markdown("### Engagement by category")
    left.plotly_chart(fig_two, width="stretch")
    scatter = frame[frame.followers.notna() & (frame.followers > 0) & frame.engagement_rate.notna() & frame.engagement_rate.between(0, 25)]
    if len(scatter) > 300: scatter = scatter.sample(300, random_state=42)
    fig_three = px.scatter(scatter, x="followers", y="engagement_rate", hover_name="display_name", color_discrete_sequence=[PALETTE["burgundy"]], log_x=True, labels={"followers": "Followers (log scale)", "engagement_rate": "Engagement rate (%)"})
    fig_three.update_layout(paper_bgcolor=PALETTE["sand"], plot_bgcolor=PALETTE["sand"], font_color=PALETTE["wine"], margin=dict(l=20, r=20, t=20, b=30))
    right.markdown("### Reach and response")
    right.plotly_chart(fig_three, width="stretch")
    st.markdown('<p class="disclosure">Historical Kaggle Instagram data, cleaned locally. Separate from the fictional creator directory and not presented as current market data.</p>', unsafe_allow_html=True)


def render_atelier() -> None:
    st.markdown('<div class="eyebrow">Extraction studio</div><h1>Data <em>Atelier.</em></h1><p class="page-lede">Explore how structured information is extracted, cleaned, and transformed into usable data.</p>', unsafe_allow_html=True)
    steps = [("01", "Retrieve", "Request public practice HTML with a bounded timeout."), ("02", "Parse", "Select quote, author, and tag elements with Beautiful Soup."), ("03", "Structure", "Normalize values into clean tabular records."), ("04", "Export", "Generate a portable CSV for further analysis.")]
    columns = st.columns(4)
    for column, (number, title, text) in zip(columns, steps):
        column.markdown(f'<div class="pipeline-step"><span>{number}</span><h3>{title}</h3><p>{text}</p></div>', unsafe_allow_html=True)
    st.markdown("### Public practice source: Quotes to Scrape")
    st.write("This bounded demonstration uses Requests and Beautiful Soup. It does not accept arbitrary URLs or bypass access controls.")
    if st.button("Run extraction", type="primary"):
        with st.spinner("Retrieving and parsing the source…"):
            try:
                st.session_state.extracted_records = scrape_quotes()
                st.success(f"Extraction complete: {len(st.session_state.extracted_records)} records parsed.")
            except Exception as exc:
                st.session_state.extracted_records = []
                st.error(f"Extraction failed honestly: {exc}")
    records = st.session_state.get("extracted_records", [])
    if records:
        data = pd.DataFrame(records)
        metric_col, note_col = st.columns([.25, .75])
        metric_col.metric("Records", len(data))
        note_col.info("Live scraping demo. This source is separate from the historical Kaggle analytics dataset.")
        st.dataframe(data.head(10), width="stretch", hide_index=True)
        st.download_button("Download CSV", data.to_csv(index=False).encode("utf-8"), "bb-studio-extracted-quotes.csv", "text/csv")


selected_page = render_sidebar()
if selected_page == "Home": render_home()
elif selected_page == "Creators": render_creators()
elif selected_page == "Matchmaker": render_matchmaker()
elif selected_page == "Analytics": render_analytics()
else: render_atelier()

st.markdown("---")
st.caption("B&B Studio · Blush & Buzz — a portfolio demonstration of Python, data workflows, recommendation logic, and responsive interface design.")
