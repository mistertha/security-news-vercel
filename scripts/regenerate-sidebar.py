#!/usr/bin/env python3
"""Regenerate _sidebar.md from summary files in the summaries/ directory."""

import os
from datetime import datetime

DOCSIFY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARIES_DIR = os.path.join(DOCSIFY_DIR, "summaries")
SIDEBAR_PATH = os.path.join(DOCSIFY_DIR, "_sidebar.md")

# ── Static sections ──
HEADER = """- **🏠 Home**
  - [Dashboard](/)
- **📅 Daily Digests**
"""

STATS = """- **📊 Stats**
  - [Threat Dashboard](/stats.md)
"""

SOURCES = """- **🔗 Sources**
  - [The Hacker News](https://thehackernews.com/)
  - [Krebs on Security](https://krebsonsecurity.com/)
  - [CISA Alerts](https://www.cisa.gov/news-events/cybersecurity-advisories)
  - [Dark Reading](https://www.darkreading.com/)
  - [SecurityWeek](https://www.securityweek.com/)
"""


def get_summary_files():
    """Get all .md files in summaries/ sorted by date descending."""
    files = []
    if not os.path.isdir(SUMMARIES_DIR):
        return files

    for fname in os.listdir(SUMMARIES_DIR):
        if not fname.endswith(".md"):
            continue
        # Extract date from filename: YYYY-MM-DD.md
        stem = fname[:-3]  # remove .md
        try:
            dt = datetime.strptime(stem, "%Y-%m-%d")
            files.append((dt, fname))
        except ValueError:
            # Non-date files (e.g., _sidebar.md) — skip
            pass

    # Sort descending (newest first)
    files.sort(key=lambda x: x[0], reverse=True)
    return files


def format_date(dt: datetime) -> str:
    """Format date as human-readable Thai month name."""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    return f"{months[dt.month - 1]} {dt.day:02d}, {dt.year}"


def regenerate():
    files = get_summary_files()

    lines = [HEADER]

    if not files:
        lines.append("  - *No digests yet*\n")
    else:
        for dt, fname in files:
            label = format_date(dt)
            path = f"/summaries/{fname}"
            lines.append(f"  - [{label}]({path})\n")

    lines.extend([STATS, SOURCES])

    content = "".join(lines)

    # Avoid unnecessary writes (preserves file mtime)
    if os.path.exists(SIDEBAR_PATH):
        with open(SIDEBAR_PATH, "r") as f:
            existing = f.read()
        if existing == content:
            print(f"No changes — {len(files)} summaries already listed")
            return

    with open(SIDEBAR_PATH, "w") as f:
        f.write(content)

    print(f"Regenerated _sidebar.md — {len(files)} daily digests listed")
    for dt, fname in files:
        print(f"  📅 {format_date(dt)} → {fname}")


if __name__ == "__main__":
    regenerate()
