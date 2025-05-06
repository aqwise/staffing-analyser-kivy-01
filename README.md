# Staffing Analyzer

A Kivy-based application for staffing analysis.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the application in development mode:
```bash
python main.py
```

## Building for Windows

To create a standalone Windows executable:

1. Ensure PyInstaller is installed:
```bash
pip install pyinstaller
```

2. Build the executable using the spec file:
```bash
pyinstaller StaffingAnalyzer.spec
```

The executable will be created in the `dist` folder as `StaffingAnalyzer.exe`.

### Build Output

After successful build:
- The executable will be located at `dist/StaffingAnalyzer/StaffingAnalyzer.exe`
- Double-click the executable to run the application
- No Python installation is required to run the built executable

## Development

- `main.py` - Main application entry point
- `logic.py` - Business logic implementation
- `ui.kv` - Kivy UI layout definitions