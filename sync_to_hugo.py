#!/usr/bin/env python3
"""
sync_to_hugo.py — Restaurant Agentic CMS → Hugo Content Sync
Converts JSON content files to Hugo Markdown content.

Run after each git commit to sync CMS JSON → Hugo content files.
Then Hugo rebuilds on the next CI/CD run.

Usage:
    python sync_to_hugo.py [--watch] [--hugo-dir ./hugo]
"""

import argparse
import json
import sys
import re
from pathlib import Path

# Resolve PROJECT_ROOT to this file's directory, then go up one level to the project root
PROJECT_ROOT = Path(__file__).parent.resolve()
CONTENT_DIR = PROJECT_ROOT / "content"
HUGO_CONTENT_DIR = PROJECT_ROOT / "site/hugo/content"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def item_to_md(title: str, description: str, price: float | None = None,
               tags: list | None = None, image: str = "", available: bool = True,
               menu_section: str = "", frontmatter: dict | None = None) -> str:
    fm = frontmatter or {}
    lines = ["---"]
    lines.append(f'title: "{title}"')
    if description:
        lines.append(f'description: "{description}"')
    if price is not None:
        lines.append(f"price: {price}")
    if tags:
        lines.append(f"tags: [{', '.join(repr(t) for t in tags)}]")
    if image:
        lines.append(f'image: "{image}"')
    if available:
        lines.append("available: true")
    else:
        lines.append("available: false")
    if menu_section:
        lines.append(f'menu_section: {menu_section}')
    for k, v in fm.items():
        if k not in ("title", "description", "price", "tags", "image", "available", "menu_section"):
            lines.append(f"{k}: {json.dumps(v) if isinstance(v, str) else v}")
    lines.append("---\n")
    return "\n".join(lines)


def sync_menu(hugo_dir: Path) -> int:
    """Sync menu.json → Hugo content/menu/*.md"""
    menu_path = CONTENT_DIR / "menu.json"
    if not menu_path.exists():
        print(f"  WARNING: {menu_path} not found")
        return 0

    data = json.loads(menu_path.read_text())
    out_dir = Path(hugo_dir) / "content/menu"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Track which files were written
    written = set()

    for cat in data.get("categories", []):
        cat_id = cat["id"]
        for item in cat.get("items", []):
            filename = f"{item['id']}.md"
            filepath = out_dir / filename

            fm = item_to_md(
                title=item["name"],
                description=item.get("description", ""),
                price=item.get("price"),
                tags=item.get("tags"),
                image=item.get("image", ""),
                available=item.get("available", True),
                menu_section=cat_id,
            )

            filepath.write_text(fm)
            written.add(filename)

    # Remove stale files (items deleted from CMS)
    for md_file in out_dir.glob("*.md"):
        if md_file.name not in written:
            md_file.unlink()
            print(f"  Removed stale: {md_file.name}")

    print(f"  Menu synced: {len(written)} items → {out_dir}")
    return len(written)


def sync_specials(hugo_dir: Path) -> int:
    """Sync specials.json → Hugo content/specials/*.md"""
    specials_path = CONTENT_DIR / "specials.json"
    if not specials_path.exists():
        print(f"  WARNING: {specials_path} not found")
        return 0

    data = json.loads(specials_path.read_text())
    out_dir = Path(hugo_dir) / "content/specials"
    out_dir.mkdir(parents=True, exist_ok=True)

    written = set()

    for special in data.get("active", []) + data.get("seasonal", []):
        if not special.get("available", True):
            continue
        filename = f"{special['id']}.md"
        filepath = out_dir / filename

        fm = item_to_md(
            title=special.get("title", ""),
            description=special.get("description", ""),
            price=special.get("price"),
            tags=[],  # specials don't use tags field in this design
            image=special.get("image", ""),
            available=True,
            frontmatter={
                "category": special.get("category", ""),
                "days": special.get("days", []),
                "note": special.get("note", ""),
                "type": "active" if special in data.get("active", []) else "seasonal",
            },
        )

        filepath.write_text(fm)
        written.add(filename)

    for md_file in out_dir.glob("*.md"):
        if md_file.name not in written:
            md_file.unlink()
            print(f"  Removed stale: {md_file.name}")

    print(f"  Specials synced: {len(written)} items → {out_dir}")
    return len(written)


def sync_all(hugo_dir: Path) -> dict:
    """Run full sync of all content types."""
    print(f"\nSyncing CMS content → Hugo content")
    print(f"  CMS content: {CONTENT_DIR}")
    print(f"  Hugo dir:   {hugo_dir}")

    menu_count = sync_menu(hugo_dir)
    specials_count = sync_specials(hugo_dir)

    result = {"ok": True, "menu_items": menu_count, "specials": specials_count}
    print(f"\nSync complete: {menu_count} menu items, {specials_count} specials")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync CMS JSON → Hugo Markdown content")
    # hugo_dir is always derived from this script's location within the repo
    # No CLI override needed — paths are relative to the script
    args = parser.parse_args()

    result = sync_all(str(PROJECT_ROOT / "site/hugo"))
    sys.exit(0 if result["ok"] else 1)
