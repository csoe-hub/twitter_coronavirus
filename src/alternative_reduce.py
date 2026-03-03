#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
from collections import defaultdict
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_date_from_filename(path: str) -> datetime | None:
    """
    Extract YYYY-MM-DD from filenames like:
      outputs/geoTwitter20-12-31.lang
      outputs/geoTwitter20-01-01.zip.lang
    """
    base = os.path.basename(path)

    # common patterns
    m = re.search(r"geoTwitter(\d{2})-(\d{2})-(\d{2})", base)
    if not m:
        return None

    yy, mm, dd = m.groups()
    # tweets are 2020
    return datetime(int("20" + yy), int(mm), int(dd))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "hashtags",
        nargs="+",
        help="Hashtags/keywords to plot (must match keys in .lang files, e.g. coronavirus covid19 코로나바이러스)",
    )
    parser.add_argument(
        "--outputs_folder",
        default="outputs",
        help="Folder containing mapper outputs (*.lang files). Default: outputs",
    )
    parser.add_argument(
        "--out_png",
        default="alternative_reduce.png",
        help="Output PNG filename. Default: alternative_reduce.png",
    )
    args = parser.parse_args()

    # We will build: series[tag][date] = count
    series = {tag: {} for tag in args.hashtags}

    lang_files = sorted(glob.glob(os.path.join(args.outputs_folder, "*.lang")))
    if not lang_files:
        print(f"No .lang files found in {args.outputs_folder}/")
        return

    # Read each day’s file, sum hashtag counts across languages
    for path in lang_files:
        day = parse_date_from_filename(path)
        if day is None:
            # skip unknown filename format
            continue
        day_str = day.strftime("%Y-%m-%d")

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)  # hashtag -> {lang -> count}
        except Exception as e:
            print(f"Skipping {path}: {e}")
            continue

        for tag in args.hashtags:
            if tag in data and isinstance(data[tag], dict):
                total = sum(int(v) for v in data[tag].values())
            else:
                total = 0
            series[tag][day_str] = total

    # Determine x-axis (all dates seen across files), sorted
    all_dates = sorted({d for tag in series for d in series[tag].keys()})
    if not all_dates:
        print("No dates parsed from filenames. Check your .lang filenames.")
        return

    # Convert dates to day-of-year numbers for plotting, but keep labels sparse
    x = [datetime.strptime(d, "%Y-%m-%d").timetuple().tm_yday for d in all_dates]

    plt.figure(figsize=(12, 6))

    for tag in args.hashtags:
        y = [series[tag].get(d, 0) for d in all_dates]
        plt.plot(x, y, label=tag)

    plt.xlabel("Day of Year (2020)")
    plt.ylabel("Number of tweets using hashtag")
    plt.title("Hashtag usage over time (2020)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.out_png, dpi=150)
    plt.close()

    print("Saved:", args.out_png)


if __name__ == "__main__":
    main()
