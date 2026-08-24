from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1080  # square - consistent across feed, no crop surprises
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

def slide(filename, slide_no, total, kicker, headline, body_lines, code=None, closing_q=None, series="APPLIED AI ENGINEERING"):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    margin = 80

    d.rectangle([0, 0, W, 12], fill=AMBER)

    f_series = ImageFont.truetype(FONT_BOLD, 24)
    d.text((margin, 50), series, font=f_series, fill=GRAY)
    f_count = ImageFont.truetype(FONT_BOLD, 24)
    ctext = f"{slide_no:02d}/{total:02d}"
    cw = d.textlength(ctext, font=f_count)
    d.text((W - margin - cw, 50), ctext, font=f_count, fill=NAVY)

    d.line([(margin, 96), (W-margin, 96)], fill=(230,230,230), width=2)

    top = 136

    f_kick = ImageFont.truetype(FONT_BOLD, 30)
    f_head = ImageFont.truetype(FONT_BOLD, 66)
    f_body = ImageFont.truetype(FONT_REG, 38)
    f_q = ImageFont.truetype(FONT_BOLD, 32)

    head_lines = wrap(d, headline, f_head, W - 2*margin)
    body_wrapped = [wrap(d, line, f_body, W - 2*margin) for line in body_lines]

    # measure total content block height so short slides don't float in a sea of white space
    content_h = 0
    if kicker:
        content_h += 52
    content_h += len(head_lines) * 76
    content_h += 20 + 6 + 50  # underline gap + underline + gap after
    for wrapped in body_wrapped:
        content_h += len(wrapped) * 50 + 18

    # reserve space at the bottom for code block / closing question, if any
    if code:
        bottom_limit = H - 200 - 40
    elif closing_q:
        q_lines = wrap(d, closing_q, f_q, W - 2*margin)
        bottom_limit = H - 100 - len(q_lines) * 42
    else:
        bottom_limit = H - 120

    available = bottom_limit - top
    y = top + max(0, (available - content_h) // 2)

    if kicker:
        d.text((margin, y), kicker.upper(), font=f_kick, fill=AMBER)
        y += 52

    for line in head_lines:
        d.text((margin, y), line, font=f_head, fill=NAVY)
        y += 76

    y += 20
    d.rectangle([margin, y, margin + 90, y + 6], fill=AMBER)
    y += 50

    for wrapped in body_wrapped:
        for line in wrapped:
            d.text((margin, y), line, font=f_body, fill=NAVY)
            y += 50
        y += 18

    # code block - pinned near bottom, dark bg like real code
    if code:
        code_h = 90
        code_y = H - 200
        d.rectangle([margin, code_y, W-margin, code_y+code_h], fill=CODE_BG)
        # fake window dots
        for i, cx in enumerate([margin+24, margin+44, margin+64]):
            d.ellipse([cx-6, code_y+16, cx+6, code_y+28], fill=(90,98,110))
        f_mono = ImageFont.truetype(FONT_MONO, 28)
        d.text((margin+24, code_y+44), code, font=f_mono, fill=CODE_TEXT)

    if closing_q:
        q_lines = wrap(d, closing_q, f_q, W - 2*margin)
        qy = H - 100 - len(q_lines) * 42
        for line in q_lines:
            d.text((margin, qy), line, font=f_q, fill=NAVY)
            qy += 42

    d.rectangle([0, H-12, W, H], fill=NAVY)
    img.save(filename)

if __name__ == "__main__":
    # demo/self-test only \u2014 does not run on import
    slide("v2_s1.png", 1, 6, "Teaching Series", "LangChain Message Types",
          ["Four roles the LLM actually sees.", "Not just plain text you're passing in."])

    slide("v2_s2.png", 2, 6, "Role 1", "HumanMessage",
          ["What the user says.", "The input side of the conversation."],
          code="from langchain_core.messages import HumanMessage")

    slide("v2_s4.png", 4, 6, "Role 3", "SystemMessage",
          ["Sets behavior, tone, and rules", "for the model before it responds."],
          code="Use SystemMessagePromptTemplate for variables")

    slide("v2_s6.png", 6, 6, "Takeaway", "Get these four right",
          ["Multi-turn chat and agent flows", "stop feeling like guesswork."],
          closing_q="Which one trips you up \u2014 System or Tool?")

    print("done")
