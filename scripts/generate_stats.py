#!/usr/bin/env python3
"""Draw this profile's local SVG graphics from GitHub's GraphQL API.

No packages, hosted card services, or personal access token are required.  GitHub
Actions supplies GITHUB_TOKEN and the profile repository owns every rendered pixel.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 760
BG = "#0d1117"
PANEL = "#161b22"
FG = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#58a6ff"
GREEN = "#3fb950"
ACCENT = "#d2a8ff"


def utc_window() -> tuple[str, str]:
    today = dt.datetime.now(dt.timezone.utc).date()
    start = today - dt.timedelta(days=364)
    return (
        f"{start.isoformat()}T00:00:00Z",
        f"{today.isoformat()}T23:59:59Z",
    )


def graphql(login: str, token: str) -> dict:
    start, end = utc_window()
    query = """
      query($login: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $login) {
          contributionsCollection(from: $from, to: $to) {
            contributionCalendar {
              totalContributions
              weeks { contributionDays { date contributionCount } }
            }
          }
          repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER,
                       isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
            nodes { name languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }}
          }
        }
      }
    """
    body = json.dumps({"query": query, "variables": {"login": login, "from": start, "to": end}}).encode()
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
      <text x="28" y="74" fill="#8b949e" font-family="monospace" font-size="12" letter-spacing="2">BUILDING USEFUL, RELIABLE SOFTWARE</text>
      <text x="28" y="136" fill="#e6edf3" font-family="system-ui, sans-serif" font-size="48" font-weight="750" letter-spacing="-1">HARSHIT GOYAL</text>
      <rect x="28" y="158" width="86" height="4" rx="2" fill="#58a6ff"/>
      <text x="28" y="204" fill="#58a6ff" font-family="monospace" font-size="15" font-weight="700">AI SYSTEMS · FULL-STACK ENGINEERING</text>
      <text x="28" y="232" fill="#d2a8ff" font-family="monospace" font-size="12">IIT DELHI · ELECTRICAL ENGINEERING · 2026</text>'''
    write("hero.svg", svg(262, body, "Harshit Goyal — AI systems and full-stack engineering"))


def flat_days(user: dict) -> list[dict]:
    return [day for week in user["contributionsCollection"]["contributionCalendar"]["weeks"] for day in week["contributionDays"]]


def stats_card(days: list[dict], total: int) -> None:
    weeks = [sum(d["contributionCount"] for d in days[i:i + 7]) for i in range(0, len(days), 7)]
    recent = weeks[-16:]
    peak = max(recent) or 1
    chart = []
    for i, value in enumerate(recent):
        h = round(54 * value / peak)
        x = 420 + i * 19
        chart.append(f'<rect x="{x}" y="{123 - h}" width="11" height="{h}" rx="2" fill="{GREEN}" opacity=".9"/>')
    body = (
        text(28, 35, "PUBLIC CONTRIBUTIONS", 12, MUTED)
        + text(28, 90, f"{total:,}", 46, FG, 700)
        + text(28, 118, "in the last 365 complete UTC days", 12, MUTED)
        + text(420, 35, "WEEKLY ACTIVITY / LAST 16 WEEKS", 11, MUTED)
        + '<line x1="420" y1="124" x2="730" y2="124" stroke="#30363d"/>'
        + "".join(chart)
    )
    write("stats.svg", svg(150, body, "Public contribution total and weekly activity"))


def streak_card(days: list[dict]) -> None:
    values = [(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for d in days]
    best = current = 0
    best_end = current_end = None
    for date, count in values:
        if count:
            current += 1
            current_end = date
            if current > best:
                best, best_end = current, date
        else:
            current = 0
    current_start = current_end - dt.timedelta(days=current - 1) if current_end else None
    best_start = best_end - dt.timedelta(days=best - 1) if best_end else None
    current_label = f"{current} days" if current else "no active streak"
    best_label = f"{best} days" if best else "no contributions in window"
    body = (
        text(28, 35, "CONTRIBUTION STREAKS", 12, MUTED)
        + text(28, 84, current_label, 30, GREEN, 700)
        + text(28, 110, "current  " + (f"{current_start} → {current_end}" if current_start else ""), 12, MUTED)
        + text(406, 84, best_label, 30, ACCENT, 700)
        + text(406, 110, "longest  " + (f"{best_start} → {best_end}" if best_start else ""), 12, MUTED)
    )
    write("streak.svg", svg(140, body, "Current and longest public contribution streaks"))


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
    days = flat_days(user)
    hero()
    stats_card(days, user["contributionsCollection"]["contributionCalendar"]["totalContributions"])
    streak_card(days)
    language_card(user)


if __name__ == "__main__":
    main()
