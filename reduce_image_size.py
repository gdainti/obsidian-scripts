"""
This script reduces the size of JPG images in a specified folder by reducing their quality.

It scans a folder (and its subfolders) for .jpg and .jpeg files and overwrites them
with a compressed version. The original files are modified in place.

This script includes safeguards:
1. It skips files that are already smaller than a specified size (default 200KB).
2. It will not re-compress an image if the resulting file would not be smaller,
   preventing quality degradation from multiple runs.

Requirements:
- Pillow: `pip install Pillow`

Usage:
- To reduce image quality to 85% in a folder named 'my_images':
  python reduce_image_size.py my_images

- To specify a different quality (e.g., 50%):
  python reduce_image_size.py my_images --quality 50

- To skip files smaller than 200KB:
  python reduce_image_size.py my_images --min-size 200
"""
import argparse
import os
import io
from PIL import Image

def reduce_image_size_in_folder(folder_path: str, quality: int, min_size_kb: int):
    """
    Scans a folder for JPG images and reduces their size by adjusting the quality.

    Args:
        folder_path: The path to the folder to scan.
        quality: The target JPEG quality (1-100).
        min_size_kb: The minimum file size in KB to process.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at {folder_path}")
        return

    print(f"Scanning for .jpg/.jpeg files in '{folder_path}' and its subdirectories...")

    total_files = 0
    processed_files = 0
    skipped_files = 0
    total_original_size = 0
    total_new_size = 0
    min_size_bytes = min_size_kb * 1024

    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg')):
                total_files += 1
                image_path = os.path.join(root, filename)
                try:
                    original_size = os.path.getsize(image_path)

                    if original_size < min_size_bytes:
                        skipped_files += 1
                        print(f"Skipped {os.path.relpath(image_path, folder_path)} (size {original_size/1024:.1f}KB < {min_size_kb}KB)")
                        continue

                    img = Image.open(image_path)

                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')

                    buffer = io.BytesIO()
                    img.save(buffer, 'JPEG', quality=quality, optimize=True)
                    new_size = buffer.tell()

                    if new_size < original_size:
                        with open(image_path, 'wb') as f:
                            f.write(buffer.getvalue())

                        total_original_size += original_size
                        total_new_size += new_size
                        processed_files += 1
                        reduction_percent = (original_size - new_size) / original_size * 100
                        print(
                            f"Processed {os.path.relpath(image_path, folder_path)}: "
                            f"{original_size / 1024 / 1024:.2f}MB -> {new_size / 1024 / 1024:.2f}MB "
                            f"({reduction_percent:.1f}% reduction)"
                        )
                    else:
                        skipped_files += 1
                        print(f"Skipped {os.path.relpath(image_path, folder_path)} (no size improvement)")

                except FileNotFoundError:
                    print(f"Error: File not found during processing: {image_path}")
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

    print("\n--- Summary ---")
    print(f"Total files found: {total_files}")
    print(f"Files processed successfully: {processed_files}")
    print(f"Files skipped: {skipped_files}")

    if total_original_size > 0:
        total_reduction_percent = (total_original_size - total_new_size) / total_original_size * 100
        print(f"Total size reduction on processed files: {total_original_size / 1024 / 1024:.2f}MB -> {total_new_size / 1024 / 1024:.2f}MB ({total_reduction_percent:.1f}%)")

    print("Done.")

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Reduce the size of JPG images in a folder by reducing their quality.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example usage:
  python reduce_image_size.py ./my_folder
  python reduce_image_size.py ./my_folder --quality 75
  python reduce_image_size.py ./my_folder --min-size 200
"""
    )
    parser.add_argument(
        "folder",
        help="Path to the folder containing JPG images to process."
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality for the output images (1-100). Default is 85."
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=100,
        help="Minimum file size in KB to process an image. Default is 100."
    )

    args = parser.parse_args()

    if not 1 <= args.quality <= 100:
        print("Error: Quality must be an integer between 1 and 100.")
        return

    reduce_image_size_in_folder(args.folder, args.quality, args.min_size)

if __name__ == "__main__":
    main()
