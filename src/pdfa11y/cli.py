"""pdfa11y command line."""
from __future__ import annotations
import argparse
import json
import sys
from .checker import FAIL, WARN, check_pdf

ICON = {"pass": "PASS", "fail": "FAIL", "warn": "WARN", "info": "INFO"}


def to_markdown(reports) -> str:
    out = ["# PDF Accessibility Check", ""]
    for r in reports:
        out += [f"## {r.file} ({r.pages} page{'s' if r.pages != 1 else ''}): "
                f"{'PASSED' if not r.failed else f'{len(r.failed)} FAILED'}", "",
                "| Status | Check | WCAG | Detail |", "|---|---|---|---|"]
        out += [f"| {ICON[c.status]} | {c.title} | {c.wcag} | {c.detail} |" for c in r.checks]
        out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pdfa11y", description="Structural accessibility checks for PDF files")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--format", choices=["text", "json", "md"], default="text")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    a = ap.parse_args(argv)
    reports = [check_pdf(f) for f in a.files]
    if a.format == "json":
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    elif a.format == "md":
        print(to_markdown(reports))
    else:
        for r in reports:
            print(f"\n{r.file}  ({r.pages} pages)")
            for c in r.checks:
                print(f"  [{ICON[c.status]}] {c.title:<36} {c.detail}")
    bad = {FAIL, WARN} if a.strict else {FAIL}
    return 1 if any(c.status in bad for r in reports for c in r.checks) else 0


if __name__ == "__main__":
    sys.exit(main())
