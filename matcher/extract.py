"""Skill extraction using scikit-learn CountVectorizer and custom vocabulary."""
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Union
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from .normalize import clean_text, normalize_token


class SkillExtractor:
    """Extracts technical skills from text using scikit-learn CountVectorizer with ngrams."""

    def __init__(self, config_path: Union[str, Path] = None):
        """Initialize extractor by loading skills configuration with Pandas and initializing CountVectorizer."""
        if config_path is None:
            # Default to config/skills.json relative to project root
            base_dir = Path(__file__).resolve().parent.parent
            config_path = base_dir / "config" / "skills.json"

        self.config_path = Path(config_path)
        self.skills_df = self._load_skills_dataframe(self.config_path)
        self.term_to_canonical: Dict[str, str] = {}
        self.vocab_list: List[str] = []
        self._build_vocabulary()

        # Initialize scikit-learn CountVectorizer with custom vocabulary and dynamic ngrams
        max_n = max(len(t.split()) for t in self.vocab_list)
        self.vectorizer = CountVectorizer(
            vocabulary=self.vocab_list,
            ngram_range=(1, max_n),
            token_pattern=r"(?u)\b\w+\b",
            lowercase=True,
        )

    def _load_skills_dataframe(self, path: Path) -> pd.DataFrame:
        """Load skills configuration file into a Pandas DataFrame."""
        if not path.exists():
            raise FileNotFoundError(f"Skills config file not found at: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Convert dictionary to Pandas DataFrame for transparent inspection and manipulation
        records = [
            {"canonical": canonical, "aliases": aliases}
            for canonical, aliases in raw_data.items()
        ]
        df = pd.DataFrame(records)
        return df

    def _build_vocabulary(self):
        """Build normalized vocabulary terms and alias mappings."""
        vocab_set: Set[str] = set()
        self.term_to_canonical = {}

        # Iterate through Pandas DataFrame records
        for _, row in self.skills_df.iterrows():
            canonical = row["canonical"]
            aliases = row["aliases"]

            # Canonical term (exclude bare single letters to avoid false positive matches)
            norm_canonical = normalize_token(canonical)
            if norm_canonical and len(norm_canonical) > 1:
                vocab_set.add(norm_canonical)
                self.term_to_canonical[norm_canonical] = canonical

            # Alias terms
            for alias in aliases:
                norm_alias = normalize_token(alias)
                if norm_alias and len(norm_alias) > 1:
                    vocab_set.add(norm_alias)
                    self.term_to_canonical[norm_alias] = canonical

        # Store sorted vocabulary for deterministic index mapping in CountVectorizer
        self.vocab_list = sorted(list(vocab_set))

    def extract_skills(self, text: str) -> List[str]:
        """Extract canonical skills from text in order of first appearance.
        
        Args:
            text: Uncleaned or cleaned text string.
            
        Returns:
            List of canonical skill names in order of their first appearance.
            Duplicate mentions are de-duplicated.
        """
        if not text or not str(text).strip():
            return []

        cleaned = clean_text(text)
        if not cleaned:
            return []

        # Vectorize text using CountVectorizer
        count_matrix = self.vectorizer.transform([cleaned])
        counts = count_matrix.toarray()[0]

        # Use NumPy to find non-zero vocabulary term indices
        detected_indices = np.where(counts > 0)[0]
        if len(detected_indices) == 0:
            return []

        detected_terms = [self.vocab_list[i] for i in detected_indices]

        # Map terms to canonical names and record their first appearance position in the text
        canonical_positions: Dict[str, int] = {}
        for term in detected_terms:
            canonical = self.term_to_canonical[term]
            
            # Find the position of the term in cleaned text using word boundaries
            match = re.search(r'\b' + re.escape(term) + r'\b', cleaned)
            pos = match.start() if match else 999999

            if canonical not in canonical_positions or pos < canonical_positions[canonical]:
                canonical_positions[canonical] = pos

        # Sort canonical skills by their first appearance order
        sorted_canonical_skills = sorted(
            canonical_positions.keys(),
            key=lambda skill: canonical_positions[skill]
        )

        return sorted_canonical_skills
