import os

# --- Configuration ---
OUTPUT_FILE = "codebase_dump.txt"
ROOT_DIR = "."

# Directories to skip completely (includes those from your .gitignore)
EXCLUDE_DIRS = {
    'node_modules', 
    'coverage', 
    'build', 
    '.git', 
    '__pycache__', 
    'dist', 
    '.next'
}

# Specific files or extensions to skip
EXCLUDE_FILES = {
    '.DS_Store', 
    '.pnp.js', 
    'dump_code.py', # Prevents the script from reading itself
    'package-lock.json', # Usually too large and not useful for text context
    'yarn.lock'
}

# Ignore common binary/media extensions
EXCLUDE_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.woff', '.woff2', '.ttf', '.eot',
    '.mp4', '.mp3', '.wav',
    '.pdf', '.zip', '.tar', '.gz'
)

def is_ignored(file_name):
    """Check if a file should be ignored based on your .gitignore rules."""
    if file_name in EXCLUDE_FILES:
        return True
    
    # Handle .env files from gitignore
    if file_name.startswith('.env.local') or file_name.startswith('.env.development') or \
       file_name.startswith('.env.test') or file_name.startswith('.env.production'):
        return True
        
    # Handle log files from gitignore
    if file_name.startswith('npm-debug.log') or file_name.startswith('yarn-debug.log') or \
       file_name.startswith('yarn-error.log'):
        return True
        
    # Handle .pnp (Yarn Plug'n'Play)
    if file_name.startswith('.pnp'):
        return True
        
    if file_name.endswith(EXCLUDE_EXTENSIONS):
        return True
        
    return False

def generate_codebase_dump():
    print(f"Starting codebase dump to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(ROOT_DIR):
            
            # Modify dirs in-place to skip excluded directories
            # Also skips any hidden directories (starting with '.')
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]

            for file in files:
                if is_ignored(file):
                    continue
                    
                file_path = os.path.join(root, file)
                
                try:
                    # Attempt to read the file
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        
                        # Write a clear visual separator and the file path
                        relative_path = os.path.relpath(file_path, ROOT_DIR)
                        outfile.write(f"\n{'='*60}\n")
                        outfile.write(f"File: {relative_path}\n")
                        outfile.write(f"{'='*60}\n\n")
                        
                        # Write the actual code
                        outfile.write(content)
                        outfile.write("\n")
                        
                except UnicodeDecodeError:
                    # Silently skip files that aren't valid UTF-8 text (e.g., hidden binaries)
                    pass
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    print("Done! Codebase has been successfully compiled.")

if __name__ == "__main__":
    generate_codebase_dump()