# Resume-to-Job Description Matcher

A recruiter screening assistant. It extracts technical skills from a resume and a job description, calculates a match score, and lists matched, missing and additional skills. It is meant to support manual review, never to reject candidates automatically.

---

## 1. Tech stack

- **Language:** Python 3 (tested with Python 3.13)
- **Web UI:** Streamlit
- **Skill extraction:** scikit-learn (`CountVectorizer` with a custom vocabulary, n-gram range up to the longest skill name)
- **Score computation:** NumPy (binary skill vector)
- **Data and reporting:** Pandas (skills config loading, results table, CSV & JSON export)
- **Document parsing:** `pypdf` (PDF), `python-docx` (DOCX), plain text (UTF-8 with Latin-1 fallback)
- **Testing:** `pytest` (38 test cases)

---

## 2. Project structure

```
project-folder/
├── app.py                  # Streamlit application (input page and results page)
├── config/
│   └── skills.json         # Canonical skills and aliases
├── matcher/
│   ├── __init__.py
│   ├── normalize.py        # Text cleaning, special tokens (C++, C#, .NET, Node.js)
│   ├── parsers.py          # PDF, DOCX, TXT parsing and file validation
│   ├── extract.py          # CountVectorizer skill extraction
│   └── scoring.py          # Score calculation and results DataFrame
├── tests/
│   ├── __init__.py
│   └── test_matcher.py     # pytest suite (38 test cases)
├── .streamlit/
│   └── config.toml         # Streamlit settings (5 MB upload limit)
├── .gitignore
├── requirements.txt
├── sample_output.json      # Output for the benchmark example
└── README.md
```

---

## 3. Setup and run

1. Go into the project folder:
```bash
   cd project-folder
```

2. Install the dependencies:
```bash
   pip install -r requirements.txt
```

3. Run the tests:
```bash
   python -m pytest -v
```

4. Start the web app:
```bash
   python -m streamlit run app.py
```

---

## 4. How each library is used

| Library | Use in this project |
| :--- | :--- |
| **scikit-learn** | `CountVectorizer` is built with a custom vocabulary made from the skill names and aliases in `skills.json`. It counts which skill terms appear in a document, including multi-word skills. |
| **NumPy** | For each required skill, a binary vector marks whether the resume contains it (1) or not (0). The sum of the vector is the number of matched skills. |
| **Pandas** | Loads `skills.json` into a DataFrame, builds the results table (Skill, In JD, In Resume, Status), and exports it to CSV. |
| **pypdf** | Reads PDF files page by page and detects password-protected and image-only files. |
| **python-docx** | Reads paragraphs and table cells from DOCX files. |

---

## 5. Input formats and validation

- Resume and job description can each be pasted as text or uploaded as PDF, DOCX or TXT (maximum 5 MB).
- If a file is uploaded, it is used instead of the pasted text.
- Clear error messages are shown for:
  - empty or whitespace-only input
  - unsupported file types
  - files larger than 5 MB
  - corrupted, password-protected or scanned (image-only) PDFs, with a suggestion to paste the text instead
- Extracted text is cleaned (hyphenated line breaks, bullets, unusual characters) so that results are the same whichever format the text came from.

---

## 6. Scoring formula and rules

```
Match score = (required skills found in resume / total required skills in job description) x 100
```

1. **Required skills** are the skills found in the job description.
2. **Equal weighting:** every required skill counts the same.
3. **Order:** matched and missing skills follow the order in the job description.
4. **Duplicates:** a skill mentioned several times counts once.
5. **Additional skills:** skills in the resume that are not in the job description are listed separately and do not change the score.
6. **No recognized skills in the job description:** no score is shown. The app displays a neutral warning asking for manual review. There is no division by zero.
7. **Disclaimer** shown with every result:
   > This score reflects text overlap with the job description and is not a definitive measure of candidate quality. It should assist, not replace, human review.
8. **Neutral wording:** the app only says "Review recommended." It never uses words such as "Rejected" or "Not suitable".

---

## 7. How to add skills and aliases

Edit `config/skills.json`. The key is the canonical skill name and the value is a list of aliases:

```json
{
  "scikit-learn": ["sklearn", "scikit learn", "scikitlearn"],
  "Machine Learning": ["ML"],
  "PostgreSQL": ["postgres", "pgsql"],
  "SQL": ["structured query language"]
}
```

### Alias Design and Disambiguation Principles
To prevent misleading false-positive matches, distinct technologies are never conflated as aliases:
- **Git vs GitHub:** Git is the version control system; GitHub is a hosting platform. They are separate skills.
- **Bash vs Linux:** Bash is a shell scripting language; Linux is an operating system.
- **TypeScript:** Ambiguous two-letter acronym "TS" is not aliased to TypeScript (avoids collisions with transport streams, security clearances, etc.).
- **TensorFlow:** Ambiguous abbreviation "tf" is not aliased to TensorFlow (avoids collisions with term frequency / TF-IDF).
- **PostgreSQL vs SQL:** PostgreSQL is a specific relational database management system; SQL is the query language standard.
- **SQL vs NoSQL:** Exact word boundary matching ensures NoSQL never falsely triggers SQL.
- **scikit-learn:** Genuine synonyms (`sklearn`, `scikit learn`, `scikitlearn`) map accurately to the canonical `scikit-learn`.

---

## 8. Sample input and output

**Job description:** `Python, SQL, Machine Learning, Pandas`
**Resume:** `Python, Pandas, SQL, Excel`

`sample_output.json`:

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

Excel is shown under "Additional skills in resume" and is not counted.

---

## 9. Known limitations

- Only skills listed in `config/skills.json` are detected. Synonyms or aliases that are not in the dictionary are not recognized.
- Matching is keyword and alias-based and does not infer semantic context or seniority (e.g., "no experience in Python" still detects "Python").
- Bare single-letter skills (like isolated "R" or "C") are excluded from bare matching to prevent false positives with common acronyms/terms (e.g., "R&D", "Type C"); specific phrases like "R programming" and "C programming" are used instead.
- All required skills have equal weight in the score calculation.
- Scanned or image-only PDFs have no extractable text layer and must be pasted directly as text.
- The score measures text overlap only. It is not a definitive measure of candidate quality, and a person must review every result.

---

## 10. Test results

All 38 tests pass.

```
============================= test session starts =============================
platform win32 -- Python 3.13.6, pytest-9.1.1, pluggy-1.6.0
rootdir: project-folder
collecting ... collected 38 items

tests/test_matcher.py::test_main_example PASSED                          [  2%]
tests/test_matcher.py::test_tc1_all_three_matched PASSED                 [  5%]
tests/test_matcher.py::test_tc2_no_required_skills PASSED                [  7%]
tests/test_matcher.py::test_tc3_every_required_skill_present PASSED      [ 10%]
tests/test_matcher.py::test_tc4_duplicate_mentions_counted_once PASSED   [ 13%]
tests/test_matcher.py::test_tc5_empty_resume_validation PASSED           [ 15%]
tests/test_matcher.py::test_tc6_alias_normalization PASSED               [ 18%]
tests/test_matcher.py::test_tc7_extra_unrelated_skills_not_counted PASSED [ 21%]
tests/test_matcher.py::test_java_vs_javascript PASSED                    [ 23%]
tests/test_matcher.py::test_special_tokens_cpp_csharp_dotnet_nodejs PASSED [ 26%]
tests/test_matcher.py::test_zero_recognized_skills_in_jd PASSED          [ 28%]
tests/test_matcher.py::test_clean_text_hyphenated_line_breaks PASSED     [ 31%]
tests/test_matcher.py::test_single_letter_skill_detection PASSED         [ 34%]
tests/test_matcher.py::test_negative_matching_rd_and_type_c PASSED       [ 36%]
tests/test_matcher.py::test_negative_matching_tfidf_and_ts_sci PASSED    [ 39%]
tests/test_matcher.py::test_positive_matching_nosql_and_reactjs PASSED   [ 42%]
tests/test_matcher.py::test_pdf_line_wrap_hyphenation PASSED             [ 44%]
tests/test_matcher.py::test_spaced_and_joined_forms_deduplicated PASSED  [ 47%]
tests/test_matcher.py::test_multi_word_skill_detection PASSED            [ 50%]
tests/test_matcher.py::test_scikit_learn_hyphenated_linebreak_extraction PASSED [ 52%]
tests/test_matcher.py::test_identical_skills_across_pdf_docx_txt PASSED  [ 55%]
tests/test_matcher.py::test_docx_table_parsing PASSED                    [ 57%]
tests/test_matcher.py::test_unsupported_file_type PASSED                 [ 60%]
tests/test_matcher.py::test_file_too_large PASSED                        [ 63%]
tests/test_matcher.py::test_empty_or_corrupted_pdf PASSED                [ 65%]
tests/test_matcher.py::test_empty_file_error PASSED                      [ 68%]
tests/test_matcher.py::test_password_protected_pdf_error PASSED          [ 71%]
tests/test_matcher.py::test_alias_separation_git_vs_github PASSED        [ 73%]
tests/test_matcher.py::test_alias_separation_bash_vs_linux PASSED        [ 76%]
tests/test_matcher.py::test_alias_separation_ts_vs_typescript PASSED     [ 78%]
tests/test_matcher.py::test_alias_separation_tf_vs_tensorflow PASSED     [ 81%]
tests/test_matcher.py::test_alias_separation_postgresql_vs_sql PASSED    [ 84%]
tests/test_matcher.py::test_valid_scikitlearn_aliases PASSED             [ 86%]
tests/test_matcher.py::test_sql_vs_nosql_boundary_regression PASSED      [ 89%]
tests/test_matcher.py::test_case_variations_and_punctuation PASSED       [ 92%]
tests/test_matcher.py::test_empty_job_description_validation PASSED      [ 94%]
tests/test_matcher.py::test_scoring_zero_and_hundred_percent PASSED      [ 97%]
tests/test_matcher.py::test_assignment_benchmark_example_75_percent PASSED [100%]

============================== 38 passed in 4.53s ==============================
```