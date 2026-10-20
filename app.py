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
        analyze_clicked = st.button("Analyze", type="primary", width="stretch")
    with btn_col2:
        st.button("Load sample data", on_click=load_sample_data, width="stretch")

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
    # Navigation and title
    if st.button("← Back to inputs", help="Return to input page"):
        st.session_state["current_view"] = "input"
        st.rerun()

    st.markdown(
        '<h1 style="font-size: 2.25rem; font-weight: 800; color: #111827; margin: 0.25rem 0 0.75rem 0; padding: 0; line-height: 1.2;">Screening results</h1>',
        unsafe_allow_html=True,
    )

    result = st.session_state.get("results")

    if result is not None:
        # 2. Directly under the title, full width, the disclaimer in st.info (keep the exact text).
        st.info(f"Notice: {DISCLAIMER_TEXT}")

        def _render_details(res):
            st.markdown("**Matched skills**")
            st.write(", ".join(res["matched_skills"]) if res["matched_skills"] else "None")

            st.markdown("**Missing skills**")
            st.write(", ".join(res["missing_skills"]) if res["missing_skills"] else "None")

            st.markdown("**Additional skills in resume**")
            st.write(", ".join(res["additional_skills"]) if res["additional_skills"] else "None")

            st.markdown("**Skill breakdown**")
            df = res["results_df"]
            st.dataframe(df, hide_index=True, width="stretch")

            with st.expander("How is this score calculated?"):
                st.write(
                    "Match score = (required skills found in resume / total required skills) * 100\n\n"
                    "- Required skills are skills extracted from the job description.\n"
                    "- Equal weighting across all required skills.\n"
                    "- Duplicate mentions of a skill count once.\n"
                    "- Additional skills in the resume are not counted in the score.\n"
                    "- If no recognized skills are found in the job description, the score is 0%."
                )

            exp_col1, exp_col2, _ = st.columns([1.5, 1.5, 3])
            with exp_col1:
                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download CSV",
                    data=csv_bytes,
                    file_name="skill_match_results.csv",
                    mime="text/csv",
                    width="stretch",
                )
            with exp_col2:
                json_payload = {
                    "matched_skills": res["matched_skills"],
                    "missing_skills": res["missing_skills"],
                    "match_score": res["match_score"],
                }
                json_bytes = json.dumps(json_payload, indent=2).encode("utf-8")
                st.download_button(
                    "Download JSON",
                    data=json_bytes,
                    file_name="skill_match_results.json",
                    mime="application/json",
                    width="stretch",
                )

        # If total_required == 0, skip the score panel and show only st.warning across full width
        if result["total_required"] == 0:
            st.warning(result["recommendation"])
            _render_details(result)
        else:
            # Two-column layout: left column for round score panel, right column for details
            col_score, col_details = st.columns([1, 2], gap="large")

            # Left column (centered, larger round score panel)
            with col_score:
                score_val = result["match_score"]
                # Circular progress geometry: r=66, circumference = 2 * pi * 66 = 414.69
                circumference = 414.69
                dashoffset = round(circumference * (1.0 - (score_val / 100.0)), 2)

                st.markdown(
                    f"""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; padding: 1.75rem 1.25rem; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); gap: 1rem;">
                        <span style="font-weight: 700; font-size: 1.35rem; color: #111827; text-align: center;">Match score</span>
                        <svg width="185" height="185" viewBox="0 0 160 160" style="display: block; margin: 0.25rem auto;">
                            <circle cx="80" cy="80" r="66" fill="none" stroke="#E5E7EB" stroke-width="13" />
                            <circle cx="80" cy="80" r="66" fill="none" stroke="#0F766E" stroke-width="13"
                                    stroke-linecap="round" stroke-dasharray="{circumference}" stroke-dashoffset="{dashoffset}"
                                    transform="rotate(-90 80 80)" />
                            <text x="80" y="93" text-anchor="middle" font-size="42px" font-weight="800" fill="#111827"
                                  font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
                                {score_val}%
                            </text>
                        </svg>
                        <div style="font-size: 1.1rem; font-weight: 500; color: #374151; line-height: 1.5; text-align: center;">
                            {result['matched_count']} of {result['total_required']} required skills found. {result['recommendation']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Right column (details)
            with col_details:
                _render_details(result)
    else:
        st.warning("No results found. Please return to the input page.")
