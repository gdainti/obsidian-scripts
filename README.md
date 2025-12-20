# Obsidian Scripts

A collection of Python scripts to automate common tasks for managing Obsidian notes.

## Scripts

### Convert Date Format (`convert_date_format.py`)

Converts various date formats found in your notes to a consistent format.

**Usage:**
```bash
python convert_date_format.py <file.md> [options]
```
*   Use `-f <format>` to specify the output format (e.g., `YYYY-MM-DD`).
*   Run with `-h` for more options.

### Remove Empty Links (`remove_empty_links.py`)

Removes `[[wiki-style]]` link brackets if the linked note does not exist, leaving just the text.

**Usage:**
```bash
python remove_empty_links.py <file.md>
```

### Remove Tag (`remove_tag.py`)

Removes a specified tag from all markdown files in a given folder. It handles tags in YAML frontmatter (e.g., `daily`, `#daily`, `"#daily"`) and in the body of the text (e.g., `#daily`).

**Usage:**
```bash
python remove_tag.py <folder_path> <tag_name>
```

**Example:**
```bash
python remove_tag.py "~/notes" daily
```
This command will remove all instances of the `daily` tag from markdown files in the `~/notes` directory.

### Reorder Table Columns (`reorder_columns.py`)

Reorders columns in a Markdown table.

**Usage:**
```bash
python reorder_columns.py <file.md> "2,0,1"
```
*   The second argument is the new, 0-indexed column order.

### Replace Markdown Links (`replace_md_links.py`)

Replaces `[[note]]` links with the content of the linked `note.md` file.

**Usage:**
```bash
python replace_md_links.py <file.md>
```

### Reverse Table (`reverse_table.py`)

Reverses the order of rows in a Markdown table.

**Usage:**
```bash
python reverse_table.py <file.md>
```
*   Use `--no-header` to include the header row in the reversal.

### Split by Year (`split_by_year.py`)

Splits a markdown file containing a table into separate files for each year, based on a date column.

**Usage:**
```bash
python split_by_year.py <file.md>
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.