"""One-off factual correction of the 18 November 2026 archived FA report.
Run from repository root; requires PyMuPDF and installed Liberation Sans fonts.
No new market snapshot, archive policy or report cutoff is created.
"""
from pathlib import Path
import hashlib
import pymupdf as pdf

TARGET = Path('report-archive/2026-11-18.pdf')
ORIGINAL_SHA256 = 'b4277fbd3bfe61ff6278b589dc22e0c9aa85da2fcb1e5f2e95767bb14e9a1511'
SOURCE = 'https://www.finanznachrichten.de/nachrichten-2026-11/70157924-boersenschluss-nvidia-nervositaet-drueckt-dax-um-2-08-ins-minus-665.htm'
HISTORY = 'https://query1.finance.yahoo.com/v8/finance/chart/%5EGDAXI?range=5d&interval=1d'

def correct():
    assert hashlib.sha256(TARGET.read_bytes()).hexdigest() == ORIGINAL_SHA256, 'Only the inspected original may be corrected'
    doc = pdf.open(TARGET)
    page = doc[0]
    spans = [s for b in page.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans']]
    replacements = []
    for span in spans:
        old = span['text']
        if old not in ('-2,63 %', '-704,58'):
            continue
        new = '-2,08 %' if old == '-2,63 %' else '-553,27'
        background = (247/255,249/255,253/255) if span['origin'][1] < 300 else (1,1,1)
        page.add_redact_annot(pdf.Rect(span['bbox']), fill=background)
        replacements.append((span,new))
    assert len(replacements) == 3
    page.apply_redactions(images=0, graphics=0)
    regular = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
    bold = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
    # Resolve the installed font location without changing the report's face.
    import subprocess
    regular = subprocess.check_output(['fc-match','-f','%{file}','Liberation Sans:style=Regular'],text=True)
    bold = subprocess.check_output(['fc-match','-f','%{file}','Liberation Sans:style=Bold'],text=True)
    page.insert_font(fontname='correctionRegular',fontfile=regular)
    page.insert_font(fontname='correctionBold',fontfile=bold)
    for span,new in replacements:
        page.insert_text(span['origin'],new,fontsize=span['size'],fontname='correctionBold' if 'Bold' in span['font'] else 'correctionRegular',color=(198/255,40/255,40/255))
    rect = pdf.Rect(42.5,599,552.5,688)
    page.draw_rect(rect,color=(207/255,224/255,247/255),fill=(241/255,246/255,253/255),width=.7)
    text = ('Korrektur vom 18.11.2026, 12:17 Uhr\n'
            'DAX-Schluss vom 17.11.: 26.045,37 Punkte, -553,27 Punkte (-2,08 %) zum Vortag.\n'
            'Zuvor standen hier irrtümlich -704,58 Punkte / -2,63 %. Schlussstand und\n'
            'Redaktionsschluss (00:55 Uhr) bleiben unverändert. Die historische Referenz\n'
            'war falsch zugeordnet. Quellen: FinanzNachrichten (Schlussbericht), Yahoo (Tageskurse).')
    remaining = page.insert_textbox(pdf.Rect(51,606,544,678),text,fontname='correctionRegular',fontsize=9,color=(.17,.20,.31),lineheight=1.35)
    assert remaining >= 0
    page.insert_link({'kind':pdf.LINK_URI,'from':pdf.Rect(180,660,370,678),'uri':SOURCE})
    page.insert_link({'kind':pdf.LINK_URI,'from':pdf.Rect(370,660,544,678),'uri':HISTORY})
    metadata=doc.metadata
    metadata['modDate']='D:20261118121700+01\'00\''
    doc.set_metadata(metadata)
    output=TARGET.with_suffix('.corrected.pdf')
    doc.save(output,garbage=4,deflate=True)
    doc.close()
    output.replace(TARGET)

if __name__ == '__main__': correct()
