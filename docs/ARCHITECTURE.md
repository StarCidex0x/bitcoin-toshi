# 🏗️ Technische Architektur

## Übersicht

Bitcoin-Toshi nutzt eine **agentenbasierte Architektur** für automatisierte Content-Generierung mit KI-gestützter Qualitätskontrolle.

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                           │
│                   (Workflow-Steuerung)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│  IMAGE    │  │  CONTENT  │  │    QA     │
│ ANALYZER  │  │ GENERATOR │  │  PUBLISH  │
└───────────┘  └───────────┘  └───────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              ┌───────────────┐
              │   DATABASE    │
              │   (SQLite)    │
              └───────────────┘
```

## Komponenten

### 00_system_core/
Basis-Infrastruktur:
- Konfigurationsdateien
- Umgebungsvariablen
- Logging-Setup
- Utility-Funktionen

### 01_agents/

#### Image Analyzer
- **Aufgabe**: Prüft generierte Bilder auf Stil-Konsistenz
- **Input**: Generiertes Bild + Style-Blueprint
- **Output**: Konsistenz-Score, Feedback für Re-Generation
- **Modelle**: Qwen3-VL (Vision-Language)

#### Content Generator
- **Aufgabe**: Erstellt Texte und Bildprompts
- **Input**: Lektions-Thema, Charakter-Kontext
- **Output**: Dialog-Text, Bild-Beschreibung
- **Stil**: Deutsche JRPG-Dialoge

#### QA Publish
- **Aufgabe**: Qualitätsprüfung & Veröffentlichung
- **Input**: Fertiger Content (Text + Bild)
- **Output**: Approved/Rejected, Publishing-Aktion
- **Checks**: Grammatik, Fakten, Stil-Konsistenz

#### Orchestrator
- **Aufgabe**: Koordiniert alle Agenten
- **Workflow**: Trigger → Generate → Analyze → QA → Publish
- **Retry-Logic**: Bei Ablehnung → Re-Generation

### 02_models/

Hugging Face Inference API Anbindung:

```python
# Beispiel-Konfiguration
MODELS = {
    "vision": "Qwen/Qwen2-VL-7B-Instruct",
    "caption": "vikhyatk/joy-caption",
    "text": "meta-llama/Llama-3-8B-Instruct",
    "image": "stabilityai/stable-diffusion-xl-base-1.0"
}
```

**Warum Hugging Face?**
- Keine lokale GPU nötig
- Skalierbar
- Modell-Vielfalt
- Pay-per-Use

### 03_workflows/

AgentFlow-Definitionen im YAML-Format:

```yaml
# Beispiel: weekly_content.yaml
name: Weekly Content Generation
trigger: cron(0 9 * * MON)
steps:
  - agent: content_generator
    input: ${week_topic}
  - agent: image_analyzer
    input: ${generated_image}
    condition: score > 0.8
  - agent: qa_publish
    input: ${content_bundle}
```

### 04_database/

SQLite-Schema:

```sql
-- Haupt-Tabellen
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY,
    week INTEGER,
    day INTEGER,
    topic TEXT,
    status TEXT,  -- draft, generated, approved, published
    created_at TIMESTAMP
);

CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    episode_id INTEGER,
    type TEXT,  -- image, text, audio
    path TEXT,
    metadata JSON,
    FOREIGN KEY (episode_id) REFERENCES episodes(id)
);

CREATE TABLE style_blueprints (
    id INTEGER PRIMARY KEY,
    name TEXT,
    parameters JSON,
    reference_images TEXT  -- comma-separated paths
);
```

### 05_assets/

```
05_assets/
├── images/
│   ├── 00_reference/     # Stil-Referenzen
│   │   ├── characters/   # Toshi, NPCs
│   │   ├── backgrounds/  # Welten
│   │   └── ui/           # Dialog-Boxen
│   ├── 01_generated/     # KI-generierte Bilder
│   └── 02_approved/      # Freigegebene Bilder
├── audio/
│   ├── sfx/              # Sound Effects
│   └── music/            # Background Music
└── fonts/
    └── pixel/            # Retro-Fonts
```

## Style-Blueprint-System

### Workflow

```
1. ANALYSE
   └── Referenzbild → Qwen3-VL → Stil-Parameter

2. EXTRAKTION
   └── Farbpalette, Pixel-Dichte, Linienführung, Proportionen

3. BLUEPRINT
   └── JSON-Dokument mit allen Stil-Parametern

4. GENERATION
   └── Neues Bild + Blueprint → Konsistenter Output

5. VALIDIERUNG
   └── Image Analyzer prüft Konsistenz (Score 0-1)
```

### Blueprint-Beispiel

```json
{
  "character": "Toshi",
  "style": {
    "pixel_density": "16x16 base",
    "palette": ["#FF6B00", "#8B4513", "#228B22", "#F5DEB3"],
    "outline": "1px black, anti-aliased",
    "shading": "dithered, 3 levels"
  },
  "proportions": {
    "head_body_ratio": "1:2.5",
    "chibi_factor": 0.7
  },
  "reference_images": [
    "toshi_neutral_standing_v1.png",
    "toshi_neutral_standing_v2.png"
  ]
}
```

## Datenfluss

```
User Input (Thema)
       │
       ▼
┌──────────────┐
│   Orchestrator│
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   Content    │────▶│    Image     │
│  Generator   │     │  Generator   │
└──────────────┘     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Image     │
                     │   Analyzer   │
                     └──────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
        Score < 0.8               Score >= 0.8
              │                           │
              ▼                           ▼
        Re-Generate              ┌──────────────┐
                                 │  QA Publish  │
                                 └──────┬───────┘
                                        │
                                        ▼
                                   Published!
```

## API-Endpunkte (Zukünftig)

```
POST /api/generate
  - Startet Content-Generation für ein Thema

GET /api/episodes
  - Liste aller Episoden

GET /api/episodes/{id}
  - Details einer Episode

POST /api/approve/{id}
  - Manuelle Freigabe

GET /api/stats
  - Generation-Statistiken
```

## Deployment

### Entwicklung
- Lokales SQLite
- Hugging Face Free Tier
- Manuelle Trigger

### Produktion
- PostgreSQL / Supabase
- Hugging Face Pro oder Self-Hosted
- Cron-basierte Automatisierung
- CDN für Assets
