import os
import glob


def count_files(base_path, pattern, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = []
    count = 0
    for root, dirs, files in os.walk(base_path):
        # Modify dirs in-place to skip ignored
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            if file.endswith(pattern):
                count += 1
    return count


private_root = "/Users/[AUTHOR]/Desktop/Project Athena"
public_root = "/Users/[AUTHOR]/Desktop/Project Athena/Athena-Public"

print("--- AUDIT RESULTS ---")

# Private Metrics
py_scripts = count_files(
    private_root, ".py", ignore_dirs=["Athena-Public", ".framework", "node_modules"]
)
protocols = len(
    glob.glob(f"{private_root}/.agent/skills/protocols/**/*.md", recursive=True)
)
case_studies = len(
    glob.glob(f"{private_root}/.context/memories/case_studies/**/*.md", recursive=True)
)
sessions = len(
    glob.glob(f"{private_root}/.context/memories/session_logs/**/*.md", recursive=True)
)

print(f"PRIVATE_PYTHON_SCRIPTS: {py_scripts}")
print(f"PRIVATE_PROTOCOLS: {protocols}")
print(f"PRIVATE_CASE_STUDIES: {case_studies}")
print(f"PRIVATE_SESSIONS: {sessions}")

# Public Metrics
public_protocols = len(
    glob.glob(f"{public_root}/examples/protocols/**/*.md", recursive=True)
)
public_case_studies = len(
    glob.glob(f"{public_root}/examples/case_studies/**/*.md", recursive=True)
)
public_py_scripts = count_files(
    public_root, ".py", ignore_dirs=[".venv", "build", "dist"]
)

print(f"PUBLIC_PROTOCOLS: {public_protocols}")
print(f"PUBLIC_CASE_STUDIES: {public_case_studies}")
print(f"PUBLIC_PYTHON_SCRIPTS: {public_py_scripts}")
