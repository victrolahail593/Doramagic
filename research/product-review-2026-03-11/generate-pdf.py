#!/usr/bin/env python3
"""
Generate PDF from Doramagic v2 product review discussion log.
Parses discussion-log.md and produces a professionally formatted PDF
with cover page, table of contents, and all 22 Q&A sections.
"""

import re
import os
from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(SCRIPT_DIR, "discussion-log.md")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "doramagic-v2-product-review-qa.pdf")
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"

# --- Colors ---
COLOR_TITLE = (30, 30, 30)
COLOR_SUBTITLE = (80, 80, 80)
COLOR_Q_HEADER = (0, 90, 160)
COLOR_SECTION_LABEL = (180, 60, 30)
COLOR_BODY = (40, 40, 40)
COLOR_ACCENT_LINE = (0, 90, 160)
COLOR_LIGHT_BG = (245, 248, 252)
COLOR_TABLE_HEADER_BG = (0, 90, 160)
COLOR_TABLE_HEADER_FG = (255, 255, 255)
COLOR_TABLE_ROW_ALT = (240, 245, 250)
COLOR_DIVIDER = (200, 200, 200)


def parse_markdown(filepath):
    """Parse the discussion-log.md into structured Q&A sections."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by ### Q markers
    sections = []
    # Find all Q sections
    pattern = r'### (Q\d+: .+?)\n(.*?)(?=\n### Q\d+:|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    for title, body in matches:
        section = {
            "title": title.strip(),
            "background": "",
            "question_note": "",
            "answer": "",
            "commentary": "",
        }

        # Extract background analysis
        bg_match = re.search(
            r'\*\*背景分析\*\*:\s*\n(.*?)(?=\n\*\*质问\*\*|\n\*\*Tang 的质问\*\*|\n\*\*Tang 的回答\*\*|\n\*\*专家回答\*\*)',
            body, re.DOTALL
        )
        if bg_match:
            section["background"] = bg_match.group(1).strip()

        # Extract Tang's question (if present as separate block)
        q_match = re.search(
            r'\*\*Tang 的质问\*\*:\s*(.*?)(?=\n\*\*专家回答\*\*|\n\*\*Tang 的回答\*\*)',
            body, re.DOTALL
        )
        if q_match:
            section["question_note"] = q_match.group(1).strip()

        # Extract Tang's answer
        a_match = re.search(
            r'\*\*Tang 的回答\*\*:\s*\n(.*?)(?=\n\*\*专家点评\*\*|\n\*\*专家分析|\n---|\Z)',
            body, re.DOTALL
        )
        if a_match:
            section["answer"] = a_match.group(1).strip()

        # Extract expert commentary (multiple possible headers)
        c_match = re.search(
            r'\*\*(专家点评|专家回答|专家分析[^*]*)\*\*:\s*?\n(.*?)(?=\n---|\Z)',
            body, re.DOTALL
        )
        if c_match:
            section["commentary"] = c_match.group(2).strip()

        sections.append(section)

    return sections


def clean_text(text):
    """Remove markdown formatting artifacts for plain text output."""
    # Remove bold markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic markers
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove link syntax, keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove code block markers
    text = re.sub(r'```\w*\n?', '', text)
    # Remove inline code backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Clean up excessive whitespace but preserve paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


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


class ProductReviewPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("STHeiti", "", FONT_PATH)
        self.add_font("STHeiti", "B", FONT_PATH)
        self.set_auto_page_break(auto=True, margin=25)

        # Track TOC entries: list of (title, page_number)
        self.toc_entries = []
        self._in_cover = True

    def header(self):
        if self._in_cover:
            return
        self.set_font("STHeiti", "", 7)
        self.set_text_color(*COLOR_SUBTITLE)
        self.cell(0, 6, "Doramagic v2 产品审查 — 第一性原理灵魂拷问", align="C")
        self.ln(2)
        # thin line under header
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

    # --- Drawing helpers ---

    def _write_rich_line(self, text, font_size=10, line_height=6):
        """Write a single logical line with inline bold support."""
        segments = extract_bold_segments(text)
        for is_bold, seg in segments:
            # Remove remaining markdown artifacts in segment
            seg = re.sub(r'\*(.+?)\*', r'\1', seg)
            seg = re.sub(r'`([^`]+)`', r'\1', seg)
            style = "B" if is_bold else ""
            self.set_font("STHeiti", style, font_size)
            self.write(line_height, seg)

    def write_body_text(self, text, indent=0):
        """Write body text with paragraph handling, bullet support, bold inline."""
        if not text.strip():
            return

        paragraphs = re.split(r'\n\n+', text)
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check for table (lines starting with |)
            table_lines = [l for l in para.split('\n') if l.strip().startswith('|')]
            if len(table_lines) >= 2:
                self._render_table(para)
                self.ln(3)
                continue

            lines = para.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect bullet points
                bullet_match = re.match(r'^[-*]\s+(.+)', line)
                numbered_match = re.match(r'^(\d+)\.\s+(.+)', line)

                if bullet_match:
                    x_start = self.l_margin + indent + 4
                    self.set_x(x_start)
                    self.set_font("STHeiti", "", 10)
                    self.set_text_color(*COLOR_BODY)
                    self.write(6, "  ")
                    self._write_rich_line(bullet_match.group(1), 10, 6)
                    self.ln(6)
                elif numbered_match:
                    x_start = self.l_margin + indent + 4
                    self.set_x(x_start)
                    self.set_font("STHeiti", "", 10)
                    self.set_text_color(*COLOR_BODY)
                    num = numbered_match.group(1)
                    self.write(6, f"{num}. ")
                    self._write_rich_line(numbered_match.group(2), 10, 6)
                    self.ln(6)
                elif line.startswith('>'):
                    # Blockquote
                    quote_text = line.lstrip('> ').strip()
                    self.set_x(self.l_margin + indent + 6)
                    self.set_draw_color(*COLOR_ACCENT_LINE)
                    self.set_line_width(0.8)
                    x_line = self.l_margin + indent + 4
                    y_start = self.get_y()
                    self.set_font("STHeiti", "", 9)
                    self.set_text_color(100, 100, 100)
                    self.multi_cell(self.w - self.l_margin - self.r_margin - indent - 10, 5.5, clean_text(quote_text))
                    y_end = self.get_y()
                    self.line(x_line, y_start, x_line, y_end)
                    self.ln(2)
                else:
                    self.set_x(self.l_margin + indent)
                    self.set_text_color(*COLOR_BODY)
                    self._write_rich_line(line, 10, 6)
                    self.ln(6)

            self.ln(2)

    def _render_table(self, table_text):
        """Render a simple markdown table."""
        lines = [l.strip() for l in table_text.strip().split('\n') if l.strip().startswith('|')]
        if len(lines) < 2:
            return

        # Parse rows
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
        col_width = usable_width / num_cols

        self.set_x(self.l_margin + 5)

        for i, row in enumerate(data_rows):
            # Pad row to num_cols
            while len(row) < num_cols:
                row.append("")

            if i == 0:
                # Header row
                self.set_fill_color(*COLOR_TABLE_HEADER_BG)
                self.set_text_color(*COLOR_TABLE_HEADER_FG)
                self.set_font("STHeiti", "B", 9)
            else:
                if i % 2 == 0:
                    self.set_fill_color(*COLOR_TABLE_ROW_ALT)
                else:
                    self.set_fill_color(255, 255, 255)
                self.set_text_color(*COLOR_BODY)
                self.set_font("STHeiti", "", 9)

            x_start = self.l_margin + 5
            for j, cell in enumerate(row):
                self.set_x(x_start + j * col_width)
                self.cell(col_width, 7, clean_text(cell), border=0, fill=True)
            self.ln(7)
            self.set_x(self.l_margin + 5)

    def add_cover_page(self):
        """Create the cover page."""
        self._in_cover = True
        self.add_page()

        # Top accent bar
        self.set_fill_color(*COLOR_ACCENT_LINE)
        self.rect(0, 0, self.w, 6, "F")

        # Title block - centered vertically
        self.ln(65)

        # Main title
        self.set_font("STHeiti", "B", 26)
        self.set_text_color(*COLOR_TITLE)
        self.cell(0, 16, "Doramagic v2 产品审查", align="C")
        self.ln(18)

        # Decorative line
        line_w = 80
        x_center = (self.w - line_w) / 2
        self.set_draw_color(*COLOR_ACCENT_LINE)
        self.set_line_width(1.2)
        self.line(x_center, self.get_y(), x_center + line_w, self.get_y())
        self.ln(10)

        # Subtitle
        self.set_font("STHeiti", "B", 18)
        self.set_text_color(*COLOR_Q_HEADER)
        self.cell(0, 12, "第一性原理灵魂拷问", align="C")
        self.ln(20)

        # Details
        self.set_font("STHeiti", "", 11)
        self.set_text_color(*COLOR_SUBTITLE)
        self.cell(0, 8, "22 轮 Q&A 完整记录", align="C")
        self.ln(10)
        self.cell(0, 8, "2026-03-11", align="C")
        self.ln(10)
        self.cell(0, 8, "Tang  x  AI 产品专家 (Claude Opus)", align="C")
        self.ln(30)

        # Bottom info block
        self.set_font("STHeiti", "", 9)
        self.set_text_color(140, 140, 140)
        self.cell(0, 7, "输入文档: PRODUCT_MANUAL.pdf (36 页, v1.0)", align="C")
        self.ln(8)
        self.cell(0, 7, "讨论形式: 第一性原理审查 + 苏格拉底式追问", align="C")

        # Bottom accent bar
        self.set_fill_color(*COLOR_ACCENT_LINE)
        self.rect(0, self.h - 6, self.w, 6, "F")

    def add_toc_page(self, sections):
        """Create table of contents."""
        self._in_cover = False
        self.add_page()

        self.set_font("STHeiti", "B", 18)
        self.set_text_color(*COLOR_Q_HEADER)
        self.cell(0, 14, "目录", align="L")
        self.ln(8)

        # Decorative line under title
        self.set_draw_color(*COLOR_ACCENT_LINE)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.l_margin + 30, self.get_y())
        self.ln(10)

        for i, section in enumerate(sections):
            title = section["title"]
            # Extract Q number and short title
            q_match = re.match(r'(Q\d+): (.+)', title)
            if q_match:
                q_num = q_match.group(1)
                q_title = q_match.group(2)
            else:
                q_num = f"Q{i+1}"
                q_title = title

            y_before = self.get_y()
            if y_before > self.h - 30:
                self.add_page()

            # Q number
            self.set_font("STHeiti", "B", 10)
            self.set_text_color(*COLOR_Q_HEADER)
            self.cell(16, 7, q_num, align="L")

            # Title
            self.set_font("STHeiti", "", 10)
            self.set_text_color(*COLOR_BODY)
            self.cell(0, 7, q_title)
            self.ln(9)

        self.ln(5)

    def add_qa_section(self, section, index):
        """Add a single Q&A section to the PDF."""
        # Start new page for each question
        self.add_page()

        title = section["title"]

        # Record TOC entry
        self.toc_entries.append((title, self.page_no()))

        # --- Question Header ---
        # Colored left bar + title
        y_start = self.get_y()
        self.set_fill_color(*COLOR_ACCENT_LINE)
        self.rect(self.l_margin, y_start, 3, 14, "F")

        self.set_x(self.l_margin + 7)
        self.set_font("STHeiti", "B", 14)
        self.set_text_color(*COLOR_Q_HEADER)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 7, 8, title)
        self.ln(6)

        # --- Background Analysis ---
        if section["background"]:
            self._section_label("背景分析")
            # Light background box
            y_box_start = self.get_y()
            self.set_fill_color(*COLOR_LIGHT_BG)

            # Calculate height needed (approximate)
            bg_text = clean_text(section["background"])
            # Draw the background box
            self.set_x(self.l_margin + 2)
            old_y = self.get_y()
            # Temporarily render to measure height
            self.set_font("STHeiti", "", 10)
            self.set_text_color(*COLOR_BODY)
            content_width = self.w - self.l_margin - self.r_margin - 8
            # Use multi_cell within a rect
            self.set_x(self.l_margin + 6)
            self.rect(self.l_margin + 2, old_y, content_width + 8, 1, "F")  # will extend

            self._write_in_box(section["background"], self.l_margin + 6, content_width)
            y_box_end = self.get_y() + 3
            # Draw full box background
            self.set_fill_color(*COLOR_LIGHT_BG)
            self.rect(self.l_margin + 2, old_y - 2, content_width + 8, y_box_end - old_y + 4, "F")
            # Re-render text on top
            self.set_y(old_y)
            self._write_in_box(section["background"], self.l_margin + 6, content_width)
            self.ln(6)

        # --- Tang's Answer ---
        if section["answer"]:
            self._section_label("Tang 的回答")
            self.write_body_text(section["answer"], indent=2)
            self.ln(2)

        # --- Expert Commentary ---
        if section["commentary"]:
            self._section_label("专家点评")
            self.write_body_text(section["commentary"], indent=2)
            self.ln(2)

    def _section_label(self, label):
        """Draw a section label like '背景分析', 'Tang 的回答', etc."""
        self.set_font("STHeiti", "B", 11)
        self.set_text_color(*COLOR_SECTION_LABEL)
        self.cell(0, 8, label)
        self.ln(8)

    def _write_in_box(self, text, x_start, width):
        """Write text inside a box area with proper formatting."""
        self.set_font("STHeiti", "", 10)
        self.set_text_color(*COLOR_BODY)

        paragraphs = re.split(r'\n\n+', text)
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            lines = para.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                bullet_match = re.match(r'^[-*]\s+(.+)', line)
                numbered_match = re.match(r'^(\d+)\.\s+(.+)', line)
                if bullet_match:
                    self.set_x(x_start + 4)
                    self.set_font("STHeiti", "", 10)
                    self.multi_cell(width - 8, 5.5, "  " + clean_text(bullet_match.group(1)))
                elif numbered_match:
                    self.set_x(x_start + 4)
                    self.set_font("STHeiti", "", 10)
                    self.multi_cell(width - 8, 5.5,
                                    f"{numbered_match.group(1)}. " + clean_text(numbered_match.group(2)))
                else:
                    self.set_x(x_start)
                    self.multi_cell(width, 5.5, clean_text(line))
            self.ln(1)


def main():
    print("Parsing discussion-log.md ...")
    sections = parse_markdown(SOURCE_FILE)
    print(f"  Found {len(sections)} Q&A sections")

    if len(sections) != 22:
        print(f"  WARNING: Expected 22 sections, got {len(sections)}")
        # Print what we found for debugging
        for i, s in enumerate(sections):
            print(f"    {i+1}. {s['title'][:60]}")

    pdf = ProductReviewPDF()
    pdf.set_margins(20, 20, 20)

    # Cover page
    print("Generating cover page ...")
    pdf.add_cover_page()

    # TOC page
    print("Generating table of contents ...")
    pdf.add_toc_page(sections)

    # Q&A sections
    for i, section in enumerate(sections):
        print(f"  Writing {section['title'][:50]} ...")
        pdf.add_qa_section(section, i)

    # Output
    print(f"Saving PDF to {OUTPUT_FILE} ...")
    pdf.output(OUTPUT_FILE)

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"PDF generated successfully!")
    print(f"  File: {OUTPUT_FILE}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"  Pages: {pdf.page_no()}")


if __name__ == "__main__":
    main()
