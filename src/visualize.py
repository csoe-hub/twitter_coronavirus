#!/usr/bin/env python3
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")  # required on servers (no display)
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True, help="Reduced JSON file from reduce.py")
    parser.add_argument("--key", required=True, help="Hashtag to visualize, e.g. #coronavirus")
    args = parser.parse_args()

    with open(args.input_path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)  # dict: hashtag -> {key -> count}

    hashtag = args.key
    if hashtag not in data:
        # be slightly forgiving (case)
        lowered = {k.lower(): k for k in data.keys()}
        if hashtag.lower() in lowered:
            hashtag = lowered[hashtag.lower()]
        else:
            print(f"Hashtag {args.key} not found in {args.input_path}")
            print("Available hashtags:", list(data.keys())[:20], "...")
            return

    counts = data[hashtag]  # dict: key -> count
    items = list(counts.items())

    # sort by count ascending, take top 10 (highest), then re-sort low->high for the plot
    items.sort(key=lambda kv: kv[1])
    top = items[-10:]
    top.sort(key=lambda kv: kv[1])

    labels = [k for k, v in top]
    values = [v for k, v in top]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)
    plt.xticks(rotation=45, ha="right")
    plt.title(f"Top 10 for {hashtag}")
    plt.tight_layout()

    base = os.path.basename(args.input_path)
    base_noext = base.split(".")[0]
    safe_tag = hashtag.replace("#", "").replace("/", "_")
    out_png = f"{safe_tag}_{base_noext}.png"

    plt.savefig(out_png, dpi=150)
    plt.close()

    print("Saved plot:", out_png)
    print("Top 10:")
    for k, v in reversed(top):
        print(k, v)


if __name__ == "__main__":
    main()
