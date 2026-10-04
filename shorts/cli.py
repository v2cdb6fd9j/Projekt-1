"""Command line: python -m shorts.cli make --channel facts [--idea ...] [--upload]"""
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


def make(channel_name: str, idea: str | None, script_file: str | None, do_upload: bool) -> dict:
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
    if do_upload:
        from . import upload_youtube

        result["youtube"] = upload_youtube.upload(
            channel, video, data["title"], caption, list(dict.fromkeys(hashtags))
        )
    with open(f"{out_dir}/history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")
    return result


def main():
    p = argparse.ArgumentParser(prog="shorts")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="create one short")
    m.add_argument("--channel", required=True, choices=["facts", "motivation", "tech"])
    m.add_argument("--idea")
    m.add_argument("--script-file", help="JSON with title/narration (skips the Claude API)")
    m.add_argument("--upload", action="store_true", help="upload to YouTube after rendering")
    a = p.parse_args()
    print(json.dumps(make(a.channel, a.idea, a.script_file, a.upload), indent=2))


if __name__ == "__main__":
    main()
