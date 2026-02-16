import os
import subprocess
import datetime
import re

TARGET_DIRS = [".context", ".agent", ".projects"]
EXCLUDE_DIRS = [
    "node_modules",
    ".git",
    "dist",
    "build",
    ".DS_Store",
    "venv",
    "__pycache__",
    "cache",
    "data_lake",
]


def get_git_dates(filepath):
    try:
        # Created: Get the date of the first commit that added the file
        cmd_created = [
            "git",
            "log",
            "--diff-filter=A",
            "--follow",
            "--format=%aI",
            "--",
            filepath,
        ]
        result = subprocess.run(cmd_created, capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        created = lines[-1] if lines and lines[-1] else None  # Oldest commit

        # Last Updated: Get the date of the last commit
        cmd_updated = ["git", "log", "-1", "--format=%aI", "--", filepath]
        result = subprocess.run(cmd_updated, capture_output=True, text=True)
        updated = result.stdout.strip()
    except Exception as e:
        created = None
        updated = None

    return created, updated


def process_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping binary/unreadable: {filepath}")
        return

    created, updated = get_git_dates(filepath)

    # Fallbacks
    if not created:
        stat = os.stat(filepath)
        created = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
    if not updated:
        updated = datetime.datetime.now().isoformat()

    # Format YYYY-MM-DD
    created_str = created[:10]
    updated_str = updated[:10]

    # Update logic
    if content.startswith("---\n"):
        # Existing Frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]

            new_lines = []
            has_created = False
            has_updated = False

            for line in frontmatter.strip().split("\n"):
                if line.strip().startswith("created:"):
                    # Keep original creation date if exists, or update if placeholder?
                    # Let's keep existing unless it's missing. Use detected if valid.
                    # Actually, user wants to know when *we discussed it*. Git creation is best proxy.
                    # But if file has "created: 2024...", keep it.
                    has_created = True
                    new_lines.append(line)
                elif line.strip().startswith("last_updated:"):
                    has_updated = True
                    # Force update "last updated" to Today if we are running this?
                    # Or roughly match Git? User wants referencing.
                    # Let's update it to the Git Last Modified Date (which is accurate).
                    new_lines.append(f"last_updated: {updated_str}")
                else:
                    new_lines.append(line)

            if not has_created:
                new_lines.append(f"created: {created_str}")
            if not has_updated:
                new_lines.append(f"last_updated: {updated_str}")

            new_frontmatter = "\n".join(new_lines) + "\n"
            new_content = f"---{new_frontmatter}---{body}"
        else:
            # Malformed frontmatter, wrap whole thing
            new_content = f"---\ncreated: {created_str}\nlast_updated: {updated_str}\n---\n\n{content}"
    else:
        # No frontmatter
        new_content = f"---\ncreated: {created_str}\nlast_updated: {updated_str}\n---\n\n{content}"

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {filepath}")


def main():
    root_dir = os.getcwd()
    for target in TARGET_DIRS:
        path = os.path.join(root_dir, target)
        if not os.path.exists(path):
            continue

        for root, dirs, files in os.walk(path):
            # Exclude logic
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for name in files:
                if name.endswith(".md"):
                    process_file(os.path.join(root, name))


if __name__ == "__main__":
    main()
