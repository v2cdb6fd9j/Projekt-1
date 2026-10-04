"""Turn AI-generated clips + a hit timeline into a finished 9:16 fight short."""
import os
import subprocess
import tempfile

import yaml

from . import sfx

W, H, FPS = 1080, 1920, 30
SHAKE_LEN, FLASH_LEN = 0.3, 0.08


def _has_audio(path: str) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    ).stdout
    return bool(out.strip())


def _duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out.strip())


def _segment(clip: dict, base_dir: str, out_path: str):
    """Normalize one clip to 1080x1920@30 and apply its hits (sfx, shake, flash)."""
    src = os.path.join(base_dir, clip["file"])
    speed = float(clip.get("speed", 1.0))  # 0.5 = slow motion
    hits = clip.get("hits", [])
    dur = _duration(src) / speed

    # hit times are given in the clip's ORIGINAL timing; convert to output timing
    shakes = [h["t"] / speed for h in hits if h.get("shake", True)]
    flashes = [h["t"] / speed for h in hits if h.get("flash", False)]
    amp = 28
    dx = "+".join(f"if(between(t,{s:.3f},{s + SHAKE_LEN:.3f}),{amp}*sin(t*90)*(1-(t-{s:.3f})/{SHAKE_LEN}),0)" for s in shakes) or "0"
    dy = "+".join(f"if(between(t,{s:.3f},{s + SHAKE_LEN:.3f}),{amp}*cos(t*70)*(1-(t-{s:.3f})/{SHAKE_LEN}),0)" for s in shakes) or "0"
    pad = 60  # extra pixels so the shake never shows borders
    v = (
        f"[0:v]setpts=PTS/{speed},fps={FPS},"
        f"scale={W + 2 * pad}:{H + 2 * pad}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H}:'(iw-{W})/2+{dx}':'(ih-{H})/2+{dy}',setsar=1"
    )
    for f in flashes:
        v += f",drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='between(t,{f:.3f},{f + FLASH_LEN:.3f})'"
    v += "[v]"

    inputs = ["-i", src]
    if _has_audio(src) and clip.get("keep_audio", True):
        tempo = f",atempo={speed}" if speed != 1.0 and 0.5 <= speed <= 2.0 else ""
        a_parts = [f"[0:a]aresample=48000,aformat=channel_layouts=stereo{tempo},volume={clip.get('clip_volume', 0.6)}[a0]"]
    else:
        inputs += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        a_parts = [f"[1:a]atrim=duration={dur:.3f}[a0]"]
    mix = ["[a0]"]
    idx = 1 if inputs.count("-i") == 1 else 2  # next free input index
    for i, h in enumerate(hits):
        if not h.get("sfx"):
            continue
        inputs += ["-i", sfx.path_for(h["sfx"])]
        ms = int(h["t"] / speed * 1000)
        a_parts.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={h.get('volume', 1.0)},adelay={ms}|{ms}[s{i}]")
        mix.append(f"[s{i}]")
        idx += 1
    a_parts.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[a]")

    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs,
           "-filter_complex", v + ";" + ";".join(a_parts),
           "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out_path]
    subprocess.run(cmd, check=True)


def render(scene_path: str) -> str:
    with open(scene_path, encoding="utf-8") as f:
        scene = yaml.safe_load(f)
    base = os.path.dirname(scene_path)
    out_dir = os.path.join("output", "fights")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, os.path.basename(base) + ".mp4")

    with tempfile.TemporaryDirectory() as tmp:
        segs = []
        for i, clip in enumerate(scene["clips"]):
            seg = os.path.join(tmp, f"seg{i:03d}.mp4")
            _segment(clip, base, seg)
            segs.append(seg)
        listing = os.path.join(tmp, "list.txt")
        with open(listing, "w") as f:
            f.writelines(f"file '{s}'\n" for s in segs)
        joined = os.path.join(tmp, "joined.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing,
                        "-c", "copy", joined], check=True)

        music = scene.get("music")
        title = scene.get("title")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", joined]
        vf = "null"
        if title:
            t = title.replace("'", "").replace(":", "\\:")
            vf = (f"drawtext=text='{t}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                  f"fontsize=88:fontcolor=white:borderw=6:bordercolor=black:x=(w-tw)/2:y=h*0.12:enable='lt(t,2.5)'")
        if music:
            cmd += ["-stream_loop", "-1", "-i", os.path.join(base, music)]
            af = f"[1:a]volume={scene.get('music_volume', 0.25)}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
        else:
            af = "[0:a]anull[a]"
        cmd += ["-filter_complex", f"[0:v]{vf}[v];{af}", "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)
    return out
