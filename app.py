import streamlit as st
import requests
import json
import time
import re
from datetime import datetime
from typing import Optional
from openai import OpenAI

st.set_page_config(
    page_title="SEO Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #0a0a0a;
    color: #e8e4dc;
}

/* Hide streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1100px; }

/* Hero */
.hero-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.2em;
    color: #5a9a6e;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.hero-title {
    font-size: clamp(32px, 5vw, 56px);
    font-weight: 800;
    color: #e8e4dc;
    line-height: 1.05;
    margin: 0 0 16px;
}
.hero-title span { color: #5a9a6e; }
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    color: #666;
    margin-bottom: 40px;
    line-height: 1.7;
}

/* Input card */
.input-card {
    background: #111;
    border: 0.5px solid #222;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 32px;
}

/* Section headers */
.section-tag {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    color: #444;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #e8e4dc;
    margin-bottom: 20px;
}

/* Result cards */
.result-card {
    background: #111;
    border: 0.5px solid #1e1e1e;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 14px;
}
.result-card.urgent {
    border-left: 3px solid #e05a4e;
    border-radius: 0 10px 10px 0;
}
.result-card.opportunity {
    border-left: 3px solid #5a9a6e;
    border-radius: 0 10px 10px 0;
}
.result-card.citation {
    border-left: 3px solid #d4a847;
    border-radius: 0 10px 10px 0;
}

.card-keyword {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    color: #5a9a6e;
    margin-bottom: 6px;
}
.card-title {
    font-size: 16px;
    font-weight: 600;
    color: #e8e4dc;
    margin-bottom: 8px;
}
.card-body {
    font-size: 13px;
    color: #888;
    line-height: 1.7;
}

/* Score badge */
.score-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 20px;
    margin-right: 8px;
    margin-top: 10px;
}
.score-high { background: #0f2e1a; color: #5a9a6e; }
.score-med  { background: #2e2410; color: #d4a847; }
.score-low  { background: #2e1010; color: #e05a4e; }

/* Citation badge */
.cited-yes { color: #e05a4e; font-family: 'DM Mono', monospace; font-size: 12px; }
.cited-no  { color: #5a9a6e; font-family: 'DM Mono', monospace; font-size: 12px; }

/* Metric row */
.metric-row {
    display: flex;
    gap: 16px;
    margin-bottom: 28px;
    flex-wrap: wrap;
}
.metric-box {
    background: #111;
    border: 0.5px solid #1e1e1e;
    border-radius: 8px;
    padding: 16px 20px;
    min-width: 140px;
    flex: 1;
}
.metric-num {
    font-size: 28px;
    font-weight: 800;
    color: #e8e4dc;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Stagger animations */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.4s ease forwards; }

/* Streamlit widget overrides */
.stTextInput > div > div > input {
    background: #0d0d0d !important;
    border: 0.5px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #5a9a6e !important;
    box-shadow: 0 0 0 1px #5a9a6e30 !important;
}
.stButton > button {
    background: #5a9a6e !important;
    color: #0a0a0a !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 32px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #4d8860 !important;
    transform: translateY(-1px) !important;
}
label { color: #666 !important; font-size: 12px !important; font-family: 'DM Mono', monospace !important; }
.stTextArea > div > div > textarea {
    background: #0d0d0d !important;
    border: 0.5px solid #2a2a2a !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
.stSpinner > div { border-top-color: #5a9a6e !important; }
.stProgress > div > div > div { background: #5a9a6e !important; }

/* Divider */
hr { border-color: #1a1a1a !important; margin: 32px 0 !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 0.5px solid #1e1e1e !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    color: #444 !important;
    background: transparent !important;
    border: none !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: #5a9a6e !important;
    border-bottom: 1.5px solid #5a9a6e !important;
}
</style>
""", unsafe_allow_html=True)


# ── helpers ──────────────────────────────────────────────────────────────────

def call_claude(prompt: str, system: str = "") -> str:
    """Call Claude via Anthropic API (uses openai-compatible endpoint for simplicity)."""
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return "⚠️ No API key provided."
    client = OpenAI(api_key=api_key, base_url="https://api.anthropic.com/v1")
    try:
        resp = client.chat.completions.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[
                {"role": "system", "content": system or "You are an expert SEO Research Agent. Always respond in valid JSON only. No markdown, no explanation outside JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": str(e)})


def fetch_serp(keyword: str, api_key: str) -> dict:
    """Fetch SERP data from Serper.dev."""
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": keyword, "num": 10},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def analyse_keyword(keyword: str, domain: str, serp_data: dict, use_serp: bool) -> dict:
    """Send keyword + SERP context to Claude for analysis."""
    serp_context = ""
    if use_serp and "organic" in serp_data:
        results = serp_data["organic"][:5]
        serp_context = "\n".join([
            f"- Position {i+1}: {r.get('title','')} | {r.get('link','')}"
            for i, r in enumerate(results)
        ])

    prompt = f"""
Analyse this SEO keyword opportunity for the website: {domain}

Keyword: "{keyword}"

SERP top results (if available):
{serp_context if serp_context else "Not available - analyse based on keyword alone."}

Respond ONLY with this JSON structure, no extra text:
{{
  "keyword": "{keyword}",
  "intent": "informational|commercial|transactional|navigational",
  "difficulty": "low|medium|high",
  "priority_score": <integer 1-100>,
  "opportunity": "<one sentence — what the opportunity is>",
  "recommended_action": "create|refresh|optimise|target",
  "content_type": "<blog post|comparison page|landing page|guide|etc>",
  "outline": ["<heading 1>", "<heading 2>", "<heading 3>", "<heading 4>"],
  "entities": ["<entity 1>", "<entity 2>", "<entity 3>"],
  "competitor_insight": "<one sentence about who dominates this SERP and why>"
}}
"""
    raw = call_claude(prompt)
    try:
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception:
        return {"keyword": keyword, "error": "Parse failed", "raw": raw}


def check_llm_citation(query: str, brand: str) -> dict:
    """Ask Claude to simulate what an LLM would cite for a commercial query."""
    prompt = f"""
You are simulating an AEO/GEO citation analysis. For the commercial query: "{query}"

Think about what brands and sources a large language model like ChatGPT or Perplexity would typically cite in its answer.

Respond ONLY with this JSON, no extra text:
{{
  "query": "{query}",
  "brand_cited": <true if "{brand}" would likely be cited, false if not>,
  "citation_probability": <integer 0-100>,
  "typically_cited_brands": ["<brand 1>", "<brand 2>", "<brand 3>"],
  "why_not_cited": "<if brand not cited, one sentence on why — content gap, entity authority, etc>",
  "fix_recommendation": "<one actionable sentence on what content to create to get cited>"
}}
"""
    raw = call_claude(prompt)
    try:
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception:
        return {"query": query, "error": "Parse failed"}


def analyse_gaps(domain: str, keywords: list, results: list) -> dict:
    """Run a holistic gap analysis across all keywords."""
    kw_summary = "\n".join([
        f"- {r.get('keyword','?')}: intent={r.get('intent','?')}, score={r.get('priority_score','?')}, action={r.get('recommended_action','?')}"
        for r in results if "error" not in r
    ])
    prompt = f"""
You are an SEO strategist. Here's a keyword analysis summary for {domain}:

{kw_summary}

Respond ONLY with this JSON, no extra text:
{{
  "top_priority": "<the single most important thing this site should do right now>",
  "content_gap_summary": "<2 sentence summary of the main content gaps>",
  "quick_wins": ["<win 1>", "<win 2>", "<win 3>"],
  "long_term_plays": ["<play 1>", "<play 2>"],
  "aeo_readiness": <integer 0-100>,
  "overall_priority_score": <integer 0-100>
}}
"""
    raw = call_claude(prompt)
    try:
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception:
        return {"error": "Gap analysis failed", "raw": raw}


# ── UI ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-label">Agentic AI · SEO Research</div>
<h1 class="hero-title">SEO Research<br><span>Agent</span></h1>
<p class="hero-sub">
Enter your domain + target keywords. The agent analyses SERP intent,<br>
keyword gaps, and which competitors LLMs are citing instead of you.
</p>
""", unsafe_allow_html=True)

# ── API key setup ─────────────────────────────────────────────────────────────
with st.expander("⚙️ API Keys (required)", expanded="api_key" not in st.session_state):
    col1, col2 = st.columns(2)
    with col1:
        ak = st.text_input("Anthropic / Claude API key", type="password", placeholder="sk-ant-...")
    with col2:
        sk = st.text_input("Serper.dev API key (optional — for live SERP)", type="password", placeholder="leave blank to skip")
    if st.button("Save keys"):
        st.session_state["api_key"] = ak
        st.session_state["serper_key"] = sk
        st.success("Keys saved for this session.")

st.markdown("---")

# ── Input form ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-tag">Step 1</div><div class="section-title">Tell the agent about your site</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 1], gap="large")
with col_a:
    domain = st.text_input("Your domain", placeholder="e.g. affiniv.com")
    brand  = st.text_input("Brand name", placeholder="e.g. Affiniv")
with col_b:
    keywords_raw = st.text_area(
        "Target keywords (one per line)",
        placeholder="best NPS software\ncustomer feedback tool\nNPS survey platform\nemployee feedback software",
        height=130
    )

col_c, col_d = st.columns([1, 1], gap="large")
with col_c:
    llm_queries_raw = st.text_area(
        "Commercial queries to test LLM citation (one per line)",
        placeholder="what is the best NPS tool\nbest customer experience software\ntop survey tools for SaaS",
        height=100
    )
with col_d:
    st.markdown("<br>", unsafe_allow_html=True)
    use_serp = st.checkbox("Fetch live SERP data (requires Serper.dev key)", value=False)
    st.markdown('<p style="font-family:\'DM Mono\',monospace;font-size:11px;color:#444;margin-top:8px;">Without Serper key, the agent reasons from keyword context alone. Still produces useful briefs.</p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("Run Research Agent →")

# ── Run agent ─────────────────────────────────────────────────────────────────
if run_btn:
    if not st.session_state.get("api_key"):
        st.error("Add your Anthropic API key above first.")
        st.stop()
    if not domain or not keywords_raw.strip():
        st.error("Domain and at least one keyword are required.")
        st.stop()

    keywords   = [k.strip() for k in keywords_raw.strip().splitlines() if k.strip()]
    llm_queries = [q.strip() for q in llm_queries_raw.strip().splitlines() if q.strip()]
    serper_key = st.session_state.get("serper_key", "")

    st.markdown("---")
    st.markdown('<div class="section-tag">Agent running</div><div class="section-title">Research in progress…</div>', unsafe_allow_html=True)

    progress = st.progress(0)
    status   = st.empty()
    total_steps = len(keywords) + len(llm_queries) + 1

    kw_results = []
    for i, kw in enumerate(keywords):
        status.markdown(f'<p style="font-family:\'DM Mono\',monospace;font-size:12px;color:#5a9a6e;">Analysing keyword {i+1}/{len(keywords)}: <b>{kw}</b></p>', unsafe_allow_html=True)
        serp_data = {}
        if use_serp and serper_key:
            serp_data = fetch_serp(kw, serper_key)
        result = analyse_keyword(kw, domain, serp_data, use_serp and bool(serper_key))
        kw_results.append(result)
        progress.progress((i + 1) / total_steps)
        time.sleep(0.3)

    citation_results = []
    for j, q in enumerate(llm_queries):
        status.markdown(f'<p style="font-family:\'DM Mono\',monospace;font-size:12px;color:#d4a847;">Checking LLM citation {j+1}/{len(llm_queries)}: <b>{q}</b></p>', unsafe_allow_html=True)
        cit = check_llm_citation(q, brand)
        citation_results.append(cit)
        progress.progress((len(keywords) + j + 1) / total_steps)
        time.sleep(0.3)

    status.markdown('<p style="font-family:\'DM Mono\',monospace;font-size:12px;color:#888;">Running holistic gap analysis…</p>', unsafe_allow_html=True)
    gap_analysis = analyse_gaps(domain, keywords, kw_results)
    progress.progress(1.0)
    status.empty()

    # ── Results ────────────────────────────────────────────────────────────────
    st.markdown("---")

    # Summary metrics
    valid_results = [r for r in kw_results if "error" not in r]
    avg_score   = int(sum(r.get("priority_score", 0) for r in valid_results) / max(len(valid_results), 1))
    not_cited   = sum(1 for c in citation_results if not c.get("brand_cited", True) and "error" not in c)
    high_pri    = sum(1 for r in valid_results if r.get("priority_score", 0) >= 70)
    aeo_score   = gap_analysis.get("aeo_readiness", 0)

    st.markdown(f"""
<div class="metric-row">
  <div class="metric-box"><div class="metric-num">{len(valid_results)}</div><div class="metric-label">Keywords analysed</div></div>
  <div class="metric-box"><div class="metric-num">{avg_score}</div><div class="metric-label">Avg priority score</div></div>
  <div class="metric-box"><div class="metric-num">{high_pri}</div><div class="metric-label">High priority gaps</div></div>
  <div class="metric-box"><div class="metric-num">{not_cited}</div><div class="metric-label">LLM citation gaps</div></div>
  <div class="metric-box"><div class="metric-num">{aeo_score}</div><div class="metric-label">AEO readiness score</div></div>
</div>
""", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["  Keyword analysis  ", "  LLM citation check  ", "  Gap analysis + brief  "])

    with tab1:
        st.markdown('<div class="section-tag">Keyword intelligence</div><div class="section-title">Opportunity analysis</div>', unsafe_allow_html=True)
        for r in valid_results:
            score = r.get("priority_score", 0)
            card_class = "urgent" if score >= 70 else "opportunity" if score >= 40 else ""
            score_class = "score-high" if score >= 70 else "score-med" if score >= 40 else "score-low"
            outline_html = "".join([f"<li>{h}</li>" for h in r.get("outline", [])])
            entities_html = " ".join([f'<span class="score-badge score-med">{e}</span>' for e in r.get("entities", [])])
            st.markdown(f"""
<div class="result-card {card_class} fade-up">
  <div class="card-keyword">{r.get('keyword','')}</div>
  <div class="card-title">{r.get('opportunity','')}</div>
  <div class="card-body">{r.get('competitor_insight','')}</div>
  <div style="margin-top:12px;">
    <span class="score-badge {score_class}">Score: {score}</span>
    <span class="score-badge score-med">{r.get('intent','')}</span>
    <span class="score-badge score-med">{r.get('difficulty','')} difficulty</span>
    <span class="score-badge score-high">{r.get('recommended_action','')} · {r.get('content_type','')}</span>
  </div>
  <div style="margin-top:16px;">
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#444;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.1em;">Content outline</div>
    <ol style="color:#888;font-size:13px;margin:0;padding-left:20px;line-height:2;">{outline_html}</ol>
  </div>
  <div style="margin-top:12px;">
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#444;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.1em;">Key entities to cover</div>
    {entities_html}
  </div>
</div>
""", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-tag">AEO / GEO intelligence</div><div class="section-title">LLM citation check</div>', unsafe_allow_html=True)
        st.markdown('<p class="card-body" style="margin-bottom:24px;">Simulates what ChatGPT / Perplexity would cite for your target commercial queries. Gaps here = lost revenue from AI search.</p>', unsafe_allow_html=True)

        for c in citation_results:
            if "error" in c:
                continue
            cited = c.get("brand_cited", False)
            prob  = c.get("citation_probability", 0)
            card_class = "citation" if not cited else "opportunity"
            cited_label = '<span class="cited-yes">✗ NOT CITED</span>' if not cited else '<span class="cited-no">✓ CITED</span>'
            competitors_html = " ".join([f'<span class="score-badge score-low">{b}</span>' for b in c.get("typically_cited_brands", [])])
            st.markdown(f"""
<div class="result-card {card_class} fade-up">
  <div class="card-keyword">"{c.get('query','')}"</div>
  <div style="display:flex;align-items:center;gap:16px;margin:8px 0 12px;">
    <div style="font-size:20px;font-weight:800;color:#e8e4dc;">{brand}</div>
    {cited_label}
    <span class="score-badge score-med">Citation probability: {prob}%</span>
  </div>
  <div style="margin-bottom:10px;">
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#444;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.1em;">LLMs typically cite instead</div>
    {competitors_html}
  </div>
  <div class="card-body" style="margin-bottom:8px;"><b style="color:#d4a847;">Why not cited:</b> {c.get('why_not_cited','')}</div>
  <div class="card-body"><b style="color:#5a9a6e;">Fix:</b> {c.get('fix_recommendation','')}</div>
</div>
""", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-tag">Strategic intelligence</div><div class="section-title">Gap analysis + action plan</div>', unsafe_allow_html=True)

        if "error" not in gap_analysis:
            st.markdown(f"""
<div class="result-card fade-up" style="border-left:3px solid #5a9a6e;border-radius:0 10px 10px 0;margin-bottom:24px;">
  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#5a9a6e;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.1em;">Top priority right now</div>
  <div style="font-size:18px;font-weight:700;color:#e8e4dc;line-height:1.4;">{gap_analysis.get('top_priority','')}</div>
</div>

<div class="result-card fade-up">
  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#444;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.1em;">Content gap summary</div>
  <div class="card-body">{gap_analysis.get('content_gap_summary','')}</div>
</div>
""", unsafe_allow_html=True)

            col_q, col_l = st.columns(2, gap="large")
            with col_q:
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#5a9a6e;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">Quick wins (do this week)</div>', unsafe_allow_html=True)
                for w in gap_analysis.get("quick_wins", []):
                    st.markdown(f'<div class="result-card fade-up" style="padding:14px 18px;margin-bottom:8px;"><span style="color:#5a9a6e;margin-right:8px;">→</span><span class="card-body">{w}</span></div>', unsafe_allow_html=True)
            with col_l:
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#d4a847;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">Long-term plays (this quarter)</div>', unsafe_allow_html=True)
                for p in gap_analysis.get("long_term_plays", []):
                    st.markdown(f'<div class="result-card fade-up" style="padding:14px 18px;margin-bottom:8px;"><span style="color:#d4a847;margin-right:8px;">◆</span><span class="card-body">{p}</span></div>', unsafe_allow_html=True)

        # JSON export
        st.markdown("---")
        st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#444;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">Raw JSON output (for orchestrator handoff)</div>', unsafe_allow_html=True)
        export = {
            "domain": domain,
            "brand": brand,
            "generated_at": datetime.now().isoformat(),
            "keyword_analysis": kw_results,
            "citation_analysis": citation_results,
            "gap_analysis": gap_analysis
        }
        st.download_button(
            "Download full brief as JSON",
            data=json.dumps(export, indent=2),
            file_name=f"seo_brief_{domain.replace('.','_')}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        st.text_area("", json.dumps(export, indent=2), height=300)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:60px;padding-top:24px;border-top:0.5px solid #1a1a1a;text-align:center;">
  <p style="font-family:'DM Mono',monospace;font-size:11px;color:#333;">
    Built by <a href="https://www.linkedin.com/in/piyush-gupta-marketing/" style="color:#5a9a6e;text-decoration:none;">Piyush Gupta</a> · Agentic AI SEO Platform · v0.1
  </p>
</div>
""", unsafe_allow_html=True)
