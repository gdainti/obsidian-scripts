
#!/usr/bin/env python3
"""
Reverse the order of rows in a markdown table while preserving frontmatter.
Usage: python reverse_table.py <file.md> [--no-header] [-o <output.md>]
"""

import sys
import re
import argparse


def reverse_markdown_table(content, keep_header=True):
    """
    Reverse the order of rows in markdown tables within the content.

    Args:
        content: The markdown content to process
        keep_header: If True, preserves the header row and separator line at the top.
                    If False, reverses all rows including the header.
    """
    lines = content.split('\n')
    result = []
    in_table = False
    table_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if '|' in line and line.strip():
            if not in_table:
                in_table = True
                table_lines = [line]
            else:
                table_lines.append(line)
        else:
            if in_table:
                processed_table = process_table(table_lines, keep_header)
                result.extend(processed_table)
                in_table = False
                table_lines = []
            result.append(line)

        i += 1

    if in_table and table_lines:
        processed_table = process_table(table_lines, keep_header)
        result.extend(processed_table)

    return '\n'.join(result)


def process_table(table_lines, keep_header=True):
    """
    Process a table by reversing its rows.

    Args:
        table_lines: List of table lines to process
        keep_header: If True, keeps the header (first row) and separator (second row) in place.
                    If False, reverses all rows including the header and separator.
    """
    if len(table_lines) <= 1:
        return table_lines

    if keep_header:
        if len(table_lines) <= 2:
            return table_lines

        header = table_lines[0]
        separator = table_lines[1]
        data_rows = table_lines[2:]

        data_rows.reverse()

        return [header, separator] + data_rows
    else:
        if len(table_lines) <= 2:
            reversed_lines = table_lines.copy()
            reversed_lines.reverse()
            return reversed_lines

        all_rows = table_lines.copy()
        all_rows.reverse()

        separator_idx = None
        for i, line in enumerate(all_rows):
            if '---' in line or ':-:' in line or ':--' in line or '--:' in line:
                separator_idx = i
                break

        if separator_idx is not None and separator_idx != 1:
            separator = all_rows.pop(separator_idx)
            all_rows.insert(1, separator)

        return all_rows


def main():
    parser = argparse.ArgumentParser(
        description='Reverse the order of rows in markdown tables.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Reverse table rows, keeping header at top (default)
  python reverse_table.py input.md

  # Reverse all rows including header
  python reverse_table.py input.md --no-header

  # Save to a different file
  python reverse_table.py input.md -o output.md
        """
    )

    parser.add_argument('input_file', help='Input markdown file to process')
    parser.add_argument('-o', '--output', dest='output_file',
                       help='Output file (default: modify input file in place)')
    parser.add_argument('--no-header', action='store_true',
                       help='Reverse all rows including header (default: keep header at top)')

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file if args.output_file else input_file
    keep_header = not args.no_header  # by default keep header

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        modified_content = reverse_markdown_table(content, keep_header)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        if input_file == output_file:
            header_msg = "with header preserved" if keep_header else "including header"
            print(f"✓ Table rows reversed {header_msg} in {input_file}")
        else:
            header_msg = "with header preserved" if keep_header else "including header"
            print(f"✓ Table rows reversed {header_msg} and saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
