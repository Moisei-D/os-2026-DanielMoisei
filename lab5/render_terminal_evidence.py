#!/usr/bin/env python3

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
LOG = ROOT / "experiment-output.txt"
OUT = ROOT / "report" / "figures"
FONT_PATH = "/usr/share/fonts/google-noto-vf/NotoSansMono[wght].ttf"

CAPTURES = {
    "part1-root.png": [(9, 31)],
    "part1-types-space.png": [(33, 59)],
    "part2-inodes-links.png": [(63, 103)],
    "part2-directories-space.png": [(105, 119)],
    "part3-file-permissions.png": [(123, 137)],
    "part3-directory-special.png": [(139, 159)],
    "part4-proc.png": [(210, 230)],
    "stretch-magic.png": [(234, 240)],
}


def selected_lines(source: list[str], ranges: list[tuple[int, int]]) -> list[str]:
    result: list[str] = []
    for start, end in ranges:
        result.extend(source[start - 1 : end])
    return result


def wrapped_lines(lines: list[str], width: int = 118) -> list[str]:
    result: list[str] = []
    for line in lines:
        expanded = line.expandtabs(4)
        if len(expanded) <= width:
            result.append(expanded)
        else:
            chunks = wrap(
                expanded,
                width=width,
                replace_whitespace=False,
                drop_whitespace=False,
                break_long_words=True,
                break_on_hyphens=False,
                subsequent_indent="  ",
            )
            result.extend(chunks or [""])
    return result


def render_terminal(path: Path, lines: list[str]) -> None:
    font = ImageFont.truetype(FONT_PATH, 22)
    title_font = ImageFont.truetype(FONT_PATH, 18)
    char_width = int(font.getlength("M"))
    line_height = 32
    left = 30
    top = 74
    width = min(1900, max(1050, left * 2 + char_width * max(len(x) for x in lines)))
    height = top + line_height * len(lines) + 28

    image = Image.new("RGB", (width, height), "#171a1f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=18, fill="#171a1f", outline="#39414c", width=2)
    draw.rounded_rectangle((1, 1, width - 2, 54), radius=17, fill="#242932")
    draw.rectangle((1, 35, width - 2, 54), fill="#242932")
    for x, color in ((24, "#ff5f57"), (49, "#febc2e"), (74, "#28c840")):
        draw.ellipse((x, 18, x + 14, 32), fill=color)
    draw.text((width // 2, 14), "moiseid@fedora — bash", font=title_font, fill="#c9d1d9", anchor="ma")

    y = top
    for line in lines:
        color = "#7ee787" if line.startswith("$") else "#f0f6fc"
        if "Permission denied" in line or "No such file" in line:
            color = "#ff7b72"
        draw.text((left, y), line, font=font, fill=color)
        y += line_height
    image.save(path, optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = LOG.read_text(encoding="utf-8").splitlines()
    for filename, ranges in CAPTURES.items():
        lines = wrapped_lines(selected_lines(source, ranges))
        render_terminal(OUT / filename, lines)
        print(OUT / filename)
    disk_lines = (ROOT / "disk-summary-output.txt").read_text(encoding="utf-8").splitlines()
    render_terminal(OUT / "part4-disks.png", wrapped_lines(disk_lines))
    print(OUT / "part4-disks.png")


if __name__ == "__main__":
    main()

