# Folder Organizer

> **Built with [Claude Code](https://claude.com/claude-code)** - A practical example of what you can create with AI-assisted development

A smart, configurable Python tool that automatically organizes files in your Downloads folder (or any folder) into categorized subfolders based on file type, with automatic archiving and cleanup of old files.

## Features

- **Automatic File Organization**: Sorts files into categorized folders (Documents, Images, Videos, etc.)
- **Highly Configurable**: Customize file type mappings, folder names, and behavior via YAML config
- **Multiple Directory Support**: Organize Downloads, Desktop, or any folders you specify
- **Smart Filename Detection**: Recognizes patterns like "Screenshot" in filenames
- **Age-Based Management**: Automatically archive old files and delete very old files
- **Safe Operation**: Handles filename conflicts with timestamps, skips hidden files
- **Comprehensive Logging**: Track all file movements with timestamped logs
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/folder-organizer.git
cd folder-organizer

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Basic Usage

```bash
# Run with default configuration
python organize_folders.py

# Or if installed as package
folder-organizer
```

On first run, a default `config.yaml` will be created. Edit it to customize your preferences.

## Configuration

The `config.yaml` file controls all aspects of organization:

```yaml
# Directories to organize
directories:
  source: "~/Downloads"           # Main folder to organize
  additional_sources:              # Additional folders (optional)
    - "~/Desktop"
  projects_folder: "Projects"      # Where to move directories

# File type mappings
file_mappings:
  Documents: [.pdf, .doc, .docx, .txt]
  Images: [.jpg, .png, .gif]
  Videos: [.mp4, .mov, .avi]
  # ... add your own categories

# Age-based management (in days)
age_management:
  archive_age_days: 30    # Move old files to Archive subfolder
  delete_age_days: 90     # Delete very old files (0 to disable)

# Behavior options
behavior:
  skip_hidden: true              # Skip files starting with .
  skip_app_bundles: true         # Skip .app bundles (macOS)
  timestamp_conflicts: true      # Add timestamps to duplicate filenames
```

### Configuration Options

#### Directories
- `source`: The main directory to organize (default: `~/Downloads`)
- `additional_sources`: List of additional directories to organize
- `projects_folder`: Name of folder to store moved directories

#### File Mappings
Define custom categories and their file extensions:

```yaml
file_mappings:
  MyDocuments: [.txt, .md, .doc]
  MyImages: [.jpg, .png]
  # Add as many categories as you need
```

#### Filename Patterns
Match files by name patterns instead of extensions:

```yaml
filename_patterns:
  Screenshots: ["screenshot", "screen recording"]
  WorkFiles: ["invoice", "receipt"]
```

#### Age Management
- `archive_age_days`: Files older than this are moved to `z_Archive` subfolder (0 to disable)
- `delete_age_days`: Files older than this are permanently deleted (0 to disable)
- `log_rotation_days`: Keep log entries for this many days

**Warning**: Deleted files cannot be recovered. Review archived files before they reach the deletion threshold.

## Command-Line Options

```bash
# Use a custom configuration file
python organize_folders.py --config /path/to/custom-config.yaml

# Show version
python organize_folders.py --version

# Show help
python organize_folders.py --help
```

## Running the Organizer

### On-Demand (Recommended)

Run manually whenever your folders need organizing:

```bash
python organize_folders.py
```

### macOS: Create a Double-Click App with Automator

The easiest way to run the organizer on Mac is to create an Automator app:

1. **Open Automator** (built into macOS)
2. Choose **"Application"** as document type
3. Search for **"Run Shell Script"** and drag it to the workflow
4. Paste this command (adjust the path to where you cloned this repo):
   ```bash
   /usr/bin/python3 "$HOME/path/to/folder-organizer/organize_folders.py"
   ```
5. **(Optional)** Add a notification:
   - Search for **"Display Notification"**
   - Drag it below the shell script
   - Set Title: `Organize Complete`
   - Set Message: `Your folders have been organized!`
6. Save the app to a convenient location (e.g., Downloads folder as **"🧹 Organize Downloads"**)

**First run:** macOS will ask for permissions to access your folders. Click "OK" to grant access.

**Usage:** Double-click the app whenever you want to organize your folders. Simple!

### Scheduled Automation (Advanced)

If you prefer automatic scheduling:

#### Linux/macOS (cron)

Add to crontab (`crontab -e`):

```bash
# Run daily at 9:00 AM
0 9 * * * /usr/bin/python3 /path/to/organize_folders.py
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 9:00 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\organize_folders.py`

**Note:** Scheduled automation may require additional setup for file access permissions.

## How It Works

1. **Scans** the configured directories for files and folders
2. **Categorizes** files based on extension or filename patterns
3. **Moves** files to appropriate category folders
4. **Handles** conflicts by adding timestamps to duplicate names
5. **Archives** files older than the archive threshold
6. **Deletes** files older than the deletion threshold
7. **Logs** all operations with timestamps

### File Organization Flow

```
Downloads/
├── document.pdf          → Downloads/PDFs/document.pdf
├── photo.jpg            → Downloads/Images/photo.jpg
├── Screenshot 2025.png  → Downloads/Screenshots/Screenshot 2025.png
├── project-folder/      → Downloads/Projects/project-folder/
└── unknown.xyz          → Downloads/Other/unknown.xyz
```

### Age-Based Management

```
Downloads/PDFs/
├── recent-file.pdf              (< 30 days old - stays)
├── z_Archive/
│   └── old-file.pdf             (30-90 days old - archived)
└── very-old-file.pdf is deleted (> 90 days old)
```

## Default File Categories

- **Audio**: mp3, wav, aac, flac, m4a, wma, ogg, aiff
- **Documents**: doc, docx, txt, rtf, odt, pages, md, html, py, vcf, vtt
- **Images**: jpg, jpeg, png, gif, bmp, svg, webp, tiff, ico, heic
- **Invitations**: ics
- **PDFs**: pdf
- **Presentations**: ppt, pptx, key, odp
- **Screenshots**: Files with "screenshot" or "screen recording" in name
- **Spreadsheets**: xls, xlsx, csv, numbers, ods
- **Videos**: mp4, avi, mov, mkv, flv, wmv, webm, m4v, mpeg, mpg
- **Other**: Any file with an extension not matching above categories

## Logging

All operations are logged to `organize_log.txt` with timestamps:

```
[2025-11-02 09:00:00] Starting file organization
[2025-11-02 09:00:01] Moved: document.pdf → PDFs/
[2025-11-02 09:00:01] Archived (>30 days old): PDFs/old-doc.pdf → PDFs/z_Archive/
[2025-11-02 09:00:02] Organization complete: 15 moved, 3 skipped, 0 errors
```

View the log:
```bash
cat organize_log.txt
# or
tail -f organize_log.txt  # Follow in real-time
```

## Safety Features

- **No Accidental Deletion**: Only deletes files exceeding configured age (disabled by default)
- **Conflict Handling**: Adds timestamps instead of overwriting
- **Hidden File Protection**: Skips hidden files by default
- **Category Folder Protection**: Won't move the organizer's own category folders
- **Error Recovery**: Continues operation even if individual files fail
- **Comprehensive Logging**: Track all operations for review

## Troubleshooting

### Permission Errors
Ensure you have read/write permissions for the directories:
```bash
chmod +x organize_folders.py
```

### Missing Dependencies
Install PyYAML:
```bash
pip install -r requirements.txt
```

### Config Not Found
On first run, a default config will be created automatically. To manually create:
```bash
python organize_folders.py
```

### Files Not Moving
- Check the log file for errors
- Verify file extensions match your config
- Ensure destination folders are writable

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the common need to keep Downloads folders organized
- Built with Python's standard library and PyYAML

## Roadmap

- [ ] Dry-run mode to preview changes
- [ ] GUI interface
- [ ] Undo last organization
- [ ] Cloud folder support (Dropbox, Google Drive, etc.)
- [ ] File deduplication
- [ ] Smart learning from manual file moves
- [ ] Plugin system for custom organizers

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the log file for detailed error messages

---

Made with ❤️ for everyone tired of messy Downloads folders
