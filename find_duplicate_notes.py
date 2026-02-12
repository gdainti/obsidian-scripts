import argparse
import os
import hashlib
from collections import defaultdict

def get_content_hash(file_path, include_empty=False):
    """
    Reads a markdown file, strips YAML frontmatter, and returns the hash of the content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        content_lines = lines
        if lines and lines[0].strip() == '---':
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    content_lines = lines[i+1:]
                    break

        content = "".join(content_lines).strip()
        if not content and not include_empty:
            return None

        return hashlib.md5(content.encode('utf-8')).hexdigest()

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def find_duplicates(folder_path, include_empty=False):
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found at {folder_path}")
        return

    print(f"Scanning '{folder_path}' for duplicate Markdown files (ignoring frontmatter)...")
    if not include_empty:
        print("Ignoring empty files (or files with only frontmatter).")

    hashes = defaultdict(list)
    count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.md'):
                file_path = os.path.join(root, file)
                file_hash = get_content_hash(file_path, include_empty)
                if file_hash:
                    hashes[file_hash].append(file_path)
                count += 1

    print(f"Processed {count} files.\n")

    duplicates_found = 0
    for file_hash, paths in hashes.items():
        if len(paths) > 1:
            duplicates_found += 1
            print(f"Duplicate content found in {len(paths)} files:")
            for path in paths:
                print(f"  - {path}")
            print("")

    if duplicates_found == 0:
        print("No duplicates found.")
    else:
        print(f"Found {duplicates_found} sets of duplicates.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find duplicate Markdown files in a folder, ignoring YAML frontmatter."
    )
    parser.add_argument("folder", type=str, help="The path to the folder to scan.")
    parser.add_argument("--include-empty", action="store_true", help="Include empty files (or files with only frontmatter) in the search.")
    args = parser.parse_args()

    find_duplicates(args.folder, args.include_empty)