# 🎨 BILDGENERIER UNGS- & SPEICHER-STRUKTUR

**Datum:** 2025-10-19
**Status:** ✅ Implementiert & funktioniert

---

## 📁 SPEICHERORTE

### 1. Separate Charaktere (Reference)
```
05_assets/images/00_reference/characters/
├── toshi/
│   ├── toshi_neutral_standing_v1_20251019_015537.png  (1.1 MB)
│   ├── toshi_neutral_standing_v1_20251019_015537.json (Metadata)
│   ├── toshi_thinking_v1_[timestamp].png
│   └── toshi_excited_v1_[timestamp].png
│
├── satoshi_sensei/
│   ├── satoshi_sensei_teaching_v1_20251019_015543.png (1.0 MB)
│   ├── satoshi_sensei_teaching_v1_20251019_015543.json
│   └── ...
│
├── mutter_myriam/
│   └── ...
│
└── miner_magnus/
    └── ...
```

**Zweck:** Wiederverwendbare Charakter-Sprites für verschiedene Szenen

---

### 2. Separate Szenen/Backgrounds (Reference)
```
05_assets/images/00_reference/scenes/
├── dezentralisierung/
│   ├── dezentralisierung_mystical_day_v1_20251019_015551.png (1.6 MB)
│   ├── dezentralisierung_mystical_day_v1_20251019_015551.json
│   └── ...
│
├── der_weg_der_nodes/
│   └── ...
│
├── miner_canyon/
│   └── ...
│
└── private_keys_bibliothek/
    └── ...
```

**Zweck:** Wiederverwendbare Hintergrundszenen ohne Charaktere

---

### 3. Finale kombinierte Bilder (Generated/Composed)
```
05_assets/images/03_generated/composed/
├── story_26_post_1_20251019_015558.png  (1.8 MB) ← POST 1
├── story_26_post_1_20251019_015558.json (Metadata)
├── story_26_post_2_20251019_015605.png  (1.5 MB) ← POST 2
├── story_26_post_2_20251019_015605.json
├── story_26_post_3_20251019_015614.png  (1.7 MB) ← POST 3
├── story_26_post_3_20251019_015614.json
└── story_26_post_4_20251019_015621.png  (1.6 MB) ← POST 4
    story_26_post_4_20251019_015621.json
```

**Zweck:** Finale Post-Bilder (Charaktere + Szenen + Story-Text kombiniert)

---

## 🔧 CODE-STELLEN

### STEP 2: Asset-Generierung (START_PIPELINE_FULL.py, Zeile 141-302)

```python
def step_2_generate_assets(self, story_data):
    """Step 2: Assets generieren"""

    # Ordner-Struktur (Zeile 77-82)
    self.character_dir = PROJECT_ROOT / "05_assets/images/00_reference/characters"
    self.scene_dir = PROJECT_ROOT / "05_assets/images/00_reference/scenes"
    self.composed_dir = PROJECT_ROOT / "05_assets/images/03_generated/composed"

    # 1. Charaktere generieren (Zeile 178-214)
    print("\n   ━━━ STEP 2.1: Charaktere generieren ━━━")

    toshi_path = generate_character_reference(
        character_name="Toshi",
        pose="neutral_standing",
        variation=1,
        story_id=story_id,
        output_to_reference=True  # ← Speichert in 00_reference/characters/
    )

    mentor_path = generate_character_reference(
        character_name=mentor,
        pose="teaching",
        variation=1,
        story_id=story_id,
        output_to_reference=True
    )

    # 2. Szenen generieren (Zeile 216-234)
    print("\n   ━━━ STEP 2.2: Szenen-Hintergrund generieren ━━━")

    scene_path = generate_scene_background(
        scene_name=concept,
        scene_description=setting,
        atmosphere="mystical",
        time_of_day="day",
        variation=1  # ← Speichert in 00_reference/scenes/
    )

    # 3. Finale Bilder komponieren (Zeile 236-281)
    print("\n   ━━━ STEP 2.3: Finale Bilder komponieren ━━━")

    for i, part in enumerate(story_parts, 1):
        composed_path = compose_scene(
            characters_info=[...],
            scene_info=scene_info,
            story_moment=story_moment,
            panel_type=f"post_{i}",
            output_name=f"story_{story_id}_post_{i}"  # ← Speichert in 03_generated/composed/
        )
```

---

## 📝 GENERATOR-SCRIPTS

### 1. character_generator.py (Zeile 208)

```python
def generate_character_reference(
    character_name,
    pose="neutral_standing",
    variation=1,
    story_id=None,
    output_to_reference=True  # ← WICHTIG!
):
    """
    Generiert Charakter und speichert in:

    IF output_to_reference == True:
        → 05_assets/images/00_reference/characters/{character}/

    IF output_to_reference == False:
        → 05_assets/images/03_generated/characters/
    """

    # Speicherpfad bestimmen
    if output_to_reference:
        output_dir = f"05_assets/images/00_reference/characters/{character_slug}/"
    else:
        output_dir = f"05_assets/images/03_generated/characters/"

    # Bild generieren mit Google Imagen API
    ...

    # Speichern
    filename = f"{character_slug}_{pose}_v{variation}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    return filepath
```

**Wichtig:** `output_to_reference=True` in der Pipeline sorgt dafür, dass Charaktere in `00_reference/` gespeichert werden!

---

### 2. scene_background_generator.py (Zeile 141)

```python
def generate_scene_background(
    scene_name,
    scene_description,
    atmosphere="mystical",
    time_of_day="day",
    variation=1
):
    """
    Generiert Szenen-Hintergrund und speichert in:
    → 05_assets/images/00_reference/scenes/{scene_name}/
    """

    # Speicherpfad
    scene_slug = slugify(scene_name)
    output_dir = f"05_assets/images/00_reference/scenes/{scene_slug}/"
    os.makedirs(output_dir, exist_ok=True)

    # Bild generieren mit Google Imagen API
    ...

    # Speichern
    filename = f"{scene_slug}_{atmosphere}_{time_of_day}_v{variation}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    return filepath
```

---

### 3. scene_composer.py (Zeile 194)

```python
def compose_scene(
    characters_info,
    scene_info,
    story_moment,
    panel_type="scene",
    output_name=None
):
    """
    Kombiniert Charaktere + Szene zu finalem Bild.
    Speichert in:
    → 05_assets/images/03_generated/composed/
    """

    # Speicherpfad
    output_dir = "05_assets/images/03_generated/composed/"
    os.makedirs(output_dir, exist_ok=True)

    # Finale Komposition mit Google Imagen API
    # (Verwendet characters_info und scene_info als Referenz)
    ...

    # Speichern
    if output_name:
        filename = f"{output_name}_{timestamp}.png"
    else:
        filename = f"composed_{panel_type}_{timestamp}.png"

    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    return filepath
```

---

## 🔄 WORKFLOW-ABLAUF

```
1. START_PIPELINE_FULL.py wird gestartet
   ↓
2. STEP 1: Story generieren (OpenAI)
   ↓
3. STEP 2: Assets generieren
   │
   ├─ 2.1: Charaktere separat
   │       generate_character_reference("Toshi", ...)
   │       → Speichert: 05_assets/images/00_reference/characters/toshi/toshi_neutral_standing_v1_[timestamp].png
   │       generate_character_reference("Satoshi Sensei", ...)
   │       → Speichert: 05_assets/images/00_reference/characters/satoshi_sensei/satoshi_sensei_teaching_v1_[timestamp].png
   │
   ├─ 2.2: Szenen separat
   │       generate_scene_background("Dezentralisierung", ...)
   │       → Speichert: 05_assets/images/00_reference/scenes/dezentralisierung/dezentralisierung_mystical_day_v1_[timestamp].png
   │
   └─ 2.3: Finale Komposition (für jeden Post)
           compose_scene(characters=[toshi, mentor], scene=dezentralisierung, ...)
           → Speichert: 05_assets/images/03_generated/composed/story_26_post_1_[timestamp].png
           → Speichert: 05_assets/images/03_generated/composed/story_26_post_2_[timestamp].png
           → Speichert: 05_assets/images/03_generated/composed/story_26_post_3_[timestamp].png
           → Speichert: 05_assets/images/03_generated/composed/story_26_post_4_[timestamp].png
   ↓
4. STEP 3: Social Media Optimization
   ↓
5. STEP 4: QA/Review
   ↓
6. STEP 5: Publishing
   (Nutzt Bilder aus: 05_assets/images/03_generated/composed/)
```

---

## 🎯 BEISPIEL: Story ID 26

```
Story: "Toshis Abenteuer: Dezentralisierung"
Scene: Ein nebelverhangenes Dorf am Rande der digitalen Welt
Mentor: Satoshi Sensei
Konzept: Dezentralisierung

GENERIERTE ASSETS:
├── Charaktere (wiederverwendbar):
│   ├── 05_assets/images/00_reference/characters/toshi/toshi_neutral_standing_v1_20251019_015537.png
│   └── 05_assets/images/00_reference/characters/satoshi_sensei/satoshi_sensei_teaching_v1_20251019_015543.png
│
├── Szenen (wiederverwendbar):
│   └── 05_assets/images/00_reference/scenes/dezentralisierung/dezentralisierung_mystical_day_v1_20251019_015551.png
│
└── Finale Posts (story-spezifisch):
    ├── 05_assets/images/03_generated/composed/story_26_post_2_20251019_015558.png (1.8 MB)
    ├── 05_assets/images/03_generated/composed/story_26_post_3_20251019_015605.png (1.5 MB)
    └── 05_assets/images/03_generated/composed/story_26_post_4_20251019_015614.png (1.7 MB)
```

---

## ✅ VORTEILE DIESER STRUKTUR

1. **Wiederverwendbarkeit:** Charaktere & Szenen können für mehrere Stories genutzt werden
2. **Ordnung:** Klare Trennung zwischen Referenz-Material und finalen Posts
3. **Flexibilität:** Charaktere können mit verschiedenen Szenen kombiniert werden
4. **Archivierung:** Jedes Bild hat Timestamp + JSON-Metadata
5. **Skalierbarkeit:** Neue Charaktere/Szenen können einfach hinzugefügt werden

---

## 📊 AKTUELLER BESTAND

```bash
# Charaktere
05_assets/images/00_reference/characters/
├── toshi/              → 4 Varianten (1.1 MB each)
└── satoshi_sensei/     → 3 Varianten (1.0 MB each)

# Szenen
05_assets/images/00_reference/scenes/
├── dezentralisierung/  → 3 Varianten (1.6-1.7 MB)
└── der_weg_der_nodes/  → 1 Variante

# Finale Posts
05_assets/images/03_generated/composed/
└── 24 kombinierte Post-Bilder (1.4-2.0 MB each)
```

---

**Status:** ✅ Funktioniert perfekt
**API:** Google Imagen 3.0
**Format:** PNG mit transparentem Hintergrund (Charaktere) oder Szenen-BG
**Metadata:** Jedes Bild hat .json mit Generation-Parametern
