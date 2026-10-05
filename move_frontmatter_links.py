#!/usr/bin/env python3
"""
Move frontmatter 'links' property contents to the beginning of the file body,
right after the frontmatter closing separator (---), avoiding duplicates.
"""

import argparse
import os
import re
import urllib.parse
from pathlib import Path


def normalize_target(target: str) -> str:
    """Extract and normalize the base note name from a link target."""
    # Strip any alias (|alias) or heading/block reference (#heading, ^block)
    t = target.split("|")[0].split("#")[0].strip()
    # Strip .md extension if present
    t = re.sub(r"\.md$", "", t, flags=re.IGNORECASE)
    # Take basename in case of paths (e.g. folder/note)
    t = os.path.basename(t)
    return t.strip().lower()


def link_exists_in_text(link: str, text: str) -> bool:
    """
    Check if a link (or a link to the same note) already exists in the given text.
    """
    if not link or not text:
        return False

    if link in text:
        return True

    # Check wikilink format [[target]]
    m_wiki = re.match(r"^\[\[(.*)\]\]$", link.strip())
    if m_wiki:
        target_norm = normalize_target(m_wiki.group(1))
        if not target_norm:
            return False

        # Match any existing wikilinks in text
        for bw in re.findall(r"\[\[(.*?)\]\]", text):
            if normalize_target(bw) == target_norm:
                return True

        # Match any existing markdown links in text [text](url)
        for md_url in re.findall(r"\[.*?\]\((.*?)\)", text):
            unquoted = urllib.parse.unquote(md_url)
            if normalize_target(unquoted) == target_norm:
                return True

        return False

    # Check markdown link format [label](url)
    m_md = re.match(r"^\[.*?\]\((.*?)\)$", link.strip())
    if m_md:
        target_norm = normalize_target(urllib.parse.unquote(m_md.group(1)))
        if not target_norm:
            return False

        for bw in re.findall(r"\[\[(.*?)\]\]", text):
            if normalize_target(bw) == target_norm:
                return True

        for md_url in re.findall(r"\[.*?\]\((.*?)\)", text):
            unquoted = urllib.parse.unquote(md_url)
            if normalize_target(unquoted) == target_norm:
                return True

        return False

    return False


def extract_links_from_block(block: str) -> list[str]:
    """
    Extract note links from the YAML frontmatter block for the links key.
    Handles Obsidian wikilinks: "[[note]]", '[[note]]', [[note]],
    lists, inline arrays, and plain note strings.
    """
    colon_idx = block.find(":")
    content = block[colon_idx + 1 :] if colon_idx != -1 else block

    raw_links = []
    lines = content.splitlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 1. Wikilinks [[...]]
        wikilinks = re.findall(r"\[\[.+?\]\]", line)
        if wikilinks:
            raw_links.extend(wikilinks)
            continue

        # 2. Markdown links [...](...)
        md_links = re.findall(r"\[.+?\]\(.+?\)", line)
        if md_links:
            raw_links.extend(md_links)
            continue

        # 3. YAML list item: - value
        m_item = re.match(r"^-\s*(.*)$", line)
        if m_item:
            val = m_item.group(1).strip()
            val = re.sub(r"\s+#.*$", "", val).strip()  # Strip comments
            val = val.strip("\"'")
            if val and val not in ("[]", "{}", "null", "~"):
                raw_links.append(f"[[{val}]]")
            continue

        # 4. Inline flow list: [a, b]
        if line.startswith("[") and line.endswith("]"):
            inner = line[1:-1].strip()
            if inner:
                items = [item.strip().strip("\"'") for item in inner.split(",")]
                for item in items:
                    if item and item not in ("null", "~"):
                        raw_links.append(f"[[{item}]]")
            continue

        # 5. Scalar value on the same line or indented
        val = re.sub(r"\s+#.*$", "", line).strip()
        val = val.strip("\"'")
        if val and val not in ("[]", "{}", "null", "~"):
            raw_links.append(f"[[{val}]]")

    # Deduplicate while preserving order
    seen = set()
    unique_links = []
    for l in raw_links:
        norm = normalize_target(l) if (l.startswith("[[") or l.startswith("[")) else l
        if norm not in seen:
            seen.add(norm)
            unique_links.append(l)

    return unique_links


def move_frontmatter_links(
    file_path: Path,
    key: str = "links",
    multiline: bool = False,
    dry_run: bool = False,
) -> tuple[bool, int]:
    """
    Moves links from the specified frontmatter key to right after the frontmatter
    separator (---) on a new line, without duplicating existing links in the file.

    Args:
        file_path: Path to the markdown file.
        key: Frontmatter property name (default: "links").
        multiline: If True, each link is placed on its own line; otherwise separated by space.
        dry_run: If True, preview without saving changes.

    Returns:
        tuple[bool, int]: (modified, num_links_moved)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return False, 0

        parts = content.split("---", 2)
        if len(parts) < 3:
            return False, 0

        frontmatter = parts[1]
        body = parts[2]

        # Pattern to match the key and all its indented or nested content
        pattern = re.compile(
            rf"^[ \t]*{re.escape(key)}:[^\n]*(?:\n(?:[ \t]+.*|[ \t]*))*?(?=\n\S|\Z)\n?",
            re.MULTILINE,
        )

        match = pattern.search(frontmatter)
        if not match:
            return False, 0

        block = match.group(0)
        links = extract_links_from_block(block)

        # Filter out links that already exist in the body
        links_to_add = []
        for link in links:
            if not link_exists_in_text(link, body):
                # Also ensure we don't duplicate within the new batch
                if not any(link_exists_in_text(link, added) for added in links_to_add):
                    links_to_add.append(link)

        # Remove the key block from frontmatter
        new_frontmatter = pattern.sub("", frontmatter)

        # Detect line endings
        nl = "\r\n" if "\r\n" in content else "\n"

        if new_frontmatter.strip():
            fm_block = f"---{nl}{new_frontmatter.strip()}{nl}---"
        else:
            fm_block = f"---{nl}---"

        if links_to_add:
            sep = nl if multiline else " "
            links_text = sep.join(links_to_add)
            body_clean = body.lstrip("\r\n")
            if body_clean:
                new_content = f"{fm_block}{nl}{links_text}{nl}{nl}{body_clean}"
            else:
                new_content = f"{fm_block}{nl}{links_text}{nl}"
        else:
            new_content = f"{fm_block}{body}"

        if new_content == content:
            return False, 0

        if not dry_run:
            file_path.write_text(new_content, encoding="utf-8")

        return True, len(links_to_add)

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return False, 0


def main():
    parser = argparse.ArgumentParser(
        description="Move frontmatter 'links' property contents to the note body after the '---' separator."
    )
    parser.add_argument("folder", help="Folder (or file) to process")
    parser.add_argument(
        "--key",
        default="links",
        help="Frontmatter property name to move (default: 'links')",
    )
    parser.add_argument(
        "--multiline",
        action="store_true",
        help="Place each link on its own line instead of space-separated on a single line",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    args = parser.parse_args()

    target_path = Path(args.folder).expanduser().resolve()
    if not target_path.exists():
        print(f"Error: Path not found at {args.folder}")
        return

    if target_path.is_file():
        files_to_process = [target_path]
    else:
        files_to_process = sorted(target_path.rglob("*.md"))

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"{prefix}Checking: {target_path}")

    modified_count = 0
    total_links_moved = 0

    for file_path in files_to_process:
        modified, count_moved = move_frontmatter_links(
            file_path,
            key=args.key,
            multiline=args.multiline,
            dry_run=args.dry_run,
        )
        if modified:
            modified_count += 1
            total_links_moved += count_moved
            print(f"  Modified: {file_path.name} (moved {count_moved} link(s))")

    print(f"\nDone. Files modified: {modified_count}, total links moved: {total_links_moved}")


if __name__ == "__main__":
    main()
