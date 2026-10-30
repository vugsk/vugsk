"""Генерирует top-langs.svg по байтам языков публичных репозиториев (без форков)."""
import collections
import json
import os
import subprocess
import sys

USER = os.environ.get("GH_USER", "vugsk")
OUT = sys.argv[1] if len(sys.argv) > 1 else "top-langs.svg"
EXCLUDE = {"Just", "CMake", "Makefile", "Dockerfile"}
LIMIT = 6
COLORS = {
    "Rust": "#dea584", "Go": "#00ADD8", "Slint": "#2379F4", "Shell": "#89e051",
    "C++": "#f34b7d", "Python": "#3572A5", "C": "#555555", "Java": "#b07219",
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#563d7c", "Lua": "#000080", "Assembly": "#6E4C13",
}
FONT = "Segoe UI,Ubuntu,sans-serif"


def gh(path):
    return json.loads(subprocess.check_output(["gh", "api", "--paginate", path]))


def collect():
    total = collections.Counter()
    for repo in gh(f"users/{USER}/repos?type=owner&per_page=100"):
        if repo["fork"] or repo["archived"]:
            continue
        total.update(gh(f"repos/{repo['full_name']}/languages"))
    for name in EXCLUDE:
        total.pop(name, None)
    return total


def render(total):
    items = total.most_common(LIMIT)
    s = sum(total.values()) or 1
    h = 60 + len(items) * 26
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="340" height="{h}" viewBox="0 0 340 {h}">',
        f'<rect width="340" height="{h}" rx="6" fill="#0d1117" stroke="#30363d"/>',
        f'<text x="20" y="32" font-family="{FONT}" font-size="16" font-weight="600" fill="#58a6ff">Top Languages</text>',
    ]
    for i, (name, size) in enumerate(items):
        y = 58 + i * 26
        pct = size / s * 100
        out.append(
            f'<text x="20" y="{y + 11}" font-family="{FONT}" font-size="12" fill="#c9d1d9">{name}</text>'
            f'<rect x="90" y="{y + 2}" width="150" height="10" rx="5" fill="#21262d"/>'
            f'<rect x="90" y="{y + 2}" width="{pct * 1.5:.1f}" height="10" rx="5" fill="{COLORS.get(name, "#8b949e")}"/>'
            f'<text x="250" y="{y + 11}" font-family="{FONT}" font-size="12" fill="#8b949e">{pct:.1f}%</text>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(collect()))
