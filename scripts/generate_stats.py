#!/usr/bin/env python3
"""Draw this profile's local SVG graphics from GitHub's GraphQL API.

No packages, hosted card services, or personal access token are required.  GitHub
Actions supplies GITHUB_TOKEN and the profile repository owns every rendered pixel.
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 760
BG = "#0d1117"
FG = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#58a6ff"
GREEN = "#3fb950"
ACCENT = "#d2a8ff"


def graphql(login: str, token: str) -> dict:
    query = """
      query($login: String!) {
        user(login: $login) {
          repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER,
                       isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
            nodes { name languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }}
          }
        }
      }
    """
    body = json.dumps({"query": query, "variables": {"login": login}}).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def svg(height: int, body: str, title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{escape(title)}">
  <rect width="100%" height="100%" rx="12" fill="{BG}"/>
  {body}
</svg>\n'''


def text(x: int, y: int, value: str, size: int = 13, color: str = FG, weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def write(name: str, content: str) -> None:
    (ROOT / name).write_text(content, encoding="utf-8")


def hero() -> None:
    body = '''
      <defs>
        <linearGradient id="edge" x1="0" x2="1"><stop stop-color="#58a6ff"/><stop offset="1" stop-color="#d2a8ff"/></linearGradient>
        <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#21262d" stroke-width="1"/></pattern>
      </defs>
      <rect x="16" y="16" width="728" height="298" rx="12" fill="#0d1117" stroke="url(#edge)"/>
      <rect x="16" y="16" width="728" height="298" rx="12" fill="url(#grid)" opacity=".42"/>
      <circle cx="43" cy="42" r="5" fill="#ff7b72"/><circle cx="61" cy="42" r="5" fill="#d29922"/><circle cx="79" cy="42" r="5" fill="#3fb950"/>
      <text x="104" y="47" fill="#8b949e" font-family="monospace" font-size="11">profile://harshit_goyal</text>
      <line x1="32" y1="62" x2="728" y2="62" stroke="#30363d"/>
      <path d="M530 108h76l19 19h72M558 224h52l18-18h74" fill="none" stroke="#58a6ff" stroke-width="1.5" opacity=".55"/>
      <circle cx="530" cy="108" r="4" fill="#58a6ff"/><circle cx="702" cy="127" r="4" fill="#d2a8ff"/><circle cx="558" cy="224" r="4" fill="#3fb950"/><circle cx="702" cy="206" r="4" fill="#58a6ff"/>
      <text x="46" y="102" fill="#8b949e" font-family="monospace" font-size="12">$ whoami</text>
      <text x="46" y="164" fill="#e6edf3" font-family="system-ui, sans-serif" font-size="50" font-weight="800" letter-spacing="-1">HARSHIT GOYAL</text>
      <rect x="46" y="181" width="94" height="4" rx="2" fill="url(#edge)"/>
      <text x="46" y="220" fill="#58a6ff" font-family="monospace" font-size="14" font-weight="700">AI SYSTEMS · FULL-STACK ENGINEERING</text>
      <rect x="46" y="244" width="153" height="28" rx="14" fill="#161b22" stroke="#30363d"/><text x="60" y="263" fill="#8b949e" font-family="monospace" font-size="10">RESEARCH INFRA</text>
      <rect x="210" y="244" width="151" height="28" rx="14" fill="#161b22" stroke="#30363d"/><text x="224" y="263" fill="#8b949e" font-family="monospace" font-size="10">DEVELOPER TOOLS</text>
      <rect x="372" y="244" width="174" height="28" rx="14" fill="#161b22" stroke="#30363d"/><text x="386" y="263" fill="#8b949e" font-family="monospace" font-size="10">PRODUCT ENGINEERING</text>
      <text x="46" y="296" fill="#d2a8ff" font-family="monospace" font-size="11">IIT DELHI · ELECTRICAL ENGINEERING · 2026</text>'''
    write("hero.svg", svg(330, body, "Harshit Goyal — AI systems and full-stack engineering"))


def language_card(user: dict) -> None:
    languages: Counter[tuple[str, str]] = Counter()
    repos: Counter[str] = Counter()
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            key = (edge["node"]["name"], edge["node"]["color"] or MUTED)
            languages[key] += edge["size"]
            repos[edge["node"]["name"]] += 1
    top = languages.most_common(5)
    total = sum(languages.values()) or 1
    rows = [text(28, 35, "PUBLIC REPOSITORY LANGUAGES", 12, MUTED)]
    y = 65
    for (name, color), count in top:
        pct = count / total
        rows.append(text(28, y, name, 13, FG, 700))
        rows.append(text(182, y, f"{pct:.0%} · {repos[name]} repos", 12, MUTED))
        rows.append(f'<rect x="360" y="{y - 12}" width="350" height="10" rx="5" fill="#21262d"/><rect x="360" y="{y - 12}" width="{max(4, round(350 * pct))}" height="10" rx="5" fill="{color}"/>')
        y += 30
    write("langs.svg", svg(max(110, y + 8), "".join(rows), "Top languages across public repositories"))


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    login = os.environ.get("GH_LOGIN")
    if not token or not login:
        raise SystemExit("GITHUB_TOKEN and GH_LOGIN are required")
    user = graphql(login, token)
    hero()
    language_card(user)


if __name__ == "__main__":
    main()
