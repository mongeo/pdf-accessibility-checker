"""Structural accessibility checks for PDFs (PDF/UA- and WCAG-informed).

These checks look at the document structure only. Passing them doesn't mean the PDF is
accessible: alt text quality, the real reading order, and contrast still need a manual
review with a screen reader and a tool like PAC.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
import pikepdf
from pikepdf import Name

PASS, FAIL, WARN, INFO = "pass", "fail", "warn", "info"


@dataclass
class Check:
    id: str
    title: str
    status: str
    detail: str
    wcag: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Report:
    file: str
    pages: int
    checks: list[Check] = field(default_factory=list)

    @property
    def failed(self) -> list[Check]:
        return [c for c in self.checks if c.status == FAIL]

    def to_dict(self):
        return {"file": self.file, "pages": self.pages, "passed": not self.failed,
                "checks": [c.to_dict() for c in self.checks]}


def _walk(elem, depth=0, seen=None):
    """Yield (struct_elem, depth) over the structure tree, guarding against cycles."""
    seen = seen if seen is not None else set()
    if isinstance(elem, pikepdf.Array):
        for k in elem:
            yield from _walk(k, depth, seen)
        return
    if not isinstance(elem, pikepdf.Dictionary):
        return
    key = elem.objgen if elem.is_indirect else id(elem)
    if key in seen:
        return
    seen.add(key)
    if Name.S in elem:
        yield elem, depth
    kids = elem.get(Name.K)
    if kids is not None:
        yield from _walk(kids, depth + 1, seen)


def check_pdf(path: str | Path) -> Report:
    with pikepdf.open(path) as pdf:
        root = pdf.Root
        rep = Report(file=str(path), pages=len(pdf.pages))
        add = rep.checks.append

        # 1. Tagged
        marked = bool(root.get(Name.MarkInfo, {}).get(Name.Marked, False))
        tree = root.get(Name.StructTreeRoot)
        if marked and tree is not None:
            add(Check("tagged", "Document is tagged", PASS, "MarkInfo/Marked is true and StructTreeRoot exists", "1.3.1"))
        else:
            add(Check("tagged", "Document is tagged", FAIL,
                      f"Marked={marked}, StructTreeRoot={'present' if tree is not None else 'missing'}", "1.3.1"))

        # 2. Title + DisplayDocTitle
        title = None
        try:
            title = str(pdf.docinfo.get(Name.Title, "")) or None
        except Exception:
            pass
        if not title:
            try:
                with pdf.open_metadata() as meta:
                    title = meta.get("dc:title") or None
            except Exception:
                pass
        add(Check("title", "Document title set", PASS if title else FAIL,
                  f"Title: {title!r}" if title else "No Title in Info dictionary or XMP dc:title", "2.4.2"))
        disp = bool(root.get(Name.ViewerPreferences, {}).get(Name.DisplayDocTitle, False))
        add(Check("display-title", "Viewer shows title, not filename", PASS if disp else WARN,
                  "ViewerPreferences/DisplayDocTitle is " + str(disp).lower(), "2.4.2"))

        # 3. Language
        lang = str(root.get(Name.Lang, "")) or None
        add(Check("lang", "Document language set", PASS if lang else FAIL,
                  f"Lang: {lang}" if lang else "Catalog /Lang missing", "3.1.1"))

        elems = list(_walk(tree.get(Name.K))) if tree is not None and Name.K in tree else []
        types = [str(e.S)[1:] for e, _ in elems]
        rolemap = {str(k)[1:]: str(v)[1:] for k, v in tree.get(Name.RoleMap, {}).items()} if tree is not None else {}
        std = [rolemap.get(t, t) for t in types]

        # 4. Figures alt text
        figs = [e for e, _ in elems if rolemap.get(str(e.S)[1:], str(e.S)[1:]) == "Figure"]
        missing = [i for i, f in enumerate(figs, 1) if not (str(f.get(Name.Alt, "")).strip() or Name.ActualText in f)]
        if not figs:
            add(Check("figure-alt", "Figures have alternate text", INFO, "No Figure elements in structure tree", "1.1.1"))
        else:
            add(Check("figure-alt", "Figures have alternate text", FAIL if missing else PASS,
                      f"{len(figs) - len(missing)}/{len(figs)} figures have /Alt"
                      + (f"; missing on figure #{', #'.join(map(str, missing))}" if missing else ""), "1.1.1"))

        # 5. Headings: present and not skipping levels
        levels = [int(t[1]) for t in std if len(t) == 2 and t[0] == "H" and t[1].isdigit()]
        if tree is None:
            pass
        elif not levels:
            add(Check("headings", "Heading structure", WARN, "No H1–H6 tags found", "1.3.1"))
        else:
            skips = [f"H{a}→H{b}" for a, b in zip(levels, levels[1:]) if b > a + 1]
            add(Check("headings", "Heading structure", WARN if skips or levels[0] != 1 else PASS,
                      f"Sequence: {' '.join('H%d' % l for l in levels)}" + (f"; skips: {', '.join(skips)}" if skips else ""),
                      "1.3.1"))

        # 6. Reading-order hints
        if tree is not None:
            hints = []
            tabs_bad = [i for i, p in enumerate(pdf.pages, 1) if str(p.obj.get(Name.Tabs, "")) != "/S"]
            if tabs_bad:
                hints.append(f"pages without /Tabs /S (structure order): {tabs_bad[:10]}")
            if Name.ParentTree not in tree:
                hints.append("StructTreeRoot has no ParentTree (content not linked to tags)")
            unlinked = sum(1 for e, _ in elems if e.get(Name.K) is None)
            if unlinked:
                hints.append(f"{unlinked} empty structure element(s)")
            add(Check("reading-order", "Reading order hints", WARN if hints else PASS,
                      "; ".join(hints) or "Tab order follows structure and content is linked to tags", "1.3.2"))

        # 7. Tables have header cells
        if "Table" in std:
            add(Check("table-headers", "Tables have TH cells", PASS if "TH" in std else FAIL,
                      f"{std.count('Table')} table(s), {std.count('TH')} TH cell(s)", "1.3.1"))

        # 8. PDF/UA identifier (informational)
        ua = None
        try:
            with pdf.open_metadata() as meta:
                ua = meta.get("pdfuaid:part")
        except Exception:
            pass
        add(Check("pdfua-id", "PDF/UA identifier", PASS if ua else INFO,
                  f"pdfuaid:part={ua}" if ua else "No PDF/UA identifier in XMP (optional)"))
        return rep
