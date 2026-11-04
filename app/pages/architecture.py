"""Offline AI-Resume-Analyzer system architecture overview for university demos.

Presentation-only page: no database reads, external requests, or authentication changes.
"""
import streamlit as st
from app.ui.workspace import page_header


_ARCH_CSS = r"""
<style>
.ara-arch { --a-gold:#efc581; --a-violet:#b69cff; --a-blue:#83d8f5; color:#edeaf6; padding-bottom:1rem; }
.ara-arch * { box-sizing:border-box; }
.ara-arch .ara-arch-eyebrow { font-size:.7rem; text-transform:uppercase; letter-spacing:.18em; color:#b9a8ff; margin:0 0 .55rem; }
.ara-arch .ara-arch-intro { color:#b9b6c9; max-width:760px; line-height:1.65; font-size:.98rem; margin:0 0 1.2rem; }
.ara-arch .ara-arch-frame { position:relative; perspective:1250px; isolation:isolate; border:1px solid rgba(190,166,255,.2); border-radius:24px; background:radial-gradient(ellipse at 48% 5%,rgba(135,105,235,.18),transparent 58%),linear-gradient(155deg,rgba(23,24,46,.92),rgba(10,13,30,.94)); box-shadow:0 30px 80px rgba(0,0,0,.22),inset 0 1px rgba(255,255,255,.045); padding:clamp(16px,3.2vw,38px); overflow:hidden; }
.ara-arch .ara-arch-frame:before { content:""; pointer-events:none; position:absolute; inset:0; opacity:.18; background-image:linear-gradient(rgba(168,151,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(168,151,255,.13) 1px,transparent 1px); background-size:40px 40px; mask-image:linear-gradient(to bottom,black,transparent 85%); }
.ara-arch .ara-arch-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:15px; position:relative; z-index:1; }
.ara-arch .ara-arch-node { position:relative; padding:20px 20px 18px; min-width:0; border-radius:17px; border:1px solid rgba(170,149,255,.27); background:linear-gradient(140deg,rgba(42,41,75,.96),rgba(17,22,43,.98)); box-shadow:0 12px 25px rgba(0,0,0,.2),inset 0 1px rgba(255,255,255,.08); transform-style:preserve-3d; transition:transform .55s cubic-bezier(.2,.8,.2,1), border-color .4s, box-shadow .4s; }
.ara-arch .ara-arch-node:hover { transform:translateY(-7px) rotateX(4deg) rotateY(-2deg); border-color:rgba(239,197,129,.65); box-shadow:0 22px 45px rgba(15,10,38,.5),0 0 28px rgba(166,133,255,.15); }
.ara-arch .ara-arch-node:hover h3 { color:#f5d8a3; }
.ara-arch .ara-arch-node h3 { font-size:1.15rem; line-height:1.4; margin:.25rem 0 .4rem; color:#f1eafa; font-weight:700; }
.ara-arch .ara-arch-node p { margin:0; color:#bcb8cc; font-size:.89rem; line-height:1.55; }
.ara-arch .ara-arch-tag { font-size:.66rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--a-blue); }
.ara-arch .ara-arch-icon { display:inline-grid; place-items:center; vertical-align:middle; width:37px; height:37px; border-radius:11px; margin-right:7px; background:rgba(166,136,246,.14); border:1px solid rgba(177,149,255,.22); font-size:1.1rem; }
.ara-arch .ara-arch-node--full { grid-column:1 / -1; max-width:620px; width:100%; margin-inline:auto; }
.ara-arch .ara-arch-arrow { grid-column:1 / -1; display:flex; align-items:center; justify-content:center; min-height:28px; color:#d1b5fa; }
.ara-arch .ara-arch-arrow:before { content:""; width:2px; height:29px; background:linear-gradient(to bottom,var(--a-violet),var(--a-gold)); border-radius:2px; box-shadow:0 0 12px rgba(182,156,255,.4); }
.ara-arch .ara-arch-split { grid-column:1 / -1; display:grid; grid-template-columns:1fr 1fr; gap:15px; align-items:stretch; }
.ara-arch .ara-arch-note { margin:16px 0 0; font-size:.8rem; color:#ada9c4; line-height:1.6; text-align:center; }
.ara-arch .ara-arch-caption { margin:1.6rem 0 .8rem; font-size:1rem; color:#e9dfef; font-weight:700; }
.ara-arch .ara-arch-flow { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }
.ara-arch .ara-arch-step { padding:16px; border:1px solid rgba(157,141,218,.22); border-radius:14px; background:rgba(30,31,57,.75); box-shadow:inset 0 1px rgba(255,255,255,.05); }
.ara-arch .ara-arch-step strong { color:#f0cd92; display:block; font-size:.83rem; margin:0 0 7px; }
.ara-arch .ara-arch-step p { margin:0; font-size:.83rem; line-height:1.5; color:#bcb8cc; }
@media (prefers-reduced-motion:no-preference) {
 .ara-arch .ara-arch-arrow:before { animation:ara-arch-pulse 2.4s ease-in-out infinite; }
 @keyframes ara-arch-pulse { 0%,100% { opacity:.45; filter:brightness(.85); } 50% { opacity:1; filter:brightness(1.4); } }
 @supports (animation-timeline:view()) {
  .ara-arch .ara-arch-node, .ara-arch .ara-arch-step { animation:ara-arch-reveal both cubic-bezier(.2,.8,.2,1); animation-timeline:view(); animation-range:entry 0% cover 28%; }
  @keyframes ara-arch-reveal { from { opacity:.42; transform:translate3d(0,38px,-90px) rotateX(12deg); filter:blur(3px); } to { opacity:1; transform:translate3d(0,0,0) rotateX(0); filter:blur(0); } }
 }
}
@media (max-width:700px) { .ara-arch .ara-arch-grid,.ara-arch .ara-arch-split { grid-template-columns:1fr; } .ara-arch .ara-arch-flow { grid-template-columns:repeat(2,minmax(0,1fr)); } .ara-arch .ara-arch-node--full,.ara-arch .ara-arch-arrow,.ara-arch .ara-arch-split { grid-column:1; } }
@media (max-width:450px) { .ara-arch .ara-arch-flow { grid-template-columns:1fr; } .ara-arch .ara-arch-node { padding:16px; } }
@media (prefers-reduced-motion:reduce) { .ara-arch .ara-arch-node,.ara-arch .ara-arch-step,.ara-arch .ara-arch-arrow:before { animation:none !important; transition:none !important; transform:none !important; opacity:1 !important; filter:none !important; } }
</style>
"""


_ARCH_HTML = """
<section class="ara-arch" aria-label="AI-Resume-Analyzer system architecture">
 <p class="ara-arch-eyebrow">Architecture at a glance</p>
 <p class="ara-arch-intro">A modular, offline-first pipeline connects the Streamlit interface to resume analysis, matching services, local data, and optional on-device AI. Each layer has a distinct responsibility.</p>
 <div class="ara-arch-frame">
  <div class="ara-arch-grid">
   <article class="ara-arch-node ara-arch-node--full"><span class="ara-arch-tag">01 / Interface</span><h3><span class="ara-arch-icon" aria-hidden="true">🖥️</span>Presentation Layer</h3><p>Streamlit pages, dashboards, resume uploads, analysis results, and interactive career exploration.</p></article>
   <div class="ara-arch-arrow" aria-hidden="true"></div>
   <div class="ara-arch-split">
    <article class="ara-arch-node"><span class="ara-arch-tag">02 / Processing</span><h3><span class="ara-arch-icon" aria-hidden="true">🧠</span>Analysis & Intelligence</h3><p>Document text extraction, ATS readiness, skill alias normalization, Job Matching Studio, and AI Career Finder.</p></article>
    <article class="ara-arch-node"><span class="ara-arch-tag">03 / Protection</span><h3><span class="ara-arch-icon" aria-hidden="true">🛡️</span>Access & Security</h3><p>Hashed passwords, sign-in sessions, authorization checks, and per-user resume ownership.</p></article>
   </div>
   <div class="ara-arch-arrow" aria-hidden="true"></div>
   <div class="ara-arch-split">
    <article class="ara-arch-node"><span class="ara-arch-tag">04 / Knowledge</span><h3><span class="ara-arch-icon" aria-hidden="true">🗃️</span>Local Data Layer</h3><p>SQLite records, resume text, skill aliases, and imported O*NET / occupation taxonomy data.</p></article>
    <article class="ara-arch-node"><span class="ara-arch-tag">05 / Optional AI</span><h3><span class="ara-arch-icon" aria-hidden="true">⚙️</span>Local Language Models</h3><p>Ollama can enhance selected explanations and interpretations; matching and catalog tools also work without it.</p></article>
   </div>
  </div>
  <p class="ara-arch-note">Conceptual component diagram — connections show responsibility and data flow, not a live network or system-health monitor.</p>
 </div>
 <h3 class="ara-arch-caption">From resume to recommendation</h3>
 <div class="ara-arch-flow">
  <div class="ara-arch-step"><strong>01 · Upload</strong><p>Submit a supported resume or CV from the user workspace.</p></div>
  <div class="ara-arch-step"><strong>02 · Understand</strong><p>Extract text and recognize evidence-backed skills and aliases.</p></div>
  <div class="ara-arch-step"><strong>03 · Compare</strong><p>Evaluate role requirements, matched skills, and missing evidence.</p></div>
  <div class="ara-arch-step"><strong>04 · Explain</strong><p>Show compatibility estimates, career options, and downloadable reports.</p></div>
 </div>
</section>
"""


def render() -> None:
    page_header(
        "PLATFORM / SYSTEM ARCHITECTURE",
        "Inside the intelligence engine.",
        "Explore the components behind AI-Resume-Analyzer and how information moves through the offline application.",
        "✦",
    )
    st.markdown(_ARCH_CSS + _ARCH_HTML, unsafe_allow_html=True)
    st.markdown("### Explore each layer")
    with st.expander("Presentation and user experience"):
        st.write("Streamlit provides the interface for login, uploads, analysis dashboards, Job Matching Studio, AI Career Finder, and report downloads. These pages call reusable Python services rather than implementing all matching logic in the UI.")
    with st.expander("Document processing and matching intelligence"):
        st.write("The resume parser extracts text from supported documents. Skill recognition resolves recognized aliases and occupation terminology. Job matching evaluates documented evidence against a selected title or pasted job description; Career Finder recommends related occupations. Scores are estimates, not employer ATS results or probabilities of hiring.")
    with st.expander("Access control and privacy"):
        st.write("User passwords are stored as hashes, and server-side role and ownership checks protect application functions. Resume data is stored locally by the configured SQLite application. Anyone with access to this computer or its backups may still pose a risk; protect backups and the operating system.")
    with st.expander("Local database, occupation catalog, and optional Ollama"):
        st.write("SQLite stores application records and local skill/occupation reference data. O*NET-derived occupational content can support matching and exploration. Ollama is an optional local language-model integration: the core matching pipeline is designed to work without paid AI services. Optional internet-connected integrations may need connectivity.")
    st.caption("University demo tip: explain the five layers from top to bottom, then open Job Matching Studio to demonstrate an evidence-backed comparison.")
