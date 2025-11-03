# Contributing to Folder Organizer

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version)
- Relevant log output

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Why this feature would be useful
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Commit your changes** with clear, descriptive messages
6. **Push to your fork** and submit a pull request

## Coding Standards

### Python Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Code Example
```python
def get_file_age_days(file_path):
    """Calculate the age of a file in days based on modification time.

    Args:
        file_path: Path object pointing to the file

    Returns:
        int: Age of file in days
    """
    # Implementation here
```

### Configuration Changes
- Maintain backward compatibility when possible
- Update `config.yaml` with sensible defaults
- Document new configuration options in README.md

### Testing
- Test on multiple platforms if possible (macOS, Linux, Windows)
- Verify edge cases (empty folders, permission errors, etc.)
- Check that existing functionality still works

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/folder-organizer.git
cd folder-organizer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies (if added in future)
pip install -r requirements-dev.txt
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add dry-run mode for previewing changes

- Implement --dry-run flag
- Update documentation
- Add tests for dry-run functionality
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description if needed (wrap at 72 chars)

## Questions?

Feel free to open an issue with the `question` label if you need clarification on anything.

Thank you for contributing!
