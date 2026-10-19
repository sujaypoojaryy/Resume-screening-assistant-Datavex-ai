"""Resume-to-Job Description Matching App.

A recruiter screening assistant built using Streamlit, scikit-learn, NumPy, and Pandas.
Implements a two-view architecture (Input View and Results View) using st.session_state.
"""
import json
import streamlit as st

from matcher.extract import SkillExtractor
from matcher.scoring import calculate_match, DISCLAIMER_TEXT
from matcher.parsers import (
    extract_text_from_file,
    validate_raw_text,
    ParsingError,
    ValidationError,
)

st.set_page_config(
    page_title="Resume-to-Job Description Matcher",
    layout="wide"
)

# Apply font-family only to body to prevent overriding Streamlit icon glyphs
st.markdown("""
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .score-title {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    .score-subtitle {
        font-size: 1rem;
        color: #4B5563;
        margin-top: 0.25rem;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_extractor() -> SkillExtractor:
    """Initialize and cache the skill extractor."""
    return SkillExtractor()


extractor = get_extractor()

# Benchmark sample data
SAMPLE_JD = "Python, SQL, Machine Learning, Pandas"
SAMPLE_RESUME = "Python, Pandas, SQL, Excel"

# Initialize Session State
if "current_view" not in st.session_state:
    st.session_state["current_view"] = "input"
if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""
if "jd_text" not in st.session_state:
    st.session_state["jd_text"] = ""
if "file_resume_text" not in st.session_state:
    st.session_state["file_resume_text"] = None
if "file_jd_text" not in st.session_state:
    st.session_state["file_jd_text"] = None
if "results" not in st.session_state:
    st.session_state["results"] = None

# Preserve keyed widget values across views where the widgets are unrendered
for key in ("resume_text", "jd_text"):
    st.session_state[key] = st.session_state[key]


def load_sample_data():
    """Populate text inputs with sample benchmark data."""
    st.session_state["resume_text"] = SAMPLE_RESUME
    st.session_state["jd_text"] = SAMPLE_JD


# =========================================================================
# VIEW 1: INPUT PAGE
# =========================================================================
if st.session_state["current_view"] == "input":
    st.title("Resume-to-Job Description Matcher")
    st.write("Recruiter screening assistant to extract skills and compare resume content against job requirements.")
    st.markdown("---")

    # Resume and Job description side by side in two equal columns
    col_resume, col_jd = st.columns(2, gap="large")

    with col_resume:
        st.subheader("Resume")
        resume_file = st.file_uploader(
            "Upload resume (.pdf, .docx, .txt)",
            type=["pdf", "docx", "txt"],
            key="file_resume",
            help="Maximum file size 5 MB"
        )
        if resume_file is not None:
            try:
                st.session_state["file_resume_text"] = extract_text_from_file(
                    resume_file, filename=resume_file.name
                )
                st.caption(f"Loaded {resume_file.name}")
            except (ValidationError, ParsingError) as err:
                st.session_state["file_resume_text"] = None
                st.error(str(err))
            except Exception as err:
                st.session_state["file_resume_text"] = None
                st.error(f"Error reading file: {err}")
        else:
            st.session_state["file_resume_text"] = None

        st.caption("An uploaded file takes priority over pasted text.")

        st.text_area(
            "Or paste resume text",
            key="resume_text",
            height=200,
            placeholder="Paste resume text here..."
        )

    with col_jd:
        st.subheader("Job description")
        jd_file = st.file_uploader(
            "Upload job description (.pdf, .docx, .txt)",
            type=["pdf", "docx", "txt"],
            key="file_jd",
            help="Maximum file size 5 MB"
        )
        if jd_file is not None:
            try:
                st.session_state["file_jd_text"] = extract_text_from_file(
                    jd_file, filename=jd_file.name
                )
                st.caption(f"Loaded {jd_file.name}")
            except (ValidationError, ParsingError) as err:
                st.session_state["file_jd_text"] = None
                st.error(str(err))
            except Exception as err:
                st.session_state["file_jd_text"] = None
                st.error(f"Error reading file: {err}")
        else:
            st.session_state["file_jd_text"] = None

        st.caption("An uploaded file takes priority over pasted text.")

        st.text_area(
            "Or paste job description text",
            key="jd_text",
            height=200,
            placeholder="Paste job description text here..."
        )

    # Action buttons below the columns
    st.markdown("<br>", unsafe_allow_html=True)
    btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 5])
    with btn_col1:
        analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)
    with btn_col2:
        st.button("Load sample data", on_click=load_sample_data, use_container_width=True)

    if analyze_clicked:
        # Effective text prioritizes uploaded file content if present, else pasted text
        effective_resume = (
            st.session_state.get("file_resume_text")
            if st.session_state.get("file_resume_text")
            else st.session_state.get("resume_text", "")
        )
        effective_jd = (
            st.session_state.get("file_jd_text")
            if st.session_state.get("file_jd_text")
            else st.session_state.get("jd_text", "")
        )

        try:
            valid_resume = validate_raw_text(effective_resume, document_name="Resume")
            valid_jd = validate_raw_text(effective_jd, document_name="Job description")
        except ValidationError as ve:
            # Stay on this view and show validation error clearly
            st.error(str(ve))
            st.stop()

        with st.spinner("Analyzing skills and computing match score..."):
            jd_skills = extractor.extract_skills(valid_jd)
            resume_skills = extractor.extract_skills(valid_resume)
            result = calculate_match(jd_skills, resume_skills)

            # Store in session state and switch views
            st.session_state["results"] = result
            st.session_state["current_view"] = "results"
            st.rerun()


# =========================================================================
# VIEW 2: RESULTS PAGE
# =========================================================================
elif st.session_state["current_view"] == "results":
    # Top navigation: Back to inputs button
    if st.button("← Back to inputs"):
        st.session_state["current_view"] = "input"
        st.rerun()

    st.title("Screening Results")

    result = st.session_state.get("results")

    if result is not None:
        # Disclaimer in st.info
        st.info(f"Notice: {DISCLAIMER_TEXT}")

        # If no recognized skills in JD, show warning and skip score title, subtitle, and progress bar
        if result["total_required"] == 0:
            st.warning(result["recommendation"])
        else:
            # Full-width score and thin progress bar
            st.markdown(f'<div class="score-title">Match score: {result["match_score"]}%</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="score-subtitle">{result["matched_count"]} of {result["total_required"]} required skills found. Review recommended.</div>',
                unsafe_allow_html=True
            )

            progress_val = result["match_score"] / 100.0
            st.progress(progress_val)

        st.markdown("---")

        # Matched / missing / additional skills in three columns
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("**Matched skills**")
            if result["matched_skills"]:
                st.write(", ".join(result["matched_skills"]))
            else:
                st.write("None")

        with col_m2:
            st.markdown("**Missing skills**")
            if result["missing_skills"]:
                st.write(", ".join(result["missing_skills"]))
            else:
                st.write("None")

        with col_m3:
            st.markdown("**Additional skills in resume**")
            if result["additional_skills"]:
                st.write(", ".join(result["additional_skills"]))
            else:
                st.write("None")

        st.markdown("---")

        # Results table (Pandas DataFrame)
        st.markdown("**Skill breakdown**")
        df = result["results_df"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        # "How is this score calculated?" expander
        with st.expander("How is this score calculated?"):
            st.write(
                "Match score = (required skills found in resume / total required skills) * 100\n\n"
                "- Required skills are skills extracted from the job description.\n"
                "- Equal weighting across all required skills.\n"
                "- Duplicate mentions of a skill count once.\n"
                "- Additional skills in the resume are not counted in the score.\n"
                "- If no recognized skills are found in the job description, the score is 0%."
            )

        # Download JSON and CSV buttons at the bottom
        st.markdown("<br>", unsafe_allow_html=True)
        exp_col1, exp_col2, _ = st.columns([1.5, 1.5, 5])
        with exp_col1:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name="skill_match_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with exp_col2:
            json_payload = {
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"],
                "match_score": result["match_score"]
            }
            json_bytes = json.dumps(json_payload, indent=2).encode("utf-8")
            st.download_button(
                "Download JSON",
                data=json_bytes,
                file_name="skill_match_results.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.warning("No results found. Please return to the input page.")
