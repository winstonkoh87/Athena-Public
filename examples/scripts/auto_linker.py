import os
import re
from pathlib import Path

# Dynamic workspace resolution
WORKSPACE_ROOT = str(Path(__file__).resolve().parent.parent.parent)
PROTOCOLS_DIR = os.path.join(WORKSPACE_ROOT, ".agent", "skills", "protocols")

# Map of Trigger Keyword -> (Link Title, Relative Path from Workspace Root)
# Using generic paths that are likely correct based on previous listings
LINK_MAP = {
    "red curve": (
        "Protocol 42: Red-Blue Curve Taxonomy",
        ".agent/skills/protocols/strategy/42-red-blue-curve-taxonomy.md",
    ),
    "blue curve": (
        "Protocol 42: Red-Blue Curve Taxonomy",
        ".agent/skills/protocols/strategy/42-red-blue-curve-taxonomy.md",
    ),
    "limerence": (
        "Protocol 114: Limerent Reality Distortion",
        ".agent/skills/protocols/psychology/114-limerent-reality-distortion.md",
    ),
    "missing baseline": (
        "Protocol 113: Missing Baseline Model",
        ".agent/skills/protocols/psychology/113-missing-baseline-model.md",
    ),
    "sovereign": (
        "Protocol 161: Sovereign Operating Protocol",
        ".agent/skills/protocols/decision/161-sovereign-operating-protocol.md",
    ),
    "amoral realism": (
        "Protocol 121: Amoral Realism",
        ".agent/skills/protocols/strategy/121-amoral-realism.md",
    ),
    "first principles": (
        "Protocol 115: First Principles Deconstruction",
        ".agent/skills/protocols/decision/115-first-principles-deconstruction.md",
    ),
    "premise audit": (
        "Protocol 111: Premise Audit",
        ".agent/skills/protocols/decision/111-premise-audit.md",
    ),
    "form vs substance": (
        "Protocol 112: Form-Substance Gap",
        ".agent/skills/protocols/pattern-detection/112-form-substance-gap.md",
    ),
    "limerent": (
        "Protocol 114: Limerent Reality Distortion",
        ".agent/skills/protocols/psychology/114-limerent-reality-distortion.md",
    ),
    "tuition": (
        "CS044: ILP Trust Arbitrage",
        ".context/memories/case_studies/CS044_ILP_Trust_Arbitrage.md",
    ),
    "recursive larp": (
        "Protocol 127: Recursive LARP Trap",
        ".agent/skills/protocols/pattern-detection/127-recursive-larp-trap.md",
    ),
    "larp": (
        "Protocol 127: Recursive LARP Trap",
        ".agent/skills/protocols/pattern-detection/127-recursive-larp-trap.md",
    ),
    "internal family systems": (
        "Protocol 128: Internal Family Systems",
        ".agent/skills/protocols/psychology/128-internal-family-systems.md",
    ),
    "ifs": (
        "Protocol 128: Internal Family Systems",
        ".agent/skills/protocols/psychology/128-internal-family-systems.md",
    ),
    "exile": (
        "Protocol 128: Internal Family Systems",
        ".agent/skills/protocols/psychology/128-internal-family-systems.md",
    ),
    "manager": (
        "Protocol 128: Internal Family Systems",
        ".agent/skills/protocols/psychology/128-internal-family-systems.md",
    ),
    "firefighter": (
        "Protocol 128: Internal Family Systems",
        ".agent/skills/protocols/psychology/128-internal-family-systems.md",
    ),
    "sdr": (
        "Protocol 124: SDR Diagnosis",
        ".agent/skills/protocols/decision/124-sdr-diagnosis.md",
    ),
    "strategic disadvantage ratio": (
        "Protocol 124: SDR Diagnosis",
        ".agent/skills/protocols/decision/124-sdr-diagnosis.md",
    ),
    "sdf": (
        "SDF (Strategic Dynamic Filtering)",
        ".framework/v8.6-stable/modules/System_Principles.md",
    ),
    "mcda": (
        "Protocol 121: Decision Frameworks (MCDA / WEU / Pairwise)",
        ".agent/skills/protocols/decision/121-mcda-weu-framework.md",
    ),
    "weu": (
        "Protocol 121: Decision Frameworks (MCDA / WEU / Pairwise)",
        ".agent/skills/protocols/decision/121-mcda-weu-framework.md",
    ),
    "pairwise": (
        "Protocol 121: Decision Frameworks (MCDA / WEU / Pairwise)",
        ".agent/skills/protocols/decision/121-mcda-weu-framework.md",
    ),
}


def get_abs_path(rel_path):
    return os.path.join(WORKSPACE_ROOT, rel_path)


def process_file(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    original_content = content
    links_to_add = []

    for keyword, (title, rel_link) in LINK_MAP.items():
        # Case insensitive word boundary search
        if re.search(r"\b" + re.escape(keyword) + r"\b", content, re.IGNORECASE):
            link_filename = os.path.basename(rel_link)
            # Check if link (by filename) is already present
            if link_filename not in content:
                # Avoid self-linking
                if os.path.basename(file_path) != link_filename:
                    # Create the full link string
                    full_link = f"- [{title}](file://{get_abs_path(rel_link)})"
                    # Avoid adding duplicates in the same run
                    if full_link not in links_to_add:
                        links_to_add.append(full_link)

    if not links_to_add:
        return False

    # Append links
    print(f"Injecting {len(links_to_add)} links into {os.path.basename(file_path)}")

    # Regex to find existing Related Protocols/References section
    header_regex = re.compile(
        r"^(##\s+(Related Protocols|Cross-References|References|Related|See Also))",
        re.M | re.IGNORECASE,
    )
    match = header_regex.search(content)

    links_text = "\n".join(links_to_add)

    if match:
        # Insert after the matched header line
        end_of_header_line = content.find("\n", match.end())
        if end_of_header_line == -1:
            end_of_header_line = len(content)

        content = (
            content[:end_of_header_line]
            + "\n"
            + links_text
            + content[end_of_header_line:]
        )
    else:
        # Append to end
        if not content.endswith("\n"):
            content += "\n"
        content += "\n## Related Protocols\n\n" + links_text + "\n"

    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False


def main():
    count = 0
    # Walk case_studies as well
    dirs_to_scan = [
        PROTOCOLS_DIR,
        os.path.join(WORKSPACE_ROOT, ".context/memories/case_studies"),
    ]

    for scan_dir in dirs_to_scan:
        if not os.path.exists(scan_dir):
            continue

        for root, dirs, files in os.walk(scan_dir):
            for file in files:
                if file.endswith(".md"):
                    if process_file(os.path.join(root, file)):
                        count += 1
    print(f"Total files updated: {count}")


if __name__ == "__main__":
    main()
