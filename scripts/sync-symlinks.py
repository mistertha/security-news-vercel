#!/usr/bin/env python3
"""Sync symlinks from Paperclip summaries into Docsify — then regenerate sidebar."""

import os
import subprocess
import sys
from datetime import datetime

# ── Paths ──
PAPERCLIP_SUMMARIES = os.path.expanduser(
    "~/.paperclip/instances/default/workspaces/"
    "e6c3bc22-82f6-4c87-9ea6-6d3a802f95fb/summaries/"
)
DOCSIFY_SUMMARIES = os.path.expanduser("~/security-news-docsify/summaries/")
REGENERATE_SCRIPT = os.path.expanduser("~/security-news-docsify/scripts/regenerate-sidebar.py")

DOCSIFY_SUMMARIES = os.path.abspath(DOCSIFY_SUMMARIES)
PAPERCLIP_SUMMARIES = os.path.abspath(PAPERCLIP_SUMMARIES)


def sync_symlinks():
    """Create symlinks for any Paperclip .md files missing in Docsify summaries."""
    if not os.path.isdir(PAPERCLIP_SUMMARIES):
        print(f"❌ Paperclip summaries dir not found: {PAPERCLIP_SUMMARIES}")
        return 0

    os.makedirs(DOCSIFY_SUMMARIES, exist_ok=True)

    created = 0
    for fname in sorted(os.listdir(PAPERCLIP_SUMMARIES)):
        if not fname.endswith(".md"):
            continue
        # Validate date-pattern filename
        stem = fname[:-3]
        try:
            datetime.strptime(stem, "%Y-%m-%d")
        except ValueError:
            continue  # skip non-date files

        src = os.path.join(PAPERCLIP_SUMMARIES, fname)
        dst = os.path.join(DOCSIFY_SUMMARIES, fname)

        if os.path.islink(dst):
            # Already exists — verify it points to the right place
            if os.readlink(dst) != src:
                os.unlink(dst)
                os.symlink(src, dst)
                print(f"🔗 Fixed symlink: {fname}")
                created += 1
        elif os.path.exists(dst):
            print(f"⚠️  Regular file at {dst} (expected symlink) — skipped {fname}")
        else:
            os.symlink(src, dst)
            print(f"🔗 Created symlink: {fname}")
            created += 1

    if created == 0:
        print("✅ All symlinks up-to-date — nothing to sync")
    else:
        print(f"✅ Synced {created} new/fixed symlink(s)")

    return created


def regenerate_sidebar():
    """Run the sidebar regeneration script."""
    result = subprocess.run(
        [sys.executable, REGENERATE_SCRIPT],
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        print(f"⚠️  Sidebar regenerate exited with code {result.returncode}")


if __name__ == "__main__":
    print(f"🔄 Syncing symlinks: {PAPERCLIP_SUMMARIES} → {DOCSIFY_SUMMARIES}")
    created = sync_symlinks()
    if created > 0:
        print("\n📋 Regenerating sidebar...")
        regenerate_sidebar()
    else:
        # Still regenerate — sidebar may need update even if no new symlinks
        # (e.g., if a symlink was deleted/renamed)
        regenerate_sidebar()