import json
import os
import re

# Configuration
CASE_STUDIES_DIR = ".context/memories/case_studies"
PROTOCOLS_DIR = ".agent/skills/protocols"

# Keywords that suggest a link SHOULD exist
KEYWORDS = {
    "red curve": "Protocol 42",
    "blue curve": "Protocol 42",
    "limerence": "Protocol 113",
    "amoral realism": "Protocol 121",
    "principal agent": "Protocol 33",
    "sovereign": "Protocol 161",
    "attack surface": "Protocol 161",
    "survivor": "Protocol 34",
    "tuition": "CS044",
    "polo": "SGP-SOC-001"
}

def scan_file(filepath):
    with open(filepath) as f:
        content = f.read()

    # Check for links
    protocol_links = re.findall(r'\[Protocol \d+.*?\]', content)
    case_links = re.findall(r'\[.*?Case.*?\]', content)
    has_related_section = "Related Protocols" in content or "Cross-References" in content

    # Check for missing keywords
    missing_links = []
    for keyword, expected_link in KEYWORDS.items():
        if keyword.lower() in content.lower():
            # Simplistic check: if keyword is present but expected link ID is NOT in content
            # This isn't perfect but good enough for a rough audit
            link_id = expected_link.split(" ")[-1] if " " in expected_link else expected_link
            if link_id not in content:
                missing_links.append(f"Has '{keyword}' but missing link to {expected_link}")

    return {
        "file": os.path.basename(filepath),
        "link_count": len(protocol_links) + len(case_links),
        "has_related_section": has_related_section,
        "missing_links": missing_links
    }

def audit_directory(directory):
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                results.append(scan_file(os.path.join(root, file)))
    return results

def main():
    print("Starting Audit...")
    case_results = audit_directory(CASE_STUDIES_DIR)

    # Filter for actionable items
    actionable = [r for r in case_results if not r['has_related_section'] or r['missing_links']]

    report = {
        "total_files": len(case_results),
        "files_needing_action": len(actionable),
        "details": actionable
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
