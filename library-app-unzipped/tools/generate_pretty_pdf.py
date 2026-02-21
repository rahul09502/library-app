from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import re

MD = 'presentation.md'
OUT = 'library_project_presentation_pretty.pdf'

def read_md(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # strip fenced code blocks (``` ... ```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    return text

def extract_table(md):
    lines = md.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('|') and 'Title' in line and 'Author' in line:
            start = i
            break
    if start is None:
        return None
    rows = []
    # skip header separator if present
    for line in lines[start:]:
        if not line.strip():
            break
        if line.strip().startswith('|'):
            parts = [p.strip() for p in line.strip().strip('|').split('|')]
            rows.append(parts)
        else:
            break
    return rows

def md_to_paragraphs(md):
    # split into blocks by blank line
    blocks = [b.strip() for b in re.split(r'\n\s*\n', md) if b.strip()]
    # remove table block
    cleaned = []
    for b in blocks:
        if b.startswith('|') and 'Title' in b:
            continue
        cleaned.append(b)
    return cleaned

def build_pdf():
    md = read_md(MD)
    rows = extract_table(md) or []
    paras = md_to_paragraphs(md)

    doc = SimpleDocTemplate(OUT, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Heading1'], fontSize=20, spaceAfter=12)
    h2 = ParagraphStyle('h2', parent=styles['Heading2'], fontSize=14, spaceAfter=6)
    body = ParagraphStyle('body', parent=styles['BodyText'], fontSize=11, leading=14)

    flow = []
    flow.append(Paragraph('Library App — Project Overview', title_style))
    flow.append(Spacer(1, 6))

    # Add paragraphs (skip the table block which we'll add as a styled table)
    for p in paras:
        # treat MD headings
        if re.match(r'^\d+\. ', p) or p.startswith('1.'):
            flow.append(Paragraph(p.replace('\n', '<br/>'), body))
        else:
            flow.append(Paragraph(p.replace('`', ''), body))
        flow.append(Spacer(1, 6))

    if rows:
        # first row is header
        header = rows[0]
        data = [header]
        for r in rows[2:]:  # skip separator line at index 1
            data.append(r)
        table = Table(data, colWidths=[90*mm, 60*mm, 18*mm, 36*mm, 20*mm, 30*mm])
        tbl_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN',(2,0),(-1,-1),'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
        ])
        table.setStyle(tbl_style)
        flow.append(Spacer(1,12))
        flow.append(Paragraph('Sample Books', h2))
        flow.append(table)

    doc.build(flow)
    print('Created pretty PDF:', OUT)

if __name__ == '__main__':
    build_pdf()
