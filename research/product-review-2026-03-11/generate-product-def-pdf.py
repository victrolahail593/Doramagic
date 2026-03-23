#!/usr/bin/env python3
"""
Generate PDF from Doramagic v2 Product Definition document.
Parses doramagic-v2-product-definition.md and produces a professionally
formatted PDF with cover page, proper markdown rendering, and consistent
styling with the Q&A PDF.
"""

import re
import os
from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(SCRIPT_DIR, "doramagic-v2-product-definition.md")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "doramagic-v2-product-definition.pdf")
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"

# --- Colors (consistent with Q&A PDF) ---
COLOR_TITLE = (30, 30, 30)
COLOR_SUBTITLE = (80, 80, 80)
COLOR_H2 = (0, 90, 160)
COLOR_H3 = (40, 75, 120)
COLOR_SECTION_LABEL = (180, 60, 30)
COLOR_BODY = (40, 40, 40)
COLOR_ACCENT_LINE = (0, 90, 160)
COLOR_LIGHT_BG = (245, 248, 252)
COLOR_TABLE_HEADER_BG = (0, 90, 160)
COLOR_TABLE_HEADER_FG = (255, 255, 255)
COLOR_TABLE_ROW_ALT = (240, 245, 250)
COLOR_DIVIDER = (200, 200, 200)
COLOR_CODE_BG = (245, 245, 240)
COLOR_CODE_BORDER = (220, 220, 210)
COLOR_BLOCKQUOTE = (90, 90, 90)
COLOR_BLOCKQUOTE_BAR = (0, 90, 160)


def extract_bold_segments(text):
    """
    Parse text into segments: list of (is_bold, content) tuples.
    This allows rendering bold inline within paragraphs.
    """
    segments = []
    pattern = r'\*\*(.+?)\*\*'
    last_end = 0
    for m in re.finditer(pattern, text):
        if m.start() > last_end:
            segments.append((False, text[last_end:m.start()]))
        segments.append((True, m.group(1)))
        last_end = m.end()
    if last_end < len(text):
        segments.append((False, text[last_end:]))
    return segments


def clean_text(text):
    """Remove markdown formatting artifacts for plain text output."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'```\w*\n?', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_document(filepath):
    """
    Parse the product definition markdown into structured sections.
    Returns a list of sections, each with title, level, and content blocks.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_section = None
    current_content_lines = []
    skip_h1 = True  # Skip the H1 title (used on cover page)

    for line in lines:
        stripped = line.rstrip('\n')

        # Detect H2 (## )
        h2_match = re.match(r'^## (.+)', stripped)
        if h2_match:
            # Save previous section
            if current_section is not None:
                current_section['content'] = '\n'.join(current_content_lines)
                sections.append(current_section)
            current_section = {
                'level': 2,
                'title': h2_match.group(1).strip(),
                'content': '',
            }
            current_content_lines = []
            continue

        # Detect H3 (### )
        h3_match = re.match(r'^### (.+)', stripped)
        if h3_match:
            if current_section is not None:
                current_section['content'] = '\n'.join(current_content_lines)
                sections.append(current_section)
            current_section = {
                'level': 3,
                'title': h3_match.group(1).strip(),
                'content': '',
            }
            current_content_lines = []
            continue

        # Detect H4 (#### )
        h4_match = re.match(r'^#### (.+)', stripped)
        if h4_match:
            if current_section is not None:
                current_section['content'] = '\n'.join(current_content_lines)
                sections.append(current_section)
            current_section = {
                'level': 4,
                'title': h4_match.group(1).strip(),
                'content': '',
            }
            current_content_lines = []
            continue

        # Skip H1
        if re.match(r'^# ', stripped) and skip_h1:
            skip_h1 = False
            continue

        # Skip standalone --- dividers
        if re.match(r'^---\s*$', stripped):
            continue

        # Accumulate content
        if current_section is not None:
            current_content_lines.append(stripped)

    # Save last section
    if current_section is not None:
        current_section['content'] = '\n'.join(current_content_lines)
        sections.append(current_section)

    return sections


class ProductDefPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("STHeiti", "", FONT_PATH)
        self.add_font("STHeiti", "B", FONT_PATH)
        self.set_auto_page_break(auto=True, margin=25)
        self._in_cover = True
        self.toc_entries = []

    def header(self):
        if self._in_cover:
            return
        self.set_font("STHeiti", "", 7)
        self.set_text_color(*COLOR_SUBTITLE)
        self.cell(0, 6, "Doramagic v2 产品定义书", align="C")
        self.ln(2)
        self.set_draw_color(*COLOR_DIVIDER)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def footer(self):
        if self._in_cover:
            return
        self.set_y(-20)
        self.set_draw_color(*COLOR_DIVIDER)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_font("STHeiti", "", 8)
        self.set_text_color(*COLOR_SUBTITLE)
        self.cell(0, 8, f"- {self.page_no()} -", align="C")

    # --- Cover page ---

    def add_cover_page(self):
        self._in_cover = True
        self.add_page()

        # Top accent bar
        self.set_fill_color(*COLOR_ACCENT_LINE)
        self.rect(0, 0, self.w, 6, "F")

        self.ln(55)

        # Main title
        self.set_font("STHeiti", "B", 28)
        self.set_text_color(*COLOR_TITLE)
        self.cell(0, 16, "Doramagic v2 产品定义", align="C")
        self.ln(20)

        # Decorative line
        line_w = 80
        x_center = (self.w - line_w) / 2
        self.set_draw_color(*COLOR_ACCENT_LINE)
        self.set_line_width(1.2)
        self.line(x_center, self.get_y(), x_center + line_w, self.get_y())
        self.ln(12)

        # Subtitle
        self.set_font("STHeiti", "B", 16)
        self.set_text_color(*COLOR_H2)
        self.cell(0, 12, "基于 22 轮第一性原理灵魂拷问", align="C")
        self.ln(20)

        # Date
        self.set_font("STHeiti", "", 12)
        self.set_text_color(*COLOR_SUBTITLE)
        self.cell(0, 8, "2026-03-11", align="C")
        self.ln(12)

        # Tagline
        self.set_font("STHeiti", "", 10)
        self.set_text_color(*COLOR_SUBTITLE)
        self.cell(0, 8, "综合 22 轮灵魂拷问全部洞察 | 终稿", align="C")
        self.ln(8)
        self.cell(0, 8, "输入: discussion-log.md + doramagic-v2-redesign.md + v2-tech-gap-analysis.md", align="C")
        self.ln(30)

        # Credits
        self.set_font("STHeiti", "", 9)
        self.set_text_color(140, 140, 140)
        self.cell(0, 7, "Tang  x  AI 产品专家 (Claude Opus)", align="C")

        # Bottom accent bar
        self.set_fill_color(*COLOR_ACCENT_LINE)
        self.rect(0, self.h - 6, self.w, 6, "F")

    # --- TOC page ---

    def add_toc_page(self, sections):
        self._in_cover = False
        self.add_page()

        self.set_font("STHeiti", "B", 18)
        self.set_text_color(*COLOR_H2)
        self.cell(0, 14, "目录", align="L")
        self.ln(8)

        self.set_draw_color(*COLOR_ACCENT_LINE)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.l_margin + 30, self.get_y())
        self.ln(10)

        for section in sections:
            if section['level'] > 3:
                continue

            if self.get_y() > self.h - 30:
                self.add_page()

            indent = 0 if section['level'] == 2 else 10

            self.set_x(self.l_margin + indent)
            if section['level'] == 2:
                self.set_font("STHeiti", "B", 10)
                self.set_text_color(*COLOR_H2)
            else:
                self.set_font("STHeiti", "", 9)
                self.set_text_color(*COLOR_BODY)

            title = section['title']
            self.cell(0, 7, title)
            self.ln(8 if section['level'] == 2 else 7)

    # --- Rich text rendering ---

    def _write_rich_line(self, text, font_size=10, line_height=6):
        """Write a single logical line with inline bold support."""
        segments = extract_bold_segments(text)
        for is_bold, seg in segments:
            seg = re.sub(r'\*(.+?)\*', r'\1', seg)
            seg = re.sub(r'`([^`]+)`', r'\1', seg)
            style = "B" if is_bold else ""
            self.set_font("STHeiti", style, font_size)
            self.write(line_height, seg)

    def _check_page_space(self, needed=20):
        """Check if there is enough space, add page if not."""
        if self.get_y() > self.h - self.b_margin - needed:
            self.add_page()

    def _render_table(self, table_text):
        """Render a markdown table."""
        lines = [l.strip() for l in table_text.strip().split('\n') if l.strip().startswith('|')]
        if len(lines) < 2:
            return

        rows = []
        for line in lines:
            cells = [c.strip() for c in line.strip('|').split('|')]
            rows.append(cells)

        # Skip separator line (contains ---)
        data_rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]
        if not data_rows:
            return

        num_cols = max(len(r) for r in data_rows)
        usable_width = self.w - self.l_margin - self.r_margin - 10

        # Calculate column widths based on content
        col_widths = self._calc_col_widths(data_rows, num_cols, usable_width)

        self._check_page_space(len(data_rows) * 8 + 5)

        for i, row in enumerate(data_rows):
            while len(row) < num_cols:
                row.append("")

            # Check page break for each row
            self._check_page_space(10)

            if i == 0:
                self.set_fill_color(*COLOR_TABLE_HEADER_BG)
                self.set_text_color(*COLOR_TABLE_HEADER_FG)
                self.set_font("STHeiti", "B", 8)
            else:
                if i % 2 == 0:
                    self.set_fill_color(*COLOR_TABLE_ROW_ALT)
                else:
                    self.set_fill_color(255, 255, 255)
                self.set_text_color(*COLOR_BODY)
                self.set_font("STHeiti", "", 8)

            x_start = self.l_margin + 5
            for j, cell in enumerate(row):
                self.set_x(x_start + sum(col_widths[:j]))
                cell_text = clean_text(cell)
                # Truncate if too long for cell
                max_chars = int(col_widths[j] / 2.2)
                if len(cell_text) > max_chars:
                    cell_text = cell_text[:max_chars - 1] + "..."
                self.cell(col_widths[j], 7, cell_text, border=0, fill=True)
            self.ln(7)

        self.set_text_color(*COLOR_BODY)

    def _calc_col_widths(self, data_rows, num_cols, usable_width):
        """Calculate proportional column widths based on content."""
        max_lens = [0] * num_cols
        for row in data_rows:
            for j, cell in enumerate(row):
                if j < num_cols:
                    max_lens[j] = max(max_lens[j], len(clean_text(cell)))

        # Ensure minimum width
        max_lens = [max(l, 3) for l in max_lens]
        total = sum(max_lens)
        if total == 0:
            return [usable_width / num_cols] * num_cols

        return [(l / total) * usable_width for l in max_lens]

    def _render_code_block(self, code_text):
        """Render a code block with background."""
        self._check_page_space(20)

        code_lines = code_text.split('\n')
        # Remove empty leading/trailing lines
        while code_lines and not code_lines[0].strip():
            code_lines.pop(0)
        while code_lines and not code_lines[-1].strip():
            code_lines.pop()

        line_h = 4.5
        padding = 4
        block_height = len(code_lines) * line_h + padding * 2
        content_width = self.w - self.l_margin - self.r_margin - 4

        # Check if block fits on page
        if self.get_y() + block_height > self.h - self.b_margin:
            self.add_page()

        y_start = self.get_y()

        # Draw background
        self.set_fill_color(*COLOR_CODE_BG)
        self.set_draw_color(*COLOR_CODE_BORDER)
        self.set_line_width(0.3)
        self.rect(self.l_margin + 2, y_start, content_width, block_height, "FD")

        # Draw code text
        self.set_font("STHeiti", "", 8)
        self.set_text_color(60, 60, 60)
        self.set_y(y_start + padding)

        for code_line in code_lines:
            self.set_x(self.l_margin + 6)
            self.cell(content_width - 8, line_h, code_line, new_x="LMARGIN", new_y="NEXT")

        self.set_y(y_start + block_height + 3)
        self.set_text_color(*COLOR_BODY)

    def _render_blockquote(self, quote_text):
        """Render a blockquote with left accent bar."""
        self._check_page_space(15)

        x_bar = self.l_margin + 4
        x_text = self.l_margin + 10
        content_width = self.w - x_text - self.r_margin - 2

        y_start = self.get_y()

        self.set_font("STHeiti", "", 9)
        self.set_text_color(*COLOR_BLOCKQUOTE)
        self.set_x(x_text)
        self.multi_cell(content_width, 5.5, clean_text(quote_text))

        y_end = self.get_y()

        # Draw accent bar
        self.set_draw_color(*COLOR_BLOCKQUOTE_BAR)
        self.set_line_width(1.0)
        self.line(x_bar, y_start, x_bar, y_end)

        self.ln(3)
        self.set_text_color(*COLOR_BODY)

    def render_content(self, content):
        """
        Render section content: handles paragraphs, bullet points,
        tables, code blocks, blockquotes, bold text.
        """
        if not content.strip():
            return

        # Split into blocks: code blocks, tables, and regular text
        blocks = self._split_content_blocks(content)

        for block_type, block_text in blocks:
            if block_type == 'code':
                self._render_code_block(block_text)
            elif block_type == 'table':
                self._render_table(block_text)
                self.ln(3)
            elif block_type == 'text':
                self._render_text_block(block_text)

    def _split_content_blocks(self, content):
        """
        Split content into typed blocks: code, table, or text.
        """
        blocks = []
        lines = content.split('\n')
        i = 0
        current_text = []

        while i < len(lines):
            line = lines[i]

            # Code block (``` ... ```)
            if line.strip().startswith('```'):
                if current_text:
                    blocks.append(('text', '\n'.join(current_text)))
                    current_text = []
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                blocks.append(('code', '\n'.join(code_lines)))
                i += 1  # skip closing ```
                continue

            # Table detection: lines starting with |
            if line.strip().startswith('|'):
                if current_text:
                    blocks.append(('text', '\n'.join(current_text)))
                    current_text = []
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                blocks.append(('table', '\n'.join(table_lines)))
                continue

            current_text.append(line)
            i += 1

        if current_text:
            blocks.append(('text', '\n'.join(current_text)))

        return blocks

    def _render_text_block(self, text):
        """Render a block of regular text with paragraphs, bullets, blockquotes."""
        paragraphs = re.split(r'\n\n+', text)

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Skip metadata lines (> 日期: etc at very top)
            if re.match(r'^>\s*(日期|状态|输入):', para):
                continue

            lines = para.split('\n')
            is_blockquote_block = all(
                l.strip().startswith('>') or not l.strip()
                for l in lines if l.strip()
            )

            if is_blockquote_block:
                quote_text = '\n'.join(
                    l.strip().lstrip('> ').strip() for l in lines if l.strip()
                )
                self._render_blockquote(quote_text)
                continue

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                self._check_page_space(10)

                # Blockquote line
                if line.startswith('>'):
                    quote = line.lstrip('> ').strip()
                    self._render_blockquote(quote)
                    continue

                # Bullet points
                bullet_match = re.match(r'^[-*]\s+(.+)', line)
                numbered_match = re.match(r'^(\d+)\.\s+(.+)', line)

                if bullet_match:
                    self.set_x(self.l_margin + 6)
                    self.set_font("STHeiti", "", 10)
                    self.set_text_color(*COLOR_BODY)
                    self.write(6, "  ")
                    self._write_rich_line(bullet_match.group(1), 10, 6)
                    self.ln(7)
                elif numbered_match:
                    self.set_x(self.l_margin + 6)
                    self.set_font("STHeiti", "", 10)
                    self.set_text_color(*COLOR_BODY)
                    num = numbered_match.group(1)
                    self.write(6, f"{num}. ")
                    self._write_rich_line(numbered_match.group(2), 10, 6)
                    self.ln(7)
                else:
                    # Regular text line
                    self.set_x(self.l_margin + 2)
                    self.set_text_color(*COLOR_BODY)
                    self._write_rich_line(line, 10, 6)
                    self.ln(7)

            self.ln(2)

    # --- Section rendering ---

    def add_h2_section(self, title):
        """Render an H2 section header."""
        self._check_page_space(30)

        y_start = self.get_y()

        # Colored left bar
        self.set_fill_color(*COLOR_ACCENT_LINE)
        self.rect(self.l_margin, y_start, 3, 12, "F")

        self.set_x(self.l_margin + 7)
        self.set_font("STHeiti", "B", 15)
        self.set_text_color(*COLOR_H2)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 7, 8, title)
        self.ln(4)

        # Thin accent line under title
        self.set_draw_color(*COLOR_ACCENT_LINE)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.l_margin + 50, self.get_y())
        self.ln(5)

    def add_h3_section(self, title):
        """Render an H3 sub-section header."""
        self._check_page_space(20)
        self.ln(2)

        self.set_x(self.l_margin + 2)
        self.set_font("STHeiti", "B", 12)
        self.set_text_color(*COLOR_H3)
        self.cell(0, 8, title)
        self.ln(9)

    def add_h4_section(self, title):
        """Render an H4 sub-sub-section header."""
        self._check_page_space(15)
        self.ln(1)

        self.set_x(self.l_margin + 4)
        self.set_font("STHeiti", "B", 10)
        self.set_text_color(*COLOR_SECTION_LABEL)
        self.cell(0, 7, title)
        self.ln(8)

    def render_section(self, section):
        """Render a complete section (header + content)."""
        level = section['level']
        title = section['title']

        if level == 2:
            self.add_h2_section(title)
        elif level == 3:
            self.add_h3_section(title)
        elif level == 4:
            self.add_h4_section(title)

        self.render_content(section['content'])


def main():
    print("Parsing doramagic-v2-product-definition.md ...")
    sections = parse_document(SOURCE_FILE)
    print(f"  Found {len(sections)} sections")

    for s in sections:
        prefix = "  " * (s['level'] - 2)
        print(f"  {prefix}[H{s['level']}] {s['title']}")

    pdf = ProductDefPDF()
    pdf.set_margins(20, 20, 20)

    # Cover page
    print("\nGenerating cover page ...")
    pdf.add_cover_page()

    # TOC page
    print("Generating table of contents ...")
    pdf.add_toc_page(sections)

    # Content pages
    pdf._in_cover = False
    print("Generating content ...")

    last_h2 = None
    for section in sections:
        if section['level'] == 2:
            # Start new page for each H2 section
            pdf.add_page()
            last_h2 = section['title']

        pdf.render_section(section)

    # Output
    print(f"\nSaving PDF to {OUTPUT_FILE} ...")
    pdf.output(OUTPUT_FILE)

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"\nPDF generated successfully!")
    print(f"  File: {OUTPUT_FILE}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"  Pages: {pdf.page_no()}")


if __name__ == "__main__":
    main()
