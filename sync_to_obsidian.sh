#!/bin/bash

# Sync script to copy project files to Windows Obsidian vault
echo "Syncing AI Employee project to Obsidian vault..."

# Source directories in WSL
SOURCE_BASE="/home/mubashar/code/Hackathon-0/Dig-AI-FTE"
TARGET_BASE="/mnt/d/Hackathon-0/Obsidian_vault/FTE-Vualt"

# Directories to sync
DIRECTORIES=("00_Workspace" "10_Governance" "20_Archive" "30_Specifications" "specs" "99_Internal")

# Sync each directory
for dir in "${DIRECTORIES[@]}"; do
    if [ -d "$SOURCE_BASE/$dir" ]; then
        echo "Syncing $dir..."
        rsync -av --delete "$SOURCE_BASE/$dir/" "$TARGET_BASE/$dir/"
    else
        echo "Warning: $SOURCE_BASE/$dir does not exist"
    fi
done

echo "Sync completed!"
echo "Files updated in: $TARGET_BASE"