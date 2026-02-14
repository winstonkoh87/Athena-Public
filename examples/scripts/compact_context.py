#!/usr/bin/env python3
import os
import re
import datetime
from pathlib import Path

# Config
CONTEXT_FILE = ".context/memory_bank/activeContext.md"
MAX_VISIBLE_COMPLETED = 3


def compact_active_context():
    """
    Scans activeContext.md.
    If > MAX_VISIBLE_COMPLETED [x] items found in the task list:
    1. Keeps the last N [x] items.
    2. Moves the older ones to a '## Compacted History' section (or similar).

    For now, we will simply Move them to the bottom or mark them as compacted.
    Actually, a better approach for V1:
    - Find all [x] lines.
    - If count > MAX_VISIBLE_COMPLETED:
    - Take the excess (oldest) items.
    - Append them to '## Recent History' at the bottom of the file (or verify it exists).
    - Remove them from the Active Tasks list.
    """

    base_path = Path(os.getcwd())
    file_path = base_path / CONTEXT_FILE

    if not file_path.exists():
        print(f"❌ Error: {CONTEXT_FILE} not found.")
        return

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    new_lines = []
    completed_tasks = []
    in_task_section = False
    task_section_header = "## Active Tasks"

    # Simple parser: extract [x] lines from Active Tasks section
    # Logic:
    # 1. Identify Task Section.
    # 2. Collect all [x] lines.
    # 3. If > MAX, keep last MAX.
    # 4. Remove others from their original position.
    # 5. Append removed ones to a history section.

    # Limitations: Complex markdown structures (nested lists) might break.
    # For V1, we assume a simple list under '## Active Tasks'.

    # 1. Pass: Identify and Collect
    # this is tricky with line indices. Let's do a robust split.

    # Easier strategy:
    # Split file into sections. Process the Active Tasks section. Reassemble.

    sections = re.split(r"(^## .*$)", content, flags=re.MULTILINE)

    out_sections = []
    compacted_items = []

    # Reconstruct with modification
    # sections[0] is premable. sections[1] is header, sections[2] is body...

    for i in range(0, len(sections)):
        part = sections[i]

        # Check if this part is the body of "Active Tasks"
        # The previous part (sections[i-1]) should be the header
        is_active_task_body = False
        if i > 0 and task_section_header in sections[i - 1]:
            is_active_task_body = True

        if is_active_task_body:
            # Process lines
            body_lines = part.splitlines()
            kept_lines = []
            current_completed = []

            # Find all completed tasks in this block
            for line in body_lines:
                if line.strip().startswith("- [x]"):
                    current_completed.append(line)
                else:
                    # It's a [ ] task or text or empty
                    pass

            # Calculate what to remove
            if len(current_completed) > MAX_VISIBLE_COMPLETED:
                # Remove oldest (first ones in the list)
                num_to_remove = len(current_completed) - MAX_VISIBLE_COMPLETED
                to_remove = current_completed[:num_to_remove]
                compacted_items.extend(to_remove)

                # Rebuild the block excluding removed lines
                # We iterate again to preserve order of non-removed lines
                remove_set = set(to_remove)
                for line in body_lines:
                    if line in remove_set:
                        # Skip (it's being moved)
                        # Remove from set to handle identical lines correctly?
                        # Ideally robust uniqueness, but for now simple check.
                        # actually, better to consume from list
                        if len(to_remove) > 0 and line == to_remove[0]:
                            to_remove.pop(0)
                            continue
                        else:
                            kept_lines.append(line)
                    else:
                        kept_lines.append(line)

                out_sections.append("\n".join(kept_lines))
                print(f"✅ Compacted {num_to_remove} tasks.")
            else:
                out_sections.append(part)
        else:
            out_sections.append(part)

    final_content = "".join(out_sections)

    # Append Compacted Items if any
    if compacted_items:
        # Check if "## Recent Context" or "## Compaction Log" exists
        log_header = "## Recent Context"

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        compaction_block = f"\n- **Compacted {timestamp}**:\n" + "\n".join(
            [f"  {item.strip().replace('- [x]', '- ')}" for item in compacted_items]
        )

        if log_header in final_content:
            # Append to existing
            # simplistic replace
            parts = final_content.split(log_header)
            # Insert after header
            final_content = parts[0] + log_header + "\n" + compaction_block + parts[1]
        else:
            # Append to end
            final_content += f"\n\n{log_header}\n{compaction_block}\n"

        # Write Back
        file_path.write_text(final_content, encoding="utf-8")
        print(f"✅ Setup Complete: {len(compacted_items)} tasks moved to history.")
    else:
        print("⚡ No compaction needed (< 3 completed tasks).")


if __name__ == "__main__":
    compact_active_context()
