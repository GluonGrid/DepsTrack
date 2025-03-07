# Contributing to DepsTrack

Thank you for considering contributing to DepsTrack! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to behave professionally and respectfully. We will not tolerate harassment, offensive comments, or any harmful behavior towards others.

## How Can I Contribute?

### Reporting Bugs

If you encounter a bug, please submit an issue with a detailed description:

1. **Title**: Concise description of the issue
2. **Environment**: Python version, operating system, and DepsTrack version
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Expected Behavior**: What you expected to happen
5. **Actual Behavior**: What actually happened
6. **Additional Information**: Logs, screenshots, or other relevant details

### Suggesting Enhancements

We welcome suggestions for improvements:

1. **Title**: Clear description of the enhancement
2. **Use Case**: Explain why this enhancement would be useful
3. **Proposed Implementation**: If you have ideas on how to implement it
4. **Alternative Approaches**: Any alternatives you've considered

### Pull Requests

We welcome code contributions through pull requests:

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Write or update tests for your changes
5. Run the test suite to ensure tests pass
6. Submit a pull request

#### Pull Request Guidelines

- Follow the existing code style
- Include tests for new features or bug fixes
- Update documentation as needed
- Keep pull requests focused on a single change
- Link related issues in the pull request description

## Development Environment

### Setting Up

```bash
# Clone the repository
git clone https://github.com/GluonGrid/DepsTrack.git
cd DepsTrack

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Code Style

We use [Black](https://black.readthedocs.io/) for code formatting and [Flake8](https://flake8.pycqa.org/) for linting:

```bash
# Format code
black .

# Check style
flake8
```

## Project Structure

```
DepsTrack/
├── depstrack/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── package_utils.py     # Package management utilities
│   ├── vulnerability.py     # Vulnerability checking
│   ├── output.py            # Output formatting
│   └── exclusions.py        # Exclusion handling
├── tests/                   # Test directory
├── README.md                # Project documentation
├── CONTRIBUTING.md          # Contributing guidelines
├── LICENSE                  # Project license
├── setup.py                 # Package setup file
└── requirements.txt         # Development requirements
```

## Feature Development Guidelines

### Adding a New Output Format

1. Create a new function in `output.py` named `output_<format>`
2. Add your format to the `--format` choices in `cli.py`
3. Update the tests in `tests/test_output.py`

### Adding a New Failure Condition

1. Add your condition to the `--fail-on` choices in `cli.py`
2. Implement the check in the main failure evaluation logic
3. Update the tests in `tests/test_failures.py`

### Adding New Exclusion Types

1. Update the parser in `exclusions.py`
2. Add handling in the failure evaluation logic
3. Update the tests in `tests/test_exclusions.py`

## Release Process

1. Update the version in `setup.py` and `__init__.py`
2. Update the CHANGELOG.md with the changes in the new version
3. Create a pull request for the version bump
4. Once merged, create a new release on GitHub
5. GitHub Actions will automatically publish to PyPI

## Getting Help

If you need help or have questions:

- Open an issue for specific questions related to the project
- Contact the maintainers for general inquiries

Thank you for contributing to DepsTrack!
