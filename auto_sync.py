#!/usr/bin/env python3
"""
Automatic sync script for AI Employee project to Obsidian vault
Monitors project files and automatically syncs to Windows Obsidian vault
"""

import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class SyncHandler(FileSystemEventHandler):
    def __init__(self, source_base, target_base, directories_to_watch):
        self.source_base = Path(source_base)
        self.target_base = Path(target_base)
        self.directories_to_watch = directories_to_watch

    def on_modified(self, event):
        if event.is_directory:
            return

        # Check if the modified file is in one of our watched directories
        file_path = Path(event.src_path)
        for watched_dir in self.directories_to_watch:
            if str(file_path).startswith(str(self.source_base / watched_dir)):
                self.sync_project()
                break

    def on_created(self, event):
        if event.is_directory:
            return

        # Check if the created file is in one of our watched directories
        file_path = Path(event.src_path)
        for watched_dir in self.directories_to_watch:
            if str(file_path).startswith(str(self.source_base / watched_dir)):
                self.sync_project()
                break

    def sync_project(self):
        """Sync the project to Obsidian vault"""
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Detected change, syncing to Obsidian...")

            # Directories to sync
            for dir_name in self.directories_to_watch:
                source_dir = self.source_base / dir_name
                target_dir = self.target_base / dir_name

                if source_dir.exists():
                    # Use rsync to sync the directory
                    cmd = ['rsync', '-av', '--delete', str(source_dir) + '/', str(target_dir) + '/']
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print(f"[{time.strftime('%H:%M:%S')}] Sync completed!")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Sync failed: {str(e)}")

def main():
    # Configuration
    SOURCE_BASE = "/home/mubashar/code/Hackathon-0/Dig-AI-FTE"
    TARGET_BASE = "/mnt/d/Hackathon-0/Obsidian_vault/FTE-Vualt"
    DIRECTORIES_TO_WATCH = ["00_Workspace", "10_Governance", "20_Archive", "30_Specifications", "specs", "99_Internal"]

    # Create the sync handler
    event_handler = SyncHandler(SOURCE_BASE, TARGET_BASE, DIRECTORIES_TO_WATCH)

    # Create observer
    observer = Observer()

    # Schedule the observer for each directory to watch
    for dir_name in DIRECTORIES_TO_WATCH:
        watch_path = Path(SOURCE_BASE) / dir_name
        if watch_path.exists():
            observer.schedule(event_handler, str(watch_path), recursive=True)
            print(f"Watching: {watch_path}")

    # Start the observer
    observer.start()
    print("Auto-sync started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping auto-sync...")

    observer.join()

if __name__ == "__main__":
    main()