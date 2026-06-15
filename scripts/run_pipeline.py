import subprocess
import sys

COMMANDS = [
    ["python", "scripts/validate_history.py"],
    ["python", "scripts/update_workbook_from_csv.py"],
    ["python", "scripts/compare_workbooks.py"],
]


def run(command):
    print()
    print("$ " + " ".join(command))
    result = subprocess.run(command)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    for command in COMMANDS:
        run(command)

    print()
    print("Pipeline OK")


if __name__ == "__main__":
    main()
