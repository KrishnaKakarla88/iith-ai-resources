from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1080
NAVY = (26, 43, 74)
AMBER = (194, 120, 3)
WHITE = (255, 255, 255)
GRAY = (120, 128, 138)
CODE_BG = (24, 32, 48)
CODE_TEXT = (226, 232, 240)

import os
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = os.path.join(SKILL_DIR, "assets/fonts/LiberationSans-Bold.ttf")
FONT_REG = os.path.join(SKILL_DIR, "assets/fonts/LiberationSans-Regular.ttf")
FONT_MONO = os.path.join(SKILL_DIR, "assets/fonts/LiberationMono-Regular.ttf")

def wrap(draw, text, font, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def single_image(filename, kicker, headline, items, footer, series="APPLIED AI ENGINEERING"):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    margin = 80

    d.rectangle([0, 0, W, 12], fill=AMBER)
    f_series = ImageFont.truetype(FONT_BOLD, 24)
    d.text((margin, 50), series, font=f_series, fill=GRAY)
    d.line([(margin, 96), (W-margin, 96)], fill=(230,230,230), width=2)

    f_kick = ImageFont.truetype(FONT_BOLD, 28)
    f_head = ImageFont.truetype(FONT_BOLD, 58)
    f_name = ImageFont.truetype(FONT_BOLD, 38)
    f_desc = ImageFont.truetype(FONT_REG, 30)
    tx = margin + 74
    desc_max_width = W - tx - margin

    head_lines = wrap(d, headline, f_head, W - 2*margin)
    desc_wrapped = [wrap(d, desc, f_desc, desc_max_width) for _, desc in items]
    # each item needs room for its name line + however many desc lines it wraps to
    row_heights = [58 + len(dw) * 34 + 26 for dw in desc_wrapped]  # +26 breathing room between rows

    # measure content block height to center it, same approach as the carousel template
    content_h = 48 + len(head_lines) * 66 + 16 + 6 + 44 + sum(row_heights)
    bottom_limit = H - 150 - 30  # leave room for the footer code block
    top = 145
    available = bottom_limit - top
    y = top + max(0, (available - content_h) // 2)

    d.text((margin, y), kicker.upper(), font=f_kick, fill=AMBER)
    y += 48

    for line in head_lines:
        d.text((margin, y), line, font=f_head, fill=NAVY)
        y += 66
    y += 16
    d.rectangle([margin, y, margin + 90, y + 6], fill=AMBER)
    y += 44

    # items: list of (name, desc)
    f_num = ImageFont.truetype(FONT_BOLD, 26)
    for i, (name, desc) in enumerate(items):
        # accent number chip, aligned to the name's line
        d.ellipse([margin, y, margin+52, y+52], outline=AMBER, width=3)
        num = str(i+1)
        nw = d.textlength(num, font=f_num)
        d.text((margin+26-nw/2, y+12), num, font=f_num, fill=AMBER)

        d.text((tx, y-2), name, font=f_name, fill=NAVY)
        dy = y + 42
        for line in desc_wrapped[i]:
            d.text((tx, dy), line, font=f_desc, fill=GRAY)
            dy += 34
        y += row_heights[i]

    # footer code block
    code_h = 80
    code_y = H - 150
    d.rectangle([margin, code_y, W-margin, code_y+code_h], fill=CODE_BG)
    for i, cx in enumerate([margin+22, margin+42, margin+62]):
        d.ellipse([cx-6, code_y+14, cx+6, code_y+26], fill=(90,98,110))
    # shrink font until the footer line fits on one row inside the block
    code_max_width = W - 2*margin - 44
    mono_size = 24
    f_mono = ImageFont.truetype(FONT_MONO, mono_size)
    while mono_size > 14 and d.textlength(footer, font=f_mono) > code_max_width:
        mono_size -= 2
        f_mono = ImageFont.truetype(FONT_MONO, mono_size)
    d.text((margin+22, code_y+40 - mono_size//2 + 8), footer, font=f_mono, fill=CODE_TEXT)

    d.rectangle([0, H-12, W, H], fill=NAVY)
    img.save(filename)

if __name__ == "__main__":
    # demo/self-test only — does not run on import
    single_image(
        "single_v1.png",
        "Teaching Series",
        "LangChain Message Types",
        [
            ("HumanMessage", "What the user says"),
            ("AIMessage", "What the model replies"),
            ("SystemMessage", "Sets behavior and rules"),
            ("ToolMessage", "Result after a tool call"),
        ],
        "from langchain_core.messages import *"
    )
    print("done")
