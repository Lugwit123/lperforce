# LPerforce Rez Package

Lugwit Perforce Library - P4 integration utilities for Python.

## Overview

This package provides Perforce (P4) integration utilities including:
- P4 base library functions
- P4 login utilities
- Workspace management
- Client operations

## Installation

```bash
cd rez-package-source/lperforce
build.bat
```

## Usage

In a Rez environment:

```bash
rez env lperforce
```

In Python:

```python
from lperforce import p4_baselib, loginP4
```

## Dependencies

- Python 3.7+
- Perforce P4 Python API (P4Python)

## Structure

```
lperforce/
├── package.py          # Rez package definition
├── build.bat          # Build script
├── README.md          # This file
└── src/
    └── lperforce/     # Source code (LPerforce library)
```

## Environment Variables

- `LPERFORCE_ROOT`: Root directory of the lperforce package
- `PYTHONPATH`: Automatically includes `{root}/src`

## Notes

- This package is designed to work within the Lugwit toolchain
- Requires P4Python to be installed separately

