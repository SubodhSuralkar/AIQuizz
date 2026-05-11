import streamlit as st
import google.generativeai as genai
import json
import re
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SSC CGL Prep AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --accent: #f59e0b;
    --accent2: #06b6d4;
    --accent3: #10b981;
    --danger: #ef4444;
    --text: #e2e8f0;
    --muted: #64748b;
    --border: #1e293b;
    --radius: 12px;
}

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Streamlit overrides */
.stApp { background-color: var(--bg) !important; }
.stSidebar { background-color: var(--surface) !important; border-right: 1px solid var(--border); }
.stSidebar > div { padding-top: 1rem; }
section[data-testid="stSidebar"] > div:first-child { background: var(--surface); }

/* Header */
.hero-header {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #f59e0b, #fbbf24, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.hero-sub {
    color: var(--muted);
    font-size: 0.95rem;
    margin-top: 0.4rem;
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-accent {
    border-left: 3px solid var(--accent);
}

/* Flashcard */
.flashcard {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin: 1rem 0;
    min-height: 140px;
    position: relative;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: transform 0.2s ease;
}
.flashcard:hover { transform: translateY(-2px); }
.flashcard-q {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.6;
}
.flashcard-a {
    background: linear-gradient(135deg, rgba(6,182,212,0.08), rgba(16,185,129,0.06));
    border: 1px solid rgba(6,182,212,0.2);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
    font-size: 1rem;
    color: var(--accent2);
    line-height: 1.7;
    font-weight: 400;
}
.flashcard-num {
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
}

/* Quiz */
.quiz-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.quiz-qnum {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.quiz-question {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Score badge */
.score-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), #fbbf24);
    color: #0a0e1a;
    font-weight: 800;
    font-size: 2rem;
    padding: 0.4rem 1.5rem;
    border-radius: 50px;
    font-family: 'JetBrains Mono', monospace;
}

/* Sidebar topic button */
.topic-btn {
    display: block;
    width: 100%;
    text-align: left;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    color: var(--muted);
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.15s ease;
    margin-bottom: 2px;
}
.topic-btn:hover { background: var(--surface2); color: var(--text); border-color: var(--border); }
.topic-btn.active { background: rgba(245,158,11,0.1); color: var(--accent); border-color: rgba(245,158,11,0.3); }

/* Steps */
.step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0;
    font-size: 0.9rem;
    color: var(--muted);
}
.step-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--surface2);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent);
    flex-shrink: 0;
}
.step-done .step-num { background: rgba(16,185,129,0.15); border-color: rgba(16,185,129,0.4); color: var(--accent3); }
.step-done { color: var(--accent3); }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #fbbf24) !important;
    color: #0a0e1a !important;
    font-weight: 700 !important;
    font-family: 'Sora', sans-serif !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(245,158,11,0.3) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Sora', sans-serif !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface2) !important;
    color: var(--accent) !important;
}

/* Radio */
.stRadio label { color: var(--text) !important; font-family: 'Sora', sans-serif !important; }
.stRadio [data-testid="stRadio"] > div { gap: 0.5rem !important; }

/* Progress */
.stProgress > div > div { background: var(--accent) !important; }

/* Alerts */
.stAlert { border-radius: var(--radius) !important; border: 1px solid var(--border) !important; }
.stSuccess { background: rgba(16,185,129,0.08) !important; border-color: rgba(16,185,129,0.3) !important; }
.stWarning { background: rgba(245,158,11,0.08) !important; border-color: rgba(245,158,11,0.3) !important; }
.stError { background: rgba(239,68,68,0.08) !important; border-color: rgba(239,68,68,0.3) !important; }
.stInfo { background: rgba(6,182,212,0.08) !important; border-color: rgba(6,182,212,0.3) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* File uploader */
.stFileUploader { 
    background: var(--surface2) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
}
.stFileUploader:hover { border-color: var(--accent) !important; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar label */
.sidebar-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700;
    color: var(--muted);
    padding: 0.5rem 0.75rem 0.25rem;
}

/* Metric card */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
}
.metric-card {
    flex: 1;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    text-align: center;
}
.metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.metric-lbl {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Answer result colors */
.ans-correct { color: var(--accent3) !important; }
.ans-wrong { color: var(--danger) !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
def init_session():
   # 1. Try to get the key from Streamlit Secrets first
    # 2. If it's not there, default to empty string
    initial_key = st.secrets.get("GEMINI_API_KEY", "")
    
    defaults = {
        "api_key": initial_key,
        "api_key_valid": True if initial_key else False, # Assume true if present
        "full_text": "",
        "topics": [],
        "selected_topic": None,
        "generated_content": None,
        "flashcard_reveals": {},   # {index: bool}
        "quiz_answers": {},        # {index: selected_option}
        "quiz_submitted": False,
        "quiz_score": None,
        "generation_error": None,
        "pdf_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── Helper: extract text from PDFs ───────────────────────────────────────────
def extract_text_from_pdfs(uploaded_files) -> tuple[str, list[str]]:
    """Extract and clean text from multiple PDFs. Returns (combined_text, warnings)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        st.error("pypdf not installed. Run: pip install pypdf")
        return "", []

    combined = []
    warnings = []

    for uf in uploaded_files:
        try:
            reader = PdfReader(io.BytesIO(uf.read()))
            if reader.is_encrypted:
                warnings.append(f"⚠️ **{uf.name}** is encrypted and could not be read.")
                continue
            pages_text = []
            for page in reader.pages:
                raw = page.extract_text() or ""
                pages_text.append(raw)
            full = "\n".join(pages_text)
            # Clean: remove non-ASCII, collapse whitespace
            full = re.sub(r'[^\x00-\x7F]+', ' ', full)
            full = re.sub(r'[ \t]+', ' ', full)
            full = re.sub(r'\n{3,}', '\n\n', full)
            full = full.strip()
            combined.append(f"\n\n=== SOURCE: {uf.name} ===\n\n{full}")
        except Exception as e:
            warnings.append(f"⚠️ Could not read **{uf.name}**: {str(e)}")

    return "\n".join(combined), warnings


# ── Helper: validate API key ──────────────────────────────────────────────────
import google.generativeai as genai

def validate_api_key(key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # We perform a tiny 'ping' request to see if the key works
        response = model.generate_content("ping")
        return True
    except Exception as e:
        # This will print the real error in your Streamlit logs
        st.sidebar.error(f"Error: {str(e)}") 
        return False


# ── Helper: get Gemini model ──────────────────────────────────────────────────
def get_model():
    if not st.session_state.api_key:
        st.error("Please enter an API Key first.")
        return None
    
    try:
        genai.configure(api_key=st.session_state.api_key)
        # Using the newest stable 2026 model name
        return genai.GenerativeModel("gemini-3-flash-preview")
    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        return None
# ── Helper: get topic index ───────────────────────────────────────────────────
def get_topic_index(text: str) -> list[str]:
    """Send first+last 5000 chars to Gemini; get back granular JSON topic list."""
    model = get_model()
    snippet = text[:5000] + "\n\n...[middle omitted]...\n\n" + text[-5000:]

    prompt = f"""You are an expert SSC CGL exam analyst.

Analyze the following text extracted from SSC CGL study material and return a comprehensive, GRANULAR list of specific topics covered.

Rules:
- Be SPECIFIC: instead of "History", write "Delhi Sultanate - Slave Dynasty" or "Mughal Empire - Akbar's Administration"
- Instead of "Polity", write "Fundamental Rights - Articles 12-35" or "DPSP - Article 36-51"
- Each topic should be distinct and testable as a standalone subject
- Return 15-35 topics minimum
- Return ONLY a valid JSON array of strings, nothing else. No markdown, no explanation.

Example format:
["Delhi Sultanate - Slave Dynasty", "Mughal Empire - Akbar's Reforms", "Fundamental Rights - Articles 12-35", ...]

Text to analyze:
{snippet}"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    topics = json.loads(raw)
    if not isinstance(topics, list):
        raise ValueError("Expected a JSON array")
    return [str(t) for t in topics]


# ── Helper: generate flashcards + quiz ───────────────────────────────────────
def generate_content(topic: str, full_text: str) -> dict:
    """Generate structured flashcards and quiz for a topic."""
    model = get_model()

    # Find a relevant excerpt (simple substring search, up to 8000 chars)
    topic_keywords = topic.lower().split()
    best_start = 0
    best_score = 0
    window = 4000
    step = 1000
    for i in range(0, max(1, len(full_text) - window), step):
        chunk = full_text[i:i+window].lower()
        score = sum(1 for kw in topic_keywords if kw in chunk)
        if score > best_score:
            best_score = score
            best_start = i
    excerpt = full_text[best_start:best_start+8000]

    prompt = f"""You are an expert SSC CGL exam coach. Generate study material for the topic: "{topic}"

Use the following reference text from the student's uploaded material:
---
{excerpt}
---

Return ONLY a valid JSON object (no markdown, no explanation) with this EXACT schema:
{{
  "flashcards": [
    {{"q": "question text", "a": "answer text"}}
  ],
  "quiz": [
    {{
      "question": "question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "exact text of the correct option"
    }}
  ]
}}

Requirements:
- Generate exactly 6 flashcards covering key facts, dates, names, concepts for SSC CGL
- Generate exactly 5 MCQ quiz questions at SSC CGL difficulty level
- Questions must be specific, factual, and exam-relevant
- Each quiz question must have exactly 4 options
- The "answer" field must match one of the 4 options exactly
- Do NOT include any text outside the JSON object"""

    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 2048, "temperature": 0.3}
    )
    raw = response.text.strip()
    # Strip possible markdown fences
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    # Find JSON object boundaries
    start = raw.find('{')
    end = raw.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in response")
    raw = raw[start:end]
    data = json.loads(raw)
    # Validate schema
    assert "flashcards" in data and "quiz" in data
    return data


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:0.5rem 0.75rem 1rem;">
        <div style="font-size:1.8rem">🎯</div>
        <div>
            <div style="font-weight:800;font-size:1rem;color:#f59e0b;letter-spacing:-0.02em">SSC CGL AI</div>
            <div style="font-size:0.7rem;color:#64748b;letter-spacing:0.05em">POWERED BY GEMINI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API Key input
    st.markdown('<div class="sidebar-label">🔑 API Configuration</div>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="AIza...",
        label_visibility="collapsed",
        key="api_input_widget"
    )

    col_v, col_c = st.columns(2)
    with col_v:
        if st.button("Validate", use_container_width=True):
            if api_key_input.strip():
                with st.spinner("Checking..."):
                    valid = validate_api_key(api_key_input.strip())
                st.session_state.api_key = api_key_input.strip()
                st.session_state.api_key_valid = valid
                if valid:
                    st.success("✓ Valid!")
                else:
                    st.error("Invalid key")
            else:
                st.warning("Enter a key first")

    with col_c:
        if st.button("Clear All", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # API status indicator
    if st.session_state.api_key_valid:
        st.markdown('<div style="font-size:0.78rem;color:#10b981;padding:0.25rem 0.75rem">● API Connected</div>', unsafe_allow_html=True)
    elif st.session_state.api_key:
        st.markdown('<div style="font-size:0.78rem;color:#ef4444;padding:0.25rem 0.75rem">● Not Validated</div>', unsafe_allow_html=True)

    st.divider()

    # Topic Index
    st.markdown('<div class="sidebar-label">📚 Topic Index</div>', unsafe_allow_html=True)

    if not st.session_state.topics:
        st.markdown(
            '<div style="font-size:0.82rem;color:#475569;padding:0.5rem 0.75rem;line-height:1.6">'
            'Upload PDFs and click <b style="color:#f59e0b">Index Topics</b> to populate the topic list.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="font-size:0.75rem;color:#64748b;padding:0.25rem 0.75rem 0.5rem">'
            f'{len(st.session_state.topics)} topics found</div>',
            unsafe_allow_html=True
        )
        for i, topic in enumerate(st.session_state.topics):
            is_active = st.session_state.selected_topic == topic
            btn_label = f"{'▶ ' if is_active else ''}{topic}"
            if st.button(
                btn_label,
                key=f"topic_btn_{i}",
                use_container_width=True,
                help=topic,
                type="primary" if is_active else "secondary"
            ):
                if st.session_state.selected_topic != topic:
                    st.session_state.selected_topic = topic
                    st.session_state.generated_content = None
                    st.session_state.flashcard_reveals = {}
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_score = None
                    st.session_state.generation_error = None
                    st.rerun()

    # Progress summary
    if st.session_state.quiz_score is not None:
        st.divider()
        st.markdown('<div class="sidebar-label">📊 Session Score</div>', unsafe_allow_html=True)
        total = len(st.session_state.generated_content.get("quiz", [])) if st.session_state.generated_content else 5
        pct = int((st.session_state.quiz_score / total) * 100) if total else 0
        st.markdown(
            f'<div style="padding:0.75rem;text-align:center">'
            f'<div class="score-badge">{st.session_state.quiz_score}/{total}</div>'
            f'<div style="font-size:0.8rem;color:#64748b;margin-top:0.4rem">{pct}% correct</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

# Hero header
st.markdown("""
<div class="hero-header">
    <div class="hero-title">SSC CGL Prep AI</div>
    <div class="hero-sub">Upload your study material → AI indexes topics → Generate flashcards & quizzes instantly</div>
</div>
""", unsafe_allow_html=True)

# ── STEP 1: Upload & Extract ──────────────────────────────────────────────────
if not st.session_state.full_text:
    st.markdown("### 📤 Upload Study Material")

    # Progress steps
    steps_html = """
    <div style="display:flex;gap:0;margin-bottom:1.5rem">
        <div class="step">
            <div class="step-num">1</div>
            <span>Upload PDFs</span>
        </div>
        <div style="flex:1;border-top:1px dashed #1e293b;margin:14px 8px 0"></div>
        <div class="step">
            <div class="step-num">2</div>
            <span>Index Topics</span>
        </div>
        <div style="flex:1;border-top:1px dashed #1e293b;margin:14px 8px 0"></div>
        <div class="step">
            <div class="step-num">3</div>
            <span>Select Topic</span>
        </div>
        <div style="flex:1;border-top:1px dashed #1e293b;margin:14px 8px 0"></div>
        <div class="step">
            <div class="step-num">4</div>
            <span>Study & Quiz</span>
        </div>
    </div>
    """
    st.markdown(steps_html, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drag & drop your PDF study materials here",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload SSC CGL notes, previous year papers, or any study PDFs"
    )

    if uploaded_files:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"📎 {len(uploaded_files)} file(s) selected: {', '.join(f.name for f in uploaded_files)}")
        with col2:
            if st.button("⚡ Extract Text", use_container_width=True):
                if not st.session_state.api_key_valid:
                    st.error("Please validate your Gemini API key in the sidebar first.")
                else:
                    with st.spinner("Extracting text from PDFs..."):
                        text, warnings = extract_text_from_pdfs(uploaded_files)
                    for w in warnings:
                        st.warning(w)
                    if text.strip():
                        st.session_state.full_text = text
                        st.session_state.pdf_count = len(uploaded_files) - len(warnings)
                        st.success(f"✅ Extracted {len(text):,} characters from {st.session_state.pdf_count} PDF(s)")
                        st.rerun()
                    else:
                        st.error("Could not extract any text. Please check your PDFs and try again.")
    else:
        # Demo info
        st.markdown("""
        <div class="card">
            <div style="font-weight:700;margin-bottom:0.75rem;color:#f59e0b">💡 How it works</div>
            <div style="font-size:0.9rem;color:#94a3b8;line-height:1.8">
                1. Enter your Gemini API key in the sidebar and click <b style="color:#e2e8f0">Validate</b><br>
                2. Upload one or more SSC CGL study PDFs (notes, books, question banks)<br>
                3. AI extracts and indexes all topics found in your material<br>
                4. Click any topic to generate flashcards and a 5-question quiz instantly
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── STEP 2: Index Topics ──────────────────────────────────────────────────────
elif st.session_state.full_text and not st.session_state.topics:
    char_count = len(st.session_state.full_text)

    st.markdown("### 🔍 Index Topics from Your Material")

    st.markdown(f"""
    <div class="card card-accent">
        <div style="font-weight:700;color:#10b981;margin-bottom:0.5rem">✅ Text Extracted Successfully</div>
        <div style="font-size:0.9rem;color:#94a3b8">
            <b style="color:#e2e8f0">{char_count:,}</b> characters extracted from 
            <b style="color:#e2e8f0">{st.session_state.pdf_count}</b> PDF(s).
            Now let AI analyze and index all the topics in your material.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            '<div style="font-size:0.9rem;color:#64748b;padding-top:0.6rem">'
            'Gemini will analyze the first and last 5,000 characters to map granular topics.'
            '</div>',
            unsafe_allow_html=True
        )
    with col2:
        if st.button("🗂️ Index Topics", use_container_width=True):
            with st.spinner("AI is analyzing your material and building the topic index..."):
                try:
                    topics = get_topic_index(st.session_state.full_text)
                    st.session_state.topics = topics
                    st.success(f"✅ Found {len(topics)} topics! Select one from the sidebar to begin studying.")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Could not parse topic list from AI. Try again. (JSON error: {e})")
                except Exception as e:
                    st.error(f"Error indexing topics: {str(e)}")

    # Show text preview
    with st.expander("👁️ Preview extracted text (first 1000 chars)"):
        st.code(st.session_state.full_text[:1000] + "...", language=None)

# ── STEP 3 & 4: Topic selected → Generate & Display ──────────────────────────
elif st.session_state.topics and st.session_state.selected_topic:
    topic = st.session_state.selected_topic

    # Topic header
    st.markdown(f"""
    <div class="hero-header" style="padding:1.5rem 2rem;margin-bottom:1rem">
        <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem">
            📖 Current Topic
        </div>
        <div style="font-size:1.4rem;font-weight:800;color:#f59e0b;letter-spacing:-0.02em">{topic}</div>
    </div>
    """, unsafe_allow_html=True)

    # Generate content if not yet generated
    if st.session_state.generated_content is None and st.session_state.generation_error is None:
        with st.spinner(f"Generating flashcards and quiz for: {topic}..."):
            try:
                content = generate_content(topic, st.session_state.full_text)
                st.session_state.generated_content = content
                st.session_state.flashcard_reveals = {i: False for i in range(len(content.get("flashcards", [])))}
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score = None
                st.rerun()
            except json.JSONDecodeError as e:
                st.session_state.generation_error = f"AI returned malformed JSON. Please try again. ({e})"
            except Exception as e:
                st.session_state.generation_error = str(e)

    if st.session_state.generation_error:
        st.error(f"❌ Generation failed: {st.session_state.generation_error}")
        if st.button("🔄 Retry"):
            st.session_state.generation_error = None
            st.rerun()

    elif st.session_state.generated_content:
        content = st.session_state.generated_content
        flashcards = content.get("flashcards", [])
        quiz_items = content.get("quiz", [])

        # Stats row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{len(flashcards)}</div>
                <div class="metric-lbl">Flashcards</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{len(quiz_items)}</div>
                <div class="metric-lbl">Quiz Questions</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            score_display = f"{st.session_state.quiz_score}/{len(quiz_items)}" if st.session_state.quiz_score is not None else "—"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{score_display}</div>
                <div class="metric-lbl">Quiz Score</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabs
        tab1, tab2 = st.tabs(["🃏 Flashcards", "📝 Quiz"])

        # ── FLASHCARDS TAB ──
        with tab1:
            if not flashcards:
                st.info("No flashcards generated for this topic.")
            else:
                revealed_count = sum(1 for v in st.session_state.flashcard_reveals.values() if v)
                st.markdown(
                    f'<div style="font-size:0.85rem;color:#64748b;margin-bottom:1rem">'
                    f'{revealed_count} of {len(flashcards)} answers revealed</div>',
                    unsafe_allow_html=True
                )
                st.progress(revealed_count / len(flashcards) if flashcards else 0)

                # Reveal All / Hide All
                col_a, col_b, _ = st.columns([1, 1, 3])
                with col_a:
                    if st.button("👁️ Reveal All"):
                        for i in range(len(flashcards)):
                            st.session_state.flashcard_reveals[i] = True
                        st.rerun()
                with col_b:
                    if st.button("🙈 Hide All"):
                        for i in range(len(flashcards)):
                            st.session_state.flashcard_reveals[i] = False
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                for i, fc in enumerate(flashcards):
                    is_revealed = st.session_state.flashcard_reveals.get(i, False)
                    answer_html = (
                        f'<div class="flashcard-a">💡 {fc.get("a", "")}</div>'
                        if is_revealed else ""
                    )
                    st.markdown(f"""
                    <div class="flashcard">
                        <div class="flashcard-num">#{i+1:02d}</div>
                        <div class="flashcard-q">❓ {fc.get("q", "")}</div>
                        {answer_html}
                    </div>
                    """, unsafe_allow_html=True)

                    btn_label = "🙈 Hide Answer" if is_revealed else "👁️ Reveal Answer"
                    if st.button(btn_label, key=f"reveal_{i}", use_container_width=False):
                        st.session_state.flashcard_reveals[i] = not is_revealed
                        st.rerun()

                    st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)

        # ── QUIZ TAB ──
        with tab2:
            if not quiz_items:
                st.info("No quiz questions generated for this topic.")
            else:
                if not st.session_state.quiz_submitted:
                    st.markdown(
                        '<div style="font-size:0.88rem;color:#64748b;margin-bottom:1.5rem">'
                        f'Answer all {len(quiz_items)} questions, then click <b style="color:#f59e0b">Submit Quiz</b>.'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    for i, q in enumerate(quiz_items):
                        st.markdown(f"""
                        <div class="quiz-card">
                            <div class="quiz-qnum">Question {i+1} of {len(quiz_items)}</div>
                            <div class="quiz-question">{q.get("question", "")}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        options = q.get("options", [])
                        current_answer = st.session_state.quiz_answers.get(i)
                        idx = options.index(current_answer) if current_answer in options else None

                        selected = st.radio(
                            f"q_{i}",
                            options=options,
                            index=idx,
                            key=f"quiz_radio_{i}",
                            label_visibility="collapsed"
                        )
                        if selected:
                            st.session_state.quiz_answers[i] = selected

                    answered = len(st.session_state.quiz_answers)
                    st.markdown(f"""
                    <div style="font-size:0.83rem;color:#64748b;margin:1rem 0 0.5rem">
                        {answered}/{len(quiz_items)} questions answered
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(answered / len(quiz_items))

                    col_sub, _ = st.columns([1, 3])
                    with col_sub:
                        submit_disabled = answered < len(quiz_items)
                        if st.button(
                            "🎯 Submit Quiz",
                            use_container_width=True,
                            disabled=submit_disabled,
                            help="Answer all questions to submit" if submit_disabled else "Submit your answers"
                        ):
                            score = 0
                            for i, q in enumerate(quiz_items):
                                if st.session_state.quiz_answers.get(i) == q.get("answer"):
                                    score += 1
                            st.session_state.quiz_score = score
                            st.session_state.quiz_submitted = True
                            st.rerun()

                else:
                    # Results view
                    score = st.session_state.quiz_score
                    total = len(quiz_items)
                    pct = int((score / total) * 100) if total else 0

                    if pct >= 80:
                        verdict = "🏆 Excellent!"
                        color = "#10b981"
                    elif pct >= 60:
                        verdict = "👍 Good job!"
                        color = "#f59e0b"
                    else:
                        verdict = "📚 Keep practicing!"
                        color = "#ef4444"

                    st.markdown(f"""
                    <div class="card" style="text-align:center;padding:2rem;border-color:{color}20;background:linear-gradient(135deg,#111827,#1a2235)">
                        <div style="font-size:0.85rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Your Score</div>
                        <div class="score-badge">{score}/{total}</div>
                        <div style="font-size:1.1rem;font-weight:700;color:{color};margin:0.75rem 0">{verdict}</div>
                        <div style="font-size:0.85rem;color:#64748b">{pct}% accuracy</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### 📋 Detailed Results")

                    for i, q in enumerate(quiz_items):
                        user_ans = st.session_state.quiz_answers.get(i, "Not answered")
                        correct_ans = q.get("answer", "")
                        is_correct = user_ans == correct_ans

                        icon = "✅" if is_correct else "❌"
                        border_color = "rgba(16,185,129,0.3)" if is_correct else "rgba(239,68,68,0.3)"
                        bg_color = "rgba(16,185,129,0.05)" if is_correct else "rgba(239,68,68,0.05)"

                        options_html = ""
                        for opt in q.get("options", []):
                            if opt == correct_ans:
                                opt_color = "#10b981"
                                opt_icon = " ✓"
                            elif opt == user_ans and not is_correct:
                                opt_color = "#ef4444"
                                opt_icon = " ✗"
                            else:
                                opt_color = "#64748b"
                                opt_icon = ""
                            options_html += f'<div style="color:{opt_color};font-size:0.88rem;padding:0.2rem 0">{opt_icon or "  "} {opt}</div>'

                        st.markdown(f"""
                        <div style="background:{bg_color};border:1px solid {border_color};border-radius:{12}px;padding:1.25rem 1.5rem;margin:0.75rem 0">
                            <div style="font-size:0.75rem;color:#64748b;margin-bottom:0.4rem;font-family:'JetBrains Mono',monospace">
                                {icon} Question {i+1}
                            </div>
                            <div style="font-weight:600;font-size:0.95rem;margin-bottom:0.75rem;color:#e2e8f0">{q.get("question", "")}</div>
                            {options_html}
                        </div>
                        """, unsafe_allow_html=True)

                    # Retry quiz
                    if st.button("🔄 Retry Quiz"):
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_score = None
                        st.rerun()

# ── Waiting for topic selection ───────────────────────────────────────────────
elif st.session_state.topics and not st.session_state.selected_topic:
    st.markdown("""
    <div class="card" style="text-align:center;padding:3rem 2rem">
        <div style="font-size:3rem;margin-bottom:1rem">📚</div>
        <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin-bottom:0.5rem">Topics Indexed!</div>
        <div style="font-size:0.9rem;color:#64748b">
            Select a topic from the sidebar to generate flashcards and quiz questions.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show topic grid preview
    st.markdown("### 🗂️ Available Topics")
    cols = st.columns(2)
    for i, topic in enumerate(st.session_state.topics):
        with cols[i % 2]:
            if st.button(f"📖 {topic}", key=f"main_topic_{i}", use_container_width=True):
                st.session_state.selected_topic = topic
                st.session_state.generated_content = None
                st.session_state.flashcard_reveals = {}
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score = None
                st.session_state.generation_error = None
                st.rerun()
