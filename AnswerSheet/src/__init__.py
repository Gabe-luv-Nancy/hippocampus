"""
AnswerSheet — 可验证填表明文范式 v1.0
纯 Python 实现，零外部依赖（除 PyYAML）
"""

from .answersheet import (
    AnswerSheet,
    AnswerSheetParser,
    AnswerSheetValidator,
    AnswerSheetFiller,
    InductionEngine,
    Module,
    Slot,
    AnswerEntry,
    VerifyMode,
    ParseError,
    parse_file,
    validate_file,
)

__version__ = "1.0.0"
__all__ = [
    "AnswerSheet",
    "AnswerSheetParser",
    "AnswerSheetValidator",
    "AnswerSheetFiller",
    "InductionEngine",
    "Module",
    "Slot",
    "AnswerEntry",
    "VerifyMode",
    "ParseError",
    "parse_file",
    "validate_file",
]
