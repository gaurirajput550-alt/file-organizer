# Smart File Organizer

A Python CLI tool that automatically sorts files in a folder into category
subfolders (Images, Documents, Videos, Audio, Archives, Code, Others) based
on file extension — with dry-run preview and one-command undo.

## Features
- 🗂️ Automatically categorizes files by extension
- 👀 `--dry-run` mode to preview changes before applying them
- ↩️ `--undo` to reverse the last organize operation
- 🔒 Never overwrites files — renames duplicates automatically
- 📦 Zero dependencies (pure Python standard library)

## Usage

```bash
# Organize a folder
python file_organizer.py /path/to/folder

# Preview what would happen, without moving anything
python file_organizer.py /path/to/folder --dry-run

# Undo the last organize operation
python file_organizer.py /path/to/folder --undo
```

## Example

Before:
```
Downloads/
├── invoice.pdf
├── vacation.jpg
├── song.mp3
└── script.py
```

After running `python file_organizer.py Downloads/`:
```
Downloads/
├── Documents/
│   └── invoice.pdf
├── Images/
│   └── vacation.jpg
├── Audio/
│   └── song.mp3
└── Code/
    └── script.py
```

## How it works
Each file's extension is matched against a category dictionary. Files are
moved into a subfolder named after their category, and every move is
recorded in a hidden `.file_organizer_log.json` file so it can be undone
with `--undo`.

## Requirements
- Python 3.7+
- No external dependencies

## License
MIT
