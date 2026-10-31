#!/usr/bin/env python3
"""Validate every article under articles/.

Checks (errors fail the build):
  - YAML front matter exists and parses
  - required fields: title, category, period, related (list), sources (list)
  - category matches the folder the file lives in
  - slug (filename) is lowercase-hyphenated and unique across categories
  - at least 2 sources, all http(s) URLs, none from banned domains
  - every slug in `related` is an existing article
  - body has a "## Sources" section
  - body word count (excluding the Sources section) is 400-900
  - every relative Markdown link resolves to an existing file

Usage: python3 scripts/lint_articles.py [--root .]
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

CATEGORIES = {"movements", "artists", "works", "techniques", "themes"}
REQUIRED = ["title", "category", "period", "related", "sources"]
BANNED_DOMAINS = ("wikipedia.org", "wikiwand.com", "fandom.com")
MIN_WORDS, MAX_WORDS = 400, 900
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)


def split_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return None, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def word_count(body):
    main = re.split(r"^##\s+Sources\s*$", body, maxsplit=1, flags=re.M | re.I)[0]
    main = re.sub(r"```.*?```", " ", main, flags=re.S)
    main = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", main)
    return len(re.findall(r"[A-Za-z0-9À-￿'’-]+", main))


def lint(root: Path):
    articles_dir = root / "articles"
    files = sorted(p for p in articles_dir.rglob("*.md"))
    slugs = {}
    for p in files:
        slugs.setdefault(p.stem, []).append(p)

    errors, warnings = [], []
    for p in files:
        rel = p.relative_to(root)
        def err(msg):
            errors.append(f"{rel}: {msg}")

        folder = p.parent.name
        if folder not in CATEGORIES:
            err(f"folder '{folder}' is not one of {sorted(CATEGORIES)}")
        if not SLUG_RE.match(p.stem):
            err("filename must be lowercase-hyphenated (e.g. artemisia-gentileschi.md)")
        if len(slugs[p.stem]) > 1:
            err(f"duplicate slug also used by {[str(x.relative_to(root)) for x in slugs[p.stem] if x != p]}")

        try:
            fm, body = split_front_matter(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            err(f"front matter is not valid YAML: {e}")
            continue
        if fm is None:
            err("missing YAML front matter (--- ... --- at top of file)")
            continue

        for key in REQUIRED:
            if key not in fm or fm[key] in (None, ""):
                err(f"front matter missing '{key}'")
        if fm.get("category") and fm["category"] != folder:
            err(f"category '{fm['category']}' does not match folder '{folder}'")

        related = fm.get("related") or []
        if not isinstance(related, list):
            err("'related' must be a list of slugs")
            related = []
        for slug in related:
            if str(slug) not in slugs:
                err(f"related slug '{slug}' is not an existing article")

        sources = fm.get("sources") or []
        if not isinstance(sources, list):
            err("'sources' must be a list of URLs")
            sources = []
        if len(sources) < 2:
            err(f"needs at least 2 sources (found {len(sources)})")
        for url in sources:
            u = str(url)
            if not u.startswith(("http://", "https://")):
                err(f"source is not an http(s) URL: {u}")
            if any(d in u for d in BANNED_DOMAINS):
                err(f"banned source domain: {u}")

        if not re.search(r"^##\s+Sources\s*$", body, flags=re.M | re.I):
            err("missing '## Sources' section")

        wc = word_count(body)
        if not MIN_WORDS <= wc <= MAX_WORDS:
            err(f"body is {wc} words; must be {MIN_WORDS}-{MAX_WORDS} (Sources section excluded)")

        for target in LINK_RE.findall(body):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if path and not (p.parent / path).resolve().exists():
                err(f"broken relative link: {target}")

    return files, errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    files, errors, warnings = lint(Path(args.root))
    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")
    print(f"Checked {len(files)} article(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
