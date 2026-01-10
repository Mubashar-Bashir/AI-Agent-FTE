#!/usr/bin/env python3
"""
Utility to update SDD specification metadata in YAML frontmatter.
Used to track progress through the SDD workflow.
"""

import sys
import os
import re
from datetime import datetime


def update_sdd_metadata(spec_file_path, step_name, percent_value, next_command):
    """
    Update the YAML frontmatter of an SDD spec file with new metadata values.
    """
    if not os.path.exists(spec_file_path):
        print(f"Error: File {spec_file_path} does not exist")
        return False

    with open(spec_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content into frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"Error: File {spec_file_path} does not contain valid YAML frontmatter (--- ... ---)")
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Update the values in the frontmatter
    updated_frontmatter = re.sub(
        r'^status:.*$',
        f'status: "🔄 In Progress"',
        frontmatter,
        flags=re.MULTILINE
    )

    updated_frontmatter = re.sub(
        r'^current_step:.*$',
        f'current_step: "{step_name}"',
        updated_frontmatter,
        flags=re.MULTILINE
    )

    updated_frontmatter = re.sub(
        r'^percent:.*$',
        f'percent: {percent_value}',
        updated_frontmatter,
        flags=re.MULTILINE
    )

    updated_frontmatter = re.sub(
        r'^next_step:.*$',
        f'next_step: "{next_command}"',
        updated_frontmatter,
        flags=re.MULTILINE
    )

    updated_frontmatter = re.sub(
        r'^last_cmd:.*$',
        f'last_cmd: "{next_command}"',
        updated_frontmatter,
        flags=re.MULTILINE
    )

    # Reconstruct the file
    updated_content = f"---\n{updated_frontmatter}\n---{body}"

    # Backup original file
    backup_path = spec_file_path + '.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Write updated content
    with open(spec_file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Updated {spec_file_path}")
    print(f"  - current_step: {step_name}")
    print(f"  - percent: {percent_value}")
    print(f"  - next_step: {next_command}")
    print(f"  - last_cmd: {next_command}")
    print(f"  - status: 🔄 In Progress")

    return True


def main():
    if len(sys.argv) != 5:
        print("Usage: python update_sdd_metadata.py <path_to_spec_file> <step_name> <percent_value> <next_command>")
        print("Example: python update_sdd_metadata.py specs/myfeature/spec.md 'Specification' 25 '/sp.plan'")
        sys.exit(1)

    spec_file = sys.argv[1]
    step_name = sys.argv[2]
    percent_value = int(sys.argv[3])
    next_command = sys.argv[4]

    success = update_sdd_metadata(spec_file, step_name, percent_value, next_command)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()