from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FormBlock:
    name: str
    start_line: int
    end_line: int
    parameters: list[str] = field(default_factory=list)


@dataclass
class FunctionBlock:
    name: str
    start_line: int
    end_line: int


@dataclass
class MethodBlock:
    name: str
    class_name: str
    start_line: int
    end_line: int


@dataclass
class DataDecl:
    name: str
    type_hint: str
    line: int


@dataclass
class Comment:
    text: str
    type: str  # "full_line" | "inline"
    line: int


@dataclass
class MacroDef:
    name: str
    start_line: int
    end_line: int


@dataclass
class ParsedABAP:
    file_name: str
    object_type: str  # "program" | "class" | "function_group" | "include" | "interface" | "unknown"
    object_name: str
    includes: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    forms: list[FormBlock] = field(default_factory=list)
    functions: list[FunctionBlock] = field(default_factory=list)
    methods: list[MethodBlock] = field(default_factory=list)
    data_declarations: list[DataDecl] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    macros: list[MacroDef] = field(default_factory=list)
