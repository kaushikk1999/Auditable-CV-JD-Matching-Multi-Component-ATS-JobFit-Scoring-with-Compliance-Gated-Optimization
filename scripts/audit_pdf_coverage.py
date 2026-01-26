
import os

# CONFIG FROM generate_pdf_docs.py
MAX_FILE_SIZE_BYTES = 1024 * 50
INCLUDED_EXTENSIONS = {
    '.py', '.md', '.txt', '.json', '.yaml', '.yml', 
    '.tex', '.mmd', '.sh', '.gitignore', '.rst'
}
EXCLUDED_DIRS = {
    '.git', '__pycache__', 'venv', '.venv', '.idea', '.vscode', 
    'node_modules', '.DS_Store', 'project_documentation_env'
}

def audit_coverage(root_dir):
    included_count = 0
    skipped_ext = []
    skipped_size = []
    skipped_dir = []

    print(f"Scanning {root_dir}...\n")

    for root, dirs, files in os.walk(root_dir):
        # Check if dir is excluded
        is_excluded_dir = False
        parts = root.split(os.sep)
        for part in parts:
            if part in EXCLUDED_DIRS:
                is_excluded_dir = True
                break
        
        if is_excluded_dir:
            # We don't even walk these in the main script, but os.walk does here unless modified
            # The main script modifies 'dirs' in place. Let's emulate that.
            continue
        
        # Modify dirs in-place to skip recursion into excluded ones
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file == ".DS_Store": continue
            
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, root_dir)
            ext = os.path.splitext(file)[1].lower()
            size = os.path.getsize(filepath)

            if ext not in INCLUDED_EXTENSIONS and file not in ['Dockerfile', 'Procfile']:
                skipped_ext.append(relpath)
                continue

            if size > MAX_FILE_SIZE_BYTES:
                skipped_size.append((relpath, size))
                continue

            included_count += 1

    print(f"=== SUMMARY ===")
    print(f"Included Files: {included_count}")
    print(f"Skipped (Extension not allowed): {len(skipped_ext)}")
    print(f"Skipped (Too large > 50KB): {len(skipped_size)}")
    
    if skipped_size:
        print("\n=== SKIPPED: TOO LARGE ===")
        for f, s in skipped_size:
            print(f"{f} ({s/1024:.1f} KB)")
            
    if skipped_ext:
        print("\n=== SKIPPED: IGNORED EXTENSION ===")
        # Group by extension for cleaner output
        from collections import defaultdict
        ext_map = defaultdict(list)
        for f in skipped_ext:
            pk = os.path.splitext(f)[1]
            ext_map[pk].append(f)
            
        for ext, fs in ext_map.items():
            print(f"Extension '{ext}': {len(fs)} files")
            for f in fs[:5]: # Show first 5
                print(f"  - {f}")
            if len(fs) > 5: print(f"  ... and {len(fs)-5} more")

if __name__ == "__main__":
    audit_coverage(os.getcwd())
