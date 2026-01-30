# 🎨 Style Guide: Bitcoin-Toshi

## Visueller Stil

### Pixel-Art Spezifikationen

| Parameter | Wert |
|-----------|------|
| **Basis-Auflösung** | 16x16 px (Charaktere), 32x32 px (Details) |
| **Upscale-Faktor** | 4x für Social Media |
| **Anti-Aliasing** | Minimal, nur an Outlines |
| **Dithering** | Ja, für Farbübergänge |

### Farbpalette

#### Toshi (Hauptcharakter)
```
Orange (Schal):     #FF6B00
Braun (Haare):      #8B4513
Dunkelbraun:        #5D3A1A
Grün (Weste):       #228B22
Beige (Hemd):       #F5DEB3
Hautton:            #FFDAB9
```

#### Bitcoin-Thema
```
Bitcoin Orange:     #F7931A
Gold:               #FFD700
Digital Blue:       #00CED1
Matrix Green:       #00FF00
```

#### UI & Dialoge
```
Box-Rahmen:         #2C3E50
Box-Hintergrund:    #1A252F (90% Opacity)
Text:               #FFFFFF
Akzent:             #F7931A
```

### Schattierung

3-Stufen-System:
1. **Basis-Farbe** (100%)
2. **Schatten** (70% Helligkeit)
3. **Highlight** (120% Helligkeit)

```
Beispiel Toshi-Schal:
  Highlight:  #FF8533
  Basis:      #FF6B00
  Schatten:   #CC5500
```

## Charakter-Design

### Toshi – Proportionen

```
        ┌───┐
        │   │  ← Kopf (1 Einheit)
        └─┬─┘
        ┌─┴─┐
        │   │  ← Torso (1 Einheit)
        └─┬─┘
        ┌─┴─┐
        │   │  ← Beine (1.5 Einheiten)
        └───┘
        
Chibi-Faktor: 0.7 (leicht überproportionaler Kopf)
```

### Emotionen & Posen

| Emotion | Beschreibung |
|---------|-------------|
| **Neutral** | Entspannt stehend, leichtes Lächeln |
| **Neugierig** | Kopf leicht geneigt, große Augen |
| **Begeistert** | Arme hoch, Mund offen, Glanz in Augen |
| **Nachdenklich** | Hand am Kinn, Blick nach oben |
| **Überrascht** | Zurückgelehnt, Ausrufezeichen über Kopf |
| **Entschlossen** | Faust geballt, fester Blick |

### Schal-Dynamik

Der orange Schal ist Toshis Markenzeichen und zeigt Bewegung:

- **Ruhig**: Schal hängt leicht gebogen
- **Wind**: Schal weht nach rechts/links
- **Aktion**: Schal fliegt dramatisch

## Hintergründe & Welten

### Blockchain-Wald
- Bäume = abstrakte Datenblöcke
- Leuchtende Verbindungslinien
- Mystische, aber freundliche Atmosphäre
- Palette: Grün, Cyan, Gold

### Mining-Höhlen
- Kristalle = Mining-Rewards
- Dampfbetriebene Maschinen (Steampunk-Touch)
- Warmes Licht von Fackeln
- Palette: Orange, Braun, Gold

### Cyberstadt
- Neon-Lichter
- Holografische Displays
- Futuristisch aber einladend
- Palette: Cyan, Magenta, Schwarz

### Festung der Banken
- Imposante Mauern
- Goldene Verzierungen (trügerischer Reichtum)
- Graue, bedrückende Atmosphäre
- Palette: Grau, Gold, Schwarz

## Dialog-System

### Box-Design

```
┌─────────────────────────────────────┐
│ CHARACTER NAME                      │  ← Gold/Orange
├─────────────────────────────────────┤
│                                     │
│  "Dialog-Text hier. Maximal drei    │  ← Weiß, Pixel-Font
│   Zeilen pro Box empfohlen."        │
│                                     │
└─────────────────────────────────────┘
         ▼ (Weiter-Indikator blinkt)
```

### Textformatierung

- **Font**: Pixel-Art, monospace-ähnlich
- **Größe**: 8px Basis, 2x skaliert
- **Zeilenabstand**: 1.5x
- **Max. Zeichen/Zeile**: 40
- **Max. Zeilen/Box**: 3

### Dialog-Stil

**DO:**
```
"Wow! Diese Blöcke sind alle verbunden!"
"Jeder neue Block enthält den Hash des vorherigen..."
"Das macht die Kette praktisch unveränderbar!"
```

**DON'T:**
```
"Die kryptografische Verkettung von Datenblöcken durch 
SHA-256 Hash-Funktionen gewährleistet die Integrität 
der distribuierten Ledger-Technologie."
```

## Sound-Design (Zukünftig)

### Kategorien
- **UI**: Blips, Bestätigungen, Menü-Sounds
- **Dialog**: Textscroll-Sound (klassisch)
- **Ambient**: Welt-spezifische Atmosphäre
- **Musik**: Chiptune, 16-bit Style

### Referenzen
- Chrono Trigger
- Final Fantasy VI
- Secret of Mana
- Earthbound

## Konsistenz-Checkliste

Vor Veröffentlichung prüfen:

- [ ] Toshis Schal ist orange (#FF6B00)
- [ ] Pixel-Dichte konsistent
- [ ] Farbpalette eingehalten
- [ ] Dialog max. 3 Zeilen
- [ ] Kein Fachjargon ohne Erklärung
- [ ] Emotionen passen zum Kontext
- [ ] Hintergrund passt zur Welt
