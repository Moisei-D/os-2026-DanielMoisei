#!/usr/bin/env python3
"""Turn selected, real xv6 terminal transcripts into report figures."""

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "report" / "figures"
FONT_PATH = "/usr/share/fonts/google-noto-vf/NotoSansMono[wght].ttf"


def lines_from(path: str, start: int, end: int) -> list[str]:
    return (ROOT / path).read_text(encoding="utf-8").splitlines()[start - 1 : end]


def wrap_lines(lines: list[str], width: int = 100) -> list[str]:
    result: list[str] = []
    for line in lines:
        chunks = wrap(line.expandtabs(4), width=width, replace_whitespace=False,
                      drop_whitespace=False, break_long_words=True,
                      break_on_hyphens=False)
        result.extend(chunks or [""])
    return result


def render(filename: str, lines: list[str]) -> None:
    lines = wrap_lines(lines)
    font = ImageFont.truetype(FONT_PATH, 20)
    title_font = ImageFont.truetype(FONT_PATH, 16)
    char_width = int(font.getlength("M"))
    left, top, line_height = 28, 64, 30
    width = min(1800, max(920, left * 2 + char_width * max(map(len, lines))))
    height = top + line_height * len(lines) + 25
    image = Image.new("RGB", (width, height), "#171a1f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=16,
                           fill="#171a1f", outline="#39414c", width=2)
    draw.rounded_rectangle((1, 1, width - 2, 48), radius=15, fill="#242932")
    draw.rectangle((1, 31, width - 2, 48), fill="#242932")
    for x, color in ((22, "#ff5f57"), (45, "#febc2e"), (68, "#28c840")):
        draw.ellipse((x, 16, x + 12, 28), fill=color)
    draw.text((width // 2, 12), "xv6-riscv — QEMU", font=title_font,
              fill="#c9d1d9", anchor="ma")
    y = top
    for line in lines:
        color = "#7ee787" if line.startswith("$") else "#f0f6fc"
        draw.text((left, y), line, font=font, fill=color)
        y += line_height
    image.save(OUT / filename, optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    render("part1-directory-types.png", lines_from("evidence/xv6-session.txt", 8, 44))
    render("part2-hard-links.png", lines_from("evidence/xv6-session.txt", 41, 53))
    render("part3-limits.png", [
        "$ grep -n \"define BSIZE\\|define NDIRECT\\|define NINDIRECT\\|define DIRSIZ\" kernel/fs.h",
        *lines_from("evidence/fs-constants.txt", 1, 4),
        "$ make clean ; make fs.img 2>&1 | grep nmeta",
        "nmeta 47 (boot, super, log blocks 31, inode blocks 13, bitmap blocks 1) blocks 1953 total 2000",
        "$ mkdir averyveryverylongname ; ls",
        "averyveryveryl 1 29 32",
    ])
    render("part4-find.png", lines_from("evidence/find-session.txt", 115, 126))


if __name__ == "__main__":
    main()
