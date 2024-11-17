import os
import zipfile
import json
from pathlib import Path

def extract_zip(zip_path, extract_path):
    print(f"Extracting {zip_path} to {extract_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f"Extraction of {zip_path} complete")

def safe_unlink(path):
    try:
        path.unlink()
    except PermissionError:
        print(f"Permission denied: {path}")

def safe_rmdir(path):
    try:
        path.rmdir()
    except OSError:
        print(f"Directory not empty or other error: {path}")

def clean_directory(path):
    for child in path.iterdir():
        if child.is_file():
            safe_unlink(child)
        elif child.is_dir():
            clean_directory(child)
            safe_rmdir(child)

def deep_merge_dicts(dest, src):
    for key, value in src.items():
        if isinstance(value, dict) and key in dest and isinstance(dest[key], dict):
            deep_merge_dicts(dest[key], value)
        elif isinstance(value, list) and key in dest and isinstance(dest[key], list):
            if key in ["rotation", "translation", "scale"]:
                dest[key] = value  # Ensure these keys are overwritten, not appended
            else:
                dest[key].extend(value)  # Append for other lists
        else:
            dest[key] = value

def combine_jsons(zip_files, json_types, output_dir):
    output_dir = Path(output_dir)
    if output_dir.is_file():
        print(f"Error: Output directory path is a file: {output_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for json_type in json_types:
        combined_data = {}
        json_filename = f"{json_type}.json"
        temp_dir = Path("/tmp/json_extract")
        temp_dir.mkdir(parents=True, exist_ok=True)
        print(f"Temporary directory created at {temp_dir}")

        for zip_file in zip_files:
            print(f"Processing ZIP file: {zip_file}")
            extract_path = temp_dir / Path(zip_file).stem
            if extract_path.exists():
                clean_directory(extract_path)
                safe_rmdir(extract_path)
            extract_path.mkdir(parents=True, exist_ok=True)
            print(f"Extract path created at {extract_path}")

            extract_zip(zip_file, extract_path)

            json_file_path = extract_path / f"assets/minecraft/models/item/{json_filename}"
            if json_file_path.exists():
                print(f"Found {json_file_path}")
                with open(json_file_path, 'r') as file:
                    json_content = json.load(file)
                    deep_merge_dicts(combined_data, json_content)
            else:
                print(f"{json_filename} not found in {zip_file}")

            # Clean up
            clean_directory(extract_path)
            safe_rmdir(extract_path)

        output_file = output_dir / f"combined_{json_filename}"
        with open(output_file, 'w') as file:
            json.dump(combined_data, file, indent=4)
        print(f"Combined JSON file created at {output_file}")

if __name__ == "__main__":
    zip_files = input("Enter the paths to the ZIP files of the resource packs separated by commas: ").split(',')
    json_types = input("Enter the types of JSON files separated by commas (e.g., bow, sword, axe, pickaxe, hoe, shovel): ").strip().lower().split(',')
    output_dir = input("Enter the output directory path: ").strip()
    combine_jsons(zip_files, json_types, output_dir)
