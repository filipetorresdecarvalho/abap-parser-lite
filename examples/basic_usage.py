from abap_parser_lite import parse_file, parse_abap, detect_object_type, ParsedABAP

result = parse_file("tests/fixtures/simple_report.abap")
print(f"File: {result.file_name}")
print(f"Type: {result.object_type}")
print(f"Name: {result.object_name}")
print(f"Forms: {[f.name for f in result.forms]}")
print(f"Calls: {result.calls}")
print(f"Tables: {result.tables}")
print(f"Data: {[d.name for d in result.data_declarations]}")
print(f"Comments: {[c.text for c in result.comments]}")

print()
source = """
REPORT z_test.
DATA: lv_a TYPE i, lv_b TYPE c LENGTH 10.
FORM process USING iv_val.
  WRITE: / iv_val.
ENDFORM.
"""
result2 = parse_abap(source, file_name="z_test.prog.abap")
print(f"Parsed from string: {result2.forms[0].name}")
