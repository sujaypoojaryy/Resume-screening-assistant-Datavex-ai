"""Match score calculation and Pandas results DataFrame construction.

Uses NumPy for binary skill vector operations and Pandas for structured tabular reporting.
Enforces recruiter-assist neutrality: never rejects or issues negative labels.
"""
from typing import Dict, List, Any
import numpy as np
import pandas as pd

DISCLAIMER_TEXT = (
    "This score reflects text overlap with the job description and is not a definitive "
    "measure of candidate quality. It should assist, not replace, human review."
)


def calculate_match(jd_skills: List[str], resume_skills: List[str]) -> Dict[str, Any]:
    """Calculate match score and skill breakdown between JD and Resume.
    
    Formula:
        match_score = (required skills found in resume / total required skills) * 100
        
    - Equal weighting for all required skills.
    - Preserves JD appearance order for matched and missing skills.
    - Additional skills found in the resume (not in JD) are categorized separately and NOT counted.
    - If total required skills is 0, score is 0 with a clear neutral explanation (no division by zero).
    
    Args:
        jd_skills: List of canonical skill names found in the Job Description (ordered).
        resume_skills: List of canonical skill names found in the Resume.
        
    Returns:
        Dict containing:
            matched_skills: List[str] in JD order
            missing_skills: List[str] in JD order
            additional_skills: List[str] in resume order
            match_score: int or float
            total_required: int
            matched_count: int
            results_df: pd.DataFrame with columns ['Skill', 'In JD', 'In Resume', 'Status']
            disclaimer: str
            recommendation: str (neutral wording)
    """
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    # Preserve JD order for matched and missing skills
    matched_skills = [skill for skill in jd_skills if skill in resume_set]
    missing_skills = [skill for skill in jd_skills if skill not in resume_set]
    additional_skills = [skill for skill in resume_skills if skill not in jd_set]

    # Handle zero required skills in JD (avoid division by zero)
    if len(jd_skills) == 0:
        match_score = 0
        total_required = 0
        matched_count = 0
        recommendation = "Review recommended: No recognized technical skills detected in the Job Description."
    else:
        # Binary vector with NumPy representing presence of required skills in resume
        res_vector = np.array([1 if skill in resume_set else 0 for skill in jd_skills], dtype=int)
        matched_count = int(res_vector.sum())
        total_required = len(jd_skills)

        score_raw = (matched_count / total_required) * 100.0
        match_score = int(score_raw) if score_raw.is_integer() else round(score_raw, 1)
        recommendation = "Review recommended."

    # Build Pandas DataFrame for detailed tabular reporting
    df_rows = []
    # 1. Required skills (in JD order)
    for skill in jd_skills:
        in_resume = "Yes" if skill in resume_set else "No"
        status = "Matched" if skill in resume_set else "Missing"
        df_rows.append({
            "Skill": skill,
            "In JD": "Yes",
            "In Resume": in_resume,
            "Status": status
        })

    # 2. Additional resume skills
    for skill in additional_skills:
        df_rows.append({
            "Skill": skill,
            "In JD": "No",
            "In Resume": "Yes",
            "Status": "Additional (Not in JD)"
        })

    results_df = pd.DataFrame(df_rows, columns=["Skill", "In JD", "In Resume", "Status"])

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "match_score": match_score,
        "total_required": total_required,
        "matched_count": matched_count,
        "results_df": results_df,
        "disclaimer": DISCLAIMER_TEXT,
        "recommendation": recommendation,
    }
