#!/usr/bin/env python3
"""
Folder Organizer
Automatically organizes files in specified folders into subfolders by type.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import yaml


class FolderOrganizer:
    """Organizes files in folders based on configurable rules."""

    def __init__(self, config_path=None):
        """Initialize the organizer with configuration."""
        self.config = self.load_config(config_path)
        self.setup_paths()

    def load_config(self, config_path=None):
        """Load configuration from YAML file."""
        if config_path is None:
            # Look for config in same directory as script
            script_dir = Path(__file__).parent.resolve()
            config_path = script_dir / "config.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            print(f"ERROR: Configuration file not found: {config_path}")
            print("Creating default config file...")
            self.create_default_config(config_path)

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"ERROR: Could not load configuration: {e}")
            sys.exit(1)

    def create_default_config(self, config_path):
        """Create a default configuration file."""
        default_config = """# Folder Organizer Configuration
directories:
  source: "~/Downloads"
  additional_sources: []
  projects_folder: "Projects"

file_mappings:
  Audio: [.mp3, .wav, .aac, .flac, .m4a, .wma, .ogg, .aiff]
  Documents: [.doc, .docx, .txt, .rtf, .odt, .pages, .md, .html, .py, .vcf, .vtt]
  Images: [.jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .tiff, .ico, .heic]
  PDFs: [.pdf]
  Videos: [.mp4, .avi, .mov, .mkv, .flv, .wmv, .webm, .m4v, .mpeg, .mpg]

filename_patterns:
  Screenshots: ["screenshot", "screen recording"]

age_management:
  archive_age_days: 30
  delete_age_days: 90
  log_rotation_days: 90

logging:
  log_file: "organize_log.txt"
  console_output: true

behavior:
  skip_hidden: true
  skip_app_bundles: true
  timestamp_conflicts: true
"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            f.write(default_config)
        print(f"Created default config at: {config_path}")

    def setup_paths(self):
        """Setup and validate paths from configuration."""
        # Main source directory
        self.source_dir = Path(self.config['directories']['source']).expanduser()

        # Additional source directories
        self.additional_sources = [
            Path(d).expanduser()
            for d in self.config['directories'].get('additional_sources', [])
        ]

        # Projects directory
        projects_folder = self.config['directories']['projects_folder']
        self.projects_dir = self.source_dir / projects_folder

        # Log file
        script_dir = Path(__file__).parent.resolve()
        log_file = self.config['logging']['log_file']
        if Path(log_file).is_absolute():
            self.log_file = Path(log_file)
        else:
            self.log_file = script_dir / log_file

    def log_message(self, message):
        """Log messages to file with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.log_file, 'a') as f:
            f.write(log_entry)

        if self.config['logging']['console_output']:
            print(log_entry.strip())

    def rotate_log(self):
        """Remove log entries older than specified days to prevent infinite growth."""
        rotation_days = self.config['age_management'].get('log_rotation_days', 90)

        if rotation_days <= 0 or not self.log_file.exists():
            return

        try:
            cutoff_date = datetime.now() - timedelta(days=rotation_days)

            with open(self.log_file, 'r') as f:
                lines = f.readlines()

            filtered_lines = []
            for line in lines:
                if line.startswith('[') and ']' in line:
                    try:
                        timestamp_str = line[1:20]
                        entry_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        if entry_date >= cutoff_date:
                            filtered_lines.append(line)
                    except (ValueError, IndexError):
                        filtered_lines.append(line)
                else:
                    filtered_lines.append(line)

            with open(self.log_file, 'w') as f:
                f.writelines(filtered_lines)

        except Exception as e:
            print(f"Warning: Could not rotate log file: {e}")

    def get_file_age_days(self, file_path):
        """Calculate the age of a file in days based on modification time."""
        try:
            mtime = file_path.stat().st_mtime
            file_date = datetime.fromtimestamp(mtime)
            age = datetime.now() - file_date
            return age.days
        except Exception as e:
            self.log_message(f"  WARNING: Could not determine age of {file_path.name}: {e}")
            return 0

    def get_destination_folder(self, file_path):
        """Determine the destination folder based on filename or file extension."""
        filename_lower = file_path.name.lower()

        # Check filename patterns
        for folder, patterns in self.config.get('filename_patterns', {}).items():
            for pattern in patterns:
                if pattern.lower() in filename_lower:
                    return folder

        # Check file extension
        extension = file_path.suffix.lower()

        for folder, extensions in self.config['file_mappings'].items():
            if extension in extensions:
                return folder

        # If no mapping found and file has an extension, send to Other folder
        if extension:
            return 'Other'

        return None

    def is_organizer_folder(self, folder_name):
        """Check if a folder is one of the organizer's category folders."""
        category_folders = set(self.config['file_mappings'].keys())
        category_folders.add('Other')
        category_folders.add(self.config['directories']['projects_folder'])
        return folder_name in category_folders

    def archive_old_files(self):
        """Move old files to archive and delete very old files."""
        archive_days = self.config['age_management'].get('archive_age_days', 0)
        delete_days = self.config['age_management'].get('delete_age_days', 0)

        if archive_days <= 0 and delete_days <= 0:
            return

        self.log_message("Checking for old files to archive or delete...")

        archived_count = 0
        deleted_count = 0
        error_count = 0

        # List of all category folders to check
        category_folders = list(self.config['file_mappings'].keys()) + ['Other']

        for category in category_folders:
            category_path = self.source_dir / category

            if not category_path.exists():
                continue

            try:
                for item in category_path.iterdir():
                    if item.is_dir():
                        continue

                    age_days = self.get_file_age_days(item)

                    # Delete files older than DELETE_AGE_DAYS
                    if delete_days > 0 and age_days >= delete_days:
                        try:
                            item.unlink()
                            self.log_message(f"  Deleted (>{delete_days} days old): {category}/{item.name}")
                            deleted_count += 1
                        except Exception as e:
                            self.log_message(f"  ERROR deleting {item.name}: {e}")
                            error_count += 1

                    # Archive files older than ARCHIVE_AGE_DAYS
                    elif archive_days > 0 and age_days >= archive_days:
                        archive_folder = category_path / "z_Archive"
                        archive_folder.mkdir(exist_ok=True)

                        destination_path = archive_folder / item.name

                        if destination_path.exists() and self.config['behavior']['timestamp_conflicts']:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            stem = destination_path.stem
                            suffix = destination_path.suffix
                            destination_path = archive_folder / f"{stem}_{timestamp}{suffix}"

                        try:
                            shutil.move(str(item), str(destination_path))
                            self.log_message(f"  Archived (>{archive_days} days old): {category}/{item.name} → {category}/z_Archive/")
                            archived_count += 1
                        except Exception as e:
                            self.log_message(f"  ERROR archiving {item.name}: {e}")
                            error_count += 1

            except Exception as e:
                self.log_message(f"  ERROR processing {category} folder: {e}")
                error_count += 1

        self.log_message(f"Archive/Delete complete: {archived_count} archived, {deleted_count} deleted, {error_count} errors")

    def organize_files_from_directory(self, source_dir, dir_name):
        """Organize files from a specific directory."""
        moved_count = 0
        skipped_count = 0
        error_count = 0

        if not source_dir.exists():
            self.log_message(f"  WARNING: Directory does not exist: {source_dir}")
            return moved_count, skipped_count, error_count

        try:
            items = list(source_dir.iterdir())

            for item in items:
                # Skip hidden items
                if self.config['behavior']['skip_hidden'] and item.name.startswith('.'):
                    skipped_count += 1
                    continue

                # Skip the script directory itself
                script_dir = Path(__file__).parent.resolve()
                if item == script_dir:
                    skipped_count += 1
                    continue

                # Handle directories
                if item.is_dir():
                    # Skip organizer category folders when in source directory
                    if source_dir == self.source_dir and self.is_organizer_folder(item.name):
                        skipped_count += 1
                        continue

                    # Skip .app bundles
                    if self.config['behavior']['skip_app_bundles'] and item.suffix == '.app':
                        skipped_count += 1
                        continue

                    # Move to projects folder
                    self.projects_dir.mkdir(exist_ok=True)
                    destination_path = self.projects_dir / item.name

                    if destination_path.exists() and self.config['behavior']['timestamp_conflicts']:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        destination_path = self.projects_dir / f"{item.name}_{timestamp}"

                    try:
                        shutil.move(str(item), str(destination_path))
                        rel_source = "source" if source_dir == self.source_dir else dir_name
                        self.log_message(f"  Moved folder from {rel_source}: {item.name} → Projects/")
                        moved_count += 1
                    except Exception as e:
                        self.log_message(f"  ERROR moving folder {item.name}: {e}")
                        error_count += 1
                    continue

                # Handle files
                destination_folder_name = self.get_destination_folder(item)

                if destination_folder_name is None:
                    self.log_message(f"  No mapping for ({dir_name}): {item.name}")
                    skipped_count += 1
                    continue

                destination_folder = self.source_dir / destination_folder_name
                destination_folder.mkdir(exist_ok=True)

                destination_path = destination_folder / item.name

                if destination_path.exists() and self.config['behavior']['timestamp_conflicts']:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    stem = destination_path.stem
                    suffix = destination_path.suffix
                    destination_path = destination_folder / f"{stem}_{timestamp}{suffix}"

                try:
                    shutil.move(str(item), str(destination_path))
                    rel_source = "source" if source_dir == self.source_dir else dir_name
                    self.log_message(f"  Moved from {rel_source}: {item.name} → {destination_folder_name}/")
                    moved_count += 1
                except Exception as e:
                    self.log_message(f"  ERROR moving {item.name}: {e}")
                    error_count += 1

        except Exception as e:
            self.log_message(f"FATAL ERROR in {dir_name}: {e}")
            error_count += 1

        return moved_count, skipped_count, error_count

    def organize(self):
        """Main organization method."""
        # Rotate log
        self.rotate_log()

        self.log_message("=" * 60)
        self.log_message(f"Starting file organization")

        total_moved = 0
        total_skipped = 0
        total_errors = 0

        # Organize main source directory
        self.log_message(f"Checking source directory: {self.source_dir}")
        moved, skipped, errors = self.organize_files_from_directory(
            self.source_dir, "source"
        )
        total_moved += moved
        total_skipped += skipped
        total_errors += errors

        # Organize additional directories
        for additional_dir in self.additional_sources:
            self.log_message(f"Checking additional directory: {additional_dir}")
            moved, skipped, errors = self.organize_files_from_directory(
                additional_dir, additional_dir.name
            )
            total_moved += moved
            total_skipped += skipped
            total_errors += errors

        self.log_message(
            f"Organization complete: {total_moved} moved, "
            f"{total_skipped} skipped, {total_errors} errors"
        )

        # Archive old files
        self.archive_old_files()

        self.log_message("=" * 60)


def main():
    """Main entry point with command-line argument support."""
    parser = argparse.ArgumentParser(
        description="Organize files in folders into categorized subfolders.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file (default: config.yaml in script directory)',
        default=None
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually moving files (not yet implemented)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Folder Organizer 1.0.0'
    )

    args = parser.parse_args()

    # Create and run organizer
    try:
        organizer = FolderOrganizer(config_path=args.config)
        organizer.organize()
    except KeyboardInterrupt:
        print("\nOrganization cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
