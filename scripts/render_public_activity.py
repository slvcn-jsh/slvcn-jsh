#!/usr/bin/env python3
"""Render a small, factual public GitHub activity card for the profile README.

Only uses the public GitHub events endpoint. This is NOT the contribution calendar,
and does not count private events, code quality, productivity, or all-time commits.
"""
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

USER = "slvcn-jsh"
URL = f"https://api.github.com/users/{USER}/events/public?per_page=100"
OUTPUT = Path("assets/public-activity.svg")

def fetch_events():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "slvcn-jsh-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urlopen(Request(URL, headers=headers), timeout=25) as response:
        result = json.load(response)
    if not isinstance(result, list):
        raise RuntimeError("Unexpected public-events response")
    return result

def text(x, y, value, size=18, color="#eaf6ff", weight=500):
    return (f'<text x="{x}" y="{y}" fill="{color}" '
            f'font-family="Arial,Helvetica,sans-serif" font-size="{size}" '
            f'font-weight="{weight}">{escape(str(value))}</text>')

def render(events):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    counts = Counter(e.get("type", "Other") for e in events)
    labels = [
        ("Push events", counts["PushEvent"], "#73e5cd"),
        ("Pull request events", counts["PullRequestEvent"], "#87b9f7"),
        ("Issue events", counts["IssuesEvent"], "#bca4ff"),
        ("Other public events", sum(v for k, v in counts.items()
                                     if k not in {"PushEvent", "PullRequestEvent", "IssuesEvent"}), "#7799af"),
    ]
    max_count = max((n for _, n, _ in labels), default=1) or 1
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="330" '
        'viewBox="0 0 1000 330" role="img" aria-label="Recent public GitHub event types">',
        '<title>Recent public GitHub activity — latest available events</title>',
        '<rect width="1000" height="330" rx="22" fill="#0b1b2b"/>',
        '<rect x="1" y="1" width="998" height="328" rx="21" fill="none" stroke="#34536b"/>',
        text(32, 48, "PUBLIC ACTIVITY / RECENT EVENTS", 22, "#eef9ff", 750),
        text(32, 78, f"Based on the latest {len(events)} public events returned by GitHub", 15, "#a9c5d7"),
    ]
    for i, (label, count, color) in enumerate(labels):
        y = 112 + i * 47
        width = int(410 * count / max_count)
        parts += [text(32, y+18, label, 16, "#c4dce9"),
                  f'<rect x="290" y="{y}" width="410" height="21" rx="8" fill="#1b3447"/>',
                  f'<rect x="290" y="{y}" width="{width}" height="21" rx="8" fill="{color}"/>',
                  text(722, y+18, count, 16, "#f2fbff", 750)]
    parts += [text(32, 310, f"Updated {now}  |  Public events only; not a contribution or commit count", 13, "#8caec1"),
              '</svg>']
    return "\n".join(parts) + "\n"

def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(fetch_events()), encoding="utf-8")

if __name__ == "__main__":
    main()
