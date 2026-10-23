"""Generate the sample PDFs in samples/ with pikepdf (no external tools needed)."""
from pathlib import Path
import pikepdf
from pikepdf import Array, Dictionary, Name, String

OUT = Path(__file__).resolve().parent.parent / "samples"
def _font(): return Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name.Helvetica)


def _page(pdf, ops: bytes):
    page = pdf.add_blank_page(page_size=(612, 792))
    page.Resources = Dictionary(Font=Dictionary(F1=pdf.make_indirect(_font())))
    page.Contents = pdf.make_stream(ops)
    return page


def untagged(path):
    pdf = pikepdf.new()
    _page(pdf, b"BT /F1 24 Tf 72 700 Td (Quarterly Training Report) Tj ET 0.5 g 72 500 200 120 re f")
    pdf.save(path)


def tagged(path, *, alt=True, title=True, lang=True, skip_heading=False):
    pdf = pikepdf.new()
    ops = (b"/H1 <</MCID 0>> BDC BT /F1 24 Tf 72 700 Td (Quarterly Training Report) Tj ET EMC "
           b"/P <</MCID 1>> BDC BT /F1 12 Tf 72 670 Td (Completion rose across all courses.) Tj ET EMC "
           b"/Figure <</MCID 2>> BDC 0.5 g 72 500 200 120 re f EMC")
    page = _page(pdf, ops)
    page.obj.Tabs = Name.S
    page.obj.StructParents = 0
    pref = page.obj
    sroot = pdf.make_indirect(Dictionary(Type=Name.StructTreeRoot))
    doc = pdf.make_indirect(Dictionary(Type=Name.StructElem, S=Name.Document, P=sroot))
    def el(tag, mcid, **kw):
        return pdf.make_indirect(Dictionary(Type=Name.StructElem, S=Name(tag), P=doc, Pg=pref, K=mcid, **kw))
    h = el("/H3" if skip_heading else "/H1", 0)
    p = el("/P", 1)
    fig = el("/Figure", 2, **({"Alt": String("Bar chart: course completion by quarter, rising from 62% to 81%")} if alt else {}))
    doc.K = Array([h, p, fig])
    sroot.K = doc
    sroot.ParentTree = pdf.make_indirect(Dictionary(Nums=Array([0, Array([h, p, fig])])))
    sroot.ParentTreeNextKey = 1
    pdf.Root.StructTreeRoot = sroot
    pdf.Root.MarkInfo = Dictionary(Marked=True)
    pdf.Root.ViewerPreferences = Dictionary(DisplayDocTitle=True)
    if lang:
        pdf.Root.Lang = String("en-US")
    if title:
        pdf.docinfo[Name.Title] = "Quarterly Training Report"
        with pdf.open_metadata() as m:
            m["dc:title"] = "Quarterly Training Report"
    pdf.save(path)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    untagged(OUT / "untagged.pdf")
    tagged(OUT / "accessible.pdf")
    tagged(OUT / "tagged_missing_alt_title_lang.pdf", alt=False, title=False, lang=False, skip_heading=True)
    print("wrote", *sorted(p.name for p in OUT.glob("*.pdf")))
