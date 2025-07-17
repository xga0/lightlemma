#!/usr/bin/env python3
"""
Simple version bumping script for pyproject.toml files.
"""
import re
import sys
from pathlib import Path

def bump_version(file_path, bump_type="patch"):
    """Bump version in pyproject.toml file."""
    content = Path(file_path).read_text()
    
    # Find current version
    version_pattern = r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
    match = re.search(version_pattern, content)
    
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    
    major, minor, patch = map(int, match.groups())
    
    # Bump version based on type
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    new_version = f"{major}.{minor}.{patch}"
    old_version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    
    # Replace version in content
    new_content = re.sub(
        version_pattern,
        f'version = "{new_version}"',
        content
    )
    
    # Write back to file
    Path(file_path).write_text(new_content)
    
    return old_version, new_version

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python version_bump.py <file_path> <bump_type>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    bump_type = sys.argv[2]
    
    try:
        old_version, new_version = bump_version(file_path, bump_type)
        print(f"Bumped version from {old_version} to {new_version}")
        print(f"::set-output name=old_version::{old_version}")
        print(f"::set-output name=new_version::{new_version}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 