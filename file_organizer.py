#!/usr/bin/env python3
"""
Smart File Organizer
=====================
Automatically sorts files in a folder into category subfolders
(Images, Documents, Videos, Audio, Archives, Code, Others) based
on file extension.

Features:
- Dry-run mode (preview changes without moving anything)
- Undo support (reverses the last run using a JSON log)
- Handles duplicate filenames safely
- Clean CLI with argparse

Usage:
    python file_organizer.py <folder_path>
    python file_organizer.py <folder_path> --dry-run
    python file_organizer.py <folder_path> --undo
"""

import argparse
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

# ---- Configuration: extension -> category mapping ----
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx", ".csv", ".md"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json"],
}

LOG_FILE = ".file_organizer_log.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


def get_category(file_ext: str) -> str:
    """Return the category name for a given file extension."""
    for category, extensions in CATEGORIES.items():
        if file_ext.lower() in extensions:
            return category
    return "Others"


def unique_destination(dest: Path) -> Path:
    """If dest already exists, append a counter to avoid overwriting files."""
    if not dest.exists():
        return dest
    counter = 1
    stem, suffix = dest.stem, dest.suffix
    parent = dest.parent
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize(folder: Path, dry_run: bool = False) -> None:
    """Organize all files in `folder` into category subfolders."""
    if not folder.is_dir():
        logger.error(f"Error: '{folder}' is not a valid directory.")
        return

    moves = []  # list of (original_path, new_path) for undo log

    files = [f for f in folder.iterdir() if f.is_file() and f.name != LOG_FILE]

    if not files:
        logger.info("No files to organize.")
        return

    for file_path in files:
        category = get_category(file_path.suffix)
        target_dir = folder / category
        destination = unique_destination(target_dir / file_path.name)

        if dry_run:
            logger.info(f"[DRY RUN] {file_path.name} -> {category}/{destination.name}")
        else:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(file_path), str(destination))
            logger.info(f"Moved: {file_path.name} -> {category}/{destination.name}")
            moves.append({"original": str(file_path), "new": str(destination)})

    if not dry_run and moves:
        log_data = {"timestamp": datetime.now().isoformat(), "moves": moves}
        (folder / LOG_FILE).write_text(json.dumps(log_data, indent=2))
        logger.info(f"\n{len(moves)} file(s) organized. Run with --undo to reverse.")
    elif dry_run:
        logger.info(f"\n[DRY RUN] {len(files)} file(s) would be organized. No changes made.")


def undo(folder: Path) -> None:
    """Reverse the last organize run using the saved log file."""
    log_path = folder / LOG_FILE
    if not log_path.exists():
        logger.error("No undo log found. Nothing to undo.")
        return

    log_data = json.loads(log_path.read_text())
    moves = log_data.get("moves", [])

    for move in reversed(moves):
        new_path = Path(move["new"])
        original_path = Path(move["original"])
        if new_path.exists():
            original_path.parent.mkdir(exist_ok=True)
            shutil.move(str(new_path), str(original_path))
            logger.info(f"Restored: {new_path.name} -> {original_path}")

    log_path.unlink()
    logger.info(f"\n{len(moves)} file(s) restored.")


def main():
    parser = argparse.ArgumentParser(
        description="Organize files in a folder into category subfolders."
    )
    parser.add_argument("folder", type=str, help="Path to the folder to organize")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without moving files"
    )
    parser.add_argument(
        "--undo", action="store_true", help="Undo the last organize operation"
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()

    if args.undo:
        undo(folder)
    else:
        organize(folder, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
