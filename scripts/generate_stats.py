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
BG = "#090d16"
CARD_BG = "#111726"
BORDER = "#1f293d"
FG = "#f1f5f9"
MUTED = "#94a3b8"
CYAN = "#38bdf8"
GREEN = "#4ade80"
PURPLE = "#c084fc"
AMBER = "#fbbf24"
PINK = "#f472b6"


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
  <rect width="100%" height="100%" rx="14" fill="{BG}"/>
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
          <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="#c084fc" stop-opacity="0.04"/>
        </linearGradient>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M20 0H0V20" fill="none" stroke="#1e293b" stroke-width="1"/>
        </pattern>
        <filter id="neon_blur" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
      </defs>

      <!-- Frame & Tech Grid -->
      <rect x="10" y="10" width="740" height="360" rx="14" fill="#090d16" stroke="url(#edge)" stroke-width="1.5"/>
      <rect x="10" y="10" width="740" height="360" rx="14" fill="url(#grid)" opacity="0.4"/>
      <rect x="11" y="11" width="738" height="358" rx="13" fill="url(#glow)"/>

      <!-- Window Header Bar -->
      <circle cx="34" cy="32" r="5" fill="#ef4444"/>
      <circle cx="50" cy="32" r="5" fill="#f59e0b"/>
      <circle cx="66" cy="32" r="5" fill="#10b981"/>
      <text x="86" y="36" fill="#64748b" font-family="monospace" font-size="11">harshit@iit-delhi:~/builder-manifest $ ./ship_systems.sh --verbose</text>
      <circle cx="718" cy="32" r="4" fill="#4ade80" filter="url(#neon_blur)"/>
      <text x="635" y="36" fill="#4ade80" font-family="monospace" font-size="10" font-weight="700">🟢 ALWAYS BUILDING</text>
      <line x1="20" y1="48" x2="740" y2="48" stroke="#1e293b"/>

      <!-- Main Developer Title -->
      <text x="32" y="78" fill="#94a3b8" font-family="monospace" font-size="12">$ whoami --fields=name,track,passions</text>
      <text x="32" y="122" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="44" font-weight="900" letter-spacing="-1">HARSHIT GOYAL</text>
      <rect x="32" y="134" width="140" height="4" rx="2" fill="url(#edge)"/>

      <!-- Subtitle Tagline -->
      <text x="32" y="164" fill="#38bdf8" font-family="monospace" font-size="13" font-weight="700">SOFTWARE (SDE) &amp; AI SYSTEMS ENGINEER · EDA TOOLING</text>
      <text x="32" y="184" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">Electrical Engineering @ IIT Delhi ('26) · Ex-Cadence Software &amp; EDA Intern</text>

      <!-- Pill Badges -->
      <rect x="32" y="204" width="170" height="26" rx="13" fill="#111726" stroke="#38bdf8" stroke-width="1"/>
      <text x="44" y="221" fill="#38bdf8" font-family="monospace" font-size="10" font-weight="700">SOFTWARE ENG (SDE)</text>

      <rect x="212" y="204" width="160" height="26" rx="13" fill="#111726" stroke="#818cf8" stroke-width="1"/>
      <text x="224" y="221" fill="#818cf8" font-family="monospace" font-size="10" font-weight="700">AI SYSTEMS &amp; RAG</text>

      <rect x="382" y="204" width="170" height="26" rx="13" fill="#111726" stroke="#c084fc" stroke-width="1"/>
      <text x="394" y="221" fill="#c084fc" font-family="monospace" font-size="10" font-weight="700">EDA &amp; COMPILER TOOLS</text>

      <rect x="562" y="204" width="158" height="26" rx="13" fill="#111726" stroke="#f472b6" stroke-width="1"/>
      <text x="574" y="221" fill="#f472b6" font-family="monospace" font-size="10" font-weight="700">GRAPH ALGORITHMS</text>

      <!-- Tech Nerd Interactive Manifest Box -->
      <rect x="32" y="246" width="688" height="110" rx="10" fill="#0d1322" stroke="#1e293b"/>
      <text x="48" y="268" fill="#64748b" font-family="monospace" font-size="11">$ cat ~/builder_manifest.json</text>
      
      <text x="48" y="292" fill="#38bdf8" font-family="monospace" font-size="11">"status":</text>
      <text x="125" y="292" fill="#f1f5f9" font-family="monospace" font-size="11">"Building fast, reliable software &amp; AI platforms that scale"</text>

      <text x="48" y="314" fill="#818cf8" font-family="monospace" font-size="11">"loop":</text>
      <text x="105" y="314" fill="#4ade80" font-family="monospace" font-size="11">["Identify Hard Problem", "Design Graph/RAG Arch", "Code &amp; Benchmark", "Ship 📦"]</text>

      <text x="48" y="336" fill="#c084fc" font-family="monospace" font-size="11">"benchmarks":</text>
      <text x="155" y="336" fill="#fbbf24" font-family="monospace" font-size="11">"0.28s AST Parser (388 fns) · JEE AIR 530 · FIFS ML Top 9 National"</text>
'''
    write("hero.svg", svg(WIDTH, 380, body, "Harshit Goyal — Software Engineering (SDE), AI Systems & EDA Tooling"))


def stats_card(user: dict | None = None) -> None:
    repo_count = len(user["repositories"]["nodes"]) if user else 12

    body = f'''
      <rect x="2" y="2" width="366" height="186" rx="10" fill="{CARD_BG}" stroke="{BORDER}"/>
      {text(18, 26, "⚡ REPO LOGIC & SYSTEM METRICS", 11, MUTED, 700)}
      
      <g transform="translate(18, 42)">
        <!-- Metric 1 -->
        <rect x="0" y="0" width="160" height="56" rx="8" fill="#090d16" stroke="#1f293d"/>
        {text(12, 22, "PUBLIC REPOS", 9, MUTED, 700)}
        {text(12, 44, f"{repo_count}+ Shipped", 15, CYAN, 800)}

        <!-- Metric 2 -->
        <rect x="172" y="0" width="160" height="56" rx="8" fill="#090d16" stroke="#1f293d"/>
        {text(184, 22, "IIT DELHI ALUM TRACK", 9, MUTED, 700)}
        {text(184, 44, "EE Class '26", 15, PURPLE, 800)}

        <!-- Metric 3 -->
        <rect x="0" y="66" width="160" height="56" rx="8" fill="#090d16" stroke="#1f293d"/>
        {text(12, 88, "JEE ADVANCED", 9, MUTED, 700)}
        {text(12, 110, "AIR 530", 16, GREEN, 800)}

        <!-- Metric 4 -->
        <rect x="172" y="66" width="160" height="56" rx="8" fill="#090d16" stroke="#1f293d"/>
        {text(184, 88, "ML COMPETITION", 9, MUTED, 700)}
        {text(184, 110, "Rank #9 National", 14, AMBER, 800)}
      </g>
      
      <rect x="18" y="168" width="332" height="1" fill="#1f293d"/>
    '''
    write("stats.svg", svg(370, 190, body, "Engineering & Profile Stats"))


def language_card(user: dict | None = None) -> None:
    top_langs = [
        ("Python", "#38bdf8", 0.48, 6),
        ("C++", "#f472b6", 0.22, 3),
        ("TypeScript", "#818cf8", 0.16, 3),
        ("Verilog / TCL", "#c084fc", 0.09, 2),
        ("SQL / Cypher", "#4ade80", 0.05, 4),
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

    rows = [text(18, 26, "💻 CORE LANGUAGES & STACK DISTRIBUTION", 11, MUTED, 700)]
    y = 52
    for name, color, pct, r_count in top_langs:
        pct_str = f"{pct:.0%}"
        rows.append(text(18, y, name[:14], 12, FG, 600))
        rows.append(text(125, y, f"{pct_str} · {r_count} repos", 10, MUTED))
        bar_width = max(6, round(180 * pct))
        rows.append(f'<rect x="220" y="{y - 10}" width="130" height="8" rx="4" fill="#090d16"/>')
        rows.append(f'<rect x="220" y="{y - 10}" width="{min(130, bar_width)}" height="8" rx="4" fill="{color}"/>')
        y += 26

    body = f'''
      <rect x="2" y="2" width="366" height="186" rx="10" fill="{CARD_BG}" stroke="{BORDER}"/>
      {"".join(rows)}
    '''
    write("langs.svg", svg(370, 190, body, "Top languages across public repositories"))


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
