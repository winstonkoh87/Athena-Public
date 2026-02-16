import os
import re
import datetime
import yaml
from pathlib import Path

# Configuration
TARGET_DIR = "/Users/[AUTHOR]/Desktop/Project Athena/.context"
DRY_RUN = False


def get_file_dates(filepath):
    """Get creation and modification dates from filesystem."""
    stat = os.stat(filepath)
    try:
        created = datetime.datetime.fromtimestamp(stat.st_birthtime).strftime(
            "%Y-%m-%d"
        )
    except AttributeError:
        # Linux might not have st_birthtime
        created = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")

    modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
    return created, modified


def fix_frontmatter(content, filepath):
    """
    Parses content, extracts all YAML frontmatter from the top,
    merges it, and returns rebuilt content with a single clean frontmatter block.
    """

    extracted_keys = {}
    working_content = content

    # improved loop to eat blocks
    while True:
        original_working = working_content
        working_content = working_content.lstrip()

        # Check if we have a block start
        if working_content.startswith("---"):
            # It starts with ---.
            # It could be `---` (standard) or `---key: val` (malformed)

            # Find the END of this block.
            # The end is a line consisting of `---` (optionally whitespace).
            # We look for `\n---`

            # SEARCH STRATEGY:
            # 1. Look for `\n---`
            # 2. If it exists, everything before it is part of the block.
            # 3. If NOT exists, is it a one-line block?

            # Special case for "Clean" new block format `{ ... }` on one line?
            # No, standard yaml is multi-line.

            # Let's verify if the start is `---` or `---text`.
            # If `---text`, it's definitely a block start.

            # We must find the closing delimiter.
            # Regex for closing delimiter: `\n---` matching start of a line.

            rest = working_content
            # Note: startswith('---') is true.

            offset_to_content = 0

            # Find closest `\n---`
            # Skip the first 3 chars to avoid matching the start if it is just `---`
            search_start = 3
            match = re.search(r"\n---", rest[search_start:])

            if match:
                end_pos = search_start + match.start()
                # content is rest[3:end_pos] IN CASE of `---`
                # IN CASE of `---key:val`, content is rest[3:end_pos] (including `key:val`)

                # Careful: if it was `---key:val`, the `key:val` is part of the content.
                # If it was `---`, the first newline is usually immediate.

                block_body = rest[3:end_pos]

                # Try to clean up block_body
                # If it was `created: ...`, `yaml.safe_load` handles it.
                # `yaml.safe_load(": val")` might fail.

                # If the line started with `---key`, we stripped `---`. `key` remains.

                try:
                    # Handle annoying tabs or malformed chars
                    clean_body = block_body.replace("\t", "  ")
                    d = yaml.safe_load(clean_body)
                    if isinstance(d, dict):
                        extracted_keys.update(d)
                except Exception as e:
                    # If parsing fails, maybe it wasn't a block?
                    # Or maybe it was just garbage.
                    # We assume if we found a closing `---`, it WAS intended as a block.
                    # We consume it regardless to "clean" the file.
                    pass

                # Advance working_content
                # match.end() points to after `\n---`.
                # We also want to strip the newline after the closing `---` if present
                next_start = end_pos + 4  # length of `\n---` is 4
                working_content = rest[next_start:]
                continue

            else:
                # No closing `---`.
                # Is it a single line `---key: val` EOF?
                # Or just `---` separator?
                # If no newline, maybe end of file?

                if "\n" not in rest:
                    # Single line file?
                    try:
                        d = yaml.safe_load(rest[3:])
                        if isinstance(d, dict):
                            extracted_keys.update(d)
                        working_content = ""
                    except:
                        break
                else:
                    # It has newlines but no closing `---`.
                    # Assume it's NOT a frontmatter block (maybe a HR).
                    pass
                break
        else:
            # content does not start with ---
            break

        if working_content == original_working:
            # Safety break to avoid infinite loop
            break

    # Now rebuild
    fs_created, fs_updated = get_file_dates(filepath)

    final_created = extracted_keys.get("created")
    final_updated = extracted_keys.get("last_updated")

    # Normalize dates
    if final_created:
        # If list or other type, convert to string
        if not isinstance(final_created, (str, datetime.date, datetime.datetime)):
            final_created = str(final_created)

        if isinstance(final_created, datetime.date):
            final_created = final_created.strftime("%Y-%m-%d")
        elif isinstance(final_created, datetime.datetime):
            final_created = final_created.strftime("%Y-%m-%d")
    else:
        final_created = fs_created

    if final_updated:
        if not isinstance(final_updated, (str, datetime.date, datetime.datetime)):
            final_updated = str(final_updated)

        if isinstance(final_updated, datetime.date):
            final_updated = final_updated.strftime("%Y-%m-%d")
        elif isinstance(final_updated, datetime.datetime):
            final_updated = final_updated.strftime("%Y-%m-%d")
    else:
        final_updated = fs_updated

    extracted_keys["created"] = str(final_created)
    extracted_keys["last_updated"] = str(final_updated)

    ordered_keys = {}
    if "created" in extracted_keys:
        ordered_keys["created"] = extracted_keys.pop("created")
    if "last_updated" in extracted_keys:
        ordered_keys["last_updated"] = extracted_keys.pop("last_updated")
    ordered_keys.update(extracted_keys)

    # Rebuild YAML
    new_yaml = yaml.dump(
        ordered_keys, sort_keys=False, default_flow_style=None, width=1000
    ).strip()

    # Strip leading newlines from content
    working_content = working_content.lstrip()

    new_content = f"---\n{new_yaml}\n---\n\n{working_content}"

    # prevent double newlines if working content already has them
    while "\n\n\n" in new_content:
        new_content = new_content.replace("\n\n\n", "\n\n")

    return new_content


def process_directory(directory):
    files_processed = 0
    files_changed = 0

    path_list = list(Path(directory).rglob("*.md"))

    for file_path in path_list:
        files_processed += 1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = fix_frontmatter(content, str(file_path))

            if new_content != content:
                print(f"[CHANGE] {file_path}")
                files_changed += 1
                if not DRY_RUN:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
            else:
                # print(f"[SKIP]   {file_path} (No changes needed)")
                pass

        except Exception as e:
            print(f"[ERROR]  {file_path}: {e}")

    print(f"\nSummary:")
    print(f"Processed: {files_processed}")
    print(f"Changed:   {files_changed}")


if __name__ == "__main__":
    print(f"Scanning {TARGET_DIR}...")
    process_directory(TARGET_DIR)
