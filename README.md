# Resume-to-Job Description Matching Web App

A recruiter screening assistant that extracts technical skills from candidate resumes and job descriptions, calculates a match score, and highlights matched and missing skills. Built for recruiters to assist and speed up manual review—never to automate rejection decisions.

---

## 1. Tech Stack

- **Language:** Python 3 (tested with Python 3.13)
- **Web UI:** Streamlit (pure Python, clean restrained UI without marketing fluff)
- **Skill Extraction:** scikit-learn (`CountVectorizer` with a custom vocabulary and n-gram range up to 3)
- **Score Computation & Arrays:** NumPy (binary skill vectors and set/array operations)
- **Data & Reporting:** Pandas (skills taxonomy loading, tabular results matrix, CSV export)
- **Document Parsing:** `pypdf` (PDF), `python-docx` (Word .docx), plain text (UTF-8 with Latin-1 fallback)
- **Testing:** `pytest` (17 test cases)

---

## 2. Project Structure

```
d:\Datavex AI\
├── app.py                      # Main Streamlit application
├── config/
│   └── skills.json             # Canonical skills and alias mappings
├── matcher/
│   ├── __init__.py             # Package exports
│   ├── normalize.py            # Text cleaning & special token preservation (C++, C#, .NET, etc.)
│   ├── parsers.py              # PDF, DOCX, and TXT parsing with size & format validation
│   ├── extract.py              # CountVectorizer skill extraction
│   └── scoring.py              # NumPy binary score computation & Pandas results DataFrame
├── tests/
│   ├── __init__.py
│   └── test_matcher.py         # Comprehensive pytest suite (TC1-TC7, edge cases)
├── requirements.txt            # Dependency manifest
├── sample_output.json          # Benchmark JSON output matching prompt specification
└── README.md                   # System documentation and interview guide
```

---

## 3. Installation & Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd "d:\Datavex AI"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run unit tests:**
   ```bash
   python -m pytest -v
   ```

4. **Launch the web application:**
   ```bash
   streamlit run app.py
   ```
   *(or `python -m streamlit run app.py`)*

---

## 4. How Each Library Is Used

| Library | Primary Responsibility in the App |
| :--- | :--- |
| **scikit-learn** | `CountVectorizer` builds an n-gram vocabulary (1 to 3 words) from canonical skill names and aliases. It tokenizes documents while preserving exact multi-word boundaries. |
| **NumPy** | Performs binary vector operations. Required skills are encoded into binary mask arrays. NumPy bitwise AND (`req_vector & res_vector`) and `np.sum()` compute matched count and score without loops. |
| **Pandas** | Loads and structures the skill configuration taxonomy into a DataFrame. Generates the final skills matrix (`Skill`, `In JD`, `In Resume`, `Status`) and powers CSV exports. |
| **pypdf** | Reads PDF documents page-by-page, detecting encryption and handling scanned/image-only PDFs gracefully. |
| **python-docx** | Traverses both body paragraphs and table cells inside `.docx` resumes. |

---

## 5. Scoring Formula & Rules

### Mathematical Formula
$$\text{Match Score} = \left( \frac{\text{Required Skills Found in Resume}}{\text{Total Required Skills in Job Description}} \right) \times 100$$

### Rules & Principles
1. **Equal Weighting:** Every required technical skill detected in the Job Description carries equal weight.
2. **Order Preservation:** Skills are ordered by their first appearance in the Job Description.
3. **De-duplication:** Repeated mentions of a skill (e.g., Python mentioned 5 times) are counted exactly once via binary arrays.
4. **Additional Skills:** Skills present in the resume but not required by the Job Description are categorized under *"Additional skills in resume"* for recruiter review; they are **not** counted toward or against the score.
5. **Zero Skills Safeguard:** If a job description contains no recognized technical skills, the score is reported as `0%` with a neutral notice, avoiding any division-by-zero error.
6. **Recruiter-Assist Disclaimer:** The app displays the disclaimer banner:
   > *"Notice: This score reflects text overlap with the job description and is not a definitive measure of candidate quality. It should assist, not replace, human review."*
7. **Neutral Phrasing:** The tool never uses negative words like "Rejected" or "Unsuitable". It uses neutral labels such as *"Review recommended."*

---

## 6. How to Add Skills and Aliases

Edit `config/skills.json`. Add a new canonical skill name as the key, and a list of alternative names or aliases as the value:

```json
{
  "scikit-learn": ["sklearn", "scikit learn"],
  "Machine Learning": ["ML"],
  "Rust": ["rustlang"],
  "PostgreSQL": ["postgres"]
}
```

The system automatically normalizes both keys and aliases, updates the `CountVectorizer` vocabulary, and ensures identical matching across both JD and resumes.

---

## 7. Sample Input and Expected Output

### Input
- **Job Description:** `"We are seeking a data scientist with strong proficiency in Python, SQL, Machine Learning, and Pandas."`
- **Candidate Resume:** `"Experienced candidate skilled in Python, Pandas, SQL, and Excel for quantitative analysis."`

### Benchmark Output (`sample_output.json`)
```json
{
  "matched_skills": [
    "Python",
    "SQL",
    "Pandas"
  ],
  "missing_skills": [
    "Machine Learning"
  ],
  "match_score": 75
}
```

---

## 8. Pytest Test Results

All 17 test cases pass:

```
============================= test session starts =============================
platform win32 -- Python 3.13.6, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Datavex AI
collected 17 items

tests/test_matcher.py::test_main_example PASSED                          [  5%]
tests/test_matcher.py::test_tc1_all_three_matched PASSED                 [ 11%]
tests/test_matcher.py::test_tc2_no_required_skills PASSED                [ 17%]
tests/test_matcher.py::test_tc3_every_required_skill_present PASSED      [ 23%]
tests/test_matcher.py::test_tc4_duplicate_mentions_counted_once PASSED   [ 29%]
tests/test_matcher.py::test_tc5_empty_resume_validation PASSED           [ 35%]
tests/test_matcher.py::test_tc6_alias_normalization PASSED               [ 41%]
tests/test_matcher.py::test_tc7_extra_unrelated_skills_not_counted PASSED [ 47%]
tests/test_matcher.py::test_java_vs_javascript PASSED                    [ 52%]
tests/test_matcher.py::test_special_tokens_cpp_csharp_dotnet_nodejs PASSED [ 58%]
tests/test_matcher.py::test_zero_recognized_skills_in_jd PASSED          [ 64%]
tests/test_matcher.py::test_clean_text_hyphenated_line_breaks PASSED     [ 70%]
tests/test_matcher.py::test_identical_skills_across_pdf_docx_txt PASSED  [ 76%]
tests/test_matcher.py::test_docx_table_parsing PASSED                    [ 82%]
tests/test_matcher.py::test_unsupported_file_type PASSED                 [ 88%]
tests/test_matcher.py::test_file_too_large PASSED                        [ 94%]
tests/test_matcher.py::test_empty_or_corrupted_pdf PASSED                [100%]

============================= 17 passed in 2.65s ==============================
```

---

## 9. Interview Talking Points

1. **Why `CountVectorizer` with a custom vocabulary instead of simple regex strings?**
   - Simple string searches like `"Java" in text` will incorrectly match `"JavaScript"`. `CountVectorizer` extracts tokens with exact n-gram token boundaries.
   - It also handles multiple aliases mapping back to one canonical skill in a single vectorized pass.
2. **Handling tricky programming language tokens (C++, C#, .NET, Node.js):**
   - Standard NLP tokenizers discard symbols like `+`, `#`, and `.`. In `matcher/normalize.py`, special tokens are mapped to safe placeholders (`__c_plus_plus__`, `__c_sharp__`, `__dot_net__`, `__node_js__`) before general punctuation stripping.
3. **Using NumPy for matching:**
   - Rather than nested Python loops or repeated lookups, NumPy binary vectors represent skills found in JD and candidate resumes. Set operations are computed via bitwise operators (`&`) and `np.sum()`.
4. **Ethical AI & Recruiter Assist Principle:**
   - Text matching does not represent soft skills, adaptability, or project depth. The tool explicitly guards against automated rejection, displays prominent disclaimers, and uses neutral guidance language.
