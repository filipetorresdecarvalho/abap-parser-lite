import json
from pathlib import Path

from abap_parser_lite import parse_file, parse_abap, detect_object_type

FIXTURES = Path(__file__).parent / "fixtures"


class TestSimpleReport:
    def test_object_type(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert p.object_type == "program"

    def test_object_name(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert p.object_name == "Z_SIMPLE_REPORT"

    def test_includes(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert "z_simple_report_top" in p.includes

    def test_forms(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert len(p.forms) == 2
        assert p.forms[0].name == "get_data"
        assert p.forms[1].name == "process_data"

    def test_form_parameters(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert p.forms[0].parameters == ["iv_matnr"]

    def test_calls(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert "Z_READ_MATERIAL" in p.calls

    def test_tables(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert "MARA" in [t.upper() for t in p.tables]
        assert "ZTABLE" in [t.upper() for t in p.tables]

    def test_data_declarations(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        names = [d.name for d in p.data_declarations]
        assert "lv_matnr" in names
        assert "lv_werks" in names
        assert "lv_name" in names
        assert "lv_counter" in names

    def test_comments(self):
        p = parse_file(FIXTURES / "simple_report.abap")
        assert len(p.comments) >= 2

    def test_json_roundtrip(self):
        from dataclasses import asdict

        p = parse_file(FIXTURES / "simple_report.abap")
        d = asdict(p)
        s = json.dumps(d)
        assert json.loads(s)


class TestFunctionGroup:
    def test_object_type(self):
        p = parse_file(FIXTURES / "function_group.abap")
        assert p.object_type == "program"

    def test_functions(self):
        p = parse_file(FIXTURES / "function_group.abap")
        assert len(p.functions) == 2
        assert p.functions[0].name == "z_get_customer"
        assert p.functions[1].name == "z_create_order"

    def test_function_lines(self):
        p = parse_file(FIXTURES / "function_group.abap")
        assert p.functions[0].end_line > p.functions[0].start_line

    def test_calls(self):
        p = parse_file(FIXTURES / "function_group.abap")
        assert "BAPI_CUSTOMER_GETDETAIL" in p.calls
        assert "BAPI_SALESORDER_CREATE" in p.calls

    def test_tables(self):
        p = parse_file(FIXTURES / "function_group.abap")
        upper = [t.upper() for t in p.tables]
        assert "KNA1" in upper
        assert "ZCUST_LOG" in upper


class TestClassWithMethods:
    def test_methods(self):
        p = parse_file(FIXTURES / "class_with_methods.abap")
        assert len(p.methods) == 3
        names = [m.name for m in p.methods]
        assert "constructor" in names
        assert "process_data" in names
        assert "cleanup" in names

    def test_method_class_name(self):
        p = parse_file(FIXTURES / "class_with_methods.abap")
        assert p.methods[0].class_name == "zcl_handler"

    def test_tables_in_methods(self):
        p = parse_file(FIXTURES / "class_with_methods.abap")
        upper = [t.upper() for t in p.tables]
        assert "ZDATA" in upper
        assert "ZCACHE" in upper


class TestDetectObjectType:
    def test_class(self):
        assert detect_object_type("zcl_foo.clas.abap") == "class"

    def test_function_group(self):
        assert detect_object_type("zfg_bar.fugr.abap") == "function_group"

    def test_program(self):
        assert detect_object_type("z_report.abap") == "program"
        assert detect_object_type("z_rep.prog.abap") == "program"

    def test_interface(self):
        assert detect_object_type("zif_baz.intf.abap") == "interface"

    def test_table(self):
        assert detect_object_type("mara.tabl.abap") == "table"

    def test_view(self):
        assert detect_object_type("z_view.view.abap") == "view"

    def test_cds_view(self):
        assert detect_object_type("z_cds.ddls.abap") == "cds_view"

    def test_unknown(self):
        assert detect_object_type("something.txt") == "unknown"
