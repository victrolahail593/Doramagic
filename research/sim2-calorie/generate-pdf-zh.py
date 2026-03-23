#!/usr/bin/env python3
"""Generate Chinese PDF for Sim2 Calorie Skill delivery."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('STHeitiLight', '/System/Library/Fonts/STHeiti Light.ttc', subfontIndex=0))

BASE = os.path.dirname(__file__)
OUTPUT = os.path.join(BASE, 'calorie-skill-sim2-zh.pdf')

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
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm,
        title='Doramagic Sim2: Calorie Tracker Skill', author='Doramagic')
    s = []

    # ===== 封面 =====
    s.append(Spacer(1, 30*mm))
    s.append(Paragraph('Doramagic', ParagraphStyle('Big', parent=title_s, fontSize=32, leading=40)))
    s.append(Spacer(1, 3*mm))
    s.append(Paragraph('食物卡路里追踪 Skill', title_s))
    s.append(Paragraph('多项目管线第二轮模拟', sub_s))
    s.append(Spacer(1, 8*mm))
    s.append(Paragraph('2026-03-17', sub_s))
    s.append(Spacer(1, 5*mm))
    s.append(Paragraph(
        '3 个开源项目 + 4 个社区 Skill + 1 个教程<br/>'
        '= 9 条共识 + 4 个冲突解决 + 11 条独创知识<br/>'
        '= 1 个可运行的 SKILL.md（433 行）',
        ParagraphStyle('Tag', parent=quote_s, alignment=TA_CENTER, fontSize=10, leading=15)
    ))
    s.append(Spacer(1, 10*mm))
    s.append(Paragraph('Phase A-H 管线：全程完成', ParagraphStyle('P1', parent=bold_s, alignment=TA_CENTER, fontSize=14, textColor=GREEN)))
    s.append(Paragraph('质量门控：7/7 通过', ParagraphStyle('P2', parent=bold_s, alignment=TA_CENTER, fontSize=12, textColor=GREEN)))

    s.append(PageBreak())

    # ===== 管线总览 =====
    s.append(Paragraph('一、管线执行总览', h1_s))
    s.append(hr())
    s.append(tbl(
        ['阶段', '任务', '状态', '产出'],
        [
            ['Phase A', '需求理解', '完成', 'need_profile.json'],
            ['Phase B', '作业发现', '完成', '3 个仓库 + 4 个社区 skill + 1 个教程'],
            ['Phase C', '并行灵魂提取（x3）', '完成', '3 份结构化提取报告（含卡片+证据）'],
            ['Phase D', '社区知识采集', '完成', '社区知识提取报告'],
            ['Phase E', '知识综合', '完成', '综合报告（9 共识 + 4 冲突 + 11 独创）'],
            ['Phase F', 'Skill 组装', '完成', 'SKILL.md（433 行）'],
            ['Phase G', '质量门控', '7/7 通过', '验证报告'],
            ['Phase H', '交付', '完成', '4 个文件：SKILL + 溯源 + 限制 + 综合'],
        ],
        [18*mm, 40*mm, 25*mm, 82*mm]
    ))

    # ===== 知识来源 =====
    s.append(Paragraph('二、知识来源', h1_s))
    s.append(hr())
    s.append(tbl(
        ['来源', '类型', '核心贡献'],
        [
            ['ai-calorie-counter', '开源项目', 'LLM 即解析器（JSON 契约）、BMR 计算、上下文动态注入'],
            ['FoodYou', '开源项目', '43 字段营养素 schema、Complete/Incomplete 空值语义、食谱拆解'],
            ['OpenNutriTracker', '开源项目', 'IOM 2005 TDEE 公式、MET 运动数据库、TrackedDay 快照、per-100g 标准'],
            ['calorie-counter', '社区 Skill', '蛋白质估算规则、基础追踪流程'],
            ['opencal', '社区 Skill', 'per-100g 缩放公式、双向交互模式'],
            ['diet-tracker', '社区 Skill', 'USER.md + memory/YYYY-MM-DD.md 架构'],
            ['health-summary', '社区 Skill', '日/周/月聚合模式'],
            ['LobsterLair', '社区教程', '照片识别流程、人格层（SOUL.md）、80-90% 准确率'],
        ],
        [35*mm, 20*mm, 110*mm]
    ))

    s.append(PageBreak())

    # ===== 知识综合 =====
    s.append(Paragraph('三、知识综合（Phase E）', h1_s))
    s.append(hr())

    s.append(Paragraph('9 条公约数（共识知识）', h2_s))
    s.append(tbl(
        ['编号', '共识内容', '支持来源'],
        [
            ['GCD-01', '宏量营养素换算：蛋白质=4、碳水=4、脂肪=9 kcal/g', '3/3 项目'],
            ['GCD-02', '每日目标 = BMR/TDEE + 运动消耗 - 热量赤字', '3/3 项目'],
            ['GCD-03', '食物营养数据按 per-100g 标准化存储', '3/3 + 社区'],
            ['GCD-04', '4 餐次分类：早餐/午餐/晚餐/零食', '3/3 项目'],
            ['GCD-05', '运动追踪使用 MET 值计算消耗', '3/3 项目'],
            ['GCD-06', '用户档案与追踪数据分离存储', '3/3 + 社区'],
            ['GCD-07', '每日总结必含：已摄入/目标/剩余', '3/3 + 社区'],
            ['GCD-08', 'YYYY-MM-DD 日期命名文件', '社区共识'],
            ['GCD-09', '用户必须能修正 AI 估算', '3/3 项目'],
        ],
        [18*mm, 95*mm, 52*mm]
    ))

    s.append(Paragraph('4 个冲突（全部解决）', h2_s))
    s.append(tbl(
        ['编号', '冲突内容', '解决方案'],
        [
            ['冲突 1', 'BMR 公式：MSJ vs IOM vs Schofield vs HB', '选 MSJ（最简洁、精度足够）'],
            ['冲突 2', '存储格式：JSON vs Markdown vs 数据库', 'JSON + Markdown 双轨（代码说事实，AI 说故事）'],
            ['冲突 3', '食物数据：API 查询 vs LLM 估算', 'LLM 优先，API 查询留到 V2'],
            ['冲突 4', '宏量比例：45/30/25 vs 60/15/25 vs 50/25/25', '默认 50/25/25，用户可自定义'],
        ],
        [18*mm, 72*mm, 75*mm]
    ))

    s.append(Paragraph('Top 5 独创知识', h2_s))
    s.append(tbl(
        ['来源', '独创知识'],
        [
            ['ai-calorie-counter', 'LLM 即解析器：AI 输出结构化 JSON，不是对话式回复'],
            ['ai-calorie-counter', '聚合数据注入上下文：传每日总量而非全部记录（省 token）'],
            ['FoodYou', 'Complete/Incomplete 空值语义（未知数据 != 零）'],
            ['OpenNutriTracker', 'TrackedDay 快照（修改设置不影响历史记录）'],
            ['社区', 'WHY 层空白：所有社区 skill 只做记录+报告，无趋势分析（差异化机会）'],
        ],
        [35*mm, 130*mm]
    ))

    s.append(PageBreak())

    # ===== Skill 设计 =====
    s.append(Paragraph('四、Skill 设计方案（Phase F）', h1_s))
    s.append(hr())

    s.append(Paragraph('6 个核心流程', h2_s))
    s.append(tbl(
        ['流程', '触发方式', '处理逻辑'],
        [
            ['1. 首次引导', '首次使用自动触发', '收集性别/年龄/身高/体重/活动/目标 -> MSJ BMR -> TDEE -> 每日目标'],
            ['2. 食物记录', '发照片/"我吃了一碗面"', 'AI -> JSON 估算 -> 写入每日日志，含 confidence 标注'],
            ['3. 运动记录', '"跑步 30 分钟"', 'MET 值查找 -> MET x 体重(kg) x 时长(h) -> 写入日志'],
            ['4. 余量查询', '"还能吃多少"', 'TDEE - 已摄入 + 运动消耗 = 剩余'],
            ['5. 每日总结', '晚 9 点自动 / 用户主动', '聚合当日数据 -> 与目标对比 -> 生成报告'],
            ['6. 定时提醒', '12:30/18:00/21:00', '午餐提醒/晚餐提醒/每日总结'],
        ],
        [22*mm, 42*mm, 101*mm]
    ))

    s.append(Paragraph('数据架构', h2_s))
    s.append(Paragraph(
        '~/clawd/memory/health/<br/>'
        '  profile.json ---- 用户档案（BMR/TDEE/目标）<br/>'
        '  daily/YYYY-MM-DD.json ---- 结构化每日日志（JSON）<br/>'
        '  daily/YYYY-MM-DD.md ---- 可读的每日报告（Markdown）<br/>'
        '  weekly/YYYY-WNN.md ---- 周报',
        code_s
    ))

    s.append(Paragraph('AI Prompt 契约', h2_s))
    s.append(Paragraph(
        '食物记录：{type:"food", time, meal, name, weight_g, calories, protein_g, carbs_g, fat_g, confidence}<br/>'
        '运动记录：{type:"exercise", time, name, duration_min, met, calories_burned, confidence}<br/>'
        '上下文注入：每日聚合总量（非原始记录）以减少 token 消耗',
        code_s
    ))

    s.append(Paragraph('7 个暗坑警告（内置于 SKILL.md）', h2_s))
    pitfalls = [
        ['1', 'AI 估算误差 15-30%', '每条记录标注 confidence 等级，用户可修正'],
        ['2', '份量不确定性', '"一碗面"可能 150-300g，鼓励使用厨房秤'],
        ['3', 'BMR 公式个体差异', '所有公式是统计平均，实际偏差 5-15%'],
        ['4', 'MET 值是群体均值', '个体差异 20-30%，仅供参考'],
        ['5', '并发写入风险', '多设备同时记录可能冲突'],
        ['6', '照片识别准确率', '复合菜品（麻辣烫等）误差更大，标注"仅供参考"'],
        ['7', '中式饮食高碳水', '默认营养估算可能低估中餐碳水含量'],
    ]
    s.append(tbl(['#', '暗坑', '防护措施'], pitfalls, [8*mm, 55*mm, 102*mm]))

    s.append(PageBreak())

    # ===== 质量门控 =====
    s.append(Paragraph('五、质量门控（Phase G）', h1_s))
    s.append(hr())
    gates = [
        ['1. 一致性', '通过', '内部知识无矛盾'],
        ['2. 完整性', '通过', '用户需求的 6 个功能全部覆盖'],
        ['3. 可追溯性', '通过', '96% 的知识可追溯到 file:line（27/28 条）'],
        ['4. 平台适配', '通过', '符合 OpenClaw SKILL.md 格式规范'],
        ['5. 冲突解决', '通过', '4/4 个冲突已解决并标注理由'],
        ['6. 许可证', '通过（警告）', '来源项目 MIT + GPLv3；知识提取 != 代码复制'],
        ['7. 暗雷扫描', '通过（警告）', 'AI 估算精度 15-30% 已在 LIMITATIONS.md 中披露'],
    ]
    s.append(tbl(['检查项', '结果', '详情'], gates, [28*mm, 25*mm, 112*mm]))

    # ===== 交付包 =====
    s.append(Paragraph('六、交付包（Phase H）', h1_s))
    s.append(hr())
    s.append(tbl(
        ['文件', '规模', '内容'],
        [
            ['SKILL.md', '433 行', '可运行的 OpenClaw Skill：6 个流程 + 定时提醒 + 7 个暗坑警告'],
            ['PROVENANCE.md', '27 条', '知识溯源表，96% 可追溯到源码 file:line'],
            ['LIMITATIONS.md', '15 项', '精度限制、公式局限、平台约束'],
            ['synthesis_report.md', '376 行', '知识综合：9 共识 + 4 冲突解决 + 11 独创 + 验证报告'],
        ],
        [35*mm, 20*mm, 110*mm]
    ))

    s.append(PageBreak())

    # ===== 对照 =====
    s.append(Paragraph('七、两轮模拟对比', h1_s))
    s.append(hr())
    s.append(tbl(
        ['维度', '第一轮（Sim1）', '第二轮（Sim2）'],
        [
            ['Stage 0 确定性提取', '跳过', '3 个项目全部完成'],
            ['结构化卡片', '自由格式报告', 'CC/WF/DR 卡片 + file:line 证据'],
            ['证据绑定', '仅有文件名', '96% 追溯到 file:line'],
            ['社区 Skill', '随意搜索', '系统化轻量提取'],
            ['知识综合', '手动总结', '9 公约数 + 4 冲突解决 + 11 独创'],
            ['质量门控', '无', '7/7 通过'],
            ['产出物', '设计文档', '可运行 SKILL.md + 3 个配套文件'],
            ['管线合规', '即兴发挥', 'Phase A-H 全程遵循'],
        ],
        [30*mm, 67*mm, 68*mm]
    ))

    s.append(Spacer(1, 8*mm))

    # ===== 结论 =====
    s.append(Paragraph('八、结论', h1_s))
    s.append(hr())
    s.append(Paragraph(
        '第二轮模拟证明了多项目管线的可行性。<br/><br/>'
        '从用户说"我想做一个记录食物卡路里的 skill"<br/>'
        '到交付一个 433 行的可运行 SKILL.md + 完整溯源 + 质量门控<br/>'
        '全程严格遵循 Phase A-H 管线。<br/><br/>'
        '这就是 Doramagic 的价值：<br/>'
        '<b>站在 8 个前人的肩膀上，把知识缝合成你的道具。</b>',
        ParagraphStyle('Final', parent=quote_s, alignment=TA_CENTER, fontSize=10, leading=16)
    ))

    doc.build(s)
    print(f'PDF: {OUTPUT} ({os.path.getsize(OUTPUT)//1024} KB)')

if __name__ == '__main__':
    build()
