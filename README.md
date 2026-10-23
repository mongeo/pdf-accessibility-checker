# pdf-accessibility-checker

`pdfa11y` is a small, dependency-light Python tool built on **[pikepdf](https://pikepdf.readthedocs.io/)**. It checks the structural accessibility requirements behind **WCAG 2.2**, **Section 508**, and **PDF/UA**. Use it to triage a batch of PDFs (for example, eLearning handouts or agency forms) before doing manual remediation and review in Acrobat, PAC, or a screen reader.

## Checks
| ID | Check | WCAG | Fails when |
|---|---|---|---|
| `tagged` | Tagged PDF | 1.3.1 | `MarkInfo/Marked` is not true or there's no `StructTreeRoot` |
| `title` | Document title | 2.4.2 | No Info `/Title` and no XMP `dc:title` |
| `display-title` | Title shown in viewer | 2.4.2 | `DisplayDocTitle` isn't set (warning) |
| `lang` | Document language | 3.1.1 | Catalog `/Lang` is missing |
| `figure-alt` | Figure alternate text | 1.1.1 | A `Figure` tag (RoleMap-aware) has no `/Alt` or `/ActualText` |
| `headings` | Heading structure | 1.3.1 | No H1–H6 tags, a skipped level, or the first heading isn't H1 (warning) |
| `reading-order` | Reading-order hints | 1.3.2 | Pages without `/Tabs /S`, no `ParentTree`, or empty structure elements (warning) |
| `table-headers` | Table headers | 1.3.1 | A `Table` with no `TH` cells |
| `pdfua-id` | PDF/UA identifier | none | Informational only |

> Structural checks can't judge whether alt text is *good*, whether the tag order matches the visual reading order, or whether colors have enough contrast. Those still need a person, ideally testing with JAWS/NVDA and a dedicated PDF checker.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pdfa11y samples/*.pdf                      # text output
pdfa11y report.pdf --format json           # JSON for pipelines
pdfa11y docs/*.pdf --format md > audit.md  # Markdown report
pdfa11y file.pdf --strict                  # count warnings as failures
pytest -v
```
The exit code is `1` when any check fails, so the tool can gate CI.

## Sample PDFs
`scripts/make_samples.py` builds them all with pikepdf, so they can be reproduced:
- `accessible.pdf`: tagged, with title, language, an H1, and a figure with alt text. Passes.
- `untagged.pdf`: no structure, no title, no language. Fails.
- `tagged_missing_alt_title_lang.pdf`: tagged, but the figure has no alt text, there's no title or language, and the only heading is H3. Fails.

## Sample output
```

samples/accessible.pdf  (1 pages)
  [PASS] Document is tagged                   MarkInfo/Marked is true and StructTreeRoot exists
  [PASS] Document title set                   Title: 'Quarterly Training Report'
  [PASS] Viewer shows title, not filename     ViewerPreferences/DisplayDocTitle is true
  [PASS] Document language set                Lang: en-US
  [PASS] Figures have alternate text          1/1 figures have /Alt
  [PASS] Heading structure                    Sequence: H1
  [PASS] Reading order hints                  Tab order follows structure and content is linked to tags
  [INFO] PDF/UA identifier                    No PDF/UA identifier in XMP (optional)

samples/tagged_missing_alt_title_lang.pdf  (1 pages)
  [PASS] Document is tagged                   MarkInfo/Marked is true and StructTreeRoot exists
  [FAIL] Document title set                   No Title in Info dictionary or XMP dc:title
  [PASS] Viewer shows title, not filename     ViewerPreferences/DisplayDocTitle is true
  [FAIL] Document language set                Catalog /Lang missing
  [FAIL] Figures have alternate text          0/1 figures have /Alt; missing on figure #1
  [WARN] Heading structure                    Sequence: H3
  [PASS] Reading order hints                  Tab order follows structure and content is linked to tags
  [INFO] PDF/UA identifier                    No PDF/UA identifier in XMP (optional)

samples/untagged.pdf  (1 pages)
  [FAIL] Document is tagged                   Marked=False, StructTreeRoot=missing
  [FAIL] Document title set                   No Title in Info dictionary or XMP dc:title
  [WARN] Viewer shows title, not filename     ViewerPreferences/DisplayDocTitle is false
  [FAIL] Document language set                Catalog /Lang missing
  [INFO] Figures have alternate text          No Figure elements in structure tree
  [INFO] PDF/UA identifier                    No PDF/UA identifier in XMP (optional)
```
There's a Markdown version in [`samples/sample-report.md`](samples/sample-report.md).

## License
MIT © Geoffrey Montague
