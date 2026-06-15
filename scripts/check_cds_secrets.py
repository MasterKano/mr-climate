import os
import sys

required = ["CDSAPI_URL", "CDSAPI_KEY"]
missing = [name for name in required if not os.getenv(name)]

if missing:
    print("Missing environment variables:")
    for name in missing:
        print(f"- {name}")
    print()
    print("For GitHub Actions, add these as repository secrets:")
    print("- Settings > Secrets and variables > Actions > New repository secret")
    sys.exit(1)

print("CDS secret environment variables are present.")
