import os
import re
import shutil

STRANGE_WHITESPACE_PATTERN = re.compile(r'[\u00A0\u202F\u200B\u2000-\u200A]')

def normalize_file(filepath):
    print(f"Checking file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    found = STRANGE_WHITESPACE_PATTERN.findall(content)
    if not found:
        print("  No strange whitespace characters found.")
        return False

    print(f"  Found {len(found)} strange whitespace characters: {[hex(ord(c)) for c in found]}")
    cleaned = STRANGE_WHITESPACE_PATTERN.sub(' ', content)

    backup_path = filepath + ".bak"
    shutil.copyfile(filepath, backup_path)
    print(f"  Backup created at: {backup_path}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print("  File normalized.")
    return True

def find_and_normalize_prompts_recursive(base_path):
    updated_files = []
    print(f"Scanning directory recursively: {base_path}")

    for root, dirs, files in os.walk(base_path):
        # Проверяем папки, которые начинаются с "agent"
        agent_dirs = [d for d in dirs if d.startswith("agent")]
        for agent_dir in agent_dirs:
            prompts_path = os.path.join(root, agent_dir, "prompts.py")
            if os.path.isfile(prompts_path):
                if normalize_file(prompts_path):
                    updated_files.append(prompts_path)

    return updated_files

if __name__ == '__main__':
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    updated = find_and_normalize_prompts_recursive(root_path)

    if updated:
        print("✔️ Updated files with backup created:")
        for path in updated:
            print("  -", path)
    else:
        print("✅ All prompts are clean.")
