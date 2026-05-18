"""abap-parser-lite — Lightweight regex-based ABAP source code parser."""

from .core import detect_object_type, parse_abap, parse_file
from .models import (
    Comment,
    DataDecl,
    FormBlock,
    FunctionBlock,
    MacroDef,
    MethodBlock,
    ParsedABAP,
)

__all__ = [
    "parse_abap",
    "parse_file",
    "detect_object_type",
    "ParsedABAP",
    "FormBlock",
    "FunctionBlock",
    "MethodBlock",
    "DataDecl",
    "Comment",
    "MacroDef",
]
__version__ = "0.1.0"
