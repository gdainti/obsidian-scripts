import argparse
import os

def check_for_yaml_frontmatter(file_path):
    """
    Checks if a file starts with a YAML frontmatter block (--- ... ---).

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file has a YAML frontmatter, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.strip() != '---':
                return False
            for line in f:
                if line.strip() == '---':
                    return True
            return False
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

def process_folder(folder_path):
    """
    Processes all Markdown files in a folder to check for YAML frontmatter.

    Args:
        folder_path (str): The path to the folder containing .md files.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found at {folder_path}")
        return

    total_files = 0
    files_with_frontmatter = 0
    files_without_frontmatter = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                total_files += 1
                file_path = os.path.join(root, file)
                if check_for_yaml_frontmatter(file_path):
                    files_with_frontmatter += 1
                else:
                    files_without_frontmatter.append(file_path)

    print(f"Scan complete. Looked at {total_files} Markdown files.\n")
    print(f"Files with YAML frontmatter: {files_with_frontmatter}")
    print(f"Files without YAML frontmatter: {len(files_without_frontmatter)}")

    if files_without_frontmatter:
        print("\nFiles missing frontmatter:")
        for file_path in files_without_frontmatter:
            print(f"- {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check for YAML frontmatter in all Markdown files in a folder."
    )
    parser.add_argument(
        "folder",
        type=str,
        help="The path to the folder to process."
    )
    args = parser.parse_args()

    process_folder(args.folder)
