from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import parse_file


def _parsed_to_dict(p):
    from dataclasses import asdict

    d = asdict(p)
    return d


def cmd_parse(args):
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    parsed = parse_file(path)
    print(json.dumps(_parsed_to_dict(parsed), indent=2))


def cmd_scan(args):
    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"Error: not a directory: {directory}", file=sys.stderr)
        sys.exit(1)
    results = []
    for p in sorted(directory.rglob("*.abap")):
        parsed = parse_file(p)
        results.append(_parsed_to_dict(parsed))
    print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="abap-parser-lite",
        description="Lightweight regex-based ABAP source code parser",
    )
    sub = parser.add_subparsers(dest="command")

    p_parse = sub.add_parser("parse", help="Parse a single ABAP file")
    p_parse.add_argument("file", help="Path to .abap file")

    p_scan = sub.add_parser("scan", help="Scan a directory for .abap files")
    p_scan.add_argument("directory", help="Directory containing .abap files")

    args = parser.parse_args()
    if args.command == "parse":
        cmd_parse(args)
    elif args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
