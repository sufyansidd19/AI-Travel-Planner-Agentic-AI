import base64
import os
import uuid

import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from graph import app

st.set_page_config(
    page_title="Wanderly — AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def _asset(name: str) -> str:
    return os.path.join(ASSETS_DIR, name)


def _img_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


_CHIP_STYLES = {
    "gold": ("#ffb400", "rgba(255,180,0,0.10)"),
    "blue": ("#38bdf8", "rgba(56,189,248,0.10)"),
    "green": ("#34d399", "rgba(52,211,153,0.10)"),
}


def _chips(items, accent="gold"):
    color, bg = _CHIP_STYLES.get(accent, _CHIP_STYLES["gold"])
    parts = []
    for item in items:
        if not item:
            continue
        parts.append(
            f'<span style="display:inline-block;background:{bg};color:{color};'
            f'border:1px solid {color}55;border-radius:999px;'
            f'padding:4px 14px;margin:3px 6px 3px 0;font-size:0.85rem;font-weight:600;">{item}</span>'
        )
    return "".join(parts)


def _card_open(title, icon="🧭", extra_css=""):
    return f"""
    <div style="background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.12);
                border-radius:18px;padding:18px 20px;margin:8px 0 20px 0;{extra_css}">
      <div style="font-size:1.15rem;font-weight:700;color:#f8fafc;margin-bottom:6px;">{icon} {title}</div>
    """


def _card_close():
    return "</div>"


# ---------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(1100px 460px at 85% -8%, rgba(56,189,248,0.16), transparent 60%),
        radial-gradient(900px 460px at 0% 12%, rgba(255,180,0,0.10), transparent 55%),
        linear-gradient(180deg, #0b1220 0%, #0d1626 55%, #0b1220 100%);
    color: #e2e8f0;
}

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1526 0%, #0a0f1c 100%);
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #f8fafc; }

/* ---- Headings ---- */
h1, h2, h3, h4 { color: #f8fafc; letter-spacing: -0.4px; }
h1 { font-weight: 800; }

/* ---- Inputs ---- */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    border-radius: 14px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    color: #f1f5f9;
    font-size: 1rem;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #ffb400;
    box-shadow: 0 0 0 1px #ffb40055;
}

/* ---- Buttons ---- */
div.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.06);
    color: #e2e8f0;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    border-color: #ffb400;
    color: #ffb400;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #ffb400, #ff8a00) !important;
    color: #1a1204 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 24px rgba(255,180,0,0.35);
}
button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 30px rgba(255,180,0,0.45);
}

/* ---- Bordered containers / cards ---- */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
}

/* ---- Expanders ---- */
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    background: rgba(255,255,255,0.03);
}
[data-testid="stExpander"] summary { color: #f1f5f9; font-weight: 600; }

/* ---- Metrics ---- */
[data-testid="stMetricValue"] { color: #ffb400; font-weight: 800; }
[data-testid="stMetricLabel"] { color: #94a3b8; }

/* ---- Tabs ---- */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 8px; }
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 6px 18px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, #ffb400, #ff8a00) !important;
    color: #1a1204 !important;
    font-weight: 700;
}

hr { border-color: rgba(255,255,255,0.12); }
.stCaption, [data-testid="stCaptionContainer"] p { color: #94a3b8; }

/* ---- Hero ---- */
.hero {
    position: relative;
    border-radius: 22px;
    overflow: hidden;
    padding: 64px 56px;
    margin: 6px 0 22px 0;
    box-shadow: 0 24px 60px rgba(0,0,0,0.45);
    border: 1px solid rgba(255,255,255,0.10);
}
.hero-content { position: relative; z-index: 2; max-width: 760px; }
.hero-badge {
    display: inline-block;
    background: rgba(255,180,0,0.15);
    color: #ffd166;
    border: 1px solid rgba(255,180,0,0.5);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 18px;
}
.hero h1 {
    font-size: 3.1rem;
    line-height: 1.12;
    color: #ffffff;
    margin: 0 0 12px 0;
}
.hero h1 span { color: #ffb400; }
.hero p { font-size: 1.12rem; color: #dbe4f0; margin: 0; }

/* ---- Step cards ---- */
.step-card {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 20px 18px;
    height: 100%;
}
.step-icon {
    width: 46px; height: 46px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 12px;
}
.step-card h4 { margin: 0 0 6px 0; font-size: 1.05rem; }
.step-card p { margin: 0; color: #94a3b8; font-size: 0.9rem; line-height: 1.5; }

/* ---- Section label ---- */
.section-label {
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 2.5px;
    color: #ffb400;
    text-transform: uppercase;
    margin: 30px 0 4px 0;
}
"""

HERO_B64 = _img_b64(_asset("hero.jpg"))

HERO_HTML = f"""
<div class="hero"
     style="background-image:
        linear-gradient(100deg, rgba(8,13,25,0.92) 0%, rgba(8,13,25,0.55) 45%, rgba(8,13,25,0.25) 100%),
        url('data:image/jpeg;base64,{HERO_B64}');
        background-size: cover; background-position: center;">
  <div class="hero-content">
    <div class="hero-badge">&#9992;&#65039; AI-POWERED TRIP CO-PILOT</div>
    <h1>Plan your dream journey,<br><span>effortlessly.</span></h1>
    <p>Flights &#8226; Hotels &#8226; Weather &#8226; Budget &#8226; Itinerary &mdash; one smart multi-agent system that researches everything and drafts a plan you approve.</p>
  </div>
</div>
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Session state
# ---------------------------------------------------------------
if "thread_id" not in st.session_state:
    user_id = st.session_state.get("user_id", "demo_user")
    st.session_state.thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"

# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:6px 0 2px 0;">
          <div style="font-size:2.2rem;line-height:1;">&#9992;&#65039;</div>
          <div style="font-size:1.5rem;font-weight:800;color:#f8fafc;">Wanderly</div>
          <div style="font-size:0.8rem;color:#94a3b8;letter-spacing:1px;">TRAVEL PLANNER</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("Session")
    user_id = st.text_input("User ID", value=st.session_state.get("user_id", "demo_user"))

    if st.button("🔄 New Thread", use_container_width=True):
        st.session_state.thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        st.session_state.pop("waiting_for_approval", None)
        st.session_state.pop("latest_result", None)
        st.session_state.pop("query", None)
        st.rerun()

    st.caption(f"Thread: `{st.session_state.thread_id}`")

    st.divider()
    st.markdown(
        """
        <div style="font-size:0.78rem;color:#64748b;text-align:center;">
          Powered by LangGraph multi-agent<br/>system with live MCP data sources.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# Hero + how it works
# ---------------------------------------------------------------
st.markdown(HERO_HTML, unsafe_allow_html=True)

st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)
sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(
        f"""
        <div class="step-card">
          <div class="step-icon" style="background:rgba(56,189,248,0.15);">&#128269;</div>
          <h4>1. Describe</h4>
          <p>Tell the planner your destination, dates, style and budget in plain language.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with sc2:
    st.markdown(
        f"""
        <div class="step-card">
          <div class="step-icon" style="background:rgba(255,180,0,0.15);">&#129517;</div>
          <h4>2. Research</h4>
          <p>Specialist agents pull real flights, hotels, weather and budget insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with sc3:
    st.markdown(
        f"""
        <div class="step-card">
          <div class="step-icon" style="background:rgba(52,211,153,0.15);">&#128221;</div>
          <h4>3. Draft</h4>
          <p>A structured day-by-day itinerary is drafted for your review.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with sc4:
    st.markdown(
        f"""
        <div class="step-card">
          <div class="step-icon" style="background:rgba(244,114,182,0.15);">&#128640;</div>
          <h4>4. Approve</h4>
          <p>Approve the plan or give feedback — the system revises it for you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# Query input
# ---------------------------------------------------------------
st.markdown('<div class="section-label">Start planning</div>', unsafe_allow_html=True)
st.markdown("### ✍️ Describe your trip")

EXAMPLES = [
    ("🇯🇵 7-day Japan trip", "Plan a 7-day Japan trip under Rs. 2 lakh. I prefer budget hotels and no overnight flights."),
    ("🏖️ Goa beach weekend", "Plan a relaxed 3-day beach vacation in Goa on a budget. I love seafood and sunset views."),
    ("🏔️ Switzerland honeymoon", "Plan a 5-day honeymoon in Switzerland. Mid-range hotels, scenic train rides and romantic spots."),
    ("🗼 Paris for two", "Plan a 4-day Paris trip for two under €1500. Include museums, cafés and a Seine cruise."),
]

cols = st.columns(len(EXAMPLES))
for col, (label, text) in zip(cols, EXAMPLES):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.query = text
            st.rerun()

query = st.text_area(
    "Travel request",
    value=st.session_state.get("query", ""),
    placeholder="Plan a 7-day Japan trip under Rs. 2 lakh. I prefer budget hotels and no overnight flights.",
    height=120,
)

config = {"configurable": {"thread_id": st.session_state.thread_id}}

run_col, hint_col = st.columns([1, 3])
with run_col:
    run_pressed = st.button("🚀 Create Draft Plan", type="primary", use_container_width=True)
with hint_col:
    st.caption("The supervisor will route your request to the right specialists, then pause for your approval.")

if run_pressed:
    if not query.strip():
        st.warning("Please enter a travel request first.")
    else:
        st.session_state.query = query
        with st.spinner("🧭 Researching flights, hotels, weather & budget…"):
            result = app.invoke(
                {
                    "messages": [HumanMessage(content=query)],
                    "user_id": user_id,
                    "user_query": query,
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "budget_results": "",
                    "itinerary": "",
                    "final_response": "",
                    "llm_calls": 0,
                },
                config=config,
            )

        st.session_state.latest_result = result
        st.session_state.waiting_for_approval = "__interrupt__" in result
        st.rerun()

# ---------------------------------------------------------------
# Results
# ---------------------------------------------------------------
result = st.session_state.get("latest_result")

if not result:
    st.markdown(
        """
        <div style="text-align:center;padding:44px 20px;border:1px dashed rgba(255,255,255,0.18);
                    border-radius:20px;margin-top:14px;">
          <div style="font-size:3rem;">&#127757;</div>
          <div style="font-size:1.2rem;font-weight:700;color:#f8fafc;margin:8px 0 4px 0;">Your trip highlights will appear here</div>
          <div style="color:#94a3b8;">Describe your trip above and hit <b>Create Draft Plan</b> to get started.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# --- Supervisor summary ---
st.markdown('<div class="section-label">Step 1 — Plan routing</div>', unsafe_allow_html=True)
st.markdown(_card_open("Supervisor Plan", "🧭"), unsafe_allow_html=True)
st.markdown(result.get("supervisor_reasoning", ""))

constraints = result.get("trip_constraints") or {}
special = constraints.get("special_preferences") or []
if isinstance(special, str):
    special = [special]
constraint_items = [
    f"📍 {constraints['destination']}" if constraints.get("destination") else "",
    f"🏁 {constraints['origin']}" if constraints.get("origin") else "",
    f"⏱️ {constraints['duration']}" if constraints.get("duration") else "",
    f"💰 {constraints['budget']}" if constraints.get("budget") else "",
    f"🧳 {constraints['travel_style']}" if constraints.get("travel_style") else "",
] + [f"❤️ {p}" for p in special]
constraint_items = [x for x in constraint_items if x]

if constraint_items:
    st.markdown("**Trip snapshot**")
    st.markdown(_chips(constraint_items), unsafe_allow_html=True)

st.markdown(_card_close(), unsafe_allow_html=True)

# --- Agent results ---
st.markdown('<div class="section-label">Step 2 — Research results</div>', unsafe_allow_html=True)

AGENT_CARDS = [
    ("flight_agent", "✈️ Flights & Airfare", "flights.jpg"),
    ("hotel_agent", "🏨 Hotels & Stays", "hotels.jpg"),
    ("weather_agent", "⛅ Weather & Season", "weather.jpg"),
    ("budget_agent", "💰 Budget & Costs", "budget.jpg"),
]

row_top, row_bottom = st.columns(2)
for i, (key, title, img) in enumerate(AGENT_CARDS):
    col = row_top if i % 2 == 0 else row_bottom
    with col:
        content = result.get(f"{key.split('_')[0]}_results") or result.get(key) or ""
        if key == "flight_agent":
            content = result.get("flight_results", "")
        elif key == "hotel_agent":
            content = result.get("hotel_results", "")
        elif key == "weather_agent":
            content = result.get("weather_results", "")
        elif key == "budget_agent":
            content = result.get("budget_results", "")
        with st.container(border=True):
            st.image(_asset(img), use_container_width=True)
            st.markdown(f"### {title}")
            st.markdown(content if content else "_No results were produced._")

# --- Draft itinerary ---
st.markdown('<div class="section-label">Step 3 — Draft itinerary</div>', unsafe_allow_html=True)

draft = ""
if "__interrupt__" in result:
    draft = result["__interrupt__"][0].value.get("draft_itinerary", "")
else:
    draft = result.get("itinerary", "")

with st.container(border=True):
    st.image(_asset("itinerary.jpg"), use_container_width=True)
    st.markdown("### 🗺️ Draft Itinerary")
    st.markdown(draft if draft else "_No itinerary drafted yet._")

# ---------------------------------------------------------------
# Human approval
# ---------------------------------------------------------------
if st.session_state.get("waiting_for_approval"):
    st.markdown('<div class="section-label">Step 4 — Your approval</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### ⚖️ Human Approval Required")
        st.markdown(
            "Review the draft above. Approve it as-is, or choose **revise** and give feedback "
            "so the system can improve the plan before finalizing."
        )
        approved = st.radio(
            "What would you like to do?",
            ["✅ Approve this draft", "🔄 No, revise it"],
            horizontal=True,
        )
        feedback = st.text_area(
            "Feedback for revision",
            disabled=approved.startswith("✅"),
            placeholder="e.g. Reduce spending on hotels, add more free activities, avoid long train rides…",
        )

        if st.button("Submit Approval", type="primary"):
            with st.spinner("✍️ Finalizing your travel plan…"):
                final_result = app.invoke(
                    Command(
                        resume={
                            "approved": approved.startswith("✅"),
                            "feedback": feedback,
                        }
                    ),
                    config=config,
                )
            st.session_state.latest_result = final_result
            st.session_state.waiting_for_approval = False
            st.rerun()

# ---------------------------------------------------------------
# Final plan
# ---------------------------------------------------------------
if result.get("final_response"):
    st.markdown('<div class="section-label">Step 5 — Final plan</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 🎉 Your Final Travel Plan")
        if result.get("human_feedback"):
            st.info(f"Revised using your feedback: _{result['human_feedback']}_")
        st.markdown(result["final_response"])