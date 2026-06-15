import argparse
import subprocess
import sys

LOCAL_COMMANDS = [
    ["python", "scripts/validate_history.py"],
    ["python", "scripts/update_workbook_from_csv.py"],
    ["python", "scripts/compare_workbooks.py"],
]

FULL_COMMANDS = [
    ["python", "scripts/fetch_weather.py"],
    # Later:
    # ["python", "scripts/fetch_weather.py", "--download"],
    # ["python", "scripts/process_era5_file.py", "YYYY", "MM"],
    # ["python", "scripts/append_new_rows.py"],
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full pipeline skeleton, including fetch dry run.",
    )
    args = parser.parse_args()

    commands = FULL_COMMANDS if args.full else LOCAL_COMMANDS

    for command in commands:
        run(command)

    print()
    print("Pipeline OK")


if __name__ == "__main__":
    main()
