import os
import sys
from pathlib import Path
from PIL import Image

def resize_images(source_folder, max_side, quality=92):
    source_path = Path(source_folder).resolve()
    if not source_path.is_dir():
        print(f"Error: '{source_folder}' is not a folder or does not exist")
        return 0
    output_folder = source_path / "resized"
    output_folder.mkdir(exist_ok=True)
    extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
    count = 0
    skipped = 0
    errors = 0
    for file_path in source_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            try:
                with Image.open(file_path) as im:
                    w, h = im.size
                    if max(w, h) <= max_side:
                        dest = output_folder / file_path.name
                        im.save(dest, quality=quality, optimize=True)
                        print(f"Copied (already ≤ {max_side}px) {file_path.name}")
                        count += 1
                        continue
                    ratio = max_side / max(w, h)
                    new_w = round(w * ratio)
                    new_h = round(h * ratio)
                    resized = im.resize((new_w, new_h), Image.LANCZOS)
                    dest = output_folder / file_path.name
                    if im.format == "JPEG":
                        save_args = {"quality": quality, "optimize": True, "progressive": True}
                        exif = im.info.get("exif")
                        if exif:
                            save_args["exif"] = exif
                        resized.save(dest, **save_args)
                    else:
                        resized.save(dest)
                    print(f"Resized {new_w}×{new_h} {file_path.name}")
                    count += 1
            except Exception as e:
                print(f"Error {file_path.name} {type(e).__name__}: {e}")
                errors += 1
    total = count + skipped + errors
    print("Finished.")
    print(f"Processed folder: {source_path}")
    print(f"Images found: {total}")
    print(f"Successfully saved: {count}")
    print(f"Skipped (too small): {skipped}")
    print(f"Errors: {errors}")
    print(f"Output folder: {output_folder}")
    return count

if __name__ == "__main__":
    folder = input("Enter folder path: ").strip() or '.'
    if not folder:
        print("No folder given.")
        exit(1)
    folder_path = Path(folder).expanduser().resolve()
    if not folder_path.is_dir():
        print(f"Error: '{folder}' is not a folder or cannot be found")
        exit(1)
    while True:
        size_str = input("Maximum longest side in pixels (e.g. 768): ").strip() or '768'
        try:
            max_side = int(size_str)
            if max_side < 32:
                print("Enter a bigger number.")
                continue
            break
        except ValueError:
            print("Enter a valid number.")
    quality = 90
    while True:
        qual_str = input(f"JPEG quality (30–100 ({quality}): ").strip() or '90'
        if not qual_str:
            break
        try:
            q = int(qual_str)
            quality = max(30, min(100, q))
            break
        except ValueError:
            print("Enter a number between 30 and 100, press Enter to keep default.")
    print(f"Starting resize:")
    print(f"  Folder: {folder_path}")
    print(f"  Max side: {max_side} pixels")
    print(f"  JPEG quality: {quality}")
    processed = resize_images(str(folder_path), max_side, quality)
    if processed > 0:
        print(f"{processed} images were processed or copied.")
    else:
        print("No images were processed.")

