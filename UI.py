import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide"
)

# ── Clean & Premium Modern Custom Denim-Slate UI Styling ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #112331;
    color: #e2f0fd;
}

/* ── Hero ── */
.hero-wrapper {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.5rem;
    height: 110px;
    background: linear-gradient(135deg, #1f3a52 0%, #112331 100%);
    border: 1px solid #2a4b6c;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
}
.hero-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 0.5rem;
}
.hero-badge {
    background: rgba(78, 168, 240, 0.2);
    border: 1px solid #4ea8f0;
    color: #a6d5fa !important;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    margin-bottom: 0.2rem;
}
.hero-title {
    font-size: 1.4rem; /* Scaled down and made small as requested */
    font-weight: 700;
    color: #ffffff;
    margin: 0;
}

/* ── Clean Functional Panels ── */
.panel-box {
    background: #1b3247;
    border: 1px solid #2e537a;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
.input-label {
    color: #7ab8f5;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Flight Timeline Track ── */
.timeline-container {
    background: #112331;
    border: 1px solid #2a4b6c;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
.timeline-header {
    display: flex;
    justify-content: space-between;
    color: #7ab8f5;
    font-size: 0.85rem;
    font-weight: 600;
}
.timeline-track {
    position: relative;
    height: 6px;
    background: #254463;
    border-radius: 3px;
    margin: 1.2rem 0;
}
.timeline-progress {
    position: absolute;
    height: 100%;
    width: 65%;
    background: linear-gradient(90deg, #3a7bd5, #4ea8f0);
    border-radius: 3px;
}
.timeline-node {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #4ea8f0;
    border: 2px solid #112331;
}
.node-start { left: 0%; }
.node-end { left: 65%; }

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #3a7bd5 0%, #20508a 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(58,123,213,0.3) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(58,123,213,0.45) !important;
}

/* ── Metrics ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}
.metric-box {
    flex: 1;
    background: #112331;
    border: 1px solid #2e537a;
    border-radius: 10px;
    padding: 0.8rem;
    text-align: center;
}
.metric-val { font-size: 1.5rem; font-weight: 700; color: #4ea8f0; }
.metric-lbl { font-size: 0.75rem; color: #94adc8; text-transform: uppercase; }

/* Final Executive Plan Display Card */
.final-card {
    background: #112331;
    border-left: 4px solid #3a7bd5;
    border-top: 1px solid #2e537a;
    border-right: 1px solid #2e537a;
    border-bottom: 1px solid #2e537a;
    border-radius: 0 10px 10px 0;
    padding: 1.2rem;
    color: #e2f0fd;
    line-height: 1.6;
}

.save-bar {
    background: #112331;
    border: 1px solid #2e537a;
    border-radius: 8px;
    padding: 0.75rem;
    color: #a6d5fa;
    font-size: 0.85rem;
}

/* Base Form Elements overrides */
.stTextArea textarea { background: #112331 !important; border: 1px solid #2e537a !important; color: #ffffff !important; }
input[type="text"], .stTextInput input { background: #112331 !important; border: 1px solid #2e537a !important; color: #ffffff !important; }
section[data-testid="stSidebar"] { background: #0b1824 !important; border-right: 1px solid #1e354d !important; }
.sidebar-chip { background: #112331; border: 1px solid #2e537a; border-radius: 6px; padding: 0.4rem; margin-bottom: 0.4rem; color: #a6d5fa; font-size: 0.85rem; }
.sidebar-title { color: #ffffff; font-size: 1rem; font-weight: 600; margin: 1rem 0 0.5rem; }

/* Hide default wrappers */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Persistent Session State Initialization ─────────────────────────────────
if "user_query_state" not in st.session_state:
    st.session_state.user_query_state = ""
if "collected_results" not in st.session_state:
    st.session_state.collected_results = None

# ── Sidebar Configuration ──
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🌍 AI Travel Planner</div>", unsafe_allow_html=True)
    st.markdown("---")
    thread_id = st.text_input("👤 User ID", value="aarohi_user")

    st.markdown("<div class='sidebar-title'>Powered by</div>", unsafe_allow_html=True)
    for tech in ["🔗 LangGraph", " Groq · LLaMA 3.3 70B", "🐘 PostgreSQL", "🔍 Tavily Search", "✈️ AviationStack"]:
        st.markdown(f"<div class='sidebar-chip'>{tech}</div>", unsafe_allow_html=True)

# ── Hero Element ──
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-content">
        <div class="hero-badge">✦ Multi-Agent AI System</div>
        <div class="hero-title"> AI Travel Booking System</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Beautiful Destination Image Strip ──
DESTINATIONS = [
    ("🇯🇵 Tokyo",     "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("🇫🇷 Paris",     "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("🇹🇭 Bangkok",   "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("🇮🇹 Rome",      "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("🇦🇪 Dubai",     "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]

img_cols = st.columns(5)
for col, (name, img_url) in zip(img_cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div style="border-radius:10px;overflow:hidden;position:relative;height:90px;margin-bottom:1.5rem;box-shadow:0 4px 10px rgba(0,0,0,0.2);">
            <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;filter:brightness(0.65);" />
            <div style="position:absolute;bottom:8px;left:0;right:0;text-align:center;color:#fff;font-size:0.8rem;font-weight:600;letter-spacing:0.05em;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Main Two Column Layout ──
left_col, right_col = st.columns([1, 1], gap="medium")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN: ACTION PLANNER & CHAT CONTROLS
# ══════════════════════════════════════════════════════════════════════════════
with left_col:
    # st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.subheader(" Travel Assistant Setup")
    
    st.markdown("<div class='input-label'>Select Destination Preset:</div>", unsafe_allow_html=True)
    QUICK = ["7-day Japan under ₹2L", "Paris trip for 5 days", "Dubai weekend trip", "Bali backpacking 10 days"]
    qcols = st.columns(len(QUICK))
    for qc, label in zip(qcols, QUICK):
        with qc:
            if st.button(label, key=f"q_{label}"):
                st.session_state.user_query_state = label
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='input-label'>Describe Your Specific Requirements:</div>", unsafe_allow_html=True)
    
    user_query = st.text_area(
        "Describe your trip",
        value=st.session_state.user_query_state,
        placeholder="Provide locations, dates, budgets or timeline items...",
        height=120,
        label_visibility="collapsed"
    )

    generate = st.button("  Execute Multi-Agent Search Engine", use_container_width=True)

    if generate:
        if not user_query.strip():
            st.warning("Please describe your trip parameters first.")
        else:
            config = {"configurable": {"thread_id": thread_id}}
            collected = {"flight_results": "", "hotel_results": "",
                         "itinerary": "", "final_response": "", "llm_calls": 0}

            st.info("Invoking downstream graph agents. Monitoring responses...")
            
            try:
                for chunk in app.stream(
                    {
                        "messages": [HumanMessage(content=user_query)],
                        "user_query": user_query,
                        "flight_results": "",
                        "hotel_results": "",
                        "itinerary": "",
                        "llm_calls": 0,
                    },
                    config=config,
                    stream_mode="updates",
                ):
                    for node_name, state_update in chunk.items():
                        st.write(f"✔️ Microservice Node `{node_name}` executed successfully.")
                        if node_name == "flight_agent":
                            collected["flight_results"] = state_update.get("flight_results", "")
                        elif node_name == "hotel_agent":
                            collected["hotel_results"] = state_update.get("hotel_results", "")
                        elif node_name == "itinerary_agent":
                            collected["itinerary"] = state_update.get("itinerary", "")
                        elif node_name == "final_agent":
                            msgs = state_update.get("messages", [])
                            collected["final_response"] = msgs[-1].content if msgs else ""
                        
                        collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])
                
                st.session_state.collected_results = collected
                st.success("Synchronized data updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Execution Error context encountered: {str(e)}")
                
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN: VISUAL SYSTEM OUTPUT LOGS
# ══════════════════════════════════════════════════════════════════════════════
with right_col:
    # st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.subheader(" Operational Analytics Display")
    
    if st.session_state.collected_results is None:
        st.info("System waiting for agent graph trigger pipeline initialization on the left panel.")
    else:
        res = st.session_state.collected_results
        
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">Active Threads</div></div>
            <div class="metric-box"><div class="metric-val">{res['llm_calls']}</div><div class="metric-lbl">API Calls</div></div>
            <div class="metric-box"><div class="metric-val" style="color:#4ea8f0;">Ready</div><div class="metric-lbl">Pipeline</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Flight Section with Time/Progress Indicators
        st.markdown("<h4 style='color:#7ab8f5;'> Flight Schedules & Logistics</h4>", unsafe_allow_html=True)
        
        if res["flight_results"] and "no flight found" not in res["flight_results"].lower():
            st.markdown("""
            <div class="timeline-container">
                <div class="timeline-header">
                    <span>Aviation Tracker Network Status</span>
                    <span style="color:#2ecc71;">Active Connection</span>
                </div>
                <div class="timeline-track">
                    <div class="timeline-progress"></div>
                    <div class="timeline-node node-start"></div>
                    <div class="timeline-node node-end"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(res["flight_results"])
        else:
            st.warning("⚠️ AviationStack API fallback: No explicit future routes returned. Review active API keys, search syntax params, or coordinate values inside tools/flight_tool.py.")
            if res["flight_results"]:
                st.info(f"Raw response trace: {res['flight_results']}")

        # Hotels Section
        st.markdown("<h4 style='color:#7ab8f5;'> Accommodation Match Engine</h4>", unsafe_allow_html=True)
        st.markdown(res["hotel_results"] if res["hotel_results"] else "_No property fields parsed._")

        # Sightseeing & Itinerary Section
        st.markdown("<h4 style='color:#7ab8f5;'> Curated Daily Excursions</h4>", unsafe_allow_html=True)
        st.markdown(res["itinerary"] if res["itinerary"] else "_No day-by-day mapping generated._")
            
        # Final Master Document Box
        if res["final_response"]:
            st.markdown("<h4 style='color:#7ab8f5;'> Final Document Output Blueprint</h4>", unsafe_allow_html=True)
            st.markdown(f"<div class='final-card'>{res['final_response']}</div>", unsafe_allow_html=True)

        # File Export block
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"
        save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
        os.makedirs(save_dir, exist_ok=True)

        file_content = f"# Travel Plan Package\n\n## Flights\n{res['flight_results']}\n\n## Hotels\n{res['hotel_results']}"
        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write(file_content)

        st.markdown("<br>", unsafe_allow_html=True)
        dl_col, info_col = st.columns([1, 2])
        with dl_col:
            st.download_button("⬇️ Download Markdown", data=file_content, file_name=filename, mime="text/markdown")
        with info_col:
            st.markdown(f"<div class='save-bar'>📁 Saved to disk → <code>travel_plans/{filename}</code></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)