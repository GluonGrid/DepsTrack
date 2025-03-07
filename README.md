# DepsTrack

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)

DepsTrack is a powerful Python dependency scanner that checks for updates, vulnerabilities, and yanked packages. It's designed to integrate with CI/CD pipelines and help you keep your dependencies secure and up-to-date.

## Features

- **Multiple vulnerability checks**: Uses OSV.dev to scan for known vulnerabilities in dependencies
- **CVSS severity scoring**: Evaluates vulnerability severity (LOW, MEDIUM, HIGH, CRITICAL)
- **Update detection**: Identifies available updates (patch, minor, major)
- **Yanked package detection**: Warns about yanked/deprecated packages
- **CI/CD integration**: Flexible exit codes for pipeline integration
- **Multiple output formats**: Text, JSON, Markdown, and GitHub Annotations
- **Package filtering**: Include/exclude specific packages
- **Customizable failure conditions**: Granular control over what causes build failures
- **Advanced exclusions**: Selectively exclude packages from specific conditions
- **Severity-specific exclusions**: Fine-grained control over vulnerability severity thresholds by package

## Installation

```bash
pip install depstrack
```

Or with UV (recommended):

```bash
uv pip install depstrack
```

## Usage

### Basic Usage

```bash
# Check all installed packages
depstrack

# Check packages defined in requirements.txt
depstrack --requirements requirements.txt

# Increase verbosity (show more info)
depstrack -v

# Show all packages, including those with no issues
depstrack -vv
```

### Output Formats

```bash
# Default colored text output
depstrack

# JSON output (useful for programmatic processing)
depstrack --format json

# Markdown output (useful for reports)
depstrack --format markdown --output-file dependencies-report.md

# GitHub Actions annotations (for GitHub CI)
depstrack --format github
```

### CI/CD Integration

```bash
# Fail if any vulnerability with HIGH or CRITICAL severity is found
depstrack --fail-on vulnerability --min-severity HIGH

# Fail on yanked packages or major updates
depstrack --fail-on yanked major-update

# Fail on all issues (vulnerabilities, updates, yanked packages)
depstrack --fail-on all
```

### Package Filtering

```bash
# Only check specific packages
depstrack --include requests flask

# Exclude certain packages
depstrack --exclude dev-packages test-tools
```

### Advanced Exclusions

```bash
# Exclude Django from major update checks
depstrack --fail-on all --exclude-from "major-update:django"

# Exclude multiple packages from specific conditions
depstrack --fail-on all \
  --exclude-from "major-update:django,flask" \
  --exclude-from "yanked:requests"

# Package-centric exclusions
depstrack --fail-on all \
  --exclude-package "django:major-update,minor-update"

# Exclude Django from CRITICAL vulnerability checks
depstrack --fail-on vulnerability --min-severity MEDIUM \
  --exclude-from "vulnerability[CRITICAL]:django"

# Complex exclusion patterns
depstrack --fail-on all \
  --exclude-package "legacy-app:vulnerability[HIGH],major-update" \
  --exclude-from "vulnerability[MEDIUM]:dev-tools"
```

## Examples

### Basic Dependency Check

```bash
depstrack
```

Output:
```
LEGEND
--------------------------------------------------------------------------------
⬆️  Major update available (potential breaking changes)
⬆️  Minor update available (new features)
⬆️  Patch update available (bug fixes)
💀 Yanked/deprecated version
🚨 Security vulnerability
⬇️  Installed version higher than latest release
✓ Up-to-date and secure package

DEPENDENCY CHECK SUMMARY
================================================================================
Total packages checked: 125
▶ 2 with security vulnerabilities
▶ 1 with yanked/deprecated versions
▶ 15 with available updates
================================================================================

SECURITY VULNERABILITIES
--------------------------------------------------------------------------------
django                   4.2.16 → 5.1.6                ⬆️  🚨
  Released: 2025-02-05 | Changelog: https://pypi.org/project/django/5.1.6/
  • Major update available: may contain breaking changes!
  • Security vulnerabilities:
    ▪ GHSA-m9g8-fxxm-xg86 (CVSS_V3, Score: 9.8, Severity: Critical)
      Django SQL injection in HasKey(lhs, rhs) on Oracle
...
```

### GitHub Actions Integration

Add to your workflow file (`.github/workflows/security.yml`):

```yaml
name: Dependency Check

on:
  schedule:
    - cron: '0 8 * * 1'  # Run every Monday at 8am
  push:
    paths:
      - 'requirements.txt'
      - 'setup.py'

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install depstrack
          pip install -r requirements.txt
      
      - name: Check for vulnerabilities
        run: |
          depstrack --format github --fail-on vulnerability --min-severity HIGH
```

## License

MIT License - See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.
