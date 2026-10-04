"""Text-to-speech with word-level timestamps (edge-tts)."""
import asyncio

import edge_tts

TICKS_PER_SEC = 10_000_000


async def _synth(text: str, voice: str, out_path: str, rate: str):
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(out_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / TICKS_PER_SEC
                words.append(
                    {
                        "text": chunk["text"],
                        "start": start,
                        "end": start + chunk["duration"] / TICKS_PER_SEC,
                    }
                )
    return words


def synthesize(text: str, voice: str, out_path: str, rate: str = "+8%") -> list[dict]:
    """Write MP3 to out_path; return [{text,start,end}] per spoken word."""
    words = asyncio.run(_synth(text, voice, out_path, rate))
    if not words:
        raise RuntimeError("TTS returned no word timings")
    return words
