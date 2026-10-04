# Prompt-Vorlagen für KI-Videogeneratoren

Gilt für Kling, Runway, Pika, Google Veo usw. Erzeuge **eigene Figuren**:
keine Namen, Figuren oder Szenen aus bestehenden Animes (z. B. Bleach) im Prompt.
Ein Stil ist frei, Figuren sind geschützt.

## 1. Figuren festlegen (einmal, dann immer gleich verwenden)
Schreib jede Figur als festen Textblock und kopiere ihn in jeden Prompt, damit sie gleich aussieht:

```
SHADOW: young swordsman, spiky silver hair, black long coat with red inner lining,
glowing violet katana, scar over left eye
BLAZE: tall female warrior, short orange hair, white armor with gold trim,
twin flame gauntlets, determined expression
```
Tipp: Erzeuge zuerst ein Standbild pro Figur und nutze es als Referenzbild ("image to video").

## 2. Shot-Prompts (je 5–10 Sekunden)
Allgemeiner Aufbau: `[Stil], [Kamera], [Figur], [Aktion], [Umgebung], [Licht]`

```
anime style, 2D cel shading, dynamic camera, vertical 9:16.
Wide shot: SHADOW and BLAZE face each other on a ruined rooftop at night,
wind blowing debris, full moon, tense standoff.
```
```
anime style, 2D cel shading, vertical 9:16, fast camera tracking.
SHADOW dashes forward and slashes with the glowing violet katana,
BLAZE blocks with flame gauntlets, sparks fly, speed lines.
```
```
anime style, vertical 9:16, low angle close-up.
BLAZE charges a huge fireball between her hands, energy aura, hair blowing upward.
```
```
anime style, vertical 9:16, slow motion.
Massive explosion of violet and orange energy colliding, shockwave, rooftop shattering.
```

## 3. Aufbau eines 30–45-s-Shorts
1. Standoff (Spannung, 3–5 s)
2. Erster Schlagabtausch (2–3 Clips)
3. Aufladen der Spezialattacke
4. Finaler Treffer in Zeitlupe (`speed: 0.5`)
5. Cliffhanger: "Wer gewinnt? Teil 2 →"

## 4. Danach
Clips in `fights_projects/<name>/` legen, Treffer-Zeitpunkte in `scene.yaml`
eintragen (Video im Player anhalten, Sekunde ablesen) und rendern.
