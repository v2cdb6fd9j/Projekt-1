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
python -m shorts.cli make --channel motivation --upload     # + YouTube-Upload
```
Ergebnis in `output/<kanal>/`: `.mp4`, `.txt` (Titel + Caption mit Hashtags).
Ohne API-Key: `--script-file skript.json` mit `{"title": ..., "narration": ...}`.

## Anpassen
- `channels/*.yaml`: Stimme, Stil, Hashtags, Farben
- `assets/backgrounds/[kanal/]*.mp4`: eigene (lizenzfreie!) Hintergrundclips, sonst animierter Farbverlauf
- `assets/music/*.mp3`: optionale Hintergrundmusik (nur lizenzfreie)

## Plattformen
- **YouTube Shorts**: Upload eingebaut (`credentials/client_secret.json` nötig, siehe `shorts/upload_youtube.py`).
- **TikTok / Instagram Reels**: Die offiziellen APIs verlangen App-Freigabe bzw. ein Business-Konto.
  Bis dahin: fertige `.mp4` + `.txt` aus `output/` hochladen.

## Hinweise für echte Reichweite
Views lassen sich nicht garantieren. Was hilft: täglich posten, Hook in den ersten
2 Sekunden, nur korrekte Fakten, Hintergrund und Stimme variieren. Rein automatisierte,
repetitive Massenware wird von den Plattformen zunehmend gedrosselt oder nicht monetarisiert.
