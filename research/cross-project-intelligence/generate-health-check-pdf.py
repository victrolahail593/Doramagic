#!/usr/bin/env python3
"""Generate PDF for Health Check Synthesis Report."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register Chinese font
pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('STHeitiLight', '/System/Library/Fonts/STHeiti Light.ttc', subfontIndex=0))

OUTPUT = os.path.join(os.path.dirname(__file__), 'health-check-synthesis.pdf')

# Colors
DARK = HexColor('#1a1a2e')
ACCENT = HexColor('#16213e')
BLUE = HexColor('#0f3460')
HIGHLIGHT = HexColor('#e94560')
LIGHT_BG = HexColor('#f5f5f5')
WHITE_BG = HexColor('#ffffff')
BORDER = HexColor('#cccccc')
GREEN = HexColor('#27ae60')
ORANGE = HexColor('#f39c12')
RED = HexColor('#e74c3c')

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle', parent=styles['Title'],
    fontName='STHeiti', fontSize=22, leading=28,
    textColor=DARK, spaceAfter=6*mm, alignment=TA_CENTER
)
subtitle_style = ParagraphStyle(
    'Subtitle', parent=styles['Normal'],
    fontName='STHeitiLight', fontSize=11, leading=15,
    textColor=HexColor('#666666'), alignment=TA_CENTER, spaceAfter=8*mm
)
h1_style = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName='STHeiti', fontSize=16, leading=22,
    textColor=DARK, spaceBefore=10*mm, spaceAfter=4*mm,
    borderColor=HIGHLIGHT, borderWidth=0, borderPadding=0
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName='STHeiti', fontSize=13, leading=18,
    textColor=BLUE, spaceBefore=6*mm, spaceAfter=3*mm
)
h3_style = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontName='STHeiti', fontSize=11, leading=15,
    textColor=ACCENT, spaceBefore=4*mm, spaceAfter=2*mm
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='STHeitiLight', fontSize=9.5, leading=14,
    textColor=black, spaceAfter=2*mm, alignment=TA_JUSTIFY
)
body_bold = ParagraphStyle(
    'BodyBold', parent=body_style,
    fontName='STHeiti'
)
quote_style = ParagraphStyle(
    'Quote', parent=body_style,
    fontName='STHeitiLight', fontSize=9.5, leading=14,
    leftIndent=10*mm, rightIndent=5*mm,
    textColor=HexColor('#444444'), spaceAfter=3*mm,
    borderColor=HIGHLIGHT, borderWidth=2, borderPadding=5,
)
code_style = ParagraphStyle(
    'Code', parent=body_style,
    fontName='Courier', fontSize=8, leading=11,
    leftIndent=5*mm, backColor=LIGHT_BG, spaceAfter=3*mm,
    borderColor=BORDER, borderWidth=0.5, borderPadding=4
)
bullet_style = ParagraphStyle(
    'Bullet', parent=body_style,
    fontName='STHeitiLight', fontSize=9.5, leading=14,
    leftIndent=8*mm, bulletIndent=3*mm,
    spaceAfter=1.5*mm
)

def B(text):
    return f'<b>{text}</b>'

def I(text):
    return f'<i>{text}</i>'

def C(text):
    return f'<font face="Courier" size="8" color="#c0392b">{text}</font>'

def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    if col_widths is None:
        col_widths = [160*mm / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'STHeiti'),
        ('FONTNAME', (0, 1), (-1, -1), 'STHeitiLight'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('LEADING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE_BG, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=4*mm, spaceBefore=2*mm)

def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title='Doramagic 知识健康检查三方研究综合报告',
        author='Claude + Gemini + Codex'
    )

    story = []

    # Title page
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph('知识健康检查', title_style))
    story.append(Paragraph('Knowledge Health Check', ParagraphStyle(
        'EN', parent=subtitle_style, fontSize=14, textColor=HexColor('#888888')
    )))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph('三方研究综合报告', ParagraphStyle(
        'Sub2', parent=subtitle_style, fontSize=13, textColor=DARK
    )))
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph('2026-03-15', subtitle_style))
    story.append(Paragraph(
        'Claude Opus（知识工程+产品设计）<br/>'
        'Gemini（产品+市场+UX）<br/>'
        'Codex（工程实现+算法）',
        ParagraphStyle('Authors', parent=subtitle_style, fontSize=10, leading=15)
    ))
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph(
        '知识健康检查 = 领域图谱的镜子功能。<br/>'
        '代码做匹配，结构做分类，措辞做尊重。<br/>'
        '三方各守一层，缺一不可。',
        ParagraphStyle('TagLine', parent=quote_style, alignment=TA_CENTER, fontSize=10, leading=15)
    ))

    story.append(PageBreak())

    # ===== Section 1: Six Consensus =====
    story.append(Paragraph('一、六项全票共识', h1_style))
    story.append(hr())

    consensus = [
        ('共识 1', '体检是图谱的消费层，不是新产品',
         'Claude："图谱的消费界面，不是新产品"\nCodex："受约束匹配与分类引擎，不是新系统"\nGemini："知识生命力的诊断"（在图谱框架内）',
         '体检不独立存在。没有图谱，就没有体检（STALE 除外）。'),
        ('共识 2', '不给总分，不定义"健康"',
         'Claude：明确拒绝总分，用雷达图/多维向量\nCodex："不是评分器"\nGemini：用"知识星系坐标"而非打分',
         '体检展示位置和差异，不做好坏判断。"不教用户做事"原则的直接推论。'),
        ('共识 3', 'STALE 检测可独立运行',
         'Claude："即使图谱尚未建成，也可以先上线知识时效检查"\nCodex：显式分离 stale_engine() 和 map_alignment_engine()\nGemini：未深入，不矛盾',
         'STALE 是体检的最小可用子集，最早能上线的功能。不依赖图谱，只依赖废弃事件数据库。'),
        ('共识 4', '参照系透明度是生死线',
         'Claude："参照系强度必须视觉上无法忽略"\nGemini：允许用户踢出项目重算\nCodex：缓存键包含 5 维版本信息',
         '用户必须始终知道"这个结论基于多大的样本"。Alpha 阶段措辞必须克制。'),
        ('共识 5', '7 类信号分类体系',
         'Claude：提出完整 7 类\nCodex：接受 7 类，补充拆成确定性+解释性双路\nGemini：引用信号分类，关注产品呈现',
         '7 类信号是体检核心骨架。工程上拆双路是正确的。'),
        ('共识 6', 'V1 从 CLI/文件输出开始',
         'Claude：/health-check 命令，输出 JSON + MD\nCodex：完整数据流到文件\nGemini：Knowledge Galaxy 是 V2+ 方向',
         'V1 产出文件，V2+ 有 web 界面时再做可视化。'),
    ]

    for tag, title, evidence, conclusion in consensus:
        story.append(Paragraph(f'{tag}：{title}', h2_style))
        for line in evidence.split('\n'):
            story.append(Paragraph(f'• {line}', bullet_style))
        story.append(Paragraph(f'{B("结论")}：{conclusion}', body_bold))
        story.append(Spacer(1, 2*mm))

    story.append(PageBreak())

    # ===== Section 2: Unique Contributions =====
    story.append(Paragraph('二、各方独有最佳贡献', h1_style))
    story.append(hr())

    # Claude
    story.append(Paragraph('Claude 独有：理论框架 + 哲学定位', h2_style))
    claude_items = [
        f'{B("GIS 叠加分析类比")}：排除三个危险类比（医疗体检/财务审计/代码审查），找到准确定位——"地图叠加分析"。产品不做诊断、不做合规检查、不看代码质量，只做知识位置定位。',
        f'{B("6 个可观测维度")}：共识覆盖率 / 时效性 / 独创密度 / 路线位置 / 缺失区域 / 参照系强度。不定义"健康"，但定义"可观测的坐标"。',
        f'{B("严重性分级")}：HIGH-SIGNAL / SIGNAL / CONTEXT，拒绝 Critical/Warning/Info（审计语言），用"信息密度"替代"严重性"。',
        f'{B("完整案例演示")}：用 geo-seo-claude 实际数据生成 130+ 行 HEALTH_CHECK.md 样例。三方唯一端到端案例。',
        f'{B("4 个新可能性")}：项目简历（OpenClaw 发布附带）/ 知识趋势追踪 / 匿名化领域健康度 / 反向体检。',
        f'{B("5 个风险分析")}：权威性错觉 / 共识偏见固化 / 吹毛求疵 / 过时误判 / 选型依赖。每个有缓解方案。',
    ]
    for item in claude_items:
        story.append(Paragraph(f'• {item}', bullet_style))

    story.append(Spacer(1, 3*mm))

    # Gemini
    story.append(Paragraph('Gemini 独有：产品体验 + 市场策略', h2_style))
    gemini_items = [
        f'{B("知识星系可视化")}：二维坐标系（横轴共识度、纵轴新颖度），项目作为"彗星"，标杆项目作为"行星群"。V2+ 交互设计方向。',
        f'{B("渐进式披露 UX")}：30 秒概览（3 个高能信号）→ 5 分钟关键发现（Feed 流）→ 按需深入（分屏对比）。即使 V1 Markdown 也应遵循此层次。',
        f'{B("情感设计")}：禁止"错误/漏掉/落后"，推荐"观测到差异/非主流路径/新兴趋势"。{B("直接采纳")}，渲染 prompt 必须包含。',
        f'{B("竞品差异化")}：SonarQube 纠错别字 / Copilot 帮写下段 / Doramagic 评估论文观点是否过时。三个完全不同的赛道。',
        f'{B("Freemium 商业模型")}：免费基础体检 → 付费证据链+保鲜订阅 → 企业技术偏离度报告。',
        f'{B("PM/CTO 翻译层")}：STALE→维护成本 / ORIGINAL→核心壁垒 / DIVERGENT→稳定性隐患。V2+ 方向。',
    ]
    for item in gemini_items:
        story.append(Paragraph(f'• {item}', bullet_style))

    story.append(Spacer(1, 3*mm))

    # Codex
    story.append(Paragraph('Codex 独有：工程深度', h2_style))
    codex_items = [
        f'{B("三段式匹配算法")}：候选召回（lexical + semantic ANN）→ 结构化裁决 → 信号分类。体检工程核心骨架。',
        f'{B("加权匹配公式")}：{C("MatchScore = 0.30×subject + 0.25×predicate + 0.15×object + 0.20×scope + 0.10×normative_force")}',
        f'{B("四段匹配阈值")}：EXACT_ALIGNED ≥0.92 / SEMANTIC ≥0.80 / PARTIAL ≥0.62 / NO_MATCH &lt;0.62。设计偏保守。',
        f'{B("MISSING 双阈值")}：coverage ≥0.60 + independence ≥0.55 + 独立支持 ≥3。比 Claude 的 "X%" 更精确。',
        f'{B("ORIGINAL 二次检验")}：更大候选窗口重新检索，确认无匹配才标 ORIGINAL。防"表述不同"假阳性。',
        f'{B("确定性/解释性双路分离")}：Route A（ALIGNED/STALE/MISSING/ORIGINAL）靠阈值，Route B（DIVERGENT/DRIFTED/CONTESTED）需上下文。',
        f'{B("5 个完整数据结构")}：ProjectAtom / AtomCluster / DeprecationEvent / HealthFinding / HealthCheckCacheKey，每个有 JSON Schema。',
        f'{B("deprecation_events.jsonl")}：独立废弃事件数据库，三级来源（official > graph > community），append-only。',
        f'{B("复杂度优化")}：type 分桶→subject 分桶→ANN 候选，O(N×M) 降到 O(N×k)。',
        f'{B("完整伪代码")}：run_health_check() 约 130 行，覆盖全部 7 类信号检测。',
        f'{B("gold set 测试设计")}：4 个 SEO 项目预期分布 + 4 个具体测试用例 + 衡量指标。',
    ]
    for item in codex_items:
        story.append(Paragraph(f'• {item}', bullet_style))

    story.append(PageBreak())

    # ===== Section 3: Disagreements =====
    story.append(Paragraph('三、分歧与决策建议', h1_style))
    story.append(hr())

    disagreements = [
        ('分歧 1：匹配方法',
         'Claude：slot matching，不用 embedding（因为 scope 问题）\nCodex：hybrid — semantic retrieval 召回 + slot matching 裁决',
         '采 Codex 方案。Claude 直觉对（纯 embedding 混淆 scope），但实现需 embedding 做召回。两阶段分工解决矛盾。'),
        ('分歧 2：Gemini 的"重构方案生成"',
         'Gemini：付费层提供"一键式 Pull Request 补丁"\nClaude：V1 不连接 StitchCraft。推荐=开处方，违反产品哲学。',
         '不做自动推荐。用户主动请求"帮我补缺失"是另一个显式请求，由 StitchCraft 处理。体检只出 X 光片。'),
        ('分歧 3：Gemini 的"健康徽章"',
         'Gemini：高分项目获官方认证，提升社区信用度\nClaude：不定义"健康"，不给总分',
         'V1 不做徽章。若做，必须是多维展示（"共识覆盖 78% / 独创密度 16%"），绝不是单一分数。V2+ 探索"项目简历"形式。'),
        ('分歧 4：V1 是否需要可视化',
         'Gemini：Knowledge Galaxy、分屏对比、Feed 流\nClaude + Codex：V1 输出 JSON + Markdown',
         'V1 只做文件输出。但 Gemini 的渐进式披露思路反映在 Markdown 结构中。情感设计用词直接采纳到渲染 prompt。'),
        ('分歧 5：Gemini 的"作者辩论"功能',
         'Gemini：让作者输入理由，AI 调整解读\nClaude + Codex：未提及',
         'V2+ 探索。好概念，但 V1 优先级是匹配引擎稳定性。'),
    ]

    for title, positions, decision in disagreements:
        story.append(Paragraph(title, h2_style))
        for line in positions.split('\n'):
            story.append(Paragraph(f'• {line}', bullet_style))
        story.append(Paragraph(f'{B("决策建议")}：{decision}', body_bold))
        story.append(Spacer(1, 2*mm))

    story.append(PageBreak())

    # ===== Section 4: Adoption List =====
    story.append(Paragraph('四、直接采纳清单', h1_style))
    story.append(hr())

    adopt_data = [
        ['Claude', 'GIS 叠加分析定位', '理论框架直接影响设计决策'],
        ['Claude', '7 类信号 + 6 维度 + 不给总分', '产品哲学一致'],
        ['Claude', 'STALE 独立运行 = 最小可用子集', 'V0 就能上线'],
        ['Claude', '案例演示格式', '直接作为 MD 模板'],
        ['Gemini', '情感设计用词', '渲染 prompt 必须包含'],
        ['Gemini', '渐进式披露层次', 'Markdown 结构遵循'],
        ['Gemini', '竞品差异化表', '产品定位参考'],
        ['Codex', '三段式匹配算法', '工程核心'],
        ['Codex', '加权匹配公式 + 四段阈值', '可直接编码'],
        ['Codex', 'MISSING 双阈值 + ORIGINAL 二次检验', '降低假阳性'],
        ['Codex', '确定性/解释性双路分离', '工程可维护性'],
        ['Codex', 'deprecation_events.jsonl', 'STALE 引擎基础设施'],
        ['Codex', '缓存 5 维键 + SQLite 索引', '可追溯性保证'],
        ['Codex', '完整伪代码', '编码起点'],
        ['Codex', 'gold set 测试设计', '验证标准'],
    ]

    adopt_table = make_table(
        ['来源', '采纳内容', '原因'],
        adopt_data,
        col_widths=[25*mm, 75*mm, 60*mm]
    )
    story.append(adopt_table)

    story.append(Spacer(1, 8*mm))

    # ===== Section 5: Implementation =====
    story.append(Paragraph('五、实施路径', h1_style))
    story.append(hr())

    impl_data = [
        ['V0', '1 天', 'STALE 检测器：deprecation_events.jsonl + stale_engine()', '只需 Soul Extractor 输出'],
        ['V0.5', '1 天', 'scope ontology 固定（engine/persona/environment/time）', '跨项目对比经验'],
        ['V1-a', '2 天', '候选召回 + 结构化裁决：ALIGNED/MISSING/ORIGINAL', '领域图谱 Alpha'],
        ['V1-b', '1 天', 'health_check.json + HEALTH_CHECK.md 渲染', 'V1-a'],
        ['V1-c', '1 天', '4 个 SEO 项目 gold set 验证', 'V1-b'],
        ['V1.1', '2 天', 'DIVERGENT + DRIFTED + CONTESTED（解释性路线）', 'StitchCraft 冲突分类'],
        ['V2', 'TBD', '知识星系可视化 + 作者辩论 + 多图谱 blended', 'Web 界面'],
    ]

    impl_table = make_table(
        ['阶段', '时间', '内容', '关键依赖'],
        impl_data,
        col_widths=[18*mm, 18*mm, 80*mm, 44*mm]
    )
    story.append(impl_table)

    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(f'{B("总 V1 工时")}：约 6 天（在图谱 Alpha 就绪后）', body_bold))

    story.append(Spacer(1, 10*mm))

    # ===== Section 6: Summary =====
    story.append(Paragraph('六、一句话总结', h1_style))
    story.append(hr())
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        '知识健康检查 = 领域图谱的镜子功能。<br/><br/>'
        '代码做匹配（Codex 的三段式算法），<br/>'
        '结构做分类（Claude 的 7 类信号），<br/>'
        '措辞做尊重（Gemini 的情感设计）。<br/><br/>'
        '三方各守一层，缺一不可。',
        ParagraphStyle('FinalQuote', parent=quote_style, alignment=TA_CENTER, fontSize=11, leading=17)
    ))

    doc.build(story)
    print(f'PDF generated: {OUTPUT}')
    print(f'Size: {os.path.getsize(OUTPUT) / 1024:.0f} KB')

if __name__ == '__main__':
    build()
