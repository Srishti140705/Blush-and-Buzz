from __future__ import annotations

import base64
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


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
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,500;0,600;1,400;1,500&family=DM+Sans:wght@400;500;600&display=swap');
    :root { --champagne:#F2E5C6; --sand:#F2D9A0; --burgundy:#75162D; --maroon:#560B18; --wine:#3B010B; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--wine); }
    .stApp { background:var(--champagne); }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stSidebar"] { background:var(--wine); border-right:1px solid var(--sand); }
    [data-testid="stSidebar"] * { color:var(--champagne); }
    [data-testid="stSidebar"] .stRadio label { padding:.35rem .5rem; border-bottom:1px solid rgba(242,217,160,.25); }
    [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child { border-color:var(--sand); }
    .block-container { max-width:1500px; padding-top:2rem; padding-bottom:4rem; }
    h1,h2,h3,.editorial-title,.brand-wordmark { font-family:'Bodoni Moda',serif !important; font-weight:500 !important; letter-spacing:-.045em; }
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
    .editorial-band strong { font:italic 1.35rem 'Bodoni Moda',serif; }
    .section-intro { margin:2.5rem 0 1.5rem; }
    .section-intro p { max-width:43rem; }
    .creator-card { min-height:23rem; height:23rem; display:grid; grid-template-rows:13rem 1fr; overflow:hidden; background:var(--sand); border:1px solid rgba(117,22,45,.45); }
    .creator-card img { width:100%; height:100%; display:block; object-fit:cover; object-position:center 28%; }
    .creator-body { min-height:0; padding:.8rem .95rem .9rem; display:flex; flex-direction:column; }
    .creator-body .meta { display:flex; justify-content:space-between; color:var(--burgundy); font-size:.58rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; }
    .creator-body h3 { margin:.45rem 0 .3rem; font-size:1.75rem; }
    .creator-body p { margin:auto 0 0; font-size:.72rem; }
    div[data-testid="stHorizontalBlock"]:has(.creator-card) { align-items:stretch; }
    div[data-testid="stHorizontalBlock"]:has(.creator-card) > div[data-testid="stColumn"] { display:flex; flex-direction:column; }
    div[data-testid="stHorizontalBlock"]:has(.creator-card) > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] { height:100%; }
    div[data-testid="stHorizontalBlock"]:has(.creator-card) > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has([data-testid="stButton"]) { margin-top:auto; }
    .st-key-creator_spotlight .section-intro { margin:1rem 0 .8rem; }
    .st-key-creator_spotlight .section-intro .eyebrow { margin-bottom:.45rem; }
    .st-key-creator_spotlight .section-intro h2 { margin:0 0 .45rem; font-size:clamp(2.6rem,3.7vw,3.9rem) !important; line-height:.9 !important; }
    .st-key-creator_spotlight .section-intro p { margin:0; max-width:50rem; font-size:.88rem; line-height:1.45; }
    .st-key-creator_spotlight .creator-card { min-height:18.5rem; height:18.5rem; grid-template-rows:10.5rem 1fr; }
    .st-key-creator_spotlight .creator-body { padding:.7rem .9rem .8rem; }
    .st-key-creator_spotlight .creator-body .meta { font-size:.5rem; }
    .st-key-creator_spotlight .creator-body h3 { margin:.35rem 0 .25rem; font-size:1.55rem; }
    .st-key-creator_spotlight .creator-body p { font-size:.63rem; }
    .st-key-creator_spotlight [data-testid="stVerticalBlock"] { gap:.6rem; }
    .st-key-creator_spotlight [data-testid="stExpander"] summary { min-height:2.25rem; padding:.35rem .7rem; }
    [data-testid="stExpander"]:has(.profile-note) { font-family:'Bodoni Moda',serif !important; }
    [data-testid="stExpander"]:has(.profile-note) details[open] { min-height:13.25rem; }
    [data-testid="stExpander"]:has(.profile-note) summary p { font-size:1rem; letter-spacing:-.02em; }
    [data-testid="stExpander"]:has(.profile-note) [data-testid="stMarkdownContainer"] p { font-size:1rem; line-height:1.4; letter-spacing:-.02em; }
    .st-key-creator_spotlight .stButton > button { min-height:2.35rem; padding:.45rem .75rem; font-size:.68rem; }
    .st-key-creator_spotlight .disclosure { margin:.7rem 0 0; font-size:.56rem; }
    .profile-note { min-height:4.05em; margin:.35rem 0 .1rem; color:var(--burgundy); font:italic 500 1rem/1.35 'Bodoni Moda',serif; letter-spacing:-.015em; }
    @keyframes creator-section-reveal { from { opacity:0; transform:translateY(3.5rem); } to { opacity:1; transform:translateY(0); } }
    @supports (animation-timeline:view()) {
      .st-key-creator_spotlight { animation:creator-section-reveal 1s cubic-bezier(.2,.7,.2,1) both; animation-timeline:view(block); animation-range:entry 8% entry 65%; }
    }
    .disclosure { margin:1.5rem 0; color:var(--burgundy); font-size:.65rem; letter-spacing:.08em; text-transform:uppercase; }
    .metric-card { min-height:9rem; padding:1.2rem; display:flex; flex-direction:column; justify-content:space-between; color:var(--champagne); background:var(--maroon); border:1px solid var(--sand); }
    .metric-card span { color:var(--sand); font-size:.6rem; letter-spacing:.12em; text-transform:uppercase; }
    .metric-card strong { font:500 clamp(2rem,4vw,3.5rem)/1 'Bodoni Moda',serif; }
    .analytics-heading h1 { margin:.15rem 0 .35rem; font-size:clamp(3.5rem,5.5vw,5.8rem) !important; }
    .analytics-heading .page-lede { margin:.15rem 0 1.2rem; }
    .analytics-note { padding:.8rem 1rem; background:rgba(242,217,160,.48); border-radius:12px; color:var(--maroon); font-size:.72rem; line-height:1.45; }
    .analytics-insight { min-height:3.7rem; margin-top:.35rem; padding:.7rem .8rem; border-radius:10px; background:rgba(242,217,160,.55); color:var(--maroon); font-size:.69rem; line-height:1.45; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color:rgba(117,22,45,.12) !important; border-radius:14px !important; background:rgba(255,250,240,.42); box-shadow:0 8px 22px rgba(59,1,11,.06); }
    [data-testid="stVerticalBlockBorderWrapper"] h3 { margin:.05rem 0 !important; font-size:1.35rem !important; letter-spacing:-.02em; }
    .match-card { margin-bottom:1rem; padding:1.1rem; background:var(--sand); border-left:4px solid var(--burgundy); }
    .match-card h3 { margin:.2rem 0; font-size:2rem; }
    .match-score { color:var(--burgundy); font:600 .65rem 'DM Sans',sans-serif; letter-spacing:.1em; text-transform:uppercase; }
    .pipeline-step { min-height:9rem; padding:1rem; color:var(--champagne); background:var(--burgundy); border-top:2px solid var(--sand); }
    .pipeline-step span { color:var(--sand); font:italic 1.1rem 'Bodoni Moda',serif; }
    .pipeline-step h3 { margin:.6rem 0; color:var(--champagne) !important; font-size:1.65rem; }
    .pipeline-step p { font-size:.72rem; }
    .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button { color:var(--champagne); background:var(--burgundy); border:1px solid var(--burgundy); border-radius:0; font-weight:600; letter-spacing:.07em; text-transform:uppercase; }
    .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { color:var(--sand); background:var(--wine); border-color:var(--wine); }
    [data-baseweb="select"] > div, .stTextInput input, .stNumberInput input { background:var(--champagne); border-color:rgba(117,22,45,.45); border-radius:0; }
    [data-testid="stExpander"] { background:rgba(242,217,160,.45); border:1px solid rgba(117,22,45,.35); border-radius:0; }
    [data-testid="stDataFrame"] { border:1px solid var(--burgundy); }
    hr { border-color:rgba(117,22,45,.35); }
    @media (max-width:800px) { .block-container{padding-left:1rem;padding-right:1rem}.hero-panel{min-height:0}.creator-card,.st-key-creator_spotlight .creator-card{min-height:0;height:auto;grid-template-rows:20rem auto}.editorial-band{flex-direction:column;gap:.4rem} }
    @media (prefers-reduced-motion:reduce) { .st-key-creator_spotlight { animation:none !important; opacity:1; transform:none; } }
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
        profile_notes = {
            1: "Luminous makeup stories with a warm, editorial finish.",
            2: "Calm, ingredient-led skincare told with everyday ease.",
            3: "Soft-glam artistry shaped by romantic visual storytelling.",
            4: "Gentle barrier-care rituals made clear, comforting, and approachable.",
            5: "Polished luxury beauty framed through cinematic detail and modern glamour.",
            6: "Bold color, precise technique, and celebratory makeup with high-energy charm.",
            7: "Thoughtful glow routines balancing clinical insight with sensorial calm.",
            8: "Beauty, style, and daily rituals woven into an effortlessly personal world.",
            9: "Refined fragrance and beauty edits with a distinctly editorial point of view.",
            10: "Fresh, budget-conscious skincare guidance grounded in consistency and care.",
        }
        note = profile_notes[int(creator["creator_id"])]
        st.markdown(f'<p class="profile-note">{note}</p>', unsafe_allow_html=True)
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
        st.markdown("<br><small>Demo creator profiles • Analytics based on historical data</small>", unsafe_allow_html=True)
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
    with st.container(key="creator_spotlight"):
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
    st.markdown('<section class="analytics-heading"><div class="eyebrow">Analytics studio</div><h1>The Insight <em>Edit.</em></h1><p class="page-lede">Explore influencer trends, audience reach, and engagement patterns through meaningful historical data.</p></section>', unsafe_allow_html=True)
    frame = load_analytics()
    valid_followers = frame[frame.followers.notna() & (frame.followers >= 0)]
    valid_engagement = frame[frame.engagement_rate.notna() & frame.engagement_rate.between(0, 100)].copy()
    category_counts = frame.category_1.value_counts()
    metrics = [
        ("Total creators", f"{len(frame):,}"),
        ("Average followers", compact_number(valid_followers.followers.mean())),
        ("Average engagement", f"{valid_engagement.engagement_rate.mean():.2f}%"),
        ("Most represented category", category_counts.index[0]),
    ]
    columns = st.columns(4, gap="small")
    for column, (label, value) in zip(columns, metrics):
        column.markdown(f'<div class="metric-card"><span>{label}</span><strong>{value}</strong></div>', unsafe_allow_html=True)

    chart_font = dict(family="DM Sans", color=PALETTE["wine"], size=11)
    chart_layout = dict(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=chart_font,
        margin=dict(l=55, r=35, t=35, b=60),
        hoverlabel=dict(bgcolor=PALETTE["champagne"], font_color=PALETTE["wine"]),
    )
    grid_color = "rgba(117,22,45,.12)"
    rose_scale = [PALETTE["maroon"], PALETTE["burgundy"], "#A73C55", "#C97582", "#E4AAA5", PALETTE["sand"]]

    st.markdown('<div class="analytics-note"><strong>Historical data note:</strong> This dashboard uses a cleaned public Instagram influencer dataset. Creator records here are historical and separate from the fictional demo profiles.</div>', unsafe_allow_html=True)
    st.write("")

    # 1. Category distribution
    top_six_counts = category_counts.head(6)
    other_count = category_counts.iloc[6:].sum()
    distribution = top_six_counts.rename_axis("category").reset_index(name="records")
    if other_count:
        distribution.loc[len(distribution)] = ["Other", other_count]
    fig_one = px.pie(distribution, names="category", values="records", hole=.55, color_discrete_sequence=rose_scale)
    fig_one.update_traces(textinfo="none", hovertemplate="%{label}<br>%{value:,} creators<br>%{percent}<extra></extra>")
    fig_one.add_annotation(text=f"<b>{len(frame):,}</b><br>records", x=.5, y=.5, showarrow=False, font=dict(family="Bodoni Moda", size=17, color=PALETTE["wine"]))
    fig_one.update_layout(**{**chart_layout, "margin": dict(l=15, r=15, t=15, b=80)}, legend=dict(orientation="h", y=-.12, x=.5, xanchor="center", font=dict(size=10), itemwidth=30))
    top_share = category_counts.iloc[0] / len(frame) * 100

    # 2. Followers and engagement by category
    combo_source = frame[frame.followers.notna() & (frame.followers >= 0) & frame.engagement_rate.between(0, 100)].copy()
    combo_source = combo_source[combo_source.category_1.isin(category_counts.head(6).index)]
    combo = combo_source.groupby("category_1", as_index=False).agg(avg_followers=("followers", "mean"), avg_engagement=("engagement_rate", "mean"))
    combo = combo.sort_values("avg_followers", ascending=False)
    combo["followers_m"] = combo.avg_followers / 1_000_000
    combo["display_category"] = combo.category_1.replace({"Cinema & Actors/actresses": "Cinema & Actors", "Sports with a ball": "Ball Sports", "Humor & Fun & Happiness": "Humor & Fun"})
    fig_two = make_subplots(specs=[[{"secondary_y": True}]])
    fig_two.add_trace(go.Bar(x=combo.display_category, y=combo.followers_m, customdata=combo.category_1, name="Avg followers (M)", marker_color=PALETTE["burgundy"], hovertemplate="%{customdata}<br>%{y:.2f}M followers<extra></extra>"), secondary_y=False)
    fig_two.add_trace(go.Scatter(x=combo.display_category, y=combo.avg_engagement, customdata=combo.category_1, name="Avg engagement (%)", mode="lines+markers", line=dict(color="#C9576B", width=2), marker=dict(size=7), hovertemplate="%{customdata}<br>%{y:.2f}% engagement<extra></extra>"), secondary_y=True)
    fig_two.update_layout(**{**chart_layout, "margin": dict(l=58, r=60, t=60, b=75)}, legend=dict(orientation="h", y=1.13, x=.5, xanchor="center", font=dict(size=10)))
    fig_two.update_xaxes(tickangle=-20, gridcolor="rgba(0,0,0,0)", tickfont=dict(color=PALETTE["wine"], size=10), automargin=True)
    fig_two.update_yaxes(title_text="Followers (millions)", gridcolor=grid_color, secondary_y=False)
    fig_two.update_yaxes(title_text="Engagement (%)", showgrid=False, secondary_y=True)

    # 3. Reach versus engagement
    scatter = frame[frame.followers.notna() & (frame.followers > 0) & frame.engagement_rate.between(0, 100)].copy()
    scatter["creator_label"] = scatter.display_name.fillna(scatter.username).fillna("Unknown creator")
    scatter["followers_label"] = scatter.followers.map(compact_number)
    fig_three = px.scatter(scatter, x="followers", y="engagement_rate", hover_name="creator_label", custom_data=["category_1", "followers_label"], log_x=True, color="category_1", color_discrete_sequence=rose_scale, labels={"followers": "Followers (log scale)", "engagement_rate": "Engagement rate (%)", "category_1": "Category"})
    fig_three.update_traces(marker=dict(size=5, opacity=.48, line=dict(width=.2, color=PALETTE["champagne"])), hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]}<br>%{customdata[1]} followers<br>%{y:.2f}% engagement<extra></extra>")
    fig_three.update_layout(**chart_layout, showlegend=False)
    fig_three.update_xaxes(gridcolor=grid_color, tickmode="array", tickvals=[10_000, 100_000, 1_000_000, 10_000_000, 100_000_000], ticktext=["10K", "100K", "1M", "10M", "100M"], automargin=True)
    fig_three.update_yaxes(gridcolor=grid_color)
    correlation = scatter[["followers", "engagement_rate"]].corr(method="spearman").iloc[0, 1]

    # 4. Engagement distribution
    fig_four = px.histogram(valid_engagement, x="engagement_rate", nbins=24, color_discrete_sequence=[PALETTE["burgundy"]], labels={"engagement_rate": "Engagement rate (%)", "count": "Creators"})
    fig_four.update_traces(hovertemplate="Engagement: %{x:.2f}%<br>Creators: %{y}<extra></extra>")
    fig_four.update_layout(**{**chart_layout, "margin": dict(l=65, r=35, t=35, b=65)}, bargap=.1, showlegend=False)
    fig_four.update_xaxes(gridcolor="rgba(0,0,0,0)", tickformat=".0f", automargin=True)
    fig_four.update_yaxes(title_text="Creators", gridcolor=grid_color, rangemode="tozero", automargin=True)
    median_engagement = valid_engagement.engagement_rate.median()

    # 5. Engagement heatmap
    follower_labels = ["<10K", "10K–100K", "100K–1M", "1M–10M", "10M+"]
    heat_source = frame[frame.followers.notna() & (frame.followers >= 0) & frame.engagement_rate.between(0, 100)].copy()
    heat_categories = category_counts[category_counts.index != "Unknown"].head(6).index
    heat_source = heat_source[heat_source.category_1.isin(heat_categories)]
    heat_source["follower_range"] = pd.cut(heat_source.followers, bins=[-1, 10_000, 100_000, 1_000_000, 10_000_000, float("inf")], labels=follower_labels, right=False)
    heat = heat_source.pivot_table(index="category_1", columns="follower_range", values="engagement_rate", aggfunc="mean", observed=False).reindex(columns=follower_labels)
    heat = heat.reindex(heat_categories)
    fig_five = go.Figure(go.Heatmap(z=heat.values, x=heat.columns, y=heat.index, colorscale=[[0, PALETTE["champagne"]], [.5, "#B85D6F"], [1, PALETTE["maroon"]]], colorbar=dict(title="%", thickness=12, len=.8), hoverongaps=False, hovertemplate="%{y}<br>%{x}<br>%{z:.2f}% engagement<extra></extra>"))
    fig_five.update_layout(**{**chart_layout, "height": 440, "margin": dict(l=150, r=55, t=35, b=70)})
    fig_five.update_xaxes(tickangle=0, automargin=True)
    fig_five.update_yaxes(automargin=True)
    heat_peak = heat.stack().idxmax() if heat.notna().any().any() else ("No category", "No range")

    # 6. Top ten creators
    top_ten = valid_engagement.copy()
    top_ten["creator_label"] = top_ten.display_name.fillna(top_ten.username).fillna("Unknown creator")
    top_ten = top_ten.nlargest(10, "engagement_rate").sort_values("engagement_rate")
    fig_six = px.bar(top_ten, x="engagement_rate", y="creator_label", orientation="h", text=top_ten.engagement_rate.map(lambda value: f"{value:.2f}%"), color="engagement_rate", color_continuous_scale=[[0, "#D99A9B"], [1, PALETTE["maroon"]]], labels={"engagement_rate": "Engagement rate (%)", "creator_label": ""})
    fig_six.update_traces(width=.62, textposition="outside", textfont=dict(color=PALETTE["wine"], size=11), cliponaxis=False, hovertemplate="<b>%{y}</b><br>%{x:.2f}% engagement<extra></extra>")
    fig_six.update_layout(**{**chart_layout, "margin": dict(l=175, r=70, t=35, b=60)}, coloraxis_showscale=False)
    fig_six.update_xaxes(gridcolor=grid_color, automargin=True)
    fig_six.update_yaxes(gridcolor="rgba(0,0,0,0)", automargin=True, tickfont=dict(color=PALETTE["wine"], size=11))

    panels = [
        ("Category Distribution", "Proportion of influencer records in each category", fig_one, f"{category_counts.index[0]} is the largest category, representing {top_share:.1f}% of all {len(frame):,} records."),
        ("Followers & Engagement by Category", "Average reach and engagement shown on separate scales", fig_two, f"{combo.iloc[0].category_1} has the highest average follower count; the engagement line uses its own percentage axis."),
        ("Reach vs. Engagement", "Follower count and engagement rate across valid records", fig_three, f"The Spearman relationship is {correlation:+.2f}; this describes association in the dataset, not causation."),
        ("Engagement Distribution", "Frequency of recorded engagement rates", fig_four, f"The median valid engagement rate is {median_engagement:.2f}% across {len(valid_engagement):,} records."),
        ("Engagement by Category & Follower Range", "Average engagement rate; blank cells have no valid observations", fig_five, f"The highest populated average occurs for {heat_peak[0]} in the {heat_peak[1]} follower range."),
        ("Top 10 Creators by Engagement", "Highest valid engagement rates in the historical dataset", fig_six, f"{top_ten.iloc[-1].creator_label} ranks first at {top_ten.iloc[-1].engagement_rate:.2f}% engagement."),
    ]
    for row_start in (0, 2, 4):
        panel_columns = st.columns(2, gap="medium")
        for panel_column, (title, subtitle, figure, insight) in zip(panel_columns, panels[row_start:row_start + 2]):
            with panel_column:
                with st.container(border=True):
                    st.markdown(f"### {title}")
                    st.caption(subtitle)
                    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
                    st.markdown(f'<div class="analytics-insight">{insight}</div>', unsafe_allow_html=True)
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
