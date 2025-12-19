#!/usr/bin/env python3
"""
Script to split a markdown file with a table by year based on the date column.
Copies the metadata header (---) to all split files.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    """
    Parse date string and extract the year.
    Handles formats like:
    - "November 29, 2024"
    - "December 30, 2024 → December 31, 2024" (takes first date)
    Returns year or None if parsing fails.
    """
    if not date_str or date_str.strip() == '':
        return None

    if '→' in date_str:
        date_str = date_str.split('→')[0].strip()

    try:
        date_obj = datetime.strptime(date_str.strip(), "%B %d, %Y")
        return date_obj.year
    except ValueError:
        return None


def split_markdown_by_year(input_file):
    """
    Split a markdown file by year based on date column in table.
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File '{input_file}' not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    metadata_lines = []
    content_start = 0
    in_metadata = False
    metadata_end = 0

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_metadata:
                in_metadata = True
                metadata_lines.append(line)
            else:
                metadata_lines.append(line)
                metadata_end = i + 1
                break
        elif in_metadata:
            metadata_lines.append(line)

    content_start = metadata_end if metadata_end > 0 else 0

    table_header = None
    table_separator = None
    table_start = None

    for i in range(content_start, len(lines)):
        line = lines[i]
        if '|' in line and 'Name' in line and 'date' in line:
            table_header = line
            table_start = i
            if i + 1 < len(lines):
                table_separator = lines[i + 1]
            break

    if not table_header:
        print("Error: Could not find table header with 'Name' and 'date' columns.")
        return

    rows_by_year = defaultdict(list)

    for i in range(table_start + 2, len(lines)):
        line = lines[i]

        if not line.strip() or not line.strip().startswith('|'):
            continue

        columns = [col.strip() for col in line.split('|')]

        if len(columns) < 3:
            continue

        date_column = columns[2] if len(columns) > 2 else ''

        year = parse_date(date_column)

        if year:
            rows_by_year[year].append(line)
        else:
            rows_by_year['unknown'].append(line)

    output_dir = input_path.parent
    base_name = input_path.stem

    sorted_years = sorted([y for y in rows_by_year.keys() if y != 'unknown'])

    if 'unknown' in rows_by_year:
        sorted_years.append('unknown')

    for year in sorted_years:
        rows = rows_by_year[year]
        if year == 'unknown':
            output_file = output_dir / f"{base_name}_unknown_dates.md"
        else:
            output_file = output_dir / f"{base_name}_{year}.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            if metadata_lines:
                f.writelines(metadata_lines)
                f.write('\n')

            f.write(table_header)
            f.write(table_separator)

            for row in rows:
                f.write(row)

        print(f"Created: {output_file} ({len(rows)} rows)")

    print(f"\nTotal years: {len([y for y in rows_by_year.keys() if y != 'unknown'])}")
    if 'unknown' in rows_by_year:
        print(f"Rows with unknown dates: {len(rows_by_year['unknown'])}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 split_by_year.py <markdown_file>")
        sys.exit(1)

    split_markdown_by_year(sys.argv[1])
