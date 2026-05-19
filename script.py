#!/usr/bin/env python3
import os
import sys

def generate_structure(startpath, output_file="PROJECT_STRUCTURE.md"):
    abs_path = os.path.abspath(startpath)
    folder_name = os.path.basename(abs_path)
    ignore = {'__pycache__', '.git', 'venv', '.gitattributes', '.gitignore', 'build', 'dist', '.gradle', '.idea', '.kotlin', 'androidTest', 'test', 'pictures'}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# PROJECT_STRUCTURE.md\n\n```\n{folder_name}/\n")
        
        def walk_dir(path, prefix=''):
            items = sorted([i for i in os.listdir(path) if i not in ignore])
            
            for i, item in enumerate(items):
                is_last = (i == len(items) - 1)
                item_path = os.path.join(path, item)
                
                f.write(f"{prefix}{'└── ' if is_last else '├── '}{item}{'/' if os.path.isdir(item_path) else ''}\n")
                
                if os.path.isdir(item_path):
                    walk_dir(item_path, prefix + ('    ' if is_last else '│   '))
        
        walk_dir(abs_path)
        f.write("```\n")
    
    print(f"✅ Готово: {output_file}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    output = sys.argv[2] if len(sys.argv) > 2 else "PROJECT_STRUCTURE.md"
    generate_structure(path, output)
