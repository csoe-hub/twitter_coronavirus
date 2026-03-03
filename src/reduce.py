#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_paths", nargs="+", required=True)
    parser.add_argument("--output_path", required=True)
    args = parser.parse_args()

    combined = defaultdict(lambda: defaultdict(int))

    for path in args.input_paths:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                data = json.load(f)  # hashtag -> {lang/country -> count}
            except Exception as e:
                print(f"Skipping {path}: cannot parse JSON ({e})")
                continue

        for tag, inner in data.items():
            if not isinstance(inner, dict):
                continue
            for key, count in inner.items():
                combined[tag][key] += int(count)

    out = {tag: dict(inner) for tag, inner in combined.items()}

    with open(args.output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    print("Wrote reduced output to", args.output_path)

if __name__ == "__main__":
    main()
