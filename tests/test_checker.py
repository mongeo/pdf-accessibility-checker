import json
from pathlib import Path
import pytest
from pdfa11y.checker import check_pdf
from pdfa11y.cli import main

S = Path(__file__).resolve().parent.parent / "samples"


def status(rep, cid):
    return next(c.status for c in rep.checks if c.id == cid)


def test_accessible_passes_everything():
    r = check_pdf(S / "accessible.pdf")
    assert not r.failed
    for cid in ("tagged", "title", "display-title", "lang", "figure-alt", "headings", "reading-order"):
        assert status(r, cid) == "pass", cid


def test_untagged_fails_tags_title_lang():
    r = check_pdf(S / "untagged.pdf")
    assert {c.id for c in r.failed} == {"tagged", "title", "lang"}
    assert status(r, "figure-alt") == "info"


def test_missing_alt_title_lang_and_heading_skip():
    r = check_pdf(S / "tagged_missing_alt_title_lang.pdf")
    assert status(r, "tagged") == "pass"
    assert {c.id for c in r.failed} == {"title", "lang", "figure-alt"}
    assert status(r, "headings") == "warn"


def test_cli_exit_codes_and_json(capsys):
    assert main([str(S / "accessible.pdf")]) == 0
    assert main([str(S / "untagged.pdf")]) == 1
    capsys.readouterr()
    main([str(S / "accessible.pdf"), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data[0]["passed"] is True


def test_strict_mode_treats_warnings_as_failures():
    assert main([str(S / "tagged_missing_alt_title_lang.pdf"), "--strict"]) == 1


def test_markdown_output(capsys):
    main([str(S / "untagged.pdf"), "--format", "md"])
    assert "| FAIL | Document is tagged |" in capsys.readouterr().out


def test_bad_file_raises(tmp_path):
    bad = tmp_path / "x.pdf"
    bad.write_bytes(b"not a pdf")
    with pytest.raises(Exception):
        check_pdf(bad)
