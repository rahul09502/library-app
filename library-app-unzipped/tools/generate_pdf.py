from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import textwrap
import sys

MD = 'presentation.md'
OUT = 'library_project_presentation.pdf'

def draw_text(c, text, x, y, max_width):
    lines = []
    for para in text.split('\n'):
        if not para.strip():
            lines.append('')
            continue
        wrapped = textwrap.wrap(para, width=100)
        lines.extend(wrapped)
    for line in lines:
        c.drawString(x, y, line)
        y -= 10
        if y < 20*mm:
            c.showPage()
            y = A4[1] - 20*mm
    return y

def main():
    try:
        with open(MD, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print('Error reading', MD, e)
        sys.exit(1)

    c = canvas.Canvas(OUT, pagesize=A4)
    left = 20*mm
    top = A4[1] - 20*mm
    c.setFont('Helvetica', 11)
    y = top
    y = draw_text(c, content, left, y, A4[0] - 40*mm)
    c.save()
    print('Created PDF:', OUT)

if __name__ == '__main__':
    main()
