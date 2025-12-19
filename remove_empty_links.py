import argparse
import os
import re


def remove_empty_links(file_path):
    """
    Processes a Markdown file to remove links to non-existent files.

    This function reads a Markdown file, finds all "wiki-style" links of the
    form [[link_text]], and checks if a corresponding Markdown file
    (link_text.md) exists in the same directory. If the linked file does not
    exist, it replaces the link [[link_text]] with just the link_text.

    Args:
        file_path (str): The path to the Markdown file to process.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found at {file_path}")
        return

    file_path = os.path.abspath(file_path)
    directory = os.path.dirname(file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    pattern = r'\[\[(.*?)\]\]'
    matches = re.findall(pattern, content)

    modified_content = content
    for file_name_in_brackets in matches:
        file_to_check = file_name_in_brackets.split('|')[0]

        if file_to_check.lower().endswith('.md'):
            potential_file_path = os.path.join(directory, file_to_check)
        else:
            potential_file_path = os.path.join(directory, f"{file_to_check}.md")

        if not os.path.exists(potential_file_path):
            print(f"'{potential_file_path}' does not exist. Removing link brackets for '[[{file_name_in_brackets}]]'")
            modified_content = modified_content.replace(f"[[{file_name_in_brackets}]]", file_name_in_brackets)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
    except Exception as e:
        print(f"Error writing to file: {e}")
        return

    print(f"Processing complete for {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove empty wiki-style links from a Markdown file."
    )
    parser.add_argument(
        "file",
        type=str,
        help="The path to the .md file to process."
    )
    args = parser.parse_args()

    remove_empty_links(args.file)
