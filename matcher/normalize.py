"""Text normalization and cleaning utilities for skill extraction.

Ensures consistent text representation across different input formats (PDF, DOCX, TXT, pasted)
and safely handles programming language symbols like C++, C#, .NET, Node.js, and CI/CD.
"""
import re


def clean_text(raw_text: str) -> str:
    """Clean and normalize raw document text.
    
    1. Removes hyphenated line breaks (e.g., 'deve-\\nlopment' -> 'development').
    2. Normalizes odd unicode characters (bullets, smart quotes, dashes, nbsp).
    3. Preserves special programming tokens before punctuation removal:
       - 'C++' -> '__c_plus_plus__'
       - 'C#' -> '__c_sharp__'
       - '.NET' -> '__dot_net__'
       - 'Node.js' -> '__node_js__'
       - 'CI/CD' -> '__ci_cd__'
    4. Replaces remaining punctuation with whitespace.
    5. Converts text to lowercase and collapses multiple spaces.
    
    Args:
        raw_text: The uncleaned text extracted from a resume or job description.
        
    Returns:
        Cleaned, normalized string ready for tokenization/vectorization.
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    text = raw_text

    # 1. Hyphenated line breaks: reconnect split words across newlines
    text = re.sub(r'(\b\w+)-\s*\r?\n\s*(\w+\b)', r'\1\2', text)

    # 2. Normalize standard bullets and strange unicode symbols to space
    bullet_chars = r'[\u2022\u2023\u25E6\u2043\u2219\uf0a7\u25cf\u25cb\u25aa\u25ab\u25b8\u27a4]'
    text = re.sub(bullet_chars, ' ', text)

    # Normalize typographic quotes and dashes
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u00a0', ' ').replace('\ufeff', '')

    # 3. Preserve special programming languages & technical terms
    # Use negative lookbehind and lookahead to avoid partial word collisions
    text = re.sub(r'(?i)(?<!\w)c\+\+(?!\w)', ' __c_plus_plus__ ', text)
    text = re.sub(r'(?i)(?<!\w)c#(?!\w)', ' __c_sharp__ ', text)
    text = re.sub(r'(?i)(?<!\w)\.net(?!\w)', ' __dot_net__ ', text)
    text = re.sub(r'(?i)(?<!\w)node\.js(?!\w)', ' __node_js__ ', text)
    text = re.sub(r'(?i)(?<!\w)ci/cd(?!\w)', ' __ci_cd__ ', text)
    text = re.sub(r'(?i)(?<!\w)react\.js(?!\w)', ' reactjs ', text)
    text = re.sub(r'(?i)(?<!\w)tf\s*-\s*idf(?!\w)', ' tfidf ', text)
    text = re.sub(r'(?i)(?<!\w)ts\s*/\s*sci(?!\w)', ' tssci ', text)
    text = re.sub(r'(?i)(?<!\w)r\s*&\s*d(?!\w)', ' randd ', text)
    text = re.sub(r'(?i)(?<!\w)type\s*[- ]\s*c(?!\w)', ' typec ', text)
    text = re.sub(r'(?i)(?<!\w)no\s*-\s*sql(?!\w)', ' nosql ', text)

    # 4. Strip remaining punctuation (keeping alphanumeric and underscores)
    text = re.sub(r'[^\w\s]', ' ', text)

    # 5. Lowercase and collapse consecutive whitespace
    cleaned = re.sub(r'\s+', ' ', text).strip().lower()
    return cleaned


def normalize_token(term: str) -> str:
    """Normalize a skill name or alias token consistently with clean_text.
    
    Ensures that vocabulary items and alias terms match their occurrences
    in the cleaned text.
    """
    return clean_text(term)
