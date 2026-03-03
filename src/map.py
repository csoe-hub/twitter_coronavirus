#!/usr/bin/env python3
import argparse
import os
import zipfile
import json
import pickle
from collections import defaultdict


def load_hashtags(path: str) -> list[str]:
    tags = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            t = line.strip()
            if t:
                tags.append(t)
    return tags


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True, help="Path to geoTwitterYY-MM-DD.zip")
    parser.add_argument("--output_folder", default="outputs", help="Folder to write mapper outputs")
    parser.add_argument("--hashtags_path", default="./hashtags", help="Path to hashtags file")
    args = parser.parse_args()

    os.makedirs(args.output_folder, exist_ok=True)

    hashtags = load_hashtags(args.hashtags_path)
    hashtags_lc = [h.lower() for h in hashtags]

    # outputs are pickled dicts keyed by (hashtag, lang/country) -> count
    counter_lang = defaultdict(int)
    counter_country = defaultdict(int)

    with zipfile.ZipFile(args.input_path) as zf:
        for hour_file in zf.namelist():
            with zf.open(hour_file) as f:
                for raw_line in f:
                    try:
                        line = raw_line.decode("utf-8", errors="ignore").strip()
                        if not line:
                            continue
                        tweet = json.loads(line)
                    except Exception:
                        # malformed JSON / encoding issues / etc.
                        continue

                    text = (tweet.get("text") or "").lower()
                    lang = tweet.get("lang") or "unknown"

                    place = tweet.get("place")
                    country = "unknown"
                    if isinstance(place, dict):
                        country = place.get("country_code") or "unknown"

                    # hashtag matching (substring match)
                    for tag, tag_lc in zip(hashtags, hashtags_lc):
                        if tag_lc in text:
                            counter_lang[(tag, lang)] += 1
                            counter_country[(tag, country)] += 1

    base = os.path.basename(args.input_path)
    out_lang = os.path.join(args.output_folder, base + ".lang")
    out_country = os.path.join(args.output_folder, base + ".country")

    with open(out_lang, "wb") as f:
        pickle.dump(dict(counter_lang), f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(out_country, "wb") as f:
        pickle.dump(dict(counter_country), f, protocol=pickle.HIGHEST_PROTOCOL)

    print("Wrote:", out_lang)
    print("Wrote:", out_country)


if __name__ == "__main__":
    main()
