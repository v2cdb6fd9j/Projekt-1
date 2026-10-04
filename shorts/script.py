"""Generate a short-form video script with the Claude API."""
import json
import os
import re

import anthropic

MODEL = os.environ.get("SHORTS_MODEL", "claude-sonnet-5-5")

SYSTEM = """You write scripts for 30-45 second vertical videos (YouTube Shorts, TikTok, Reels).
Return ONLY a JSON object with keys:
  "title": catchy title, max 70 chars, no hashtags
  "narration": the spoken text, 70-110 words, plain sentences, no stage directions, no emojis
  "description": 1-2 sentence caption for the post
  "tags": list of 3-6 extra lowercase hashtag words (no #)
Never invent statistics or quotes. If unsure of a fact, pick a different one."""


def generate(channel: dict, idea: str | None = None, avoid: list[str] | None = None) -> dict:
    client = anthropic.Anthropic()
    prompt = (
        f"Channel topic: {channel['topic']}\n"
        f"Style guide: {channel['style']}\n"
        f"Language: English\n"
        + (f"Specific idea: {idea}\n" if idea else "Pick a fresh idea yourself.\n")
        + (f"Do NOT repeat these earlier titles: {json.dumps(avoid)}\n" if avoid else "")
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON in model reply: {text[:200]}")
    data = json.loads(match.group(0))
    for key in ("title", "narration", "description"):
        if not data.get(key):
            raise ValueError(f"Script missing '{key}'")
    data.setdefault("tags", [])
    return data
