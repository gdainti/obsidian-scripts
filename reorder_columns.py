#!/usr/bin/env python3
"""
Script to reorder columns in markdown tables while preserving frontmatter.
Usage: python3 reorder_columns.py <file.md> <column_order>
Example: python3 reorder_columns.py daily.md "2,0,1" # Move 3rd column to 1st position
"""

import sys
import argparse
import re


def parse_frontmatter(lines):
    """
    Extract frontmatter (--- ... ---) from the beginning of the file.
    Returns (frontmatter_lines, remaining_lines)
    """
    if not lines or not lines[0].strip().startswith('---'):
        return [], lines

    frontmatter = [lines[0]]
    for i, line in enumerate(lines[1:], start=1):
        frontmatter.append(line)
        if line.strip().startswith('---'):
            return frontmatter, lines[i+1:]

    return [], lines


def is_table_separator(line):
    """Check if line is a table separator (e.g., | --- | --- |)"""
    stripped = line.strip()
    if not stripped.startswith('|') or not stripped.endswith('|'):
        return False

    parts = [p.strip() for p in stripped.split('|')[1:-1]]
    return all(re.match(r'^:?-+:?$', p) for p in parts if p)


def parse_table_row(line):
    """Parse a table row into columns by splitting on ' | ' delimiter"""
    original = line.rstrip('\n\r')

    if '|' not in original:
        return None, None

    stripped = original.strip()
    if not stripped.startswith('|') or not stripped.endswith('|'):
        return None, None

    parts = original.split('|')

    if parts and parts[0].strip() == '':
        parts = parts[1:]
    if parts and parts[-1].strip() == '':
        parts = parts[:-1]

    if not parts:
        return None, None

    return parts, original
def format_table_row(columns, original_line):
    """Format columns back into a table row, preserving format"""
    return '|' + '|'.join(columns) + '|'


def reorder_columns(columns, order):
    """Reorder columns based on the given order (list of indices)"""
    try:
        return [columns[i] for i in order]
    except IndexError as e:
        raise ValueError(f"Invalid column index in order: {e}")


def process_table(table_lines, order):
    """Process and reorder columns in a table"""
    if not table_lines:
        return table_lines

    result = []
    for line in table_lines:
        columns, original = parse_table_row(line)
        if columns is None:
            result.append(line)
            continue

        if len(columns) != len(order):
            raise ValueError(
                f"Column count mismatch: table has {len(columns)} columns, "
                f"but order specifies {len(order)} columns"
            )

        reordered = reorder_columns(columns, order)
        result.append(format_table_row(reordered, original) + '\n')

    return result


def find_and_process_tables(lines, order):
    """Find all tables in the content and reorder their columns"""
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        columns, _ = parse_table_row(line)
        if columns is None:
            result.append(line)
            i += 1
            continue

        table_lines = []
        while i < len(lines):
            current_columns, _ = parse_table_row(lines[i])
            if current_columns is None:
                break
            table_lines.append(lines[i])
            i += 1

        processed_table = process_table(table_lines, order)
        result.extend(processed_table)

    return result


def parse_column_order(order_str):
    """Parse column order from string like '2,0,1' or '1 3 2 0'"""
    order_str = order_str.replace(',', ' ')
    try:
        order = [int(x) for x in order_str.split()]

        if sorted(order) != list(range(len(order))):
            raise ValueError(
                "Column order must be a permutation of column indices starting from 0"
            )

        return order
    except ValueError as e:
        raise ValueError(f"Invalid column order format: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Reorder columns in markdown tables while preserving frontmatter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Swap first two columns (assumes 3 columns total)
  python3 reorder_columns.py daily.md "1,0,2"

  # Move last column to first position (4 columns)
  python3 reorder_columns.py daily.md "3,0,1,2"

  # Reverse 3 columns
  python3 reorder_columns.py daily.md "2,1,0"
        """
    )
    parser.add_argument('file', help='Markdown file to process')
    parser.add_argument(
        'order',
        help='New column order as comma or space-separated indices (0-based), e.g., "2,0,1" or "1 0 2"'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: modify file in place)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Print result without modifying file'
    )

    args = parser.parse_args()

    try:
        order = parse_column_order(args.order)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    frontmatter, content = parse_frontmatter(lines)

    try:
        processed_content = find_and_process_tables(content, order)
    except ValueError as e:
        print(f"Error processing table: {e}", file=sys.stderr)
        return 1

    result = frontmatter + processed_content

    if args.dry_run:
        print(''.join(result))
    else:
        output_file = args.output or args.file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(result)
            print(f"Successfully reordered columns in {output_file}")
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
