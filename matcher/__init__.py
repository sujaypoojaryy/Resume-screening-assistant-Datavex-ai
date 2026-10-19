"""Matcher package for resume and job description skill screening."""
from .normalize import clean_text, normalize_token
from .parsers import (
    extract_text_from_file,
    validate_raw_text,
    ParsingError,
    ValidationError,
    FileTooLargeError,
    UnsupportedFormatError,
    EmptyDocumentError,
    NoExtractableTextError,
)
from .extract import SkillExtractor
from .scoring import calculate_match

__all__ = [
    "clean_text",
    "normalize_token",
    "extract_text_from_file",
    "validate_raw_text",
    "ParsingError",
    "ValidationError",
    "FileTooLargeError",
    "UnsupportedFormatError",
    "EmptyDocumentError",
    "NoExtractableTextError",
    "SkillExtractor",
    "calculate_match",
]
