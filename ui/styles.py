import streamlit as st


def load_custom_css() -> None:
    """
    Apply the custom CSS used throughout the ResumeAI application.
    Professional dark navy + blue theme.
    """

    st.markdown(
        """
        <style>

        /* =========================================================
           GLOBAL APPLICATION
           ========================================================= */

        .stApp {
            background: #0b1120;
            color: #e2e8f0;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Main text */
        .stApp p,
        .stApp label,
        .stApp span {
            color: #cbd5e1;
        }

        /* =========================================================
           HEADER
           ========================================================= */

        .resumeai-header {
            background: linear-gradient(
                135deg,
                #111c35 0%,
                #16264a 55%,
                #20205a 100%
            );

            border: 1px solid #26375c;
            border-radius: 18px;

            padding: 2rem 2.2rem;
            margin-bottom: 1.5rem;

            box-shadow:
                0 12px 35px rgba(0, 0, 0, 0.30);
        }

        .resumeai-title {
            font-size: 2.7rem;
            font-weight: 800;
            color: #f8fafc !important;

            margin-bottom: 0.25rem;
            letter-spacing: -1px;
        }

        .resumeai-title span {
            color: #60a5fa !important;
        }

        .resumeai-subtitle {
            font-size: 1.05rem;
            color: #94a3b8 !important;
            margin-top: 0;
        }

        /* =========================================================
           SECTION HEADINGS
           ========================================================= */

        .section-title {
            color: #f1f5f9 !important;
            font-size: 1.45rem;
            font-weight: 750;

            margin-top: 1.5rem;
            margin-bottom: 0.25rem;
        }

        .section-description {
            color: #94a3b8 !important;
            margin-bottom: 1rem;
        }

        /* =========================================================
           FEATURE CARDS
           ========================================================= */

        .feature-card {
            background: #111827;

            border: 1px solid #26334d;
            border-radius: 16px;

            padding: 1.35rem;

            min-height: 150px;

            box-shadow:
                0 8px 25px rgba(0, 0, 0, 0.20);

            transition:
                transform 0.2s ease,
                border-color 0.2s ease,
                box-shadow 0.2s ease;
        }

        .feature-card:hover {
            transform: translateY(-3px);

            border-color: #3b82f6;

            box-shadow:
                0 12px 30px rgba(37, 99, 235, 0.15);
        }

        .feature-card h3 {
            margin-top: 0;

            color: #f8fafc !important;
            font-size: 1.1rem;
        }

        .feature-card p {
            color: #94a3b8 !important;
            line-height: 1.6;
        }

        /* =========================================================
           FILE UPLOADER
           ========================================================= */

        [data-testid="stFileUploader"] {
            background: #111827;

            border: 2px dashed #334155;
            border-radius: 14px;

            padding: 0.8rem;

            transition:
                border-color 0.2s ease,
                background 0.2s ease;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #3b82f6;
            background: #131d31;
        }

        [data-testid="stFileUploader"] section {
            background: transparent !important;
        }

        /* =========================================================
           TEXT AREA
           ========================================================= */

        textarea {
            background-color: #111827 !important;

            color: #e2e8f0 !important;

            border: 1px solid #334155 !important;

            border-radius: 12px !important;
        }

        textarea:focus {
            border-color: #3b82f6 !important;

            box-shadow:
                0 0 0 1px #3b82f6 !important;
        }

        textarea::placeholder {
            color: #64748b !important;
        }

        /* =========================================================
           BUTTON
           ========================================================= */

        .stButton > button {
            background: linear-gradient(
                135deg,
                #2563eb,
                #4f46e5
            );

            color: white !important;

            border: none;

            border-radius: 10px;

            font-weight: 700;

            padding: 0.65rem 1.2rem;

            box-shadow:
                0 6px 18px rgba(37, 99, 235, 0.25);

            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);

            box-shadow:
                0 10px 25px rgba(37, 99, 235, 0.35);
        }

        /* =========================================================
           METRICS
           ========================================================= */

        [data-testid="stMetric"] {
            background: #111827;

            border: 1px solid #26334d;

            border-radius: 14px;

            padding: 1rem;
        }

        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
        }

        [data-testid="stMetricValue"] {
            color: #60a5fa !important;
        }

        /* =========================================================
           STATUS CARD
           ========================================================= */

        .status-card {
            background: #10203b;

            border: 1px solid #1d4ed8;

            border-radius: 14px;

            padding: 1rem 1.2rem;

            color: #bfdbfe;
        }

        /* =========================================================
           STREAMLIT ALERTS
           ========================================================= */

        [data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* =========================================================
           SIDEBAR
           ========================================================= */

        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #080f1f 0%,
                #0c162b 100%
            );

            border-right: 1px solid #1e293b;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #f8fafc !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: #94a3b8 !important;
        }

        /* Sidebar divider */
        [data-testid="stSidebar"] hr {
            border-color: #1e293b;
        }

        /* =========================================================
           RADIO BUTTON
           ========================================================= */

        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: transparent;

            border-radius: 8px;

            padding: 0.35rem 0.5rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: #16233d;
        }

        /* =========================================================
           DIVIDERS
           ========================================================= */

        hr {
            border-color: #1e293b !important;
        }

        /* =========================================================
           FOOTER
           ========================================================= */

        .resumeai-footer {
            text-align: center;

            color: #64748b !important;

            font-size: 0.85rem;

            padding-top: 2rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )