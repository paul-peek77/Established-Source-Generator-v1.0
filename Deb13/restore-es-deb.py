#!/usr/bin/env python3
# [file name]: restore-es-deb.py
# [directory]: ./ (Run in the folder where you want to restore)
import os
import sys

def restore_pimpire_standard():
    # Priority: Check for Purified version first
    es_filename = "PURIFIED-established-source.txt" if os.path.exists("PURIFIED-established-source.txt") else "established-source.txt"

    print(f"⚜️ Shadow Scribe restoring from: {es_filename}")

    if not os.path.exists(es_filename):
        print("❌ Error: Manifest not found!")
        return

    with open(es_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    collecting = False
    file_content = []
    restored_count = 0
    current_file_path = None

    dry_run = '--dry-run' in sys.argv

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Path line like ./path or .\path
        if not collecting and (stripped.startswith('.\\') or stripped.startswith('./')):
            p = stripped.replace('\\', '/')
            if p.startswith('./'):
                p = p[2:]
            current_file_path = p
            i += 1
            continue

        # A file-block opener. Manifests sometimes put a path between two begin markers.
        if not collecting and stripped == '[file content begin]':
            # look ahead for a path line or a nested begin marker
            j = i + 1
            # skip blank lines
            while j < n and lines[j].strip() == '':
                j += 1
            if j < n:
                nextstr = lines[j].strip()
                if nextstr.startswith('./') or nextstr.startswith('.\\'):
                    # path follows this begin marker
                    p = nextstr.replace('\\', '/')
                    if p.startswith('./'):
                        p = p[2:]
                    current_file_path = p
                    # advance i to the line after the path
                    i = j + 1
                    # If another begin marker follows, consume it and start collecting afterwards
                    if i < n and lines[i].strip() == '[file content begin]':
                        collecting = True
                        file_content = []
                        i += 1
                        continue
                    # else continue loop to find explicit content begin or start collecting immediately
                    collecting = True
                    file_content = []
                    continue
                elif nextstr == '[file content begin]':
                    # nested begin — consume both and start collecting
                    collecting = True
                    file_content = []
                    i = j + 1
                    continue
            # fallback: start collecting from next line
            collecting = True
            file_content = []
            i += 1
            continue

        # End of content for current file
        if collecting and stripped == '[file content end]':
            if current_file_path:
                dirpath = os.path.dirname(current_file_path)
                if dirpath and not dry_run:
                    os.makedirs(dirpath, exist_ok=True)
                if dry_run:
                    print(f"DRY-RUN: would restore: {current_file_path}")
                else:
                    with open(current_file_path, 'w', encoding='utf-8') as f_out:
                        f_out.writelines(file_content)
                    print(f"✅ Restored: {current_file_path}")
                restored_count += 1
            collecting = False
            current_file_path = None
            file_content = []
            i += 1
            continue

        # Normal collection of content lines
        if collecting:
            file_content.append(line)
            i += 1
            continue

        # Nothing matched; move on
        i += 1

    print(f"\n⚜️ VICTORY! {restored_count} artifacts resurrected.")

if __name__ == "__main__":
    restore_pimpire_standard()
