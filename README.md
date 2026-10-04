# Shorts Pipeline

Erzeugt vertikale Kurzvideos (1080x1920) für drei englischsprachige Kanäle:
`facts` (Mind Blown Daily), `motivation` (Daily Fuel), `tech` (Tech in 30).

Ablauf: Claude schreibt das Skript → edge-tts spricht es (Wort-Timings) →
ffmpeg rendert Hintergrund + Stimme + animierte Untertitel (+ optional Musik).

## Setup
```
pip install -r requirements.txt     # ffmpeg muss installiert sein
export ANTHROPIC_API_KEY=...
```

## Benutzen
```
python -m shorts.cli make --channel facts
python -m shorts.cli make --channel tech --idea "How does GPS work?"
python -m shorts.cli batch --count 3     # 3 Videos pro Kanal + output/UPLOAD.md
```
Ergebnis in `output/<kanal>/`: `.mp4`, `.txt` (Titel + Caption mit Hashtags).
Ohne API-Key: `--script-file skript.json` mit `{"title": ..., "narration": ...}`.

## Anpassen
- `channels/*.yaml`: Stimme, Stil, Hashtags, Farben
- `assets/backgrounds/[kanal/]*.mp4`: eigene (lizenzfreie!) Hintergrundclips, sonst animierter Farbverlauf
- `assets/music/*.mp3`: optionale Hintergrundmusik (nur lizenzfreie)

## Hochladen (manuell)
`output/UPLOAD.md` ist deine Checkliste: pro Video Datei, Titel und Caption zum Kopieren.
Jedes Video auf YouTube Shorts, TikTok und Instagram Reels posten.

## Hinweise für echte Reichweite
Views lassen sich nicht garantieren. Was hilft: täglich posten, Hook in den ersten
2 Sekunden, nur korrekte Fakten, Hintergrund und Stimme variieren. Rein automatisierte,
repetitive Massenware wird von den Plattformen zunehmend gedrosselt oder nicht monetarisiert.
