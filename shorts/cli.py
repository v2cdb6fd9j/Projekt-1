"""Command line: python -m shorts.cli make|batch ..."""
import argparse
import json
import os
import re
import time

import yaml

from . import render, script, tts


def load_channel(name: str) -> dict:
    with open(f"channels/{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def past_titles(channel: str) -> list[str]:
    path = f"output/{channel}/history.jsonl"
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line)["title"] for line in f if line.strip()]


def make(channel_name: str, idea: str | None, script_file: str | None) -> dict:
    channel = load_channel(channel_name)
    out_dir = f"output/{channel_name}"
    os.makedirs(out_dir, exist_ok=True)

    if script_file:
        with open(script_file, encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("tags", [])
        data.setdefault("description", data["title"])
    else:
        data = script.generate(channel, idea, past_titles(channel_name)[-30:])

    stem = f"{time.strftime('%Y%m%d-%H%M%S')}-{re.sub(r'[^a-z0-9]+', '-', data['title'].lower())[:40].strip('-')}"
    audio = f"{out_dir}/{stem}.mp3"
    video = f"{out_dir}/{stem}.mp4"

    words = tts.synthesize(data["narration"], channel["voice"], audio)
    render.render(channel, audio, words, video)

    hashtags = channel["hashtags"] + data["tags"]
    caption = data["description"] + "\n\n" + " ".join("#" + h for h in dict.fromkeys(hashtags))
    with open(f"{out_dir}/{stem}.txt", "w", encoding="utf-8") as f:
        f.write(f"{data['title']}\n\n{caption}\n")

    result = {"title": data["title"], "video": video, "caption": caption}
    with open(f"{out_dir}/history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")
    return result


def batch(count: int, channels: list[str]) -> None:
    """Make `count` videos per channel and write output/UPLOAD.md as a manual upload checklist."""
    rows = []
    for ch in channels:
        for _ in range(count):
            try:
                r = make(ch, None, None)
            except Exception as e:  # keep going if one video fails
                print(f"[{ch}] failed: {e}")
                continue
            rows.append((ch, r))
            print(f"[{ch}] {r['video']}")
    with open("output/UPLOAD.md", "w", encoding="utf-8") as f:
        f.write("# Upload checklist\n\nPost each video on YouTube Shorts, TikTok and Instagram Reels.\n\n")
        for ch, r in rows:
            f.write(f"## [ ] {ch}: {r['title']}\n\nFile: `{r['video']}`\n\n```\n{r['title']}\n\n{r['caption']}\n```\n\n")


def main():
    p = argparse.ArgumentParser(prog="shorts")
    sub = p.add_subparsers(dest="cmd", required=True)
    channels = ["facts", "motivation", "tech"]
    m = sub.add_parser("make", help="create one short")
    m.add_argument("--channel", required=True, choices=channels)
    m.add_argument("--idea")
    m.add_argument("--script-file", help="JSON with title/narration (skips the Claude API)")
    b = sub.add_parser("batch", help="create several shorts per channel + upload checklist")
    b.add_argument("--count", type=int, default=3, help="videos per channel")
    b.add_argument("--channel", choices=channels, action="append", help="repeatable; default all")
    a = p.parse_args()
    if a.cmd == "make":
        print(json.dumps(make(a.channel, a.idea, a.script_file), indent=2))
    else:
        batch(a.count, a.channel or channels)


if __name__ == "__main__":
    main()
