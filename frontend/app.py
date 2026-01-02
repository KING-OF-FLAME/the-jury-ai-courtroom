import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="The Jury: AI Courtroom", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")

def load_css():
    css_file = "frontend/styles.css"
    if os.path.exists(css_file):
        with open(css_file) as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

if "case_state" not in st.session_state: st.session_state.case_state = "IDLE"
if "current_case" not in st.session_state: st.session_state.current_case = None
if "input_query" not in st.session_state: st.session_state.input_query = ""

def set_query(t): st.session_state.input_query = t
def reset(): 
    st.session_state.case_state = "IDLE"
    st.session_state.current_case = None
    st.session_state.input_query = ""
    st.rerun()

def api_call(endpoint, payload=None, method="POST"):
    url = f"{API_URL}/{endpoint}"
    try:
        if method == "POST": res = requests.post(url, json=payload, timeout=600)
        else: res = requests.get(url, timeout=20)
        return res.json() if res.status_code == 200 else None
    except: return None

def generate_markdown(case):
    if not case: return ""
    md = f"# ⚖️ Case #{case.get('id', '?')}\n\n**Confidence:** {case.get('confidence_score', 0)}%\n**Cost:** ${case.get('estimated_cost', 0):.5f}\n\n"
    if case.get('logs'):
        for log in case['logs']:
            md += f"### {log.get('role')} ({log.get('model')})\n{log.get('content')}\n\n---\n"
    return md

def render_card(role, content, model, time_t, tokens, cost, confidence, persona):
    css = f"role-{role.lower()}"
    icon = {"Proposer":"🏗️", "Critic":"🕵️", "Judge":"⚖️"}.get(role, "🤖")
    
    thinking, output = "", content
    if "[Thinking Process]" in content:
        parts = content.split("[Output]")
        if len(parts) > 1: thinking, output = parts[0].replace("[Thinking Process]", "").strip(), parts[1].strip()

    st.markdown(f"""<div class="agent-card {css}"><div class="agent-header"><span>{icon} {persona}</span></div>""", unsafe_allow_html=True)
    
    # FIXED: Clean Columns for Badges
    c1, c2, c3, c4 = st.columns(4)
    c1.caption(f"⏱️ {time_t}s")
    c2.caption(f"🪙 {tokens}")
    c3.caption(f"💵 ${cost:.5f}")
    c4.caption(f"🤖 {model.split(':')[0]}")
    if role == "Judge" and confidence > 0: st.caption(f"🎯 Confidence: **{confidence}%**")

    if thinking:
        with st.expander("🧠 View Thinking Process"): st.info(thinking)
    st.markdown(output)
    st.markdown("</div>", unsafe_allow_html=True)

# --- SIDEBAR (HISTORY FIXED) ---
with st.sidebar:
    st.title("⚖️ Config")
    if st.button("✨ New Case", type="primary", use_container_width=True): reset()
    
    with st.expander("🎭 Personas", expanded=True):
        p_per = st.text_input("Proposer Persona", "Senior Solutions Architect")
        p_mod = st.text_input("Proposer Model", "nvidia/nemotron-3-nano-30b-a3b:free")
        c_per = st.text_input("Critic Persona", "NSA Security Auditor")
        c_mod = st.text_input("Critic Model", "allenai/olmo-3.1-32b-think:free")
        j_per = st.text_input("Judge Persona", "Chief Justice")
        j_mod = st.text_input("Judge Model", "meta-llama/llama-3.1-405b-instruct:free")

    st.subheader("🗄️ Case Log")
    hist_data = api_call("history", method="GET")
    
    if hist_data:
        for h in hist_data:
            # FIXED: Label shows Query Text + Cost
            q_text = h.get('query', 'Case')[:20].replace("\n", " ")
            cost = h.get('estimated_cost', 0)
            
            # Example: #5 Zero Trust Fi.. ($0.002)
            label = f"#{h['id']} {q_text}.. (${cost:.3f})"
            
            if st.button(label, key=f"hist_{h['id']}", use_container_width=True):
                full_case = api_call(f"case/{h['id']}", method="GET")
                if full_case:
                    st.session_state.current_case = full_case
                    # Smart Resume logic
                    if full_case.get('verdict'): st.session_state.case_state = "COMPLETED"
                    elif full_case.get('critic_output'): st.session_state.case_state = "JUDGING"
                    else: st.session_state.case_state = "PROPOSING"
                    st.rerun()
    else:
        st.caption("No cases found.")

# --- MAIN ---
st.title("⚖️ The Jury: AI Courtroom")

if st.session_state.case_state == "IDLE":
    st.markdown("### 🧪 Test Cases")
    c1, c2, c3 = st.columns(3)
    if c1.button("☢️ SCADA Stuxnet", use_container_width=True): 
        st.session_state.input_query = "Design a 'Zero-Trust Firmware Update Mechanism' for air-gapped Centrifuges. Constraints: Offline USB, Insider Threats. Critic MUST use Power Analysis Attack."
    if c2.button("💰 DeFi Arbitrage", use_container_width=True): 
        st.session_state.input_query = "Write a Flash Loan Arbitrage Bot in Solidity using Aave. Critic MUST try Reentrancy Attack."
    if c3.button("💻 3D Portfolio", use_container_width=True): 
        st.session_state.input_query = "Create a 3D Portfolio Website using Next.js 14 and Three.js. Include Dark Mode and Tilt effects."
    
    q = st.text_area("Case Query:", st.session_state.input_query, height=120)
    
    if st.button("🚀 Start Case", type="primary"):
        if q:
            with st.spinner("Initializing..."):
                payload = {"query": q, "proposer_model": p_mod, "critic_model": c_mod, "judge_model": j_mod, "proposer_persona": p_per, "critic_persona": c_per, "judge_persona": j_per}
                data = api_call("case/start", payload, method="POST")
                if data:
                    st.session_state.current_case = data
                    st.session_state.case_state = "PROPOSING" if not data.get("verdict") else "COMPLETED"
                    st.rerun()
                else:
                    st.error("Failed to start case.")

# --- LIVE EXECUTION ---
if st.session_state.current_case:
    c = st.session_state.current_case
    
    # Render Logs
    if c.get("logs"):
        for l in c["logs"]:
            role = l.get("role")
            name = p_per if role == "Proposer" else c_per if role == "Critic" else j_per
            render_card(role, l.get("content",""), l.get("model",""), l.get("duration",0), l.get("tokens",0), l.get("cost",0), c.get("confidence_score",0), name)

    step_map = {
        "PROPOSING": ("proposer", "CRITIQUING"),
        "CRITIQUING": ("critic", "JUDGING"),
        "JUDGING": ("judge", "COMPLETED")
    }
    
    curr = st.session_state.case_state
    if curr in step_map:
        endpoint, next_state = step_map[curr]
        
        case_id = c.get('id')
        if case_id:
            with st.status(f"⚙️ Running {endpoint.title()} Step...", expanded=True):
                data = api_call(f"case/{case_id}/{endpoint}", payload={}, method="POST")
                if data:
                    st.session_state.current_case = data
                    st.session_state.case_state = next_state
                    st.rerun()
                else:
                    st.error("Workflow Halted. Check Backend.")
                    st.stop()
    
    if curr == "COMPLETED":
        st.success("Verdict Reached.")
        st.download_button("📥 Download Report", generate_markdown(c), "report.md")
        if st.button("🔄 Restart"): reset()