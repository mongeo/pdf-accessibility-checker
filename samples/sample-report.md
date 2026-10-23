# PDF Accessibility Check

## samples/accessible.pdf (1 page): PASSED

| Status | Check | WCAG | Detail |
|---|---|---|---|
| PASS | Document is tagged | 1.3.1 | MarkInfo/Marked is true and StructTreeRoot exists |
| PASS | Document title set | 2.4.2 | Title: 'Quarterly Training Report' |
| PASS | Viewer shows title, not filename | 2.4.2 | ViewerPreferences/DisplayDocTitle is true |
| PASS | Document language set | 3.1.1 | Lang: en-US |
| PASS | Figures have alternate text | 1.1.1 | 1/1 figures have /Alt |
| PASS | Heading structure | 1.3.1 | Sequence: H1 |
| PASS | Reading order hints | 1.3.2 | Tab order follows structure and content is linked to tags |
| INFO | PDF/UA identifier |  | No PDF/UA identifier in XMP (optional) |

## samples/tagged_missing_alt_title_lang.pdf (1 page): 3 FAILED

| Status | Check | WCAG | Detail |
|---|---|---|---|
| PASS | Document is tagged | 1.3.1 | MarkInfo/Marked is true and StructTreeRoot exists |
| FAIL | Document title set | 2.4.2 | No Title in Info dictionary or XMP dc:title |
| PASS | Viewer shows title, not filename | 2.4.2 | ViewerPreferences/DisplayDocTitle is true |
| FAIL | Document language set | 3.1.1 | Catalog /Lang missing |
| FAIL | Figures have alternate text | 1.1.1 | 0/1 figures have /Alt; missing on figure #1 |
| WARN | Heading structure | 1.3.1 | Sequence: H3 |
| PASS | Reading order hints | 1.3.2 | Tab order follows structure and content is linked to tags |
| INFO | PDF/UA identifier |  | No PDF/UA identifier in XMP (optional) |

## samples/untagged.pdf (1 page): 3 FAILED

| Status | Check | WCAG | Detail |
|---|---|---|---|
| FAIL | Document is tagged | 1.3.1 | Marked=False, StructTreeRoot=missing |
| FAIL | Document title set | 2.4.2 | No Title in Info dictionary or XMP dc:title |
| WARN | Viewer shows title, not filename | 2.4.2 | ViewerPreferences/DisplayDocTitle is false |
| FAIL | Document language set | 3.1.1 | Catalog /Lang missing |
| INFO | Figures have alternate text | 1.1.1 | No Figure elements in structure tree |
| INFO | PDF/UA identifier |  | No PDF/UA identifier in XMP (optional) |

