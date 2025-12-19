#!/usr/bin/env python3
"""
Script to replace [[file name]] patterns with actual content from file name.md files.
Usage: python replace_md_links.py <file_path>
"""

import sys
import re
import os
from pathlib import Path

def read_file_content(file_path):
    """Read and return the content of a file, skipping frontmatter between --- --- blocks."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            lines = content.split('\n')
            closing_index = -1

            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    closing_index = i
                    break

            if closing_index != -1:
                content = '\n'.join(lines[closing_index + 1:]).lstrip('\n')

        return content
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return None


def convert_newlines_preserve_codeblocks(content):
    """
    Convert newlines to <br> tags, but convert code blocks (```...```) to HTML <pre><code>
    to preserve formatting inside table cells
    """
    result = []
    in_codeblock = False
    codeblock_language = ''
    codeblock_lines = []
    lines = content.split('\n')

    for line in lines:
        if line.strip().startswith('```'):
            if not in_codeblock:
                in_codeblock = True
                codeblock_language = line.strip()[3:].strip()
                codeblock_lines = []
            else:
                # &#10; instead of actual newlines to keep it in one table cell
                in_codeblock = False
                code_content = '&#10;'.join(codeblock_lines)
                if codeblock_language:
                    result.append(f'<pre><code class="language-{codeblock_language}">{code_content}</code></pre>')
                else:
                    result.append(f'<pre><code>{code_content}</code></pre>')
        elif in_codeblock:
            codeblock_lines.append(line)
        else:
            result.append(line)

    return '<br>'.join(result)


def replace_links_with_content(file_path):
    """
    Find all [[file name]] patterns and replace them with the content of file name.md
    """
    content = read_file_content(file_path)
    if content is None:
        return False

    file_dir = os.path.dirname(os.path.abspath(file_path))

    pattern = r'\[\[([^\]]+)\]\]'

    def replace_match(match):
        file_name = match.group(1).strip()

        if '\\|' in file_name:
            file_name = file_name.split('\\|')[0].strip()
        elif '|' in file_name:
            file_name = file_name.split('|')[0].strip()

        if not file_name.endswith('.md'):
            file_name += '.md'

        referenced_file = os.path.join(file_dir, file_name)

        referenced_content = read_file_content(referenced_file)

        if referenced_content is not None:
            return convert_newlines_preserve_codeblocks(referenced_content.strip())
        else:
            return match.group(0)

    new_content = re.sub(pattern, replace_match, content)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully processed: {file_path}")
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python replace_md_links.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File does not exist: {file_path}", file=sys.stderr)
        sys.exit(1)

    success = replace_links_with_content(file_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
