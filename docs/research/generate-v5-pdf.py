#!/usr/bin/env python3
"""Generate PDF for Doramagic V5 Product Definition."""

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('STHeitiLight', '/System/Library/Fonts/STHeiti Light.ttc', subfontIndex=0))

BASE = os.path.dirname(__file__)
INPUT = os.path.join(BASE, '20260315_doramagic_v5_product_definition.md')
OUTPUT = os.path.join(BASE, '20260315_doramagic_v5_product_definition.pdf')

DARK = HexColor('#1a1a2e')
ACCENT = HexColor('#16213e')
BLUE = HexColor('#0f3460')
HIGHLIGHT = HexColor('#e94560')
LIGHT_BG = HexColor('#f5f5f5')
BORDER = HexColor('#cccccc')

styles = getSampleStyleSheet()

title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
    fontName='STHeiti', fontSize=24, leading=32, textColor=DARK, spaceAfter=4*mm, alignment=TA_CENTER)
subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
    fontName='STHeitiLight', fontSize=11, leading=15, textColor=HexColor('#666'), alignment=TA_CENTER, spaceAfter=6*mm)
h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
    fontName='STHeiti', fontSize=18, leading=24, textColor=DARK, spaceBefore=12*mm, spaceAfter=4*mm)
h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
    fontName='STHeiti', fontSize=14, leading=19, textColor=BLUE, spaceBefore=8*mm, spaceAfter=3*mm)
h3_style = ParagraphStyle('H3', parent=styles['Heading3'],
    fontName='STHeiti', fontSize=11, leading=15, textColor=ACCENT, spaceBefore=5*mm, spaceAfter=2*mm)
body_style = ParagraphStyle('Body', parent=styles['Normal'],
    fontName='STHeitiLight', fontSize=9, leading=13.5, textColor=black, spaceAfter=2*mm, alignment=TA_JUSTIFY)
bold_style = ParagraphStyle('Bold', parent=body_style, fontName='STHeiti')
quote_style = ParagraphStyle('Quote', parent=body_style,
    leftIndent=8*mm, rightIndent=5*mm, textColor=HexColor('#444'),
    borderColor=HIGHLIGHT, borderWidth=2, borderPadding=4, spaceAfter=3*mm)
bullet_style = ParagraphStyle('Bullet', parent=body_style,
    leftIndent=8*mm, bulletIndent=3*mm, spaceAfter=1.5*mm)
code_style = ParagraphStyle('Code', parent=body_style,
    fontName='Courier', fontSize=7.5, leading=10, leftIndent=5*mm,
    backColor=LIGHT_BG, borderColor=BORDER, borderWidth=0.5, borderPadding=3, spaceAfter=3*mm)

def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    if col_widths is None:
        w = 165*mm / len(headers)
        col_widths = [w] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'STHeiti'),
        ('FONTNAME', (0, 1), (-1, -1), 'STHeitiLight'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LEADING', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    return t

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=3*mm, spaceBefore=1*mm)

def escape_xml(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def md_to_flowables(md_text):
    """Convert markdown to reportlab flowables."""
    story = []
    lines = md_text.split('\n')
    in_code = False
    code_buf = []
    in_table = False
    table_rows = []
    table_headers = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                code_text = escape_xml('\n'.join(code_buf))
                if code_text.strip():
                    story.append(Paragraph(code_text.replace('\n', '<br/>'), code_style))
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Table
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and all(set(c) <= set('- :') for c in cells):
                # separator row
                i += 1
                continue
            if not in_table:
                in_table = True
                table_headers = cells
                table_rows = []
            else:
                table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            # end of table
            if table_headers and table_rows:
                # Normalize row lengths
                ncols = len(table_headers)
                norm_rows = []
                for r in table_rows:
                    while len(r) < ncols:
                        r.append('')
                    norm_rows.append(r[:ncols])
                w = 165*mm / ncols
                story.append(make_table(table_headers, norm_rows, [w]*ncols))
                story.append(Spacer(1, 2*mm))
            in_table = False
            table_headers = []
            table_rows = []
            # Don't increment i, process current line

        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # Headings
        if stripped.startswith('# ') and not stripped.startswith('## '):
            text = stripped[2:]
            if text.startswith('第') or text.startswith('附录'):
                story.append(PageBreak())
            story.append(Paragraph(text, h1_style))
            story.append(hr())
            i += 1
            continue
        if stripped.startswith('## '):
            story.append(Paragraph(stripped[3:], h2_style))
            i += 1
            continue
        if stripped.startswith('### '):
            story.append(Paragraph(stripped[4:], h3_style))
            i += 1
            continue

        # Blockquote
        if stripped.startswith('> '):
            quote_text = stripped[2:]
            # Collect multi-line quotes
            while i + 1 < len(lines) and lines[i+1].strip().startswith('> '):
                i += 1
                quote_text += '<br/>' + lines[i].strip()[2:]
            story.append(Paragraph(process_inline(quote_text), quote_style))
            i += 1
            continue

        # Horizontal rule
        if stripped == '---':
            story.append(hr())
            i += 1
            continue

        # Bullet
        if stripped.startswith('- ') or stripped.startswith('* '):
            text = stripped[2:]
            story.append(Paragraph(f'• {process_inline(text)}', bullet_style))
            i += 1
            continue

        # Numbered list
        if re.match(r'^\d+\.\s', stripped):
            text = re.sub(r'^\d+\.\s', '', stripped)
            story.append(Paragraph(f'• {process_inline(text)}', bullet_style))
            i += 1
            continue

        # Regular paragraph
        story.append(Paragraph(process_inline(stripped), body_style))
        i += 1

    # Flush remaining table
    if in_table and table_headers and table_rows:
        ncols = len(table_headers)
        norm_rows = []
        for r in table_rows:
            while len(r) < ncols:
                r.append('')
            norm_rows.append(r[:ncols])
        w = 165*mm / ncols
        story.append(make_table(table_headers, norm_rows, [w]*ncols))

    return story

def process_inline(text):
    """Process inline markdown formatting."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<font face="Courier" size="7.5" color="#c0392b">\1</font>', text)
    # Links (just show text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    return text

def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title='Doramagic v5 产品定义与技术规划全书',
        author='Tang + Claude + Gemini + Codex'
    )

    story = []

    # Title page
    story.append(Spacer(1, 40*mm))
    story.append(Paragraph('Doramagic v5', ParagraphStyle('BigTitle', parent=title_style, fontSize=36, leading=44)))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph('产品定义与技术规划全书', title_style))
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph('2026-03-15', subtitle_style))
    story.append(Paragraph('汇总 ~15 轮三方研究，为开发做准备', subtitle_style))
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(
        'Tang（产品决策）<br/>'
        'Claude Opus（知识工程+架构）<br/>'
        'Gemini（产品+市场+UX）<br/>'
        'Codex（工程实现+算法）',
        ParagraphStyle('Authors', parent=subtitle_style, fontSize=10, leading=14)
    ))
    story.append(Spacer(1, 25*mm))
    story.append(Paragraph(
        '不教用户做事，给他工具。<br/>'
        '代码说事实，AI 说故事。<br/>'
        '能力升级，本质不变。',
        ParagraphStyle('Tagline', parent=quote_style, alignment=TA_CENTER, fontSize=11, leading=16)
    ))

    story.append(PageBreak())

    # Read markdown and convert
    with open(INPUT, 'r', encoding='utf-8') as f:
        md = f.read()

    # Skip the title block (first few lines until first #)
    lines = md.split('\n')
    start = 0
    for idx, line in enumerate(lines):
        if line.startswith('# 第一部分'):
            start = idx
            break
    md_body = '\n'.join(lines[start:])

    flowables = md_to_flowables(md_body)
    story.extend(flowables)

    doc.build(story)
    size = os.path.getsize(OUTPUT)
    print(f'PDF generated: {OUTPUT}')
    print(f'Size: {size / 1024:.0f} KB')

if __name__ == '__main__':
    build()
