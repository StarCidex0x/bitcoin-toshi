# SETUP GUIDE: COMPLETE END-TO-END PIPELINE

**Datum:** 2025-10-18
**Ziel:** Von Story bis Telegram-Post - komplett automatisiert!

---

## 🎯 ÜBERSICHT

Diese Pipeline generiert automatisch Bitcoin-Lerngeschichten mit konsistenten Charakteren und postet sie auf Telegram.

```
Story Generator → Image Generator → Caption → Telegram → DB Log
    (Claude)      (Leonardo AI)                 (Bot)
```

**Budget:** ~$0.01 pro Post
**Zeit:** ~2 Minuten pro Post
**Konsistenz:** 90%+ identischer Character (Leonardo Character Reference)

---

## 📦 KOMPONENTEN

### 1. Story Generator (`story_generator.py`)
- Generiert Bitcoin-Lerngeschichten im Retro-RPG-Stil
- Nutzt Claude 3.5 Sonnet
- Output: JSON mit Titel, Story (150-200 Wörter), Lernziel, Visual-Prompt
- Fallback: Template-Generator (funktioniert ohne API)

### 2. Image Generator (`leonardo_generator.py`)
- Generiert konsistente Toshi-Panels
- Nutzt Leonardo.AI mit Character Reference Feature
- Output: PNG (1024x1024, Retro Comic Style)
- Konsistenz: 90%+ durch Character Reference

### 3. Telegram Poster (`telegram_poster.py`)
- Postet Bild + Caption auf Telegram Channel
- Nutzt python-telegram-bot
- Output: Post auf Telegram
- Kosten: $0 (kostenlos!)

### 4. Pipeline Orchestrator (`complete_pipeline.py`)
- Koordiniert alle Komponenten
- Error Handling & Logging
- Automatische Retry-Logik

---

## 🚀 INSTALLATION

### 1. Python Dependencies

```bash
cd /Users/fabric/Bitcoin-Toshi
source .venv/bin/activate
pip install anthropic python-telegram-bot requests
```

### 2. Environment Variables

Erstelle `.env` File oder setze direkt:

```bash
# Claude API (Story Generation)
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Leonardo.AI (Image Generation)
export LEONARDO_API_KEY="..."
export LEONARDO_CHARACTER_REF_ID="..."  # Nach Master-Character Upload

# Telegram Bot (Posting)
export TELEGRAM_BOT_TOKEN="1234567890:ABCdef..."
export TELEGRAM_CHANNEL_ID="@your_channel"
```

---

## 📋 SETUP SCHRITT-FÜR-SCHRITT

### PHASE 1: Leonardo.AI Character Reference Setup

**1.1 Account erstellen**
```
https://leonardo.ai
→ Sign Up
→ Verifiziere E-Mail
```

**1.2 API Key holen**
```
https://app.leonardo.ai/settings
→ API Keys
→ Create API Key
→ Copy Key
→ export LEONARDO_API_KEY="..."
```

**1.3 Master Character erstellen**
```bash
cd /Users/fabric/Bitcoin-Toshi/00_system_core/scripts
source ../../.venv/bin/activate

python3 -c "
from leonardo_generator import create_master_character
import asyncio
asyncio.run(create_master_character())
"
```

Das generiert 4 Master-Character-Optionen in:
`/Users/fabric/Bitcoin-Toshi/05_assets/images/03_generated/leonardo/`

**1.4 Besten Master wählen & uploaden**
```python
from leonardo_generator import LeonardoGenerator

gen = LeonardoGenerator()

# Upload best master character
character_ref_id = gen.upload_character_reference(
    "/path/to/chosen/master_character.png"
)

print(f"Character Reference ID: {character_ref_id}")
# Speichere diese ID!
```

**1.5 Character Reference ID setzen**
```bash
export LEONARDO_CHARACTER_REF_ID="the_id_from_above"
```

**1.6 Consistency Test**
```python
from leonardo_generator import test_consistency

# Test mit 3 verschiedenen Szenen
test_consistency(character_ref_id="your_id_here")
```

Prüfe die 3 generierten Panels:
- Sieht Toshi 90%+ identisch aus?
- ✅ JA → Weiter mit Phase 2
- ❌ NEIN → Anderen Master wählen oder Strength anpassen

---

### PHASE 2: Telegram Bot Setup

**2.1 Bot erstellen**
```
1. Öffne Telegram
2. Suche nach @BotFather
3. Sende: /newbot
4. Folge Anweisungen
5. Kopiere Bot Token
```

**2.2 Channel erstellen**
```
1. Erstelle neuen Channel (public/private)
2. Füge Bot als Admin hinzu
3. Gib "Post Messages" Berechtigung
4. Notiere Channel-Username (@your_channel)
```

**2.3 Environment Variables setzen**
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdef..."
export TELEGRAM_CHANNEL_ID="@your_channel"
```

**2.4 Bot testen**
```bash
cd /Users/fabric/Bitcoin-Toshi/00_system_core/scripts
source ../../.venv/bin/activate
python3 telegram_poster.py
```

Sollte ausgeben:
```
✅ Bot connected: @your_bot
✅ Bot is ready to post!
```

---

### PHASE 3: Complete Pipeline Test

**3.1 Test mit Template (ohne API Keys)**
```bash
cd /Users/fabric/Bitcoin-Toshi/00_system_core/scripts
source ../../.venv/bin/activate

# Story Generator Test
python3 story_generator.py
# → Generiert Story mit Template
```

**3.2 Test mit Claude API**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python3 story_generator.py
# → Generiert Story mit Claude
```

**3.3 Complete Pipeline Test**
```bash
# Alle Environment Variables setzen (siehe oben)
export ANTHROPIC_API_KEY="..."
export LEONARDO_API_KEY="..."
export LEONARDO_CHARACTER_REF_ID="..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHANNEL_ID="..."

# Pipeline starten
python3 complete_pipeline.py
```

**Erwartetes Ergebnis:**
```
🎬 STARTING COMPLETE PIPELINE
📝 STEP 1: GENERATING STORY
✅ Story generated: Der Nebel der Unsicherheit
🎨 STEP 2: GENERATING IMAGE
✅ Image generated: panel_01_20251018_123456.png
✍️  STEP 3: CAPTION READY
📤 STEP 4: POSTING TO TELEGRAM
✅ Posted to Telegram!
💾 STEP 5: LOGGING RESULTS
✅ Results logged

📊 PIPELINE SUMMARY
Status: COMPLETED
Duration: 87.3s
Story: Der Nebel der Unsicherheit
Image: panel_01_20251018_123456.png
Posted: Message ID 123

💰 Estimated Cost: ~$0.01
```

Prüfe Telegram Channel → Post sollte da sein!

---

## 🎬 PRODUKTION: KOMPLETTE EPISODE GENERIEREN

### Episode Generator Script erstellen

```bash
cd /Users/fabric/Bitcoin-Toshi/00_system_core/scripts
nano generate_episode_01.py
```

```python
#!/usr/bin/env python3
import asyncio
from complete_pipeline import CompletePipeline

# Episode 01: Der Nebel der Unsicherheit
EPISODE_01_SCENES = [
    {
        "kapitel": 1,
        "szene": 1,
        "setting": "Nebel-Dorf der Unsicherheit",
        "herausforderung": "Toshi versteht nicht, warum Geld seinen Wert verliert",
        "lernziel": "Bitcoin ist digitales Geld mit fixer Menge",
        "mentor": "Satoshi",
        "konzept": "Dezentralisierung"
    },
    {
        "kapitel": 1,
        "szene": 2,
        "setting": "Höhle der verteilten Macht",
        "herausforderung": "Wer kontrolliert Bitcoin?",
        "lernziel": "Bitcoin hat keine zentrale Autorität",
        "mentor": "Satoshi",
        "konzept": "Dezentralisierung"
    },
    # ... 3 weitere Szenen
]

async def main():
    pipeline = CompletePipeline()

    for i, scene in enumerate(EPISODE_01_SCENES, 1):
        print(f"\n{'='*70}")
        print(f"🎬 SCENE {i}/{len(EPISODE_01_SCENES)}")
        print(f"{'='*70}\n")

        await pipeline.run_complete_pipeline(scene)

        # Pause zwischen Posts (Telegram Rate Limit)
        if i < len(EPISODE_01_SCENES):
            print("\n⏸️  Waiting 30s before next post...")
            await asyncio.sleep(30)

    print("\n🎉 EPISODE 01 COMPLETE!")

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
chmod +x generate_episode_01.py
python3 generate_episode_01.py
```

---

## 💰 KOSTEN-KALKULATION

**Pro Post:**
- Story (Claude): $0.001
- Image (Leonardo): $0.007
- Telegram: $0.000
- **TOTAL: ~$0.01**

**200 Posts:**
- Stories: $0.20
- Images: $1.40
- **TOTAL: ~$1.60**

**Monatliches Budget für 1 Post/Tag:**
- ~$0.30/Monat
- Extrem günstig!

---

## 🔧 TROUBLESHOOTING

### Problem: Character nicht konsistent genug

**Lösung A:** Höhere Character Strength
```python
# In leonardo_generator.py
character_strength="High"  # statt "Medium"
```

**Lösung B:** Neuen Master Character
```python
# Generiere neue Master-Optionen
create_master_character()
# Wähle einen mit klareren Features
```

**Lösung C:** Mehr Details im Visual Prompt
```python
# In story_generator.py, mehr spezifische Details:
"Toshi, young man, bright orange scarf, green vest, brown spiky hair, blue eyes"
```

### Problem: Telegram Bot kann nicht posten

**Prüfungen:**
1. Bot ist Channel-Admin?
2. Bot hat "Post Messages" Permission?
3. Channel-ID korrekt? (@username oder -1001234...)
4. Bot Token gültig?

**Test:**
```python
from telegram_poster import test_bot
import asyncio
asyncio.run(test_bot())
```

### Problem: Claude API Limit erreicht

**Fallback auf Template:**
```bash
# Setze API Key nicht
unset ANTHROPIC_API_KEY

# Story Generator nutzt automatisch Template
python3 story_generator.py
```

### Problem: Leonardo API Limit erreicht

**Check Credits:**
```
https://app.leonardo.ai/settings
→ API Usage
```

**Buy more Credits:**
```
$10 = ~1400 Bilder = genug für Monate
```

---

## 🎯 NÄCHSTE SCHRITTE

### SOFORT (Heute):
1. ✅ Leonardo.AI Master Character erstellen
2. ✅ 3 Test-Panels generieren → Konsistenz prüfen
3. ✅ Telegram Bot Setup & Test
4. ✅ Complete Pipeline Test (1 Post)

### DANN (Morgen):
5. ✅ Episode 01 komplett generieren (5 Panels)
6. ✅ Auf Telegram posten
7. ✅ Qualität & Konsistenz prüfen

### FINAL (Übermorgen):
8. ✅ Proxmox DB Integration (optional)
9. ✅ Scheduling Setup (cron/n8n)
10. ✅ Monitoring & Alerts
11. ✅ Skalierung auf alle Kapitel

---

## 📊 SUCCESS CRITERIA

Pipeline ist produktionsreif wenn:
1. ✅ Toshi sieht in Test-Panels 90%+ gleich aus
2. ✅ Story-Qualität ist gut (Claude oder Template)
3. ✅ Posts landen automatisch auf Telegram
4. ✅ Alle Steps werden korrekt geloggt
5. ✅ Kosten sind unter $0.02/Post
6. ✅ Runtime ist unter 3 Min/Post
7. ✅ Error Rate ist unter 5%

---

## 📞 SUPPORT & DOKUMENTATION

**Scripts:**
- `/00_system_core/scripts/story_generator.py`
- `/00_system_core/scripts/leonardo_generator.py`
- `/00_system_core/scripts/telegram_poster.py`
- `/00_system_core/scripts/complete_pipeline.py`

**Logs:**
- Stories: `/05_outputs/stories/`
- Images: `/05_assets/images/03_generated/leonardo/`
- Pipeline Logs: `/05_outputs/pipeline_logs/`

**Dokumentation:**
- `NEW_PLAN_COMPLETE_PIPELINE.md` - Pipeline-Architektur
- `COMPLETE_SYSTEM_ANALYSIS.md` - System-Analyse
- `SETUP_GUIDE_COMPLETE_PIPELINE.md` - Diese Anleitung

---

## 🚀 LET'S GO!

**Ready to start?**

```bash
# 1. Setup
export LEONARDO_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHANNEL_ID="..."

# 2. Create Master Character
cd /Users/fabric/Bitcoin-Toshi/00_system_core/scripts
python3 leonardo_generator.py

# 3. Upload & Get Character Ref ID
# ... (follow prompts)

# 4. Set Character Ref ID
export LEONARDO_CHARACTER_REF_ID="..."

# 5. Run Complete Pipeline
python3 complete_pipeline.py

# 6. Check Telegram!
```

**🎉 VIEL ERFOLG!**
