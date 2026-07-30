#!/usr/bin/env python3
"""Draw this profile's local SVG graphics from GitHub's GraphQL API.

Supports both GitHub Actions execution (with GITHUB_TOKEN & GH_LOGIN)
and local fallback execution so graphics can be previewed anytime.
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
CARD_BG = "#161b22"
BORDER = "#30363d"
FG = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#38bdf8"
GREEN = "#3fb950"
PURPLE = "#c084fc"
AMBER = "#f59e0b"


def graphql(login: str, token: str) -> dict | None:
    query = """
      query($login: String!) {
        user(login: $login) {
          repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER,
                       isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
            nodes {
              name
              stargazerCount
              languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                edges { size node { name color } }
              }
            }
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
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.load(response)
        if payload.get("errors"):
            return None
        return payload["data"]["user"]
    except Exception:
        return None


def svg(width: int, height: int, body: str, title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
  <rect width="100%" height="100%" rx="12" fill="{BG}"/>
  {body}
</svg>\n'''


def text(x: int, y: int, value: str, size: int = 13, color: str = FG, weight: int = 400, family: str = "monospace") -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def write(name: str, content: str) -> None:
    (ROOT / name).write_text(content, encoding="utf-8")


def hero() -> None:
    body = '''
      <defs>
        <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#38bdf8"/>
          <stop offset="50%" stop-color="#818cf8"/>
          <stop offset="100%" stop-color="#c084fc"/>
        </linearGradient>
        <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.2"/>
          <stop offset="100%" stop-color="#c084fc" stop-opacity="0.05"/>
        </linearGradient>
        <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
          <path d="M24 0H0V24" fill="none" stroke="#21262d" stroke-width="1"/>
        </pattern>
      </defs>

      <!-- Frame & Grid Background -->
      <rect x="12" y="12" width="736" height="326" rx="12" fill="#0d1117" stroke="url(#edge)" stroke-width="1.5"/>
      <rect x="12" y="12" width="736" height="326" rx="12" fill="url(#grid)" opacity="0.35"/>
      <rect x="13" y="13" width="734" height="324" rx="11" fill="url(#glow)"/>

      <!-- Window Control Dots -->
      <circle cx="38" cy="36" r="5" fill="#ff7b72"/>
      <circle cx="56" cy="36" r="5" fill="#d29922"/>
      <circle cx="74" cy="36" r="5" fill="#3fb950"/>
      <text x="96" y="40" fill="#8b949e" font-family="monospace" font-size="11">profile://goyal-harshit ~ iit-delhi-ee'26</text>
      <line x1="24" y1="54" x2="736" y2="54" stroke="#30363d"/>

      <!-- Terminal Command & Name Header -->
      <text x="36" y="82" fill="#8b949e" font-family="monospace" font-size="12">$ whoami</text>
      <text x="36" y="128" fill="#e6edf3" font-family="system-ui, -apple-system, sans-serif" font-size="42" font-weight="800" letter-spacing="-0.5">HARSHIT GOYAL</text>
      <rect x="36" y="142" width="120" height="4" rx="2" fill="url(#edge)"/>

      <!-- Subtitle Tagline -->
      <text x="36" y="174" fill="#38bdf8" font-family="monospace" font-size="13" font-weight="700">SOFTWARE (SDE) &amp; AI SYSTEMS · VLSI &amp; EDA ENGINEERING</text>
      <text x="36" y="196" fill="#8b949e" font-family="system-ui, sans-serif" font-size="12">Electrical Engineering @ IIT Delhi | Ex-Cadence ASIC Synthesis Intern</text>

      <!-- Pill Badges -->
      <rect x="36" y="218" width="180" height="26" rx="13" fill="#161b22" stroke="#38bdf8" stroke-width="1"/>
      <text x="48" y="235" fill="#38bdf8" font-family="monospace" font-size="10" font-weight="700">SOFTWARE ENG (SDE)</text>

      <rect x="226" y="218" width="168" height="26" rx="13" fill="#161b22" stroke="#818cf8" stroke-width="1"/>
      <text x="238" y="235" fill="#818cf8" font-family="monospace" font-size="10" font-weight="700">AI SYSTEMS &amp; RAG</text>

      <rect x="404" y="218" width="176" height="26" rx="13" fill="#161b22" stroke="#c084fc" stroke-width="1"/>
      <text x="416" y="235" fill="#c084fc" font-family="monospace" font-size="10" font-weight="700">VLSI &amp; EDA TOOLING</text>

      <!-- Right Graphic / Circuit & Neural Mesh -->
      <g opacity="0.6">
        <path d="M600 80 H670 L700 110 V170 L670 200 H610 L580 170 V120 Z" fill="none" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="4,2"/>
        <path d="M620 100 H680 L690 110 V150" fill="none" stroke="#c084fc" stroke-width="1.2"/>
        <circle cx="600" cy="80" r="3.5" fill="#38bdf8"/>
        <circle cx="700" cy="110" r="3.5" fill="#c084fc"/>
        <circle cx="670" cy="200" r="3.5" fill="#3fb950"/>
        <circle cx="610" cy="200" r="3.5" fill="#f59e0b"/>
        <circle cx="650" cy="135" r="5" fill="#38bdf8"/>
      </g>

      <!-- Terminal Bottom Bar / Highlights -->
      <rect x="36" y="264" width="688" height="60" rx="8" fill="#161b22" stroke="#21262d"/>
      <text x="52" y="286" fill="#8b949e" font-family="monospace" font-size="11">$ cat highlights.json</text>
      <text x="52" y="306" fill="#3fb950" font-family="monospace" font-size="11">✓ JEE Adv AIR 530</text>
      <text x="200" y="306" fill="#38bdf8" font-family="monospace" font-size="11">✓ FIFS ML Top 9 National</text>
      <text x="410" y="306" fill="#c084fc" font-family="monospace" font-size="11">✓ Cadence Synthesis Intern</text>
'''
    write("hero.svg", svg(WIDTH, 350, body, "Harshit Goyal — Software Engineering, AI Systems & VLSI EDA"))


def stats_card(user: dict | None = None) -> None:
    repo_count = len(user["repositories"]["nodes"]) if user else 12

    body = f'''
      <defs>
        <linearGradient id="stats_grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#38bdf8"/>
          <stop offset="100%" stop-color="#818cf8"/>
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="366" height="176" rx="10" fill="{CARD_BG}" stroke="{BORDER}"/>
      {text(20, 28, "ENGINEERING & PROFILE STATS", 11, MUTED, 700)}
      
      <!-- Metrics Grid -->
      <g transform="translate(20, 48)">
        <!-- Metric 1 -->
        <rect x="0" y="0" width="156" height="52" rx="6" fill="#0d1117" stroke="#21262d"/>
        {text(12, 22, "PUBLIC REPOS", 9, MUTED, 700)}
        {text(12, 42, str(repo_count), 18, BLUE, 800)}

        <!-- Metric 2 -->
        <rect x="170" y="0" width="156" height="52" rx="6" fill="#0d1117" stroke="#21262d"/>
        {text(182, 22, "IIT DELHI TRACK", 9, MUTED, 700)}
        {text(182, 42, "EE '26", 18, PURPLE, 800)}

        <!-- Metric 3 -->
        <rect x="0" y="60" width="156" height="52" rx="6" fill="#0d1117" stroke="#21262d"/>
        {text(12, 82, "JEE ADVANCED", 9, MUTED, 700)}
        {text(12, 102, "AIR 530", 18, GREEN, 800)}

        <!-- Metric 4 -->
        <rect x="170" y="60" width="156" height="52" rx="6" fill="#0d1117" stroke="#21262d"/>
        {text(182, 82, "ML COMPETITION", 9, MUTED, 700)}
        {text(182, 102, "Rank #9", 18, AMBER, 800)}
      </g>
    '''
    write("stats.svg", svg(370, 180, body, "Engineering & Profile Stats"))


def language_card(user: dict | None = None) -> None:
    top_langs = [
        ("Python", "#3572A5", 0.48, 6),
        ("C++", "#f34b7d", 0.22, 3),
        ("TypeScript", "#3178c6", 0.16, 3),
        ("Verilog / TCL", "#b2b7f8", 0.09, 2),
        ("SQL / Other", "#e34c26", 0.05, 4),
    ]

    if user:
        languages: Counter[tuple[str, str]] = Counter()
        repos: Counter[str] = Counter()
        for repo in user["repositories"]["nodes"]:
            for edge in repo["languages"]["edges"]:
                key = (edge["node"]["name"], edge["node"]["color"] or MUTED)
                languages[key] += edge["size"]
                repos[edge["node"]["name"]] += 1
        if languages:
            total = sum(languages.values()) or 1
            top = languages.most_common(5)
            top_langs = [(name, color, count / total, repos[name]) for (name, color), count in top]

    rows = [text(20, 28, "TOP LANGUAGES & TECH STACK", 11, MUTED, 700)]
    y = 54
    for name, color, pct, r_count in top_langs:
        pct_str = f"{pct:.0%}"
        rows.append(text(20, y, name[:14], 12, FG, 600))
        rows.append(text(125, y, f"{pct_str} · {r_count} repos", 10, MUTED))
        bar_width = max(6, round(180 * pct))
        rows.append(f'<rect x="220" y="{y - 10}" width="130" height="8" rx="4" fill="#21262d"/>')
        rows.append(f'<rect x="220" y="{y - 10}" width="{min(130, bar_width)}" height="8" rx="4" fill="{color}"/>')
        y += 24

    body = f'''
      <rect x="2" y="2" width="366" height="176" rx="10" fill="{CARD_BG}" stroke="{BORDER}"/>
      {"".join(rows)}
    '''
    write("langs.svg", svg(370, 180, body, "Top languages across public repositories"))


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    login = os.environ.get("GH_LOGIN")
    user = None
    if token and login:
        try:
            user = graphql(login, token)
        except Exception:
            user = None

    hero()
    stats_card(user)
    language_card(user)
    print("[OK] Successfully generated hero.svg, stats.svg, and langs.svg")


if __name__ == "__main__":
    main()
