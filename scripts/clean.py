#!/usr/bin/env python3
"""Cleanup script for removing build artifacts and cache files."""

import os
import shutil
from pathlib import Path

def clean_build_artifacts():
    """Remove build artifacts."""
    artifacts = ['build', 'dist', '*.egg-info']
    for pattern in artifacts:
        if '*' in pattern:
            # Handle glob patterns
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Removed {path}/")
                else:
                    os.remove(path)
                    print(f"Removed {path}")
        else:
            if os.path.exists(pattern):
                if os.path.isdir(pattern):
                    shutil.rmtree(pattern)
                    print(f"Removed {pattern}/")
                else:
                    os.remove(pattern)
                    print(f"Removed {pattern}")

def clean_cache_files():
    """Remove Python cache files."""
    cache_patterns = ['__pycache__', '*.pyc', '*.pyo', '.pytest_cache', '.coverage']
    
    for root, dirs, files in os.walk('.'):
        # Remove cache directories
        for cache_dir in cache_patterns:
            if cache_dir in dirs:
                cache_path = os.path.join(root, cache_dir)
                shutil.rmtree(cache_path)
                print(f"Removed {cache_path}/")
        
        # Remove cache files
        for file in files:
            if file.endswith(('.pyc', '.pyo')) or file == '.coverage':
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Removed {file_path}")

def main():
    """Main cleanup process."""
    print("Cleaning build artifacts and cache files...")
    clean_build_artifacts()
    clean_cache_files()
    print("Cleanup complete!")

if __name__ == '__main__':
    main()