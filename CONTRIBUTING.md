# Contributing to MP3 Downloader

Thank you for your interest in contributing to the MP3 Downloader project! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- FFmpeg
- Basic knowledge of Flask and web development

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/mp3-downloader.git
   cd mp3-downloader
   ```

2. **Set up the development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Run tests**
   ```bash
   pytest tests/
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes** - Fix issues in existing code
- **Feature additions** - Add new functionality
- **Documentation** - Improve or add documentation
- **Performance improvements** - Optimize existing code
- **Platform support** - Add support for new platforms
- **UI/UX improvements** - Enhance user interface
- **Testing** - Add or improve test coverage

### Before You Start

1. **Check existing issues** - Look for existing issues or feature requests
2. **Create an issue** - If none exists, create one to discuss your idea
3. **Get feedback** - Wait for maintainer feedback before starting work
4. **Assign yourself** - Comment on the issue to get it assigned to you

## Pull Request Process

### 1. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add support for new platform XYZ"

# Or for bug fixes
git commit -m "fix: resolve download timeout issue"
```

**Commit Message Format:**
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 4. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

### 5. Pull Request Requirements

Your PR should include:

- **Clear description** - Explain what changes you made and why
- **Issue reference** - Link to the related issue (e.g., "Fixes #123")
- **Screenshots** - For UI changes, include before/after screenshots
- **Testing** - Describe how you tested your changes
- **Documentation** - Update relevant documentation

### 6. Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black formatter)
- **Imports**: Use isort for import organization
- **Type hints**: Use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Code Formatting

We use automated tools for code formatting:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

### Example Code Style

```python
from typing import Dict, List, Optional

def download_audio(
    url: str, 
    quality: str = "192k", 
    format: str = "mp3"
) -> Dict[str, str]:
    """Download audio from a given URL.
    
    Args:
        url: The URL to download from
        quality: Audio quality (default: "192k")
        format: Output format (default: "mp3")
        
    Returns:
        Dictionary containing download information
        
    Raises:
        ValueError: If URL is invalid
        DownloadError: If download fails
    """
    if not url:
        raise ValueError("URL cannot be empty")
    
    # Implementation here
    return {"status": "success", "filename": "audio.mp3"}
```

## Testing

### Writing Tests

- Write tests for all new functionality
- Use pytest for testing framework
- Aim for high test coverage (>80%)
- Include both unit tests and integration tests

### Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock

class TestDownloadFunction:
    """Test cases for download functionality."""
    
    def test_valid_url_download(self):
        """Test downloading with a valid URL."""
        # Test implementation
        pass
    
    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises appropriate error."""
        with pytest.raises(ValueError):
            download_audio("")
    
    @patch('main.yt_dlp.YoutubeDL')
    def test_download_with_mock(self, mock_ydl):
        """Test download with mocked dependencies."""
        # Test implementation with mocks
        pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::TestDownloadFunction::test_valid_url_download
```

## Documentation

### Code Documentation

- Use clear, descriptive variable and function names
- Add docstrings to all public functions and classes
- Include type hints for better code understanding
- Comment complex logic or algorithms

### API Documentation

- Update `API.md` for any API changes
- Include request/response examples
- Document error conditions and status codes

### README Updates

- Update installation instructions if dependencies change
- Add new features to the features list
- Update usage examples if needed

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Environment details** (OS, Python version, etc.)
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Error messages** or logs
- **Screenshots** if applicable

### Feature Requests

For feature requests, please include:

- **Clear description** of the proposed feature
- **Use case** - why is this feature needed?
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**

### Issue Templates

Use the provided issue templates when creating new issues:

- Bug Report Template
- Feature Request Template
- Documentation Improvement Template

## Platform Support

### Adding New Platforms

To add support for a new platform:

1. **Research the platform** - Understand their API/scraping requirements
2. **Check legal compliance** - Ensure it's legal to download from the platform
3. **Implement detection** - Add URL pattern matching in `detect_platform()`
4. **Add configuration** - Add platform toggle in `config.py`
5. **Implement download logic** - Modify `download_audio()` function
6. **Add tests** - Create comprehensive tests for the new platform
7. **Update documentation** - Add platform to supported list

### Platform Guidelines

- Respect robots.txt and terms of service
- Implement rate limiting to avoid overwhelming servers
- Handle errors gracefully
- Provide clear error messages to users

## Performance Considerations

### Optimization Guidelines

- **Async operations** - Use async/await for I/O operations when possible
- **Caching** - Cache frequently accessed data
- **Memory usage** - Be mindful of memory consumption for large files
- **Error handling** - Implement proper error handling and recovery
- **Resource cleanup** - Always clean up temporary files and resources

### Profiling

```bash
# Profile memory usage
python -m memory_profiler main.py

# Profile execution time
python -m cProfile -o profile.stats main.py
```

## Security Guidelines

### Security Best Practices

- **Input validation** - Validate all user inputs
- **SQL injection** - Use parameterized queries (if using databases)
- **XSS prevention** - Escape user content in templates
- **File uploads** - Validate file types and sizes
- **Dependencies** - Keep dependencies updated
- **Secrets** - Never commit API keys or secrets

### Security Testing

```bash
# Run security checks
bandit -r .

# Check for known vulnerabilities
safety check
```

## Release Process

### Version Numbering

We follow Semantic Versioning (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality
- **PATCH** version for backwards-compatible bug fixes

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version number is bumped
- [ ] Changelog is updated
- [ ] Security scan passes
- [ ] Performance benchmarks are acceptable

## Getting Help

### Communication Channels

- **GitHub Issues** - For bug reports and feature requests
- **GitHub Discussions** - For general questions and discussions
- **Email** - For security-related issues (contact maintainers directly)

### Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [Python Testing with pytest](https://docs.pytest.org/)
- [Git Workflow Guide](https://www.atlassian.com/git/tutorials/comparing-workflows)

## Recognition

Contributors will be recognized in:

- **README.md** - Contributors section
- **CHANGELOG.md** - Release notes
- **GitHub** - Contributor graphs and statistics

Thank you for contributing to MP3 Downloader! 🎵