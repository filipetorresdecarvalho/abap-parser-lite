# abap-parser-lite

Lightweight regex-based ABAP source code parser. Zero external dependencies — uses only the Python standard library.

## Installation

```bash
pip install -e .
```

## Usage

### CLI

```bash
# Parse a single file
abap-parser-lite parse path/to/file.abap

# Scan a directory for all .abap files
abap-parser-lite scan /path/to/abap/files
```

### Python API

```python
from abap_parser_lite import parse_file, parse_abap, detect_object_type

# Parse from file path
result = parse_file("my_program.abap")

# Parse from string
result = parse_abap(source_code, file_name="z_report.prog.abap")

# Detect object type from filename
detect_object_type("z_cl_foo.clas.abap")  # → "class"
```

## Output JSON Example

```json
{
  "file_name": "z_report.prog.abap",
  "object_type": "program",
  "object_name": "Z_REPORT",
  "includes": ["Z_REPORT_TOP", "Z_REPORT_F01"],
  "calls": ["Z_FUNCTION_MODULE"],
  "tables": ["MARA", "VBAK"],
  "forms": [
    {
      "name": "GET_DATA",
      "start_line": 15,
      "end_line": 30,
      "parameters": ["IV_MATNR", "ET_RESULT"]
    }
  ],
  "functions": [],
  "methods": [],
  "data_declarations": [
    {"name": "lv_matnr", "type_hint": "matnr", "line": 10}
  ],
  "comments": [
    {"text": "Fetch material data", "type": "full_line", "line": 14}
  ],
  "macros": []
}
```

## Supported Constructs

- **Object type detection** from filename (program, class, function group, interface, etc.)
- **INCLUDE** statements
- **FORM/ENDFORM** blocks with parameters
- **FUNCTION/ENDFUNCTION** blocks
- **METHOD/ENDMETHOD** blocks
- **CLASS/ENDCLASS** and **INTERFACE/ENDINTERFACE**
- **CALL FUNCTION** targets
- **Table references** (SELECT FROM, MODIFY, DELETE FROM, INSERT INTO, UPDATE)
- **DATA/DATA:** declarations including chained statements
- **Full-line comments** (`*`) and **inline comments** (`"`)
- **DEFINE/END-OF-DEFINITION** macros
- **Chained statements** (colon syntax)

## Requirements

- Python 3.10+

## License

MIT — 2026 Filipe Torres de Carvalho
