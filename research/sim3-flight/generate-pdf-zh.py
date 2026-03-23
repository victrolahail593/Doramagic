#!/usr/bin/env python3
"""Generate Chinese PDF for Sim3 Flight Skill delivery."""

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

OUTPUT = os.path.join(os.path.dirname(__file__), 'flight-skill-sim3-zh.pdf')

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

    # 封面
    s.append(Spacer(1, 30*mm))
    s.append(Paragraph('Doramagic', ParagraphStyle('Big', parent=title_s, fontSize=32, leading=40)))
    s.append(Spacer(1, 3*mm))
    s.append(Paragraph('机票搜索与最优飞行路线 Skill', title_s))
    s.append(Paragraph('多项目管线第三轮模拟', sub_s))
    s.append(Spacer(1, 8*mm))
    s.append(Paragraph('2026-03-17', sub_s))
    s.append(Spacer(1, 5*mm))
    s.append(Paragraph(
        '3 个开源项目 + 8 个社区 Skill<br/>'
        '= 5 条共识 + 3 个冲突解决 + 4 组独创知识<br/>'
        '核心差异化：多城市最优路线组合（社区空白）',
        ParagraphStyle('Tag', parent=quote_s, alignment=TA_CENTER, fontSize=10, leading=15)
    ))
    s.append(Spacer(1, 10*mm))
    s.append(Paragraph('Phase A-H 管线：全程完成', ParagraphStyle('P1', parent=bold_s, alignment=TA_CENTER, fontSize=14, textColor=GREEN)))
    s.append(Paragraph('质量门控：6 PASS + 1 PASS(附注)', ParagraphStyle('P2', parent=bold_s, alignment=TA_CENTER, fontSize=12, textColor=GREEN)))

    s.append(PageBreak())

    # 管线总览
    s.append(Paragraph('一、管线执行总览', h1_s))
    s.append(hr())
    s.append(tbl(
        ['阶段', '任务', '状态', '产出'],
        [
            ['Phase A', '需求理解', '完成', 'need_profile.json'],
            ['Phase B', '作业发现', '完成', '3 个仓库 + 8 个社区 skill'],
            ['Phase C', '并行灵魂提取(x3)', '完成', '3 份结构化提取报告'],
            ['Phase D', '社区知识采集', '完成', '8 个 skill 轻量提取 + API 选型'],
            ['Phase E', '知识综合', '完成', '5 共识 + 3 冲突 + 4 独创'],
            ['Phase F', 'Skill 组装', '完成', 'SKILL.md'],
            ['Phase G', '质量门控', '6+1 通过', '验证报告'],
            ['Phase H', '交付', '完成', '4 个文件'],
        ],
        [18*mm, 38*mm, 25*mm, 84*mm]
    ))

    # 知识来源
    s.append(Paragraph('二、知识来源', h1_s))
    s.append(hr())

    s.append(Paragraph('开源项目（Phase C 深度提取）', h2_s))
    s.append(tbl(
        ['项目', '核心贡献'],
        [
            ['fast-flights (AWeirdDev)', 'Google Flights Protobuf 逆向爬虫，零 API Key 航班搜索'],
            ['Travel Smart Planner', '多城市路线优化算法（Dijkstra + 优先队列），多目标权重公式'],
            ['gpt-search-flights', 'OpenAI function calling 航班搜索范式，LLM 是翻译器不是搜索引擎'],
        ],
        [40*mm, 125*mm]
    ))

    s.append(Paragraph('社区 Skill（Phase D 轻量提取）', h2_s))
    s.append(tbl(
        ['Skill', '核心贡献'],
        [
            ['FlightClaw (jackculpan)', 'Google Flights 价格追踪 + 告警 + 持久化设计'],
            ['skill-google-flights', 'fast-flights + Playwright 双轨，参数最完整'],
            ['flights-skill', 'Protobuf 逆向，最轻量'],
            ['flight-pricer', 'Duffel API 集成，CLI 子命令架构'],
            ['Aerobase', '唯一有时差评分（0-100）的差异化 Skill'],
            ['travel-manager', 'LLM-only，文档驱动旅行管理'],
            ['openclaw-travel-planner', '中文用户家庭旅行，含儿童年龄+三档预算'],
            ['TripGenie (Trip.com)', '封闭系统，参考价值有限'],
        ],
        [42*mm, 123*mm]
    ))

    s.append(PageBreak())

    # 知识综合
    s.append(Paragraph('三、知识综合（Phase E）', h1_s))
    s.append(hr())

    s.append(Paragraph('5 条公约数', h2_s))
    s.append(tbl(
        ['编号', '共识内容'],
        [
            ['GCD-01', 'IATA 代码是航班数据的统一语言（所有项目和 API 都用 3 字母代码）'],
            ['GCD-02', '最小完备参数集：出发地/目的地/日期/乘客数/舱位（缺一不可）'],
            ['GCD-03', 'LLM 是翻译器不是搜索引擎——自然语言→结构化参数→真实 API→结构化数据→自然语言'],
            ['GCD-04', '不替用户订票——只展示信息和链接，预订在航司/OTA 完成'],
            ['GCD-05', 'JSON 结构化输出优先（确定性处理 > 自然语言解析）'],
        ],
        [18*mm, 147*mm]
    ))

    s.append(Paragraph('3 个冲突（全部解决）', h2_s))
    s.append(tbl(
        ['冲突', '各方立场', '解决方案'],
        [
            ['数据源选择', 'fast-flights: 逆向爬虫零成本\nAmadeus: 商业 API 稳定\n社区: 多种方案', '双轨：Amadeus（主）+ fast-flights（备），自动降级'],
            ['多城市算法', 'Travel Planner: Dijkstra\ngpt-flights: 无此能力\n社区: 全部空白', '分层：<=8 城市精确解（穷举+Pareto）\n>8 城市近似解（贪心+2-opt）'],
            ['货币处理', 'fast-flights: 无货币字段\nAmadeus: 多币种\n社区: 各异', '固定 CNY 默认，API 返回非 CNY 时标注原始币种'],
        ],
        [22*mm, 60*mm, 83*mm]
    ))

    s.append(Paragraph('4 组独创知识', h2_s))
    s.append(tbl(
        ['来源', '独创知识'],
        [
            ['fast-flights', 'Protobuf 逆向链路：URL tfs 参数 = Base64(序列化 Info 消息)，Chrome TLS 指纹伪装'],
            ['Travel Planner', '多目标权重公式：score = w1*price + w2*duration + w3*stops，Dijkstra+优先队列骨架可复用'],
            ['gpt-search-flights', 'Function calling 两轮对话闭环 + 数据裁剪（只传前 N 条结果给 LLM）'],
            ['社区', '六大空白：多城市组合/中转成本/帕累托排序/日期弹性/价格预测/行李规则——全部未实现'],
        ],
        [30*mm, 135*mm]
    ))

    s.append(PageBreak())

    # Skill 设计
    s.append(Paragraph('四、Skill 设计方案（Phase F）', h1_s))
    s.append(hr())

    s.append(Paragraph('3 个核心流程', h2_s))
    s.append(tbl(
        ['流程', '触发方式', '处理逻辑'],
        [
            ['1. 单程/往返搜索', '"北京飞东京下周五"\n"3月25去巴厘岛往返5天"',
             '自然语言→参数提取→Amadeus/fast-flights 查询→帕累托排序→展示结果+预订链接'],
            ['2. 多城市最优路线\n（核心差异化）', '"我要去东京、首尔、曼谷，\n预算8000"',
             '参数提取→搜索矩阵（N*(N-1) 城市对）→穷举/贪心排列→帕累托过滤→展示 Top 3 方案'],
            ['3. 价格追踪', '"帮我盯着北京飞大阪\n低于2000告诉我"',
             '保存追踪条件→定时查询→价格下降时推送通知'],
        ],
        [28*mm, 42*mm, 95*mm]
    ))

    s.append(Paragraph('数据源双轨设计', h2_s))
    s.append(Paragraph(
        '主数据源：Amadeus Self-Service API（GDS 直连，数据最权威，有免费额度）<br/>'
        '备用数据源：fast-flights（Google Flights Protobuf 逆向，零成本但不稳定）<br/>'
        '策略：Amadeus 优先 -> 失败/超时 -> 自动降级到 fast-flights -> 标注数据源',
        code_s
    ))

    s.append(Paragraph('多城市路线优化算法', h2_s))
    s.append(Paragraph(
        '城市数 &lt;= 8：精确解<br/>'
        '  1. 搜索矩阵：查询所有城市对的最优航班（N*(N-1) 组合）<br/>'
        '  2. 全排列枚举：生成所有可能的行程顺序<br/>'
        '  3. 帕累托过滤：总价/总时长/总中转 三维不支配筛选<br/>'
        '  4. 展示 Top 3 方案<br/><br/>'
        '城市数 &gt; 8：近似解<br/>'
        '  1. 贪心最近邻：从出发地开始，每次选最便宜的下一站<br/>'
        '  2. 2-opt 局部优化：交换路线中的两段看能否更优<br/>'
        '  3. 标注"近似最优，非全局最优"',
        code_s
    ))

    s.append(Paragraph('帕累托排序（默认排序方式）', h2_s))
    s.append(Paragraph(
        '三个维度：价格(CNY) / 总时长(分钟) / 中转次数<br/>'
        '方案 A 支配方案 B = A 在所有维度都不差于 B，且至少一个维度更优<br/>'
        '帕累托前沿 = 所有不被支配的方案集合<br/>'
        '用户可切换单维排序：/sort price | /sort duration | /sort stops',
        code_s
    ))

    s.append(PageBreak())

    # 质量门控
    s.append(Paragraph('五、质量门控（Phase G）', h1_s))
    s.append(hr())
    s.append(tbl(
        ['检查项', '结果', '详情'],
        [
            ['1. 一致性', '通过', '内部知识无矛盾'],
            ['2. 完整性', '通过', '单程/往返/多城市/价格追踪全覆盖'],
            ['3. 可追溯性', '通过', '100% 知识可追溯到来源'],
            ['4. 平台适配', '通过', '符合 OpenClaw SKILL.md 格式'],
            ['5. 冲突解决', '通过', '3/3 冲突已解决并标注理由'],
            ['6. 许可证', '通过', '无直接代码复用，知识提取无许可证风险'],
            ['7. 暗雷扫描', '通过（附注）', '6 个暗坑已标注；消息推送需平台层支持'],
        ],
        [28*mm, 25*mm, 112*mm]
    ))

    # 暗坑
    s.append(Paragraph('6 个暗坑警告', h2_s))
    s.append(tbl(
        ['#', '暗坑', '防护'],
        [
            ['1', 'fast-flights 依赖 Google 页面结构，随时可能失效', 'Amadeus 为主，fast-flights 仅备用'],
            ['2', '价格无货币标注（fast-flights）', '统一转 CNY，非 CNY 标注原始币种'],
            ['3', '多城市穷举在城市多时指数爆炸', '<=8 精确解，>8 近似解，硬上限 15 城市'],
            ['4', '中文城市名→IATA 解析不完美', '内置常见城市字典 + API 兜底'],
            ['5', 'Amadeus 免费额度有限（5000 次/月）', '缓存策略 + 同航线 30 分钟缓存'],
            ['6', '航班价格实时波动', '结果标注查询时间，提醒"价格仅供参考"'],
        ],
        [8*mm, 65*mm, 92*mm]
    ))

    # 交付包
    s.append(Paragraph('六、交付包（Phase H）', h1_s))
    s.append(hr())
    s.append(tbl(
        ['文件', '内容'],
        [
            ['SKILL.md', '可运行的 OpenClaw Skill：3 个流程 + 双轨数据源 + 帕累托排序 + 多城市优化'],
            ['PROVENANCE.md', '知识溯源表，100% 可追溯'],
            ['LIMITATIONS.md', '已知限制 + 暗坑 + 质量门控详情'],
            ['synthesis_report.md', '知识综合：5 共识 + 3 冲突解决 + 4 独创 + 验证报告'],
        ],
        [35*mm, 130*mm]
    ))

    s.append(PageBreak())

    # 三轮模拟对比
    s.append(Paragraph('七、三轮模拟对比', h1_s))
    s.append(hr())
    s.append(tbl(
        ['维度', 'Sim1（卡路里v1）', 'Sim2（卡路里v2）', 'Sim3（机票）'],
        [
            ['管线遵循', '即兴', 'Phase A-H', 'Phase A-H'],
            ['Stage 0', '跳过', '完成', '完成'],
            ['证据绑定', '文件名', '96% file:line', '100% file:line'],
            ['质量门控', '无', '7/7 PASS', '6+1 PASS'],
            ['产出', '设计文档', 'SKILL.md + 3文件', 'SKILL.md + 3文件'],
            ['社区 skill', '4 个', '4 个', '8 个'],
            ['差异化', '—', '趋势分析空白', '多城市路线空白'],
            ['领域', '健康/饮食', '健康/饮食', '旅行/航班'],
        ],
        [20*mm, 40*mm, 45*mm, 60*mm]
    ))

    s.append(Spacer(1, 8*mm))
    s.append(Paragraph(
        '三轮模拟验证了 Doramagic 多项目管线的<b>跨领域适应性</b>。<br/><br/>'
        '从健康饮食到航班旅行，同一条管线（Phase A-H）<br/>'
        '在完全不同的领域中产出了同等质量的可运行 Skill。<br/><br/>'
        '<b>管线是通用的，知识是领域特定的。</b><br/>'
        '这正是 Doramagic 的设计目标。',
        ParagraphStyle('Final', parent=quote_s, alignment=TA_CENTER, fontSize=10, leading=16)
    ))

    doc.build(s)
    print(f'PDF: {OUTPUT} ({os.path.getsize(OUTPUT)//1024} KB)')

if __name__ == '__main__':
    build()
