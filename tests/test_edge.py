import json
from dataclasses import asdict

from abap_parser_lite import parse_abap, detect_object_type


class TestEmptyFile:
    def test_empty(self):
        p = parse_abap("", file_name="empty.abap")
        assert p.object_type == "program"
        assert p.object_name == ""
        assert p.forms == []
        assert p.calls == []
        assert p.tables == []

    def test_whitespace_only(self):
        p = parse_abap("   \n  \n", file_name="blank.abap")
        assert p.forms == []


class TestChainedStatements:
    def test_chained_data(self):
        source = "DATA: a TYPE i, b TYPE c LENGTH 10, c LIKE b."
        p = parse_abap(source, file_name="chain.abap")
        names = [d.name for d in p.data_declarations]
        assert "a" in names
        assert "b" in names
        assert "c" in names

    def test_chained_data_type_hints(self):
        source = "DATA: lv_x TYPE i, lv_y TYPE string."
        p = parse_abap(source, file_name="chain.abap")
        by_name = {d.name: d.type_hint for d in p.data_declarations}
        assert by_name["lv_x"] == "i"
        assert by_name["lv_y"] == "string"

    def test_multiline_chained_data(self):
        source = "DATA: lv_a TYPE i,\n      lv_b TYPE c LENGTH 10,\n      lv_c LIKE lv_b."
        p = parse_abap(source, file_name="chain.abap")
        names = [d.name for d in p.data_declarations]
        assert "lv_a" in names
        assert "lv_b" in names
        assert "lv_c" in names


class TestMacros:
    def test_macro_detection(self):
        source = 'DEFINE check_field.\n  IF &1 IS INITIAL.\n    WRITE: / "Empty".\n  ENDIF.\nEND-OF-DEFINITION.'
        p = parse_abap(source, file_name="macro.abap")
        assert len(p.macros) == 1
        assert p.macros[0].name == "check_field"
        assert p.macros[0].end_line > p.macros[0].start_line


class TestComments:
    def test_full_line_comment(self):
        source = "* This is a comment\nWRITE: / 'hello'."
        p = parse_abap(source, file_name="comment.abap")
        assert len(p.comments) >= 1
        assert p.comments[0].type == "full_line"
        assert "comment" in p.comments[0].text.lower()

    def test_multiple_comments(self):
        source = "* First\n* Second\nWRITE: / 'hi'."
        p = parse_abap(source, file_name="comment.abap")
        full_line = [c for c in p.comments if c.type == "full_line"]
        assert len(full_line) == 2


class TestDuplicateFiltering:
    def test_duplicate_calls(self):
        source = "CALL FUNCTION 'Z_FOO'.\nCALL FUNCTION 'Z_FOO'."
        p = parse_abap(source, file_name="dup.abap")
        assert len(p.calls) == 1
        assert p.calls[0] == "Z_FOO"

    def test_duplicate_tables(self):
        source = "SELECT * FROM mara.\nSELECT * FROM mara."
        p = parse_abap(source, file_name="dup.abap")
        assert len([t for t in p.tables if t.upper() == "MARA"]) == 1

    def test_duplicate_data(self):
        source = "DATA: lv_x TYPE i.\nDATA: lv_x TYPE i."
        p = parse_abap(source, file_name="dup.abap")
        assert len([d for d in p.data_declarations if d.name == "lv_x"]) == 1


class TestParseAbapFromStrings:
    def test_report_detection(self):
        source = "REPORT z_test_program.\nWRITE: / 'hello'."
        p = parse_abap(source, file_name="z_test.abap")
        assert p.object_name == "Z_TEST_PROGRAM"

    def test_call_function_single_quotes(self):
        source = "CALL FUNCTION 'RFC_READ_TABLE'."
        p = parse_abap(source, file_name="test.abap")
        assert p.calls == ["RFC_READ_TABLE"]

    def test_form_with_no_params(self):
        source = "FORM show_data.\n  WRITE: / 'data'.\nENDFORM."
        p = parse_abap(source, file_name="test.abap")
        assert len(p.forms) == 1
        assert p.forms[0].parameters == []

    def test_function_block(self):
        source = "FUNCTION z_my_func.\n  DATA: lv_x TYPE i.\nENDFUNCTION."
        p = parse_abap(source, file_name="test.abap")
        assert len(p.functions) == 1
        assert p.functions[0].end_line > p.functions[0].start_line

    def test_method_block(self):
        source = (
            "CLASS zcl_test DEFINITION PUBLIC.\n"
            "  PUBLIC SECTION.\n"
            "    METHODS run.\n"
            "ENDCLASS.\n"
            "CLASS zcl_test IMPLEMENTATION.\n"
            "  METHOD run.\n"
            "    WRITE: / 'running'.\n"
            "  ENDMETHOD.\n"
            "ENDCLASS."
        )
        p = parse_abap(source, file_name="test.abap")
        assert len(p.methods) == 1
        assert p.methods[0].name == "run"
        assert p.methods[0].class_name == "zcl_test"

    def test_interface_detection(self):
        p = parse_abap("", file_name="zif_example.intf.abap")
        assert p.object_type == "interface"

    def test_json_serializable(self):
        source = "REPORT z_json_test.\nDATA: lv_x TYPE i.\nFORM test USING iv_val.\nENDFORM."
        p = parse_abap(source, file_name="test.abap")
        s = json.dumps(asdict(p))
        loaded = json.loads(s)
        assert loaded["object_name"] == "Z_JSON_TEST"
        assert len(loaded["forms"]) == 1
        assert len(loaded["data_declarations"]) == 1
