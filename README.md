# Python System Diagnostic Tool

A beginner-friendly command-line project that checks basic computer and Python setup information.

## Features

- Reports operating system, machine type, Python version, and Python executable path.
- Checks available disk space.
- Checks whether `git`, `pip`, and `pytest` can be found.
- Reports environment-variable names, but **does not show their values** because values may contain passwords or API tokens.
- Optionally validates a JSON configuration file.
- Prints a readable text report or JSON.
- Saves reports to a file.
- Includes unit tests for important behaviours.

## Requirements

- Python 3.10 or newer
- No third-party runtime packages are required

## 1. Download or extract the project

Extract the ZIP file, then open a terminal/command prompt inside the `python_system_diagnostic_tool` folder.

## 2. Create a virtual environment (recommended)

### Windows

```bash
py -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install the project

```bash
python -m pip install -e .
```

## 4. Run the tool

Readable text report:

```bash
machine-diagnostic
```

JSON report:

```bash
machine-diagnostic --format json
```

Save a text report:

```bash
machine-diagnostic --output report.txt
```

Save a JSON report:

```bash
machine-diagnostic --format json --output report.json
```

## 5. Test configuration files

Create a file named `config.json` containing:

```json
{
  "project_name": "my-demo-project",
  "environment": "development"
}
```

Validate it:

```bash
machine-diagnostic --config config.json
```

Try a missing or invalid JSON path to see how the program reports configuration errors.

## 6. Run unit tests

Install pytest if it is not already available:

```bash
python -m pip install pytest
```

Then run:

```bash
python -m pytest
```

You can also use Python's built-in test runner:

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
python_system_diagnostic_tool/
├── pyproject.toml
├── README.md
├── src/
│   └── machine_diag/
│       ├── __init__.py
│       └── cli.py
└── tests/
    └── test_cli.py
```

## Exit codes

- `0`: The report was generated successfully. Configuration problems are included in the report rather than crashing the tool.
- `2`: The report could not be written to the requested output file.

## Before publishing

1. Run the tool and unit tests.
2. Read the generated report and make sure it contains no private information.
3. Create a public GitHub repository.
4. Upload the project files and README.
5. Submit the public repository URL as the task proof if the internship portal accepts repository links.

Do not upload personal reports, passwords, access tokens, or other private system information to a public repository.
