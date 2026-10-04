"""Render a 1080x1920 video: background + voice + burned-in word captions."""
import glob
import os
import random
import subprocess

W, H = 1080, 1920


def _ass_time(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def build_ass(words: list[dict], path: str, per_chunk: int = 3):
    header = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {W}\nPlayResY: {H}\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding\n"
        "Style: Default,DejaVu Sans,96,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,"
        "-1,0,0,0,100,100,0,0,1,7,2,5,60,60,0,1\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    )
    lines = []
    for i in range(0, len(words), per_chunk):
        chunk = words[i : i + per_chunk]
        end = chunk[-1]["end"]
        if i + per_chunk < len(words):
            end = max(end, words[i + per_chunk]["start"])  # no flicker between chunks
        text = " ".join(w["text"] for w in chunk).upper().replace("{", "(").replace("}", ")")
        lines.append(
            f"Dialogue: 0,{_ass_time(chunk[0]['start'])},{_ass_time(end)},Default,,0,0,0,,{text}"
        )
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines) + "\n")


def _background_input(channel: dict, duration: float):
    """Return ffmpeg input args + the video filter prefix for the background."""
    clips = glob.glob(os.path.join("assets", "backgrounds", channel["name"], "*.mp4")) + glob.glob(
        os.path.join("assets", "backgrounds", "*.mp4")
    )
    if clips:
        clip = random.choice(clips)
        args = ["-stream_loop", "-1", "-i", clip]
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
        return args, vf
    c0, c1 = [c.lstrip("#") for c in channel["gradient"]]
    src = f"gradients=s={W}x{H}:c0=0x{c0}:c1=0x{c1}:speed=0.015:rate=30:d={duration:.2f}"
    return ["-f", "lavfi", "-i", src], "setsar=1"


def render(channel: dict, audio_path: str, words: list[dict], out_path: str):
    duration = words[-1]["end"] + 0.6
    ass_path = out_path.rsplit(".", 1)[0] + ".ass"
    build_ass(words, ass_path)
    bg_args, bg_vf = _background_input(channel, duration)

    music = glob.glob(os.path.join("assets", "music", "*.mp3"))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *bg_args, "-i", audio_path]
    if music:
        cmd += ["-stream_loop", "-1", "-i", random.choice(music)]
        af = "[1:a]apad[v];[2:a]volume=0.08[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]"
    else:
        af = "[1:a]apad[a]"
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    vf = f"[0:v]{bg_vf},subtitles='{ass_escaped}'[v]"
    cmd += [
        "-filter_complex", f"{vf};{af}",
        "-map", "[v]", "-map", "[a]",
        "-t", f"{duration:.2f}",
        "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        out_path,
    ]
    subprocess.run(cmd, check=True)
    return out_path
