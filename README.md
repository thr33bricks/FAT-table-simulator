# FAT-table-simulator

My course work for the Operating Systems class at the University of Ruse. This project implements a FAT table simulator that simulates a FAT table with **10 blocks × 1024 B**.

## Building the Executable

**1. Install PyInstaller:**

```bash
pip install pyinstaller
```

**2. Build the .exe file:**

```bash
python -m PyInstaller --onefile --windowed fat_sim.py
```

> **Note:** The generated executable will appear in the `dist/` directory.

## Running the Application

Run the script directly with Python:

```bash
python fat_sim.py
```
