import streamlit as st
from src.rag_pipeline import ask_question

st.set_page_config(page_title="History Bot", layout="centered")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap');

        /* Base App & Film Grain Overlay */
        .stApp {
            background-color: #1a1310 !important;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
            color: #E7E5E4 !important;
            font-family: 'Manrope', sans-serif !important;
        }

        /* Typography Overrides */
        h1, h2, h3, p, span, div, label {
            font-family: 'Manrope', sans-serif !important;
            color: #E7E5E4 !important;
        }

        /* Secondary/Muted Text */
        label p, .st-emotion-cache-16idsys p {
            color: #A8A29E !important;
        }

        /* Input Fields (Card Surface) */
        .stTextInput > div > div > input {
            background-color: #28201E !important;
            border: 1px solid #292524 !important;
            color: #E7E5E4 !important;
            border-radius: 4px !important;
        }

        /* Buttons (Lava Red Accent) */
        .stButton > button {
            background-color: #D93829 !important;
            color: #E7E5E4 !important;
            border: 1px solid #292524 !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease-in-out !important;
        }

        .stButton > button:hover {
            background-color: #EA580C !important;
            border-color: #F59E0B !important;
            color: #ffffff !important;
        }

        /* Alert Boxes (Results) */
        div[data-testid="stAlert"] {
            background-color: #28201E !important;
            border: 1px solid #D93829 !important;
            border-radius: 4px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4) !important;
        }

        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span {
            color: #E7E5E4 !important;
            font-size: 16px !important;
            font-weight: 600 !important;
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown(
        """
        <div class="catalogue-kicker">Orient BlackSwan Digital Reference Desk</div>
        <h1 class="catalogue-title">History Bot</h1>
        <p class="catalogue-subtitle">
            Search the Orient BlackSwan History 2024–25 catalogue through a
            strictly grounded research assistant.
        </p>
        <div class="academic-rule" aria-hidden="true">◆</div>
        """,
        unsafe_allow_html=True,
    )

with st.container():
    query: str = st.text_input(
        "Ask the catalogue",
        placeholder="e.g. When were the catalogue prices last updated?",
    )

    if st.button("Search Catalogue", type="primary"):
        if not query.strip():
            st.warning("Enter a question before searching the catalogue.")
        else:
            try:
                with st.spinner("Consulting the history catalogue..."):
                    answer: str = ask_question(query)

                if answer == "Not found":
                    st.info(answer)
                else:
                    st.success(answer)
            except Exception:
                st.error(
                    "An error occurred while processing your request. "
                    "Please verify your API key and try again."
                )
