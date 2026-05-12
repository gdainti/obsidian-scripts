import argparse
import re
from pathlib import Path

def remove_frontmatter_key(file_path: Path, key: str) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return False

        parts = content.split("---", 2)
        if len(parts) < 3:
            return False

        frontmatter = parts[1]
        body = parts[2]

        # This regex finds the key and any indented lines (the 'block')
        # Matches 'key:', any text on that line, and any following lines starting with spaces
        pattern = re.compile(
            fr"^(\s*){re.escape(key)}:[^\n]*(?:\n\s+.*)*", 
            re.MULTILINE
        )

        if not pattern.search(frontmatter):
            return False

        new_frontmatter = pattern.sub("", frontmatter)
        
        # Prevent file rewrite if nothing actually changed
        if new_frontmatter == frontmatter:
            return False

        new_content = f"---{new_frontmatter}---{body}"
        file_path.write_text(new_content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"Error in {file_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="Folder to process")
    parser.add_argument("key", help="Key to remove")
    args = parser.parse_args()

    # Use resolve() to handle any path formatting issues
    folder_path = Path(args.folder).expanduser().resolve()
    
    print(f"Checking folder: {folder_path}")
    
    count = 0
    # rglob("*.md") looks for all markdown files in this folder and subfolders
    for file_path in folder_path.rglob("*.md"):
        if remove_frontmatter_key(file_path, args.key):
            print(f"  Modified: {file_path.name}")
            count += 1

    print(f"Done. Files modified: {count}")

if __name__ == "__main__":
    main()