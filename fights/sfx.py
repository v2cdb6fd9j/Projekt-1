"""Sound effects: use files from assets/sfx/<name>/*.wav|mp3, else synthesize a default.

Drop real (CC0 / royalty-free) sounds into assets/sfx/<name>/ to replace the
synthesized placeholders; one is picked at random per hit.
"""
import glob
import os
import random
import subprocess

SFX_DIR = os.path.join("assets", "sfx")
CACHE = os.path.join(SFX_DIR, "_generated")

# ffmpeg lavfi recipes for placeholder sounds
RECIPES = {
    "slash": "anoisesrc=d=0.35:c=white:a=0.6,highpass=f=2500,afade=t=in:d=0.03,afade=t=out:st=0.05:d=0.3",
    "whoosh": "anoisesrc=d=0.6:c=pink:a=0.7,bandpass=f=900:w=600,afade=t=in:d=0.25,afade=t=out:st=0.3:d=0.3",
    "impact": "aevalsrc='0.9*sin(2*PI*(90-60*t)*t)*exp(-7*t)+0.3*(random(0)-0.5)*exp(-25*t)':d=0.6",
    "clang": "aevalsrc='0.25*(sin(2*PI*2100*t)+sin(2*PI*3370*t)+sin(2*PI*5230*t))*exp(-5*t)':d=1.0",
    "charge": "aevalsrc='0.35*sin(2*PI*(150+700*t)*t)*min(1,t*2)':d=1.4,afade=t=out:st=1.2:d=0.2",
    "explosion": "anoisesrc=d=1.8:c=brown:a=1.0,lowpass=f=600,volume=4,afade=t=out:st=0.1:d=1.7",
}


def path_for(name: str) -> str:
    files = glob.glob(os.path.join(SFX_DIR, name, "*.wav")) + glob.glob(os.path.join(SFX_DIR, name, "*.mp3"))
    if files:
        return random.choice(files)
    if name not in RECIPES:
        raise ValueError(f"Unknown sfx '{name}'. Add files to {SFX_DIR}/{name}/ or use one of {sorted(RECIPES)}")
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, f"{name}.wav")
    if not os.path.exists(out):
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", RECIPES[name], "-ar", "48000", "-ac", "2", out],
            check=True,
        )
    return out
