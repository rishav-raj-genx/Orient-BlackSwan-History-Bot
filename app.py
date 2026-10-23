import streamlit as st

from src.rag_pipeline import ask_question


st.set_page_config(page_title="History Bot", layout="centered")

st.markdown(
    """
    <style>
        :root {
            --obs-maroon: #6f1726;
            --obs-crimson: #9d2338;
            --obs-parchment: #f7f0df;
            --obs-ink: #30251f;
            --obs-gold: #b78a35;
        }

        html, body, [class*="st-"] {
            font-family: Georgia, "Times New Roman", serif;
        }

        .stApp {
            background:
                linear-gradient(rgba(247, 240, 223, 0.94), rgba(247, 240, 223, 0.94)),
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 3px,
                    rgba(111, 23, 38, 0.035) 3px,
                    rgba(111, 23, 38, 0.035) 4px
                );
            color: var(--obs-ink);
        }

        .block-container {
            max-width: 760px;
            padding-top: 4.5rem;
        }

        .catalogue-kicker {
            color: var(--obs-gold);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            margin-bottom: 0.55rem;
            text-align: center;
            text-transform: uppercase;
        }

        .catalogue-title {
            color: var(--obs-maroon);
            font-size: clamp(2.5rem, 7vw, 4.25rem);
            font-weight: 700;
            letter-spacing: -0.045em;
            line-height: 0.96;
            margin: 0;
            text-align: center;
        }

        .catalogue-subtitle {
            color: #66564d;
            font-size: 1.08rem;
            line-height: 1.65;
            margin: 1.25rem auto 1.75rem;
            max-width: 610px;
            text-align: center;
        }

        .academic-rule {
            align-items: center;
            color: var(--obs-gold);
            display: flex;
            gap: 0.85rem;
            justify-content: center;
            margin: 0 auto 2.25rem;
        }

        .academic-rule::before,
        .academic-rule::after {
            background: linear-gradient(90deg, transparent, var(--obs-gold));
            content: "";
            height: 1px;
            width: 110px;
        }

        .academic-rule::after {
            background: linear-gradient(90deg, var(--obs-gold), transparent);
        }

        div[data-testid="stTextInput"] label p {
            color: var(--obs-maroon);
            font-size: 1rem;
            font-weight: 700;
        }

        div[data-testid="stTextInput"] input {
            background-color: rgba(255, 253, 246, 0.92);
            border: 1px solid #ccb982;
            border-radius: 3px;
            color: var(--obs-ink);
            font-family: Georgia, "Times New Roman", serif;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: var(--obs-crimson);
            box-shadow: 0 0 0 1px var(--obs-crimson);
        }

        .stButton > button {
            background: var(--obs-maroon);
            border: 1px solid var(--obs-maroon);
            border-radius: 3px;
            color: #fffaf0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.025em;
            min-height: 3rem;
            width: 100%;
        }

        .stButton > button:hover,
        .stButton > button:focus {
            background: var(--obs-crimson);
            border-color: var(--obs-gold);
            color: #ffffff;
        }

        div[data-testid="stAlert"] {
            background-color: rgba(255, 252, 240, 0.94);
            border-left-color: var(--obs-gold);
            border-radius: 3px;
            color: var(--obs-ink);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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
        except Exception as exc:
            st.error(f"The catalogue search could not be completed: {exc}")
