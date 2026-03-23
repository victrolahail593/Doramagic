#!/usr/bin/env python3
"""Generate PDF for Sim2 Calorie Skill - complete delivery package."""

import re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('STHeitiLight', '/System/Library/Fonts/STHeiti Light.ttc', subfontIndex=0))

BASE = os.path.dirname(__file__)
OUTPUT = os.path.join(BASE, 'calorie-skill-sim2.pdf')

DARK = HexColor('#1a1a2e')
ACCENT = HexColor('#16213e')
BLUE = HexColor('#0f3460')
HIGHLIGHT = HexColor('#e94560')
LIGHT_BG = HexColor('#f5f5f5')
BORDER = HexColor('#cccccc')
GREEN = HexColor('#27ae60')

styles = getSampleStyleSheet()
title_s = ParagraphStyle('T', parent=styles['Title'], fontName='STHeiti', fontSize=22, leading=28, textColor=DARK, spaceAfter=4*mm, alignment=TA_CENTER)
sub_s = ParagraphStyle('Sub', parent=styles['Normal'], fontName='STHeitiLight', fontSize=11, leading=15, textColor=HexColor('#666'), alignment=TA_CENTER, spaceAfter=6*mm)
h1_s = ParagraphStyle('H1', parent=styles['Heading1'], fontName='STHeiti', fontSize=16, leading=22, textColor=DARK, spaceBefore=10*mm, spaceAfter=4*mm)
h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontName='STHeiti', fontSize=13, leading=18, textColor=BLUE, spaceBefore=6*mm, spaceAfter=3*mm)
body_s = ParagraphStyle('B', parent=styles['Normal'], fontName='STHeitiLight', fontSize=9.5, leading=14, textColor=black, spaceAfter=2*mm)
bold_s = ParagraphStyle('Bd', parent=body_s, fontName='STHeiti')
quote_s = ParagraphStyle('Q', parent=body_s, leftIndent=8*mm, rightIndent=5*mm, textColor=HexColor('#444'), borderColor=HIGHLIGHT, borderWidth=2, borderPadding=4, spaceAfter=3*mm)
bullet_s = ParagraphStyle('Bu', parent=body_s, leftIndent=8*mm, bulletIndent=3*mm, spaceAfter=1.5*mm)
code_s = ParagraphStyle('Co', parent=body_s, fontName='Courier', fontSize=8, leading=11, leftIndent=5*mm, backColor=LIGHT_BG, borderColor=BORDER, borderWidth=0.5, borderPadding=3, spaceAfter=3*mm)

def tbl(headers, rows, widths=None):
    data = [headers] + rows
    if not widths: widths = [165*mm/len(headers)] * len(headers)
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,0),'STHeiti'),('FONTNAME',(0,1),(-1,-1),'STHeitiLight'),
        ('FONTSIZE',(0,0),(-1,-1),8.5),('LEADING',(0,0),(-1,-1),12),
        ('BACKGROUND',(0,0),(-1,0),ACCENT),('TEXTCOLOR',(0,0),(-1,0),white),
        ('ALIGN',(0,0),(-1,0),'CENTER'),('ALIGN',(0,1),(-1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.5,BORDER),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,LIGHT_BG]),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
    ]))
    return t

def hr(): return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=3*mm, spaceBefore=1*mm)

def build():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    s = []

    # Title
    s.append(Spacer(1, 30*mm))
    s.append(Paragraph('Doramagic', ParagraphStyle('Big', parent=title_s, fontSize=32)))
    s.append(Spacer(1, 3*mm))
    s.append(Paragraph('Calorie Tracker Skill', title_s))
    s.append(Paragraph('Multi-Project Pipeline Sim2', sub_s))
    s.append(Spacer(1, 8*mm))
    s.append(Paragraph('2026-03-17', sub_s))
    s.append(Spacer(1, 5*mm))
    s.append(Paragraph(
        '3 projects + 4 community skills + 1 tutorial<br/>'
        '= 9 GCD + 4 conflicts resolved + 11 unique insights<br/>'
        '= 1 runnable SKILL.md (433 lines)',
        ParagraphStyle('Tag', parent=quote_s, alignment=TA_CENTER, fontSize=10, leading=15)
    ))
    s.append(Spacer(1, 10*mm))
    s.append(Paragraph('Phase A-H Pipeline: Complete', ParagraphStyle('Pass', parent=bold_s, alignment=TA_CENTER, fontSize=14, textColor=GREEN)))
    s.append(Paragraph('Quality Gate: 7/7 PASS', ParagraphStyle('Pass2', parent=bold_s, alignment=TA_CENTER, fontSize=12, textColor=GREEN)))

    s.append(PageBreak())

    # Pipeline Overview
    s.append(Paragraph('Pipeline Overview', h1_s))
    s.append(hr())
    s.append(tbl(
        ['Phase', 'Task', 'Status', 'Output'],
        [
            ['A', 'Need Understanding', 'DONE', 'need_profile.json'],
            ['B', 'Project Discovery', 'DONE', '3 repos + 4 skills + 1 tutorial'],
            ['C', 'Parallel Soul Extraction (x3)', 'DONE', '3 extraction.md (structured cards)'],
            ['D', 'Community Knowledge', 'DONE', 'community/extraction.md'],
            ['E', 'Knowledge Synthesis', 'DONE', 'synthesis_report.md'],
            ['F', 'Skill Assembly', 'DONE', 'SKILL.md (433 lines)'],
            ['G', 'Quality Gate', '7/7 PASS', 'validation in synthesis_report.md'],
            ['H', 'Delivery', 'DONE', '4 files: SKILL + PROVENANCE + LIMITATIONS + synthesis'],
        ],
        [15*mm, 50*mm, 30*mm, 70*mm]
    ))

    # Knowledge Sources
    s.append(Paragraph('Knowledge Sources', h1_s))
    s.append(hr())
    s.append(tbl(
        ['Source', 'Type', 'Key Contribution'],
        [
            ['ai-calorie-counter', 'GitHub', 'LLM-as-Parser (JSON contract), BMR calc, context injection'],
            ['FoodYou', 'GitHub', '43-field nutrition schema, Complete/Incomplete semantics, Recipe.unpack'],
            ['OpenNutriTracker', 'GitHub', 'IOM 2005 TDEE, MET exercise DB, TrackedDay snapshot, per-100g standard'],
            ['calorie-counter (ClawHub)', 'Skill', 'Protein estimation rules, basic tracking flow'],
            ['opencal (ClawHub)', 'Skill', 'Per-100g scaling formula, dual-direction interaction'],
            ['diet-tracker (ClawHub)', 'Skill', 'USER.md + memory/YYYY-MM-DD.md architecture'],
            ['health-summary (ClawHub)', 'Skill', 'Daily/weekly/monthly aggregation patterns'],
            ['LobsterLair Tutorial', 'Tutorial', 'Photo recognition flow, personality layer (SOUL.md), 80-90% accuracy'],
        ],
        [40*mm, 20*mm, 105*mm]
    ))

    s.append(PageBreak())

    # Phase E: Synthesis
    s.append(Paragraph('Phase E: Knowledge Synthesis', h1_s))
    s.append(hr())

    s.append(Paragraph('9 Consensus Items (GCD)', h2_s))
    gcds = [
        ('GCD-01', 'Macronutrient conversion: P=4, C=4, F=9 kcal/g', '3/3'),
        ('GCD-02', 'Daily goal = BMR/TDEE + exercise - deficit', '3/3'),
        ('GCD-03', 'Per-100g normalized storage', '3/3'),
        ('GCD-04', '4 meal categories (breakfast/lunch/dinner/snack)', '3/3'),
        ('GCD-05', 'Exercise tracking with MET values', '3/3'),
        ('GCD-06', 'User profile separate from tracking data', '3/3 + community'),
        ('GCD-07', 'Daily summary: consumed/target/remaining', '3/3 + community'),
        ('GCD-08', 'YYYY-MM-DD date-named files', 'community consensus'),
        ('GCD-09', 'User correction must be available', '3/3'),
    ]
    s.append(tbl(['ID', 'Consensus', 'Support'], gcds, [20*mm, 115*mm, 30*mm]))

    s.append(Paragraph('4 Conflicts (All Resolved)', h2_s))
    conflicts = [
        ('CONFLICT-01', 'BMR formula: MSJ vs IOM vs Schofield vs HB', 'Resolved: MSJ (simplest, accurate enough)'),
        ('CONFLICT-02', 'Storage: JSON vs Markdown vs DB', 'Resolved: JSON + MD dual-track'),
        ('CONFLICT-03', 'Food data: API lookup vs LLM estimation', 'Resolved: LLM-first, API optional V2'),
        ('CONFLICT-04', 'Macro ratio: 45/30/25 vs 60/15/25 vs 50/25/25', 'Resolved: 50/25/25 default, user customizable'),
    ]
    s.append(tbl(['ID', 'Conflict', 'Resolution'], conflicts, [25*mm, 65*mm, 75*mm]))

    s.append(Paragraph('Top 5 Unique Insights Adopted', h2_s))
    uniques = [
        ('ai-calorie-counter', 'LLM-as-Parser: AI outputs structured JSON, not conversation'),
        ('ai-calorie-counter', 'Context injection: pass aggregated daily totals, not raw records'),
        ('FoodYou', 'Complete/Incomplete nutrient semantics (unknown != zero)'),
        ('OpenNutriTracker', 'TrackedDay snapshot (history unaffected by profile changes)'),
        ('Community', 'WHY-layer gap: no skill does trend analysis (our differentiator)'),
    ]
    s.append(tbl(['Source', 'Unique Insight'], uniques, [40*mm, 125*mm]))

    s.append(PageBreak())

    # Phase F: SKILL.md Summary
    s.append(Paragraph('Phase F: SKILL.md Design', h1_s))
    s.append(hr())

    s.append(Paragraph('Core Flows', h2_s))
    flows = [
        ['1. First-time Setup', 'Collect: gender/age/height/weight/activity/goal', 'Calculate MSJ BMR -> TDEE -> daily targets'],
        ['2. Food Logging', 'User: text/photo -> AI: JSON estimate -> Write daily log', 'Fields: name/weight/calories/P/C/F/confidence'],
        ['3. Exercise Logging', 'User: "ran 30 min" -> MET lookup -> calorie burn', 'Formula: MET x weight(kg) x duration(h)'],
        ['4. Remaining Query', '"How much can I still eat?"', 'TDEE - consumed + exercise = remaining'],
        ['5. Daily Summary', 'Auto at 9PM or user-triggered', 'Aggregate -> compare to target -> generate report'],
        ['6. Cron Reminders', '12:30 lunch / 18:00 dinner / 21:00 summary', 'Configurable in metadata.openclaw.cron'],
    ]
    s.append(tbl(['Flow', 'Trigger', 'Logic'], flows, [35*mm, 65*mm, 65*mm]))

    s.append(Paragraph('Data Architecture', h2_s))
    s.append(Paragraph(
        '~/clawd/memory/health/<br/>'
        '  profile.json — User profile (BMR/TDEE/targets)<br/>'
        '  daily/YYYY-MM-DD.json — Structured daily log (JSON)<br/>'
        '  daily/YYYY-MM-DD.md — Human-readable daily report (Markdown)<br/>'
        '  weekly/YYYY-WNN.md — Weekly summary',
        code_s
    ))

    s.append(Paragraph('AI Prompt Contract (from ai-calorie-counter)', h2_s))
    s.append(Paragraph(
        'Food: {type:"food", time, meal, name, weight_g, calories, protein_g, carbs_g, fat_g, confidence}<br/>'
        'Exercise: {type:"exercise", time, name, duration_min, met, calories_burned, confidence}<br/>'
        'Context injection: daily aggregates (not raw records) to minimize tokens',
        code_s
    ))

    s.append(PageBreak())

    # Phase G: Quality Gate
    s.append(Paragraph('Phase G: Quality Gate', h1_s))
    s.append(hr())
    gates = [
        ['1. Consistency', 'PASS', 'No internal contradictions found'],
        ['2. Completeness', 'PASS', 'All 6 user-requested features covered'],
        ['3. Traceability', 'PASS', '96% of knowledge traceable to file:line (27/28 items)'],
        ['4. Platform Fit', 'PASS', 'Valid OpenClaw SKILL.md format with frontmatter'],
        ['5. Conflict Resolution', 'PASS', '4/4 conflicts resolved with rationale'],
        ['6. License', 'PASS (warn)', 'Source projects: MIT + GPLv3. Knowledge extraction = not code copying'],
        ['7. Dark Trap Scan', 'PASS (warn)', 'AI estimation accuracy 15-30% (disclosed in LIMITATIONS.md)'],
    ]
    s.append(tbl(['Check', 'Result', 'Detail'], gates, [35*mm, 25*mm, 105*mm]))

    # Phase H: Delivery
    s.append(Paragraph('Phase H: Delivery Package', h1_s))
    s.append(hr())
    delivery = [
        ['SKILL.md', '433 lines', 'Runnable OpenClaw skill with 6 flows + cron + 7 pitfall warnings'],
        ['PROVENANCE.md', '27 entries', '96% traceable to source file:line evidence'],
        ['LIMITATIONS.md', '15 items', 'Accuracy limits, formula caveats, platform constraints'],
        ['synthesis_report.md', '376 lines', '9 GCD + 4 conflicts + 11 unique insights + validation'],
    ]
    s.append(tbl(['File', 'Size', 'Content'], delivery, [35*mm, 25*mm, 105*mm]))

    # Comparison
    s.append(Paragraph('Sim1 vs Sim2 Comparison', h1_s))
    s.append(hr())
    comparison = [
        ['Stage 0 (repo_facts)', 'Skipped', 'Done (all 3 projects)'],
        ['Structured Cards', 'Free-form report', 'CC/WF/DR cards with file:line'],
        ['Evidence Binding', 'File names only', '96% file:line traceable'],
        ['Community Skills', 'Searched but ad-hoc', 'Systematic lightweight extraction'],
        ['Knowledge Synthesis', 'Manual summary', '9 GCD + 4 conflicts + 11 unique'],
        ['Quality Gate', 'None', '7/7 PASS'],
        ['Output', 'Design doc only', 'Runnable SKILL.md + 3 companion files'],
        ['Pipeline Compliance', 'Ad-hoc', 'Phase A-H fully followed'],
    ]
    s.append(tbl(['Dimension', 'Sim1', 'Sim2'], comparison, [35*mm, 65*mm, 65*mm]))

    s.append(Spacer(1, 8*mm))
    s.append(Paragraph(
        'Sim2 proves the multi-project pipeline works.<br/>'
        'From "I want a calorie tracking skill" to a runnable 433-line SKILL.md<br/>'
        'with full provenance and quality gates — all in one session.',
        ParagraphStyle('Final', parent=quote_s, alignment=TA_CENTER, fontSize=10, leading=15)
    ))

    doc.build(s)
    print(f'PDF: {OUTPUT} ({os.path.getsize(OUTPUT)//1024} KB)')

if __name__ == '__main__':
    build()
