
import streamlit as st
import language_tool_python
import nltk
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from collections import Counter

st.set_page_config(
    page_title="Grammar Assistant",
    page_icon="✍️",
    layout="wide"
)

# ---------- SESSION STATE ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- THEME ----------
theme = st.sidebar.radio("Theme", ["Dark", "Light"])
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {background:#101522;color:#f4f6fb}
    div[data-testid="stMetric"] {
        background:#202a3d;padding:15px;border-radius:12px}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {background:#f5f7fb;color:#172033}
    div[data-testid="stMetric"] {
        background:white;padding:15px;border-radius:12px}
    </style>
    """, unsafe_allow_html=True)

# ---------- TITLE ----------
st.title("✍️ Grammar Error Detection & Correction")
st.caption("An NLP-powered English writing assistant")

@st.cache_resource
def load_tool():
    return language_tool_python.LanguageTool("en-US")

@st.cache_resource
def load_nlp():
    return WordNetLemmatizer()

# ---------- INPUT ----------
text = st.text_area(
    "Enter your English text",
    height=200,
    placeholder="Example: She go to college every day."
)

col1, col2 = st.columns(2)
with col1:
    check_button = st.button("🔍 Check Grammar", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear Text", use_container_width=True)

if clear_button:
    st.session_state.input_text = ""
    st.rerun()

# ---------- GRAMMAR CHECK ----------
if check_button:
    if not text.strip():
        st.warning("Please enter some text before checking.")
    else:
        try:
            with st.spinner("Analyzing your text..."):
                tool = load_tool()
                matches = tool.check(text)
                corrected = language_tool_python.utils.correct(
                    text, matches
                )

            st.session_state.last_text = text
            st.session_state.corrected = corrected
            st.session_state.matches = [
                {
                    "message": m.message,
                    "context": m.context,
                    "offset": m.offset,
                    "length": m.errorLength,
                    "suggestions": m.replacements[:5],
                    "rule": m.ruleId,
                    "category": str(m.category)
                }
                for m in matches
            ]
            st.session_state.history.insert(
                0, {"Original": text, "Corrected": corrected}
            )
            st.success("Grammar check completed!")

        except Exception as error:
            st.error(
                "Grammar checking failed. Check the environment's "
                "internet access and LanguageTool setup."
            )
            st.caption(str(error))

# ---------- RESULTS ----------
if "corrected" in st.session_state:
    original = st.session_state.last_text
    corrected = st.session_state.corrected
    errors = st.session_state.matches

    st.divider()
    st.subheader("📋 Correction Results")

    a, b, c = st.columns(3)
    a.metric("Words", len(original.split()))
    b.metric("Issues detected", len(errors))
    c.metric("Characters", len(original))

    left, right = st.columns(2)
    with left:
        st.markdown("#### Original Text")
        st.text_area("Original", original, height=180,
                     disabled=True, label_visibility="collapsed")
    with right:
        st.markdown("#### Corrected Text")
        st.text_area("Corrected", corrected, height=180,
                     disabled=True, label_visibility="collapsed")
        st.download_button(
            "⬇️ Download corrected text",
            corrected,
            file_name="corrected_text.txt",
            mime="text/plain"
        )

    st.subheader("🧠 Error Explanations")
    if not errors:
        st.success("No issues were reported by the grammar checker.")
    else:
        for i, error in enumerate(errors, 1):
            with st.expander(f"Issue {i}: {error['message']}"):
                st.write("**Context:**", error["context"])
                st.write("**Category:**", error["category"])
                st.write("**Rule:**", error["rule"])
                if error["suggestions"]:
                    st.write("**Suggestions:**")
                    st.write(", ".join(error["suggestions"]))
                else:
                    st.write("No alternative suggestion provided.")

    # ---------- NLP ANALYSIS ----------
    st.divider()
    st.subheader("🔬 NLP Analysis")

    try:
        tokens = word_tokenize(original)
        tags = pos_tag(tokens)
        lem = load_nlp()

        x, y = st.columns(2)
        x.metric("Tokens", len(tokens))
        y.metric("Unique words", len(set(t.lower() for t in tokens)))

        st.markdown("#### Part-of-Speech Tags")
        st.dataframe(
            [{"Word": word, "POS Tag": tag} for word, tag in tags],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Lemmatization")
        st.dataframe(
            [{"Word": word, "Lemma": lem.lemmatize(word.lower())}
             for word in tokens if word.isalpha()],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Most Frequent Words")
        frequencies = Counter(
            word.lower() for word in tokens if word.isalpha()
        )
        st.bar_chart(dict(frequencies.most_common(10)))

    except LookupError:
        st.warning(
            "NLTK language data is missing. Install the required "
            "NLTK resources in your hosted environment."
        )
    except Exception as error:
        st.warning(f"NLP analysis could not run: {error}")

# ---------- HISTORY ----------
st.divider()
st.subheader("🕘 Recent Checking History")

if st.session_state.history:
    st.dataframe(
        st.session_state.history[:10],
        use_container_width=True,
        hide_index=True
    )
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("Your recent checks will appear here during this session.")

st.caption("Grammar suggestions are automated and may not always be correct.")
