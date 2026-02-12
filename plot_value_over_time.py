
import argparse
import os
import re
import statistics
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def extract_frontmatter(file_path, property_name='v'):
    """
    Extracts 'date' and a specified numerical property from the YAML frontmatter
    of a markdown file using regex, avoiding a full YAML parser.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None
            frontmatter_str = parts[1]

            date_match = re.search(r'^\s*date:\s*(.*)\s*$', frontmatter_str, re.MULTILINE)
            if not date_match:
                date_match = re.search(r'^\s*created:\s*(.*)\s*$', frontmatter_str, re.MULTILINE)

            prop_match = re.search(fr'^\s*{re.escape(property_name)}:\s*"?([0-9.]+)"?\s*$', frontmatter_str, re.MULTILINE)

            if date_match and prop_match:
                date_str = date_match.group(1).strip()
                prop_str = prop_match.group(1).strip()
                return {'date': date_str, property_name: prop_str}

    except Exception as e:
        print(f"Error reading or parsing frontmatter from {file_path}: {e}")
    return None

def save_matplotlib_plot(data, property_name='v'):
    """Generates and saves a matplotlib plot."""
    if not data:
        print("No data to plot.")
        return

    dates = [d['date'] for d in data]
    values = [d['v'] for d in data]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(dates, values, marker='o', linestyle='-')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    ax.set_title(f"Plot of '{property_name}' Value Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel(property_name)
    ax.grid(True)

    min_val = min(values)
    max_val = max(values)
    min_date = dates[values.index(min_val)]
    max_date = dates[values.index(max_val)]

    ax.annotate(f'Low: {min_val:.2f}', xy=(min_date, min_val), xytext=(-20, -30),
                textcoords='offset points', arrowprops=dict(arrowstyle="->"))
    ax.annotate(f'High: {max_val:.2f}', xy=(max_date, max_val), xytext=(-20, 30),
                textcoords='offset points', arrowprops=dict(arrowstyle="->"))


    output_dir = 'plot'
    os.makedirs(output_dir, exist_ok=True)
    plot_filename = os.path.join(output_dir, 'plot.png')
    plt.savefig(plot_filename)
    print(f"\n--- Plot saved to {plot_filename} ---")


def plot_value_over_time(folder_path, property_name='v'):
    """
    Scans a folder for markdown files, extracts a numerical property and date
    from the frontmatter, and generates a plot and statistics.
    """
    data = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file
                frontmatter = extract_frontmatter(file_path, property_name)
                if frontmatter and property_name in frontmatter and 'date' in frontmatter:
                    try:
                        value = float(frontmatter[property_name])
                        date_str = frontmatter['date'].strip('\'"')
                        date_str = date_str.replace(' ', 'T')
                        date = datetime.fromisoformat(date_str)
                        data.append({'date': date, 'v': value, 'file': file_path.name})
                    except (ValueError, TypeError) as e:
                        print(f"Could not process data from {file_path}: {e}")

    if not data:
        print(f"No data found. Ensure .md files have 'date' and '{property_name}' properties in their frontmatter.")
        return

    data.sort(key=lambda x: x['date'])

    values = [d['v'] for d in data]
    latest_entry = data[-1]

    if len(data) > 1:
        latest_delta = latest_entry['v'] - data[-2]['v']
    else:
        latest_delta = 0.0

    all_time_low = min(values)
    all_time_high = max(values)
    low_entry = min(data, key=lambda x: x['v'])
    high_entry = max(data, key=lambda x: x['v'])

    mean_value = statistics.mean(values)
    median_value = statistics.median(values)

    print("--- Value Statistics ---")
    print(f"Latest value ({latest_entry['date'].date()}): {latest_entry['v']:.2f}")
    print(f"Change from previous: {latest_delta:.2f}")
    print(f"All-time low: {all_time_low:.2f} on {low_entry['date'].date()}")
    print(f"All-time high: {all_time_high:.2f} on {high_entry['date'].date()}")
    print(f"Average value: {mean_value:.2f}")
    print(f"Median value: {median_value:.2f}")
    print("------------------------")

    save_matplotlib_plot(data, property_name)

def main():
    parser = argparse.ArgumentParser(description=f'Plot a numerical value from frontmatter of .md files over time.')
    parser.add_argument('folder', type=str, help='The path to the folder containing the markdown files.')
    parser.add_argument('--prop', type=str, default='v', help='The numerical frontmatter property to plot. Defaults to "v".')
    args = parser.parse_args()

    plot_value_over_time(args.folder, args.prop)

if __name__ == '__main__':
    main()
