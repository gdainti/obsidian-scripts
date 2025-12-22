import argparse
import os
import re
from pathlib import Path

def rename_frontmatter_key(file_path: Path, old_key: str, new_key: str) -> bool:
    """
    Renames a key in the YAML frontmatter of a markdown file.

    Args:
        file_path: The path to the markdown file.
        old_key: The old frontmatter key name.
        new_key: The new frontmatter key name.

    Returns:
        True if the file was modified, False otherwise.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return False

        parts = content.split("---", 2)
        if len(parts) < 3:
            return False

        frontmatter_content = parts[1]
        body_content = parts[2]

        key_regex = re.compile(fr"^(\s*){re.escape(old_key)}:", re.MULTILINE)

        if not key_regex.search(frontmatter_content):
            return False

        new_frontmatter_content = key_regex.sub(fr"\1{new_key}:", frontmatter_content)

        if new_frontmatter_content == frontmatter_content:
            return False

        new_content = f"---{new_frontmatter_content}---{body_content}"

        file_path.write_text(new_content, encoding="utf-8")

        return True

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False

def main():
    """
    Main function to parse arguments and process files.
    """
    parser = argparse.ArgumentParser(
        description="Rename a key in the YAML frontmatter of markdown files."
    )
    parser.add_argument("folder", help="The folder containing markdown files to process.")
    parser.add_argument("old_name", help="The old frontmatter key name.")
    parser.add_argument("new_name", help="The new frontmatter key name.")

    args = parser.parse_args()

    folder_path = Path(args.folder)
    if not folder_path.is_dir():
        print(f"Error: Folder not found at {args.folder}")
        return

    affected_files = 0
    print("Modifying files...")
    for file_path in folder_path.rglob("*.md"):
        if rename_frontmatter_key(file_path, args.old_name, args.new_name):
            print(f"  - {file_path}")
            affected_files += 1

    print(f"\nFinished. Affected files: {affected_files}")

if __name__ == "__main__":
    main()
