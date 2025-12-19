#!/usr/bin/env python3
"""
Script to convert date formats in markdown files to a specified format.
Handles:
- "December 30, 2024" (Month Day, Year)
- "30.12.2024" (Day.Month.Year)

Output formats:
- YYYY-MM-DD (e.g., 2024-12-30)
- DD.MM.YYYY (e.g., 30.12.2024)
- DD.MM (e.g., 30.12)
- MM-DD (e.g., 12-30)
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def convert_date_format(content, output_format="%Y-%m-%d", input_formats=None):
    """
    Convert dates in content from various formats to specified output format.

    Args:
        content: The text content to process
        output_format: strftime format string or shorthand (YYYY-MM-DD, DD.MM.YYYY, DD.MM, MM-DD)
        input_formats: List of input formats to detect, or None to detect all. Options:
                      'month-day-year', 'DD.MM.YYYY', 'YYYY-MM-DD', 'MM-DD-YYYY', 'all'
    """

    format_map = {
        "YYYY-MM-DD": "%Y-%m-%d",
        "DD.MM.YYYY": "%d.%m.%Y",
        "DD.MM": "%d.%m",
        "MM-DD": "%m-%d",
        "YYYY-MM": "%Y-%m",
        "MM.DD": "%m.%d",
    }

    strftime_format = format_map.get(output_format, output_format)

    if input_formats is None or 'all' in input_formats:
        input_formats = ['month-day-year', 'DD.MM.YYYY', 'YYYY-MM-DD', 'MM-DD-YYYY']

    def replace_month_day_year(match):
        """Convert 'Month Day, Year' to specified format"""
        date_str = match.group(0)
        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
            return date_obj.strftime(strftime_format)
        except ValueError:
            return date_str

    def replace_day_month_year_dots(match):
        """Convert 'DD.MM.YYYY' to specified format"""
        day, month, year = match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime(strftime_format)
        except ValueError:
            return match.group(0)

    def replace_iso_date(match):
        """Convert 'YYYY-MM-DD' to specified format"""
        year, month, day = match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime(strftime_format)
        except ValueError:
            return match.group(0)

    def replace_mm_dd_yyyy(match):
        """Convert 'MM-DD-YYYY' to specified format"""
        month, day, year = match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime(strftime_format)
        except ValueError:
            return match.group(0)

    if 'month-day-year' in input_formats:
        # "December 30, 2024"
        month_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b'
        content = re.sub(month_pattern, replace_month_day_year, content)

    if 'DD.MM.YYYY' in input_formats:
        # "30.12.2024"
        dot_pattern = r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b'
        content = re.sub(dot_pattern, replace_day_month_year_dots, content)

    if 'YYYY-MM-DD' in input_formats:
        # "2024-12-30"
        iso_pattern = r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b'
        content = re.sub(iso_pattern, replace_iso_date, content)

    if 'MM-DD-YYYY' in input_formats:
        # "12-30-2024"
        us_pattern = r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b'
        content = re.sub(us_pattern, replace_mm_dd_yyyy, content)

    return content


def process_markdown_file(input_file, output_file=None, output_format="%Y-%m-%d", input_formats=None):
    """
    Process a markdown file and convert date formats.
    If output_file is not specified, overwrites the input file.

    Args:
        input_file: Path to the input markdown file
        output_file: Optional path to save the result
        output_format: Date format string (e.g., 'YYYY-MM-DD', 'DD.MM', '%Y-%m-%d')
        input_formats: List of input formats to detect, or None to detect all
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File '{input_file}' not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    converted_content = convert_date_format(content, output_format, input_formats)

    if output_file is None:
        output_path = input_path
    else:
        output_path = Path(output_file)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(converted_content)

    print(f"Date formats converted successfully!")
    print(f"Output written to: {output_path}")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("""Usage: python convert_date_format.py <input_file> [options]

Options:
  -o, --output <file>     Output file (default: overwrite input)
  -f, --format <format>   Output format (default: YYYY-MM-DD)
  -i, --input <format>    Input format to detect (default: all)

Output Formats: YYYY-MM-DD, DD.MM.YYYY, DD.MM, MM-DD, YYYY-MM, MM.DD, or strftime codes.
Input Formats: month-day-year, DD.M.YYYY, YYYY-MM-DD, MM-DD-YYYY, or 'all'.

Examples:
  python convert_date_format.py notes.md
  python convert_date_format.py notes.md -f DD.MM.YYYY
  python convert_date_format.py notes.md -i DD.MM.YYYY -o output.md
""")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    output_format = "YYYY-MM-DD"
    input_formats = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                print("Error: -o/--output requires a file path")
                sys.exit(1)
        elif arg in ['-f', '--format']:
            if i + 1 < len(sys.argv):
                output_format = sys.argv[i + 1]
                i += 2
            else:
                print("Error: -f/--format requires a format string")
                sys.exit(1)
        elif arg in ['-i', '--input']:
            if i + 1 < len(sys.argv):
                if input_formats is None:
                    input_formats = []
                input_formats.append(sys.argv[i + 1])
                i += 2
            else:
                print("Error: -i/--input requires a format string")
                sys.exit(1)
        else:
            if arg.endswith('.md') or '/' in arg or '\\' in arg:
                output_file = arg
            else:
                output_format = arg
            i += 1

    process_markdown_file(input_file, output_file, output_format, input_formats)


if __name__ == "__main__":
    main()
