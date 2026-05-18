from __future__ import annotations

import re
from pathlib import Path

from .models import Comment, DataDecl, FormBlock, FunctionBlock, MacroDef, MethodBlock, ParsedABAP

PROGRAM_NAME = re.compile(r"^\s*(?:REPORT|PROGRAM)\s+(\w+)", re.IGNORECASE)
INCLUDES = re.compile(r"^\s*INCLUDE\s+(\w+)\s*\.", re.IGNORECASE)
FORM_START = re.compile(r"^\s*FORM\s+(\w+)(?:\s+USING\s+(.+?))?\s*\.", re.IGNORECASE)
FORM_END = re.compile(r"^\s*ENDFORM\s*\.", re.IGNORECASE)
FUNCTION = re.compile(r"^\s*FUNCTION\s+(\w+)\s*\.", re.IGNORECASE)
METHOD_START = re.compile(r"^\s*METHOD\s+(\w+)(?:\s+.*?)?\s*\.", re.IGNORECASE)
METHOD_END = re.compile(r"^\s*ENDMETHOD\s*\.", re.IGNORECASE)
CLASS_START = re.compile(r"^\s*CLASS\s+(\w+)", re.IGNORECASE)
CLASS_END = re.compile(r"^\s*ENDCLASS\s*\.", re.IGNORECASE)
TABLE_REF = re.compile(
    r"(?:SELECT.*?FROM|MODIFY|DELETE\s+FROM|INSERT\s+INTO|UPDATE)\s+(\w+)",
    re.IGNORECASE,
)
CALL_FUNCTION = re.compile(r"^\s*CALL\s+FUNCTION\s+['\"]?(\w+)", re.IGNORECASE)
DATA_DECL = re.compile(r"^\s*DATA(?:S)?:?\s+(?::\s*)?(\w+)", re.IGNORECASE)
COMMENT_FULL = re.compile(r"^\s*\*\s*(.+)")
COMMENT_INLINE = re.compile(r"(?<=[^.])\s*\"(?!\").*?(?=\.)")
MACRO_DEFINE = re.compile(r"^\s*DEFINE\s+(\w+)\s*\.", re.IGNORECASE)
MACRO_END = re.compile(r"^\s*END-OF-DEFINITION\s*\.", re.IGNORECASE)
CHAIN_SPLIT = re.compile(r":\s*(.+?)(?=\.|\s*:)")
INTERFACE_START = re.compile(r"^\s*INTERFACE\s+(\w+)", re.IGNORECASE)
INTERFACE_END = re.compile(r"^\s*ENDINTERFACE\s*\.", re.IGNORECASE)


def detect_object_type(filename: str) -> str:
    lower = filename.lower()
    if ".clas.abap" in lower:
        return "class"
    if ".fugr.abap" in lower:
        return "function_group"
    if ".intf.abap" in lower:
        return "interface"
    if ".tabl.abap" in lower:
        return "table"
    if ".view.abap" in lower:
        return "view"
    if ".ddls.abap" in lower:
        return "cds_view"
    if ".prog.abap" in lower or lower.endswith(".abap"):
        return "program"
    return "unknown"


def _parse_data_items(text: str, line_num: int, seen: set[str]) -> list[DataDecl]:
    results: list[DataDecl] = []
    text = text.rstrip(".")
    parts = text.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        name_match = re.match(r"(\w+)", part)
        if name_match:
            name = name_match.group(1)
            type_hint = ""
            type_match = re.search(r"(?:TYPE|LIKE)\s+(\S+)", part, re.IGNORECASE)
            if type_match:
                type_hint = type_match.group(1).rstrip(",.")
            if name not in seen:
                seen.add(name)
                results.append(DataDecl(name=name, type_hint=type_hint, line=line_num))
    return results


def _extract_type_hint(line: str) -> str:
    type_match = re.search(r"(?:TYPE|LIKE)\s+(\S+)", line, re.IGNORECASE)
    if type_match:
        return type_match.group(1).rstrip(",.")
    return ""


def parse_abap(source: str, file_name: str = "") -> ParsedABAP:
    lines = source.splitlines()
    result = ParsedABAP(
        file_name=file_name,
        object_type=detect_object_type(file_name),
        object_name="",
    )

    if not lines:
        return result

    seen_data: set[str] = set()
    seen_calls: set[str] = set()
    seen_tables: set[str] = set()
    seen_includes: set[str] = set()

    in_form = False
    in_function = False
    in_method = False
    in_macro = False
    in_chain_data = False

    current_form: FormBlock | None = None
    current_function: FunctionBlock | None = None
    current_method: MethodBlock | None = None
    current_macro: MacroDef | None = None
    current_class: str = ""

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()

        if in_chain_data:
            if line.strip().endswith("."):
                in_chain_data = False
            decls = _parse_data_items(line, i, seen_data)
            result.data_declarations.extend(decls)
            continue

        if in_macro:
            if MACRO_END.match(line):
                if current_macro is not None:
                    current_macro.end_line = i
                in_macro = False
            continue

        if in_form:
            if FORM_END.match(line):
                if current_form is not None:
                    current_form.end_line = i
                in_form = False
            continue

        if in_function:
            if line.strip().startswith("ENDFUNCTION"):
                if current_function is not None:
                    current_function.end_line = i
                in_function = False
                continue
            m = CALL_FUNCTION.match(line)
            if m:
                name = m.group(1)
                if name.upper() not in seen_calls:
                    seen_calls.add(name.upper())
                    result.calls.append(name)
            m = TABLE_REF.search(line)
            if m:
                tbl = m.group(1)
                if tbl.upper() not in seen_tables:
                    seen_tables.add(tbl.upper())
                    result.tables.append(tbl)
            continue

        if in_method:
            if METHOD_END.match(line):
                if current_method is not None:
                    current_method.end_line = i
                in_method = False
                continue
            m = CALL_FUNCTION.match(line)
            if m:
                name = m.group(1)
                if name.upper() not in seen_calls:
                    seen_calls.add(name.upper())
                    result.calls.append(name)
            m = TABLE_REF.search(line)
            if m:
                tbl = m.group(1)
                if tbl.upper() not in seen_tables:
                    seen_tables.add(tbl.upper())
                    result.tables.append(tbl)
            continue

        m = COMMENT_FULL.match(line)
        if m:
            result.comments.append(Comment(text=m.group(1).strip(), type="full_line", line=i))
            continue

        m = MACRO_DEFINE.match(line)
        if m:
            macro = MacroDef(name=m.group(1), start_line=i, end_line=i)
            result.macros.append(macro)
            current_macro = macro
            in_macro = True
            continue

        m = CLASS_START.match(line)
        if m:
            current_class = m.group(1)

        m = INTERFACE_START.match(line)
        if m:
            current_class = m.group(1)

        m = INCLUDES.match(line)
        if m:
            name = m.group(1)
            if name.lower() not in seen_includes:
                seen_includes.add(name.lower())
                result.includes.append(name)
            continue

        m = CALL_FUNCTION.match(line)
        if m:
            name = m.group(1)
            if name.upper() not in seen_calls:
                seen_calls.add(name.upper())
                result.calls.append(name)
            continue

        m = TABLE_REF.search(line)
        if m:
            tbl = m.group(1)
            if tbl.upper() not in seen_tables:
                seen_tables.add(tbl.upper())
                result.tables.append(tbl)

        m = FORM_START.match(line)
        if m:
            params = []
            if m.group(2):
                params = [p.strip() for p in m.group(2).split() if p.strip()]
            form = FormBlock(name=m.group(1), start_line=i, end_line=i, parameters=params)
            result.forms.append(form)
            current_form = form
            in_form = True
            continue

        m = FUNCTION.match(line)
        if m:
            func = FunctionBlock(name=m.group(1), start_line=i, end_line=i)
            result.functions.append(func)
            current_function = func
            in_function = True
            continue

        m = METHOD_START.match(line)
        if m:
            method = MethodBlock(
                name=m.group(1),
                class_name=current_class,
                start_line=i,
                end_line=i,
            )
            result.methods.append(method)
            current_method = method
            in_method = True
            continue

        m = DATA_DECL.match(line)
        if m:
            colon_pos = line.find(":")
            if colon_pos >= 0:
                rest = line[colon_pos + 1 :]
                if rest.strip().endswith(".") and "," in rest:
                    decls = _parse_data_items(rest, i, seen_data)
                    result.data_declarations.extend(decls)
                else:
                    name = m.group(1)
                    if name not in seen_data:
                        seen_data.add(name)
                        type_hint = _extract_type_hint(line)
                        result.data_declarations.append(
                            DataDecl(name=name, type_hint=type_hint, line=i)
                        )
                    if not line.strip().endswith("."):
                        in_chain_data = True
            else:
                name = m.group(1)
                if name not in seen_data:
                    seen_data.add(name)
                    type_hint = _extract_type_hint(line)
                    result.data_declarations.append(
                        DataDecl(name=name, type_hint=type_hint, line=i)
                    )
            continue

        if not result.object_name:
            m = PROGRAM_NAME.match(line)
            if m:
                result.object_name = m.group(1).upper()

        im = COMMENT_INLINE.search(line)
        if im:
            result.comments.append(Comment(text=im.group(0).strip(), type="inline", line=i))

    return result


def parse_file(path: str | Path) -> ParsedABAP:
    p = Path(path)
    source = p.read_text(encoding="utf-8", errors="replace")
    return parse_abap(source, file_name=p.name)
