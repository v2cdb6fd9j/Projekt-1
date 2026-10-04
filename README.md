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

---

# Fight-Videos (KI-Clips + Sound-Design)

Du erzeugst kurze Kampf-Clips mit einem KI-Videogenerator (Prompts: `fights/PROMPTS.md`).
Das Tool macht daraus ein fertiges 9:16-Short mit Treffer-Sounds, Bildschirmwackeln,
Blitzen, Zeitlupe, Titel und Musik.

```
python -m fights.cli render fights_projects/example/scene.yaml   # -> output/fights/example.mp4
```

## Projekt anlegen
1. Ordner `fights_projects/<name>/` erstellen, Clips hineinlegen
2. `scene.yaml` schreiben (Vorlage: `fights_projects/example/scene.yaml`)
3. Für jeden Treffer: `{t: Sekunde im Clip, sfx: name, shake: true, flash: true, volume: 1.0}`
4. Pro Clip optional: `speed: 0.5` (Zeitlupe), `keep_audio: false`, `clip_volume: 0.6`

## Sounds
Eingebaut sind synthetische Platzhalter: `slash`, `whoosh`, `impact`, `clang`, `charge`, `explosion`.
Für echten Kino-Sound lege lizenzfreie Dateien ab, z. B. `assets/sfx/slash/*.wav`.
Sie ersetzen dann automatisch den Platzhalter, bei mehreren Dateien wird zufällig gewählt.
Eigene Namen gehen auch: `assets/sfx/thunder/` → `sfx: thunder`.
Gute Quellen: pixabay.com/sound-effects, freesound.org (Filter: CC0), Sonniss GDC Bundle (gratis).

## Urheberrecht
Nur eigene Figuren, keine Szenen oder Figuren aus bestehenden Animes. Sonst drohen
Content-ID-Sperren und Strikes. Musik und Sounds müssen lizenzfrei sein.
