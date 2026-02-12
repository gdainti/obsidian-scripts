import argparse
import os
import fnmatch

def search_files(folder_path, pattern):
    """
    Searches for files in a folder based on a name pattern.
    Supports simple substring matching and wildcard (*, ?) matching.

    Args:
        folder_path (str): Path to the folder to search.
        pattern (str): Substring or wildcard pattern to match against filenames.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found at {folder_path}")
        return

    use_wildcard = '*' in pattern or '?' in pattern

    matches = []

    print(f"Searching in: {folder_path}")
    print(f"Pattern: {pattern} ({'Wildcard' if use_wildcard else 'Substring'} mode)")

    for root, _, files in os.walk(folder_path):
        for filename in files:
            if use_wildcard:
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(root, filename))
            else:
                if pattern.lower() in filename.lower():
                    matches.append(os.path.join(root, filename))

    print(f"\nFound {len(matches)} matching files:")
    for match in matches:
        print(f"- {match}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search for files by name using a substring or wildcard pattern.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Search for files containing "notes" in the name (substring match)
  python find_files.py ./my_vault notes

  # Search for all markdown files (wildcard match)
  python find_files.py ./my_vault *.md

  # Search for files starting with "2024-"
  python find_files.py ./my_vault "2024-*"

  # Search for patterns starting with '-' (use -- to separate flags)
  python find_files.py ./my_vault -- "-.md"
"""
    )
    parser.add_argument(
        "folder",
        type=str,
        help="The path to the folder to search."
    )
    parser.add_argument(
        "pattern",
        type=str,
        nargs='?',
        help="The filename pattern to search for (e.g., 'notes', '*.md', '2024-*')."
    )
    args = parser.parse_args()
    args, unknown = parser.parse_known_args()

    if args.pattern is None:
        if unknown:
            args.pattern = unknown.pop(0)
        else:
            parser.error("the following arguments are required: pattern")

    if unknown:
        parser.error(f"unrecognized arguments: {' '.join(unknown)}")

    search_files(args.folder, args.pattern)