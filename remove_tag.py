import argparse
import os
import re

def remove_tag_from_file(file_path, tag):
    """
    Removes a specific tag from a Markdown file.
    It handles tags in YAML frontmatter (with or without #) and in the body (requires #).

    Args:
        file_path (str): The path to the Markdown file to process.
        tag (str): The tag to remove (without the '#').

    Returns:
        bool: True if the file was modified, False otherwise.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found at {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    modified_content = ""
    total_replacements = 0

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            frontmatter = parts[1]
            body = "---".join(parts[2:])

            # yaml - meta area, both <#tag> and <tag>
            fm_pattern = r'^\s*-\s*["\']?#?' + re.escape(tag) + r'["\']?\s*$'
            new_frontmatter, count = re.subn(fm_pattern, '', frontmatter, flags=re.MULTILINE | re.IGNORECASE)
            total_replacements += count
            if count > 0:
                new_frontmatter = re.sub(r'\n\s*\n', '\n', new_frontmatter)

            # body: only remove tags with #
            body_pattern = r'(?i)(^|\s)#' + re.escape(tag) + r'\b'
            new_body, count = re.subn(body_pattern, r'\1', body)
            total_replacements += count

            modified_content = f"---{new_frontmatter}---{new_body}"
        else:
            body_pattern = r'(?i)(^|\s)#' + re.escape(tag) + r'\b'
            modified_content, total_replacements = re.subn(body_pattern, r'\1', content)
    else: # no meta
        body_pattern = r'(?i)(^|\s)#' + re.escape(tag) + r'\b'
        modified_content, total_replacements = re.subn(body_pattern, r'\1', content)

    if total_replacements > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False
        print(f"Removed {total_replacements} instance(s) of '{tag}' from {os.path.basename(file_path)}")
        return True

    return False


def remove_tag_in_folder(folder_path, tag):
    """
    Processes all Markdown files in a folder to remove a specific tag.

    Args:
        folder_path (str): The path to the folder containing .md files.
        tag (str): The tag to remove (without the '#').
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found at {folder_path}")
        return

    md_files_found = 0
    files_modified = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                md_files_found += 1
                file_path = os.path.join(root, file)
                if remove_tag_from_file(file_path, tag):
                    files_modified += 1

    print(f"\nScan complete.")
    print(f"Looked at {md_files_found} Markdown files.")
    print(f"Removed tag '#{tag}' from {files_modified} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove a specific tag from all Markdown files in a folder."
    )
    parser.add_argument(
        "folder",
        type=str,
        help="The path to the folder to process."
    )
    parser.add_argument(
        "tag",
        type=str,
        help="The tag to remove (e.g., 'daily' for '#daily')."
    )
    args = parser.parse_args()

    remove_tag_in_folder(args.folder, args.tag)

