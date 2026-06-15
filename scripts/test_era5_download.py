from pathlib import Path
import cdsapi

OUTPUT = Path("data/test_era5_single_point.nc")

def main():
    client = cdsapi.Client()

    request = {
        "product_type": ["reanalysis"],
        "variable": ["2m_temperature"],
        "year": ["2024"],
        "month": ["01"],
        "day": ["01"],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        # Small area around Switzerland / Alpine region.
        # Format: North, West, South, East
        "area": [48, 5, 45, 11],
    }

    client.retrieve(
        "reanalysis-era5-single-levels",
        request,
        str(OUTPUT),
    )

    print(f"Downloaded: {OUTPUT}")
    print(f"Size bytes: {OUTPUT.stat().st_size}")

if __name__ == "__main__":
    main()
