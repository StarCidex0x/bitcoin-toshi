# 🎨 Image Consistency Analyzer

Automatische Analyse und Qualitätsprüfung von generierten Bildern (Charaktere, Szenen).

---

## 📋 Was macht der Analyzer?

Der **Image Consistency Analyzer** sorgt für ein einheitliches visuelles Erscheinungsbild:

### 🔍 Analyse-Funktionen:

1. **Farbpaletten-Extraktion**
   - Extrahiert dominante Farben aus jedem Bild
   - Zeigt die 8 wichtigsten Farben
   - Überspringt Weiß/Transparent automatisch

2. **Stil-Analyse mit Gemini Vision**
   - Pixel-Art-Stil (SNES, 16-bit, etc.)
   - Detailgrad (low/medium/high)
   - Outline-Stärke
   - Shading-Technik
   - Farbsättigung
   - Kontrast
   - Komposition

3. **Konsistenz-Prüfung (NEU: Zweistufig!)**
   - **Stufe 1:** Reference Assets (Charaktere + Szenen einzeln)
   - **Stufe 2:** Finale Post-Bilder (komponierten 4 Posts)
   - **Gesamtbewertung:** Durchschnitt beider Scores
   - Berechnet Konsistenz-Score (0.0 - 1.0)
   - ✅ Konsistent ab Score >= 0.7
   - ⚠️ Inkonsistent bei Score < 0.7

4. **Style-Guide-Erstellung**
   - Kombiniert alle Charaktere und Szenen
   - Zeigt alle Assets auf einen Blick
   - Speichert als PNG

---

## 🚀 Verwendung

### 1. Automatisch in Pipeline

Der Analyzer läuft **automatisch** in beiden Pipelines:

```bash
# Standard Pipeline
./start_full.sh --scene 1

# StoryRider Pipeline
./start_full.sh --storyrider
```

**Output (NEU: Prüft jetzt auch finale Post-Bilder!):**
```
━━━ STEP 2.4: Style-Konsistenz prüfen ━━━

   🔍 Analysiere 3 Reference Assets (Charaktere + Szenen)...
   🎨 toshi_20251019_031526.png: 8 Hauptfarben
   🎨 safekeeper_20251019_031526.png: 7 Hauptfarben
   🎨 self_custody_20251019_031526.png: 8 Hauptfarben
   ✅ Reference Assets konsistent (Score: 0.85)

   🔍 Analysiere 4 finale Post-Bilder...
   🎨 story_58_post_1_20251019_035725.png: 8 Hauptfarben
   🎨 story_58_post_2_20251019_035732.png: 8 Hauptfarben
   🎨 story_58_post_3_20251019_035739.png: 8 Hauptfarben
   🎨 story_58_post_4_20251019_035745.png: 8 Hauptfarben
   ✅ Post-Bilder konsistent (Score: 0.82)

   📊 GESAMTBEWERTUNG:
      Reference Assets: 0.85
      Post-Bilder: 0.82
      Overall: 0.84
   ✅ Gesamtkonsistenz erreicht!
```

### 2. Manuell für alle Assets

Erstellt Style-Guide aus ALLEN existierenden Assets:

```bash
./create_style_guide.sh
```

**Output:**
```
🔍 Vergleiche 12 Bilder...
✅ Charaktere konsistent (Score: 0.82)
✅ Szenen konsistent (Score: 0.78)
🎨 Erstelle Style-Guide-Bild...
✅ Style-Guide gespeichert: 05_assets/images/04_analysis/style_guides/style_guide_20251019_123456.png
```

### 3. Programmatisch

```python
from image_consistency_analyzer import ImageConsistencyAnalyzer

analyzer = ImageConsistencyAnalyzer()

# Alle Assets analysieren
results = analyzer.analyze_all_assets()

# Spezifische Bilder analysieren
image_paths = [Path("char1.png"), Path("char2.png")]
comparison = analyzer.compare_styles(image_paths)

print(f"Konsistent: {comparison['consistent']}")
print(f"Score: {comparison['consistency_score']}")
```

---

## 📂 Output-Struktur

```
05_assets/images/04_analysis/
├── consistency_analysis_20251019_123456.json   # JSON-Analyse
└── style_guides/
    └── style_guide_20251019_123456.png        # Visueller Style-Guide
```

### Analysis JSON Format:

```json
{
  "timestamp": "2025-10-19T12:34:56",
  "characters": {
    "toshi_20251019_031526.png": {
      "path": "/path/to/image.png",
      "palette": ["rgb(234,156,78)", "rgb(89,123,201)", ...]
    }
  },
  "scenes": {
    "self_custody_20251019_031526.png": {
      "path": "/path/to/image.png",
      "palette": ["rgb(145,198,234)", ...]
    }
  },
  "consistency": {
    "characters": {
      "images_analyzed": 5,
      "consistency_score": 0.82,
      "consistent": true,
      "analyses": [...]
    },
    "scenes": {
      "images_analyzed": 3,
      "consistency_score": 0.78,
      "consistent": true,
      "analyses": [...]
    }
  },
  "style_guide": "/path/to/style_guide.png"
}
```

---

## 🎯 Konsistenz-Score

Der Score wird berechnet aus:

- **30%** - Stil-Konsistenz (alle gleicher Stil?)
- **30%** - Detailgrad-Konsistenz (alle gleicher Detailgrad?)
- **40%** - Durchschnittliche Qualität (0.0 - 1.0)

**Interpretation:**
- ✅ **0.7 - 1.0:** Konsistent, ready for production
- ⚠️ **0.5 - 0.7:** Leichte Inkonsistenzen, manuelle Prüfung empfohlen
- ❌ **0.0 - 0.5:** Starke Inkonsistenzen, Regenerierung empfohlen

---

## 🔧 Konfiguration

### API-Keys

Benötigt wird:
```env
GOOGLE_API_KEY=...  # Für Gemini Vision (Stil-Analyse)
```

### Directories

```python
character_dir = "05_assets/images/00_reference/characters"
scene_dir = "05_assets/images/00_reference/scenes"
analysis_dir = "05_assets/images/04_analysis"
style_guide_dir = "05_assets/images/04_analysis/style_guides"
```

---

## 🎯 Zweistufige Konsistenz-Prüfung (NEU!)

Seit Version 1.1 prüft der Analyzer **zwei verschiedene Ebenen** der Pipeline:

### Stufe 1: Reference Assets
Prüft die **einzelnen Bausteine** (Charaktere + Szenen):
- Toshi-Charakter (neutral_standing)
- Mentor-Charakter (teaching pose)
- Szenen-Hintergrund

**Ziel:** Sicherstellen, dass alle Bausteine denselben Pixel-Art-Stil haben.

### Stufe 2: Finale Post-Bilder
Prüft die **4 komponierten Post-Bilder**:
- Post 1: Die Begegnung
- Post 2: Die Herausforderung
- Post 3: Die Erkenntnis
- Post 4: Die Lektion

**Ziel:** Sicherstellen, dass die finalen Posts untereinander konsistent sind.

### Gesamtbewertung
Die **Overall Score** ist der Durchschnitt beider Ebenen:
```
Overall Score = (Reference Assets Score + Post-Bilder Score) / 2
```

**Beispiel:**
```
Reference Assets: 0.85  ✅ Gut
Post-Bilder: 0.82       ✅ Gut
Overall: 0.84           ✅ Konsistent!
```

**Warum zweistufig?**
- Reference Assets können konsistent sein, aber finale Posts trotzdem inkonsistent (z.B. durch schlechte Komposition)
- Finale Posts können inkonsistent sein, aber Reference Assets gut (zeigt Problem in Komposition, nicht Generation)
- Gibt genauere Diagnose, wo das Problem liegt

---

## 📊 Features

### ✅ Implementiert:
- Farbpaletten-Extraktion
- Gemini Vision Stil-Analyse
- Konsistenz-Vergleich
- Style-Guide-Erstellung
- Auto-Integration in Pipelines
- JSON-Export

### 🔄 Geplant:
- Automatische Stil-Korrektur
- Training eines Custom-Modells auf Basis der Referenzen
- Batch-Verarbeitung mehrerer Stories
- Web-Dashboard zur Visualisierung

---

## 🎨 Beispiel-Output

**Console:**
```
🔍 IMAGE CONSISTENCY ANALYZER
================================================================================
📊 12 Charakter-Bilder gefunden
📊 6 Szenen-Bilder gefunden

🔍 Analysiere Charakter-Konsistenz...
✅ Charaktere konsistent (Score: 0.82)

🔍 Analysiere Szenen-Konsistenz...
✅ Szenen konsistent (Score: 0.78)

🎨 Erstelle Style-Guide-Bild...
✅ Style-Guide gespeichert: style_guide_20251019_123456.png

💾 Analyse gespeichert: consistency_analysis_20251019_123456.json

================================================================================
✅ ANALYSE COMPLETE
================================================================================

📊 ZUSAMMENFASSUNG:
   Charaktere: 12
   Szenen: 6
   Charakter-Konsistenz: 0.82
   Szenen-Konsistenz: 0.78
   Style-Guide: /path/to/style_guide.png
```

**Style-Guide Bild:**
```
┌─────────────────────────────────────────┐
│         TOSHI STYLE GUIDE               │
├─────────────────────────────────────────┤
│ CHARAKTERE:                              │
│ [Toshi] [Satoshi] [Myriam] [Magnus] ... │
│                                          │
│ SZENEN:                                  │
│ [Dezentralisierung] [Private Keys] ...  │
└─────────────────────────────────────────┘
```

---

## 🚨 Troubleshooting

### Import Error
```
⚠️ Image Consistency Analyzer nicht verfügbar: No module named 'PIL'
```

**Lösung:**
```bash
source .venv/bin/activate
pip install Pillow
```

### API Error
```
❌ Fehler bei Stil-Analyse: 404 Not Found
```

**Lösung:**
- Prüfe GOOGLE_API_KEY
- Stelle sicher, dass Gemini API aktiviert ist

### Keine Bilder gefunden
```
📊 0 Charakter-Bilder gefunden
```

**Lösung:**
- Prüfe ob Bilder in `05_assets/images/00_reference/` existieren
- Führe erst Pipeline aus: `./start_full.sh --scene 1`

---

## 💡 Best Practices

1. **Nach jeder Bild-Generierung:**
   - Analyzer läuft automatisch
   - Prüfe Console-Output
   - Bei Score < 0.7: Manuelle Prüfung

2. **Wöchentliche Style-Guide-Erstellung:**
   ```bash
   ./create_style_guide.sh
   ```
   - Zeigt Evolution des Stils
   - Dokumentiert Assets

3. **Vor Production-Release:**
   - Analysiere ALLE Assets
   - Stelle sicher Score >= 0.7
   - Prüfe Style-Guide visuell

---

## 📖 Weiterführende Dokumentation

- **Pipeline-Dokumentation:** `AGENTS_SYSTEM_OVERVIEW.md`
- **Charakter-Generator:** `00_system_core/scripts/character_generator.py`
- **Szenen-Generator:** `00_system_core/scripts/scene_background_generator.py`

---

**Status:** ✅ Production-Ready
**Version:** 1.0
**Letzte Aktualisierung:** 2025-10-19
