#!/usr/bin/env python3
"""
TOSHI - STORYRIDER PIPELINE
Erstellt komplett neue Stories mit neuen Charakteren und Szenen als Referenzen
"""

import sys
import json
import os
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Add imports
sys.path.insert(0, str(Path(__file__).parent / "00_system_core"))
sys.path.insert(0, str(Path(__file__).parent / "00_system_core" / "scripts"))

# Jetzt importieren
from generate_daily_story import DailyStoryGenerator
from character_generator import generate_character_reference
from scene_background_generator import generate_scene_background
from scene_composer import compose_scene
from social_media_optimizer import SocialMediaOptimizer
from image_consistency_analyzer import ImageConsistencyAnalyzer
from image_regeneration_loop import ImageRegenerationLoop
from telegram_poster import TelegramPoster
from kodex_card_generator import KodexCardGenerator

# Try to import CharacterExtractor
try:
    from character_extractor import CharacterExtractor
    CHARACTER_EXTRACTOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  CharacterExtractor nicht verfügbar: {e}")
    CHARACTER_EXTRACTOR_AVAILABLE = False
    CharacterExtractor = None

from npc_generator import generate_npc_reference

# Try to import speech bubble and video modules
try:
    from speech_bubble_overlay import SpeechBubble
    SPEECH_BUBBLE_AVAILABLE = True
except ImportError:
    print("⚠️  SpeechBubble nicht verfügbar")
    SPEECH_BUBBLE_AVAILABLE = False
    SpeechBubble = None

try:
    from fal_video_generator import FalVideoGenerator
    FAL_VIDEO_AVAILABLE = True
except ImportError:
    print("⚠️  FalVideoGenerator nicht verfügbar")
    FAL_VIDEO_AVAILABLE = False
    FalVideoGenerator = None

# Paths
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "04_database" / "local_cache.sqlite"

class StoryRiderPipeline:
    def __init__(self, dry_run=False, skip_images=False, auto_approve=False, auto_regenerate=False, extract_all_characters=True, add_speech_bubbles=False, generate_videos=False):
        self.dry_run = dry_run
        self.skip_images = skip_images
        self.auto_approve = auto_approve
        self.auto_regenerate = auto_regenerate
        self.extract_all_characters = extract_all_characters
        self.add_speech_bubbles = add_speech_bubbles
        self.generate_videos = generate_videos
        self.story_generator = DailyStoryGenerator(use_ai=True)

        # Initialize OpenAI client for dynamic content generation
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Initialize CharacterExtractor if available
        if extract_all_characters and CHARACTER_EXTRACTOR_AVAILABLE:
            try:
                self.character_extractor = CharacterExtractor()
                print("✅ CharacterExtractor initialisiert (Gender-Erkennung AKTIV)")
            except Exception as e:
                print(f"⚠️  CharacterExtractor Init-Fehler: {e}")
                self.character_extractor = None
        else:
            self.character_extractor = None
            if not CHARACTER_EXTRACTOR_AVAILABLE:
                print("⚠️  CharacterExtractor nicht verfügbar (Gender-Erkennung INAKTIV)")
        
    def get_next_story_request(self):
        """Erstellt IMMER eine neue Story-Request (StoryRider-Modus!)"""
        print("\n📋 Erstelle neue Story-Request...")

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # STORYRIDER: IMMER neue Story generieren!
        print("   🎭 StoryRider-Modus: Generiere komplett neue Story...")
        request_id = self.create_new_story_request()

        if request_id:
            cursor.execute("SELECT * FROM story_requests WHERE id = ?", (request_id,))
            request = dict(cursor.fetchone())
            print(f"   ✅ Story-Request erstellt: ID {request['id']}")
            print(f"      Kapitel {request['chapter_number']}, Szene {request['scene_number']}")
            print(f"      Konzept: {request['concept']}")
            print(f"      Mentor: {request['mentor']} ({request['mentor_gender']})")
            conn.close()
            return request

        conn.close()
        return None
    
    def generate_dynamic_content(self, used_concepts):
        """
        Generiert AUTOMATISCH neues Bitcoin-Content mit OpenAI!
        Keine festen Listen mehr - UNBEGRENZT erweiterbar!

        Returns: Dict mit concept, mentor, mentor_gender, setting, challenge, learning_goal
        """
        print("   🤖 Generiere automatisch neues Bitcoin-Content...")

        # Liste bereits verwendeter Konzepte für Kontext
        used_concepts_str = ", ".join(used_concepts) if used_concepts else "Noch keine"

        prompt = f"""Du bist ein Bitcoin-Experte und Story-Architekt. Erstelle AUTOMATISCH ein neues Bitcoin-Lernkonzept für eine Retro-RPG Story.

BEREITS BEHANDELTE KONZEPTE (nicht wiederholen):
{used_concepts_str}

AUFGABE:
Erstelle ein NEUES, unbehandeltes Bitcoin-Konzept mit ALLEM was dafür benötigt wird:

1. KONZEPT: Ein neues Bitcoin-Thema (technisch präzise, noch nicht behandelt)
2. MENTOR: Erfinde einen NEUEN, passenden Charakter (Name + Geschlecht)
   - Gib dem Mentor einen kreativen Namen der zum Thema passt
   - Jeder Mentor ist einzigartig - keine Wiederholungen!
3. SETTING: Eine atmosphärische Retro-RPG Location (Zelda/Pokémon-Stil)
4. CHALLENGE: Die zentrale Frage/Herausforderung für Toshi
5. LEARNING_GOAL: Das präzise Bitcoin-Lernziel (technisch korrekt!)
6. MENTOR_APPEARANCE: DETAILLIERTE visuelle Beschreibung für Bildgenerierung (FIX v2.3.4)

WICHTIG:
- 100% Bitcoin-Genauigkeit (BIP-Nummern, exakte Werte, Mechanismen)
- NEUER Mentor bei jedem Aufruf (keine Wiederholungen!)
- Kreative, atmosphärische Settings (Retro-RPG-Welt)
- Technisch tiefgehend aber verständlich

🎨 KRITISCH - MENTOR_APPEARANCE (FIX v2.3.4):
Beschreibe den Mentor SO DETAILLIERT, dass ein Bildgenerator ihn konsistent zeichnen kann!

MUST INCLUDE:
- Haarfarbe, Frisur, Gesichtsbehaarung (Bart, etc.)
- Gesichtsausdruck (weise, streng, freundlich, etc.)
- Kleidung (Farben, Stil, besondere Elemente)
- Accessoires (Stab, Schmuck, Werkzeug, etc.)
- Körperbau (schlank, kräftig, alt, jung, etc.)
- Besondere Merkmale (Narben, Tattoos, etc.)

BEISPIEL:
"elderly wise woman, long flowing silver hair in elegant braid, warm nurturing expression, kind eyes, wearing elegant purple robes with golden trim, golden keys hanging from ornate belt, tall staff with crystal top, regal posture, dignified presence"

Antworte NUR mit validem JSON in diesem Format:
{{
  "concept": "Bitcoin Konzept Name",
  "mentor": "Kreativer Mentor Name",
  "mentor_gender": "male" oder "female",
  "mentor_appearance": "SEHR DETAILLIERTE visuelle Beschreibung (mind. 30 Wörter!)",
  "setting": "Die atmosphärische Location",
  "challenge": "Die zentrale Frage für Toshi",
  "learning_goal": "Das präzise technische Lernziel mit konkreten Details"
}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,  # Kreativität für neue Mentoren/Settings
                response_format={"type": "json_object"}
            )

            content_data = json.loads(response.choices[0].message.content)

            print(f"   ✅ Neues Konzept generiert: {content_data['concept']}")
            print(f"   ✅ Neuer Mentor: {content_data['mentor']} ({content_data['mentor_gender']})")
            print(f"   ✅ Setting: {content_data['setting']}")
            print(f"   🎨 Appearance: {content_data.get('mentor_appearance', 'N/A')[:50]}...")

            return content_data

        except Exception as e:
            print(f"   ❌ Fehler bei Content-Generierung: {e}")
            # Fallback: Einfaches Beispiel
            return {
                "concept": "Bitcoin Basics",
                "mentor": "Genesis Guide",
                "mentor_gender": "male",
                "mentor_appearance": "elderly wise sage, long white beard, bald head with straw hat, serene expression, traditional brown monk robes, wooden staff, calm presence",
                "setting": "Der Ursprungs-Platz",
                "challenge": "Was macht Bitcoin besonders?",
                "learning_goal": "Bitcoin ist digitales, dezentrales Geld ohne zentrale Kontrolle"
            }

    def create_new_story_request(self):
        """Erstellt neue Story-Request mit VOLLAUTOMATISCHER Content-Generierung!"""

        print("\n📋 Erstelle neue Story-Request (DYNAMISCH)...")

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Hole bereits verwendete Konzepte
        cursor.execute("SELECT DISTINCT concept FROM story_requests WHERE concept IS NOT NULL")
        used_concepts = [row['concept'] for row in cursor.fetchall()]

        print(f"   📊 Bereits behandelt: {len(used_concepts)} Konzepte")

        # AUTOMATISCHE GENERIERUNG mit OpenAI!
        concept_data = self.generate_dynamic_content(used_concepts)

        # 🤖 VOLLAUTOMATISCHE CONTENT-GENERIERUNG (keine festen Listen!)
        # Keine Limits, keine Rotation - JEDES MAL neu und einzigartig!

        # Hole Count für Kapitel/Szenen-Berechnung
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM story_requests")
        count = cursor.fetchone()[0]

        # Automatisches Kapitel-System (7 Szenen pro Kapitel)
        chapter = (count // 7) + 1
        scene = (count % 7) + 1

        # Erstelle Request (FIX v2.3.4: mentor_appearance hinzugefügt!)
        cursor.execute("""
            INSERT INTO story_requests
            (scene_id, chapter_number, scene_number, setting, challenge,
             learning_goal, mentor, mentor_gender, mentor_appearance, concept, status, story_generated, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 0, ?)
        """, (
            100 + count,  # Unique Scene ID
            chapter, scene,
            concept_data['setting'],
            concept_data['challenge'],
            concept_data['learning_goal'],
            concept_data['mentor'],
            concept_data['mentor_gender'],
            concept_data.get('mentor_appearance', ''),  # NEU: Detaillierte visuelle Beschreibung!
            concept_data['concept'],
            datetime.now().isoformat()
        ))

        request_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"   ✅ Neue Story-Request erstellt: ID {request_id}")
        print(f"      Kapitel {chapter}, Szene {scene}/7")
        print(f"      Konzept: {concept_data['concept']}")
        print(f"      Mentor: {concept_data['mentor']} ({concept_data['mentor_gender']})")
        print(f"      🎉 DYNAMISCH GENERIERT - Unbegrenzt erweiterbar!")

        return request_id
    
    def run(self):
        """Hauptworkflow"""
        print("\n" + "="*80)
        print("🎮 TOSHI - STORYRIDER PIPELINE")
        print("   Neue Stories mit neuen Charakteren und Szenen")
        print("="*80)
        print(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"🎨 Bilder: {'SKIP' if self.skip_images else 'GENERIEREN'}")
        print(f"✅ Review: {'AUTO' if self.auto_approve else 'MANUAL'}")
        print("="*80)
        
        # Step 1: Story-Request holen/erstellen
        request = self.get_next_story_request()
        
        if not request:
            print("\n❌ Konnte keine Story-Request erstellen")
            return {"success": False}
        
        # Step 2: Story generieren (nutzt OpenAI)
        print("\n" + "━"*80)
        print("📝 STEP 1: Story generieren")
        print("━"*80)
        
        # Erstelle Scene-Daten im Format von generate_daily_story
        scene_data = {
            'id': request['scene_id'],
            'chapter_id': request['chapter_number'],
            'scene_number': request['scene_number'],
            'setting': request['setting'],
            'challenge': request['challenge'],
            'learning_goal': request['learning_goal'],
            'mentor': request['mentor'],
            'mentor_gender': request.get('mentor_gender', 'male'),
            'mentor_appearance': request.get('mentor_appearance', ''),  # FIX v2.3.4: Visuelle Details!
            'concept': request['concept'],
            'chapter_title': f"Kapitel {request['chapter_number']}",
            'chapter_theme': "Bitcoin Advanced"
        }
        
        story_output = self.story_generator.generate_story_parts(scene_data, num_posts=4)
        post_plan = self.story_generator.create_post_plan(request['scene_id'], story_output)
        # FIX v2.3.3: Übergebe request_id damit story_outputs korrekt verknüpft wird!
        story_id = self.story_generator.save_to_database(
            scene_id=request['scene_id'],
            story_output=story_output,
            post_plan=post_plan,
            request_id=request['id']  # WICHTIG: Nutze existierende request ID!
        )
        
        print(f"\n✅ Story: {story_output['title']}")
        print(f"   Mentor: {scene_data['mentor']}")
        print(f"   Konzept: {scene_data['concept']}")
        print(f"   Story ID: {story_id}")
        print(f"   Posts: {len(story_output['parts'])}")
        
        result = {
            "success": True,
            "story_output": story_output,
            "scene_data": scene_data,
            "story_id": story_id,
            "post_plan": post_plan
        }
        
        # Step 2: Assets generieren
        if not self.skip_images:
            print("\n" + "━"*80)
            print("🎨 STEP 2: Assets generieren (NEUE REFERENZEN)")
            print("━"*80)
            result["assets"] = self.generate_assets(story_id, scene_data, story_output)
        else:
            result["assets"] = {"success": True, "skipped": True}
        
        # Step 3: Social Media Optimization
        print("\n" + "━"*80)
        print("🎨 STEP 3: Social Media Optimization")
        print("━"*80)
        result["optimized_posts"] = self.optimize_posts(result)
        
        # Step 4: Approval
        if not self.auto_approve:
            print("\n" + "━"*80)
            print("✅ STEP 4: Quality Review & Approval")
            print("━"*80)
            approval = input("👉 Content freigeben? (y/n): ")
            result["approval"] = {"approved": approval.lower() == 'y', "auto": False}
        else:
            print("\n" + "━"*80)
            print("✅ STEP 4: Quality Review & Approval")
            print("━"*80)
            print("   🤖 AUTO-APPROVE aktiviert")
            print("   ✅ Content automatisch freigegeben")
            result["approval"] = {"approved": True, "auto": True}
        
        # Step 5: Publishing
        if result["approval"]["approved"]:
            print("\n" + "━"*80)
            print("📤 STEP 5: Publishing")
            print("━"*80)
            result["publish"] = self.publish(result)
        else:
            print("\n   ❌ Content nicht freigegeben - Abbruch")
            result["publish"] = {"success": False, "reason": "not_approved"}
        
        # Save results
        self.save_results(result)
        
        return result

    def _load_or_generate_character(self, character_name, pose, gender, story_id, ref_dir, description=None):
        """
        Lädt bestehende Charakter-Varianten oder generiert neue

        Args:
            character_name: Name des Charakters
            pose: Pose (z.B. "neutral_standing", "teaching")
            gender: Gender (male/female/unknown)
            story_id: Story ID
            ref_dir: Reference-Directory für den Charakter
            description: (Optional) Detaillierte visuelle Beschreibung (FIX v2.3.4)

        Returns:
            Dict mit paths für forward, left, right
        """
        paths = {}

        # Prüfe ob Reference-Directory existiert
        if ref_dir.exists():
            print(f"\n   📂 {character_name} existiert bereits - lade Referenzen...")

            # Suche nach vorhandenen Varianten
            for facing in ["forward", "left", "right"]:
                # Pattern: charactername_pose_facing_direction_*.png
                pattern = f"{character_name.lower()}_{pose}_facing_{facing}_*.png"
                matches = list(ref_dir.glob(pattern))

                if matches:
                    # Nehme neueste Datei
                    latest = max(matches, key=lambda p: p.stat().st_mtime)
                    paths[facing] = str(latest)
                    print(f"      ✅ {facing}: {latest.name}")

            # Wenn alle 3 Varianten gefunden, nutze diese
            if len(paths) == 3:
                print(f"   ♻️  Wiederverwendung bestehender Charaktere (keine neue Generierung!)")
                return paths
            else:
                print(f"   ⚠️  Nur {len(paths)}/3 Varianten gefunden - generiere fehlende...")

        # Generiere fehlende oder alle Varianten
        print(f"\n   🎨 Generiere {character_name} in allen Blickrichtungen...")
        print(f"   👤 Gender: {gender}")
        if description:
            print(f"   🎨 Description: {description[:50]}...")

        for facing in ["forward", "left", "right"]:
            if facing in paths:
                print(f"   ✅ {facing}: bereits vorhanden")
                continue

            print(f"   📸 Facing: {facing}")
            path_variant = generate_character_reference(
                character_name=character_name,
                pose=pose,
                facing_direction=facing,
                variation=1,
                story_id=story_id,
                output_to_reference=True,
                gender=gender,
                description=description  # FIX v2.3.4: Übergebe visuelle Details!
            )
            if path_variant:
                paths[facing] = path_variant
                print(f"      ✅ {character_name} {facing}: {Path(path_variant).name}")

        return paths

    def generate_assets(self, story_id, scene_data, story_output):
        """Generiert Charaktere + Szenen als REFERENZEN"""
        assets = {
            "characters": [],
            "scenes": [],
            "composed": []
        }

        # Extract story_parts from story_output
        story_parts = story_output.get('parts', [])

        mentor = scene_data['mentor']
        concept = scene_data['concept']
        setting = scene_data['setting']

        # 0. Gender & Appearance aus DB verwenden (FIX v2.3.3 & v2.3.4!)
        print(f"\n   ━━━ STEP 2.0: Mentor-Daten aus DB laden ━━━")
        # WICHTIG: Gender kommt aus DB (story_requests.mentor_gender)
        # NICHT aus Story extrahieren wegen deutscher Grammatik (Artikel != Gender!)
        mentor_gender = scene_data.get('mentor_gender', 'male')
        mentor_appearance = scene_data.get('mentor_appearance', '')  # FIX v2.3.4: Detaillierte visuelle Beschreibung!
        print(f"   ✅ Mentor-Gender aus DB: {mentor_gender}")
        if mentor_appearance:
            print(f"   🎨 Mentor-Appearance: {mentor_appearance[:60]}...")
        print(f"   💡 DB ist die einzige zuverlässige Quelle für Gender (deutsche Artikel-Problem umgangen)")

        # 1. Charaktere generieren (als Referenzen!)
        print(f"\n   ━━━ STEP 2.1: NEUE Charaktere generieren ━━━")
        print(f"   ℹ️  Diese werden als REFERENZEN gespeichert!")

        # Check if auto-regeneration is enabled
        if self.auto_regenerate:
            print(f"   🔄 Auto-Regeneration AKTIV (Ziel-Score: 0.7)")
            regen_loop = ImageRegenerationLoop(target_score=0.7, max_attempts=3)

            # Get existing characters for comparison
            existing_chars = []
            char_ref_dir = PROJECT_ROOT / "05_assets/images/00_reference/characters"
            for char_dir in char_ref_dir.iterdir():
                if char_dir.is_dir():
                    for img in char_dir.glob("*.png"):
                        existing_chars.append(img)
                        break  # Nur 1 pro Charakter

            # Regenerate Toshi
            print(f"\n   🎨 Generiere Toshi (mit Auto-Regeneration)...")
            toshi_result = regen_loop.regenerate_character_until_consistent(
                character_name="Toshi",
                pose="neutral_standing",
                story_id=story_id,
                existing_characters=existing_chars[:3]  # Compare with 3 existing
            )

            toshi_path = toshi_result.get('path')
            if toshi_path:
                print(f"   ✅ Toshi: {Path(toshi_path).name} (Score: {toshi_result['final_score']:.2f}, Versuche: {toshi_result['attempts']})")
                assets['characters'].append({
                    'character': 'Toshi',
                    'path': str(toshi_path),
                    'pose': 'neutral_standing',
                    'consistency_score': toshi_result['final_score'],
                    'attempts': toshi_result['attempts']
                })
                existing_chars.append(Path(toshi_path))

            # Regenerate Mentor (FIX v2.3.4: mit detaillierter Beschreibung!)
            print(f"\n   🎨 Generiere NEUEN Mentor: {mentor} (mit Auto-Regeneration)...")
            print(f"   👤 Gender: {mentor_gender}")
            if mentor_appearance:
                print(f"   🎨 Appearance: {mentor_appearance[:60]}...")
            mentor_result = regen_loop.regenerate_character_until_consistent(
                character_name=mentor,
                pose="teaching",
                story_id=story_id,
                existing_characters=existing_chars[:3],
                gender=mentor_gender,
                description=mentor_appearance  # FIX v2.3.4: Übergebe visuelle Details!
            )

            mentor_path = mentor_result.get('path')
            if mentor_path:
                print(f"   ✅ {mentor}: {Path(mentor_path).name} (Score: {mentor_result['final_score']:.2f}, Versuche: {mentor_result['attempts']})")
                assets['characters'].append({
                    'character': mentor,
                    'path': str(mentor_path),
                    'pose': 'teaching',
                    'consistency_score': mentor_result['final_score'],
                    'attempts': mentor_result['attempts']
                })

        else:
            # Standard generation (no regeneration loop)
            # Extrahiere Gender für ALLE Charaktere
            full_story_text = "\n\n".join([part.get('text', '') for part in story_parts])
            toshi_gender = "male"  # Default
            if self.character_extractor:
                all_chars = self.character_extractor.extract_characters_from_story_part(
                    story_text=full_story_text,
                    known_characters=["Toshi", mentor]
                )
                for char in all_chars:
                    if char['name'] == 'Toshi' and 'gender' in char:
                        toshi_gender = char['gender']
                        print(f"   ✅ Toshi-Gender erkannt: {toshi_gender}")
                        break

            # Toshi - Prüfe ob bereits vorhanden, sonst generiere
            toshi_ref_dir = Path("05_assets/images/00_reference/characters/toshi")
            toshi_paths = self._load_or_generate_character(
                character_name="Toshi",
                pose="neutral_standing",
                gender=toshi_gender,
                story_id=story_id,
                ref_dir=toshi_ref_dir
            )

            # Default: forward
            toshi_path = toshi_paths.get('forward', list(toshi_paths.values())[0] if toshi_paths else None)

            if toshi_path:
                assets['characters'].append({
                    'character': 'Toshi',
                    'path': str(toshi_path),
                    'path_forward': str(toshi_paths.get('forward', toshi_path)),
                    'path_left': str(toshi_paths.get('left', toshi_path)),
                    'path_right': str(toshi_paths.get('right', toshi_path)),
                    'pose': 'neutral_standing'
                })

            # Mentor - Prüfe ob bereits vorhanden, sonst generiere (FIX v2.3.4: mit Beschreibung!)
            mentor_ref_dir = Path(f"05_assets/images/00_reference/characters/{mentor.lower()}")
            mentor_paths = self._load_or_generate_character(
                character_name=mentor,
                pose="teaching",
                gender=mentor_gender,
                story_id=story_id,
                ref_dir=mentor_ref_dir,
                description=mentor_appearance  # FIX v2.3.4: Übergebe visuelle Details!
            )

            # Default: forward
            mentor_path = mentor_paths.get('forward', list(mentor_paths.values())[0] if mentor_paths else None)

            if mentor_path:
                assets['characters'].append({
                    'character': mentor,
                    'path': str(mentor_path),
                    'path_forward': str(mentor_paths.get('forward', mentor_path)),
                    'path_left': str(mentor_paths.get('left', mentor_path)),
                    'path_right': str(mentor_paths.get('right', mentor_path)),
                    'pose': 'teaching'
                })
        
        # 2.2 ENTFÄLLT - Jeder Post bekommt seinen eigenen Hintergrund!
        # 2.5 Extrahiere ALLE Charaktere aus Story (NEW!)
        all_post_characters = {}
        if self.extract_all_characters and self.character_extractor:
            print(f"\n   ━━━ STEP 2.5: Extrahiere ALLE Charaktere aus Story ━━━")
            all_post_characters = self.character_extractor.extract_characters_from_full_story(
                story_parts=story_parts,
                mentor_name=mentor
            )

            # NPC-Generierung ENTFERNT (Optimierung v2.4.0)
            # NPCs werden NICHT mehr als separate Sprites generiert!
            # Grund: NPCs sind bereits im Scene Background enthalten (via scene_background_generator.py)
            # Der Scene Generator analysiert den Story-Text automatisch und malt NPCs direkt ins Hintergrundbild
            # Dies spart Kosten (~$0.20-0.40 pro Story) und beschleunigt die Pipeline
            print(f"\n   ℹ️  NPCs werden im Scene Background generiert (keine separaten Sprites)")

            # Nur Hauptcharaktere (Toshi + Mentor) bekommen Pfade zugewiesen
            for post_num, characters in all_post_characters.items():
                for char in characters:
                    char_name = char['name']
                    if char_name == 'Toshi':
                        char['path'] = str(toshi_path)
                    elif char_name == mentor:
                        char['path'] = str(mentor_path)
                    # NPCs werden übersprungen - sie sind im Background!

        # 2.6: Kodexkarten generieren (falls vorhanden)
        if 'kodex_karten' in story_output and story_output['kodex_karten']:
            print(f"\n   ━━━ STEP 2.6: Kodexkarte generieren ━━━")

            try:
                kodex_generator = KodexCardGenerator()
                kodex_data = kodex_generator.extract_kodex_from_story(story_output)

                if kodex_data:
                    print(f"   🎴 Kodexkarte erkannt: {kodex_data['name']}")
                    kodex_path = kodex_generator.generate_card(kodex_data)

                    assets['kodex_card'] = {
                        'name': kodex_data['name'],
                        'path': str(kodex_path),
                        'kapitel': kodex_data.get('kapitel', '')
                    }
                    print(f"   ✅ Kodexkarte generiert: {kodex_path.name}")
                else:
                    print(f"   ⚠️  Kodexkarte-Daten konnten nicht extrahiert werden")
            except Exception as e:
                print(f"   ❌ Fehler bei Kodexkarten-Generierung: {e}")
                assets['kodex_card'] = None
        else:
            print(f"\n   ℹ️  Keine Kodexkarte in dieser Story")
            assets['kodex_card'] = None

        # 3. Finale Bilder komponieren
        print(f"\n   ━━━ STEP 2.7: Finale Bilder komponieren ━━━")

        # Check if auto-regeneration is enabled for composed images
        composed_images_for_check = []  # Track for consistency check

        # Initialize composed regen_loop if needed
        composed_regen_loop = None
        if self.auto_regenerate:
            print(f"   🔄 Auto-Regeneration für Post-Bilder AKTIV")
            composed_regen_loop = ImageRegenerationLoop(target_score=0.7, max_attempts=3)

        # STORY-KONTEXT für alle Hintergründe (gemeinsame Basis für Konsistenz)
        full_story_text = "\n\n".join([part.get('text', '') for part in story_parts])
        print(f"\n   📝 Story-Kontext: {len(full_story_text)} Zeichen (Basis für alle Hintergründe)")

        # Kodexkarte-Pfad extrahieren (falls vorhanden)
        kodex_card_path_global = None
        if assets.get('kodex_card') and assets['kodex_card'].get('path'):
            kodex_card_path_global = assets['kodex_card']['path']
            print(f"   🎴 Kodexkarte verfügbar: {Path(kodex_card_path_global).name}")

        # Kodexkarte wird IMMER in Post 4 angezeigt (Verstehen/Resolution)
        kodex_post_number = 4
        print(f"   🎴 Kodexkarte wird in Post {kodex_post_number} (letzter Post) angezeigt")

        for i, part in enumerate(story_parts, 1):
            print(f"\n   🎬 Komponiere Post {i}/{len(story_parts)}...")

            # INDIVIDUELLER Hintergrund pro Post mit Story-Kontext
            post_title = part.get('title', f'Post {i}')
            post_text = part.get('text', '')
            print(f"   🏞️  Generiere Hintergrund für '{post_title}'...")

            # Kombiniere Story-Kontext (Konsistenz) + Post-Text (Variation)
            combined_context = f"STORY-KONTEXT (für Konsistenz):\n{full_story_text}\n\n" \
                              f"DIESER MOMENT (Post {i} - {post_title}):\n{post_text}"

            scene_path_post = generate_scene_background(
                scene_name=f"{concept}_post_{i}",
                scene_description=setting,
                atmosphere="mystical",
                time_of_day="day",
                variation=i,  # Variation pro Post
                story_text=combined_context
            )

            if scene_path_post:
                print(f"   ✅ Szene Post {i}: {Path(scene_path_post).name}")
                assets['scenes'].append({
                    'scene': f"{concept}_post_{i}",
                    'path': str(scene_path_post),
                    'setting': setting,
                    'post_number': i
                })

            # Use extracted characters if available
            if self.extract_all_characters and i in all_post_characters:
                characters_info = []
                for char in all_post_characters[i]:
                    if char.get('path'):
                        # Wähle richtige Blickrichtung basierend auf facing_direction
                        char_path = char.get('path')
                        facing = char.get('facing_direction', 'forward')

                        # Prüfe ob wir alle Blickrichtungen haben
                        char_name = char['name']
                        if char_name == 'Toshi' and facing in toshi_paths:
                            char_path = str(toshi_paths[facing])
                        elif char_name == mentor and facing in mentor_paths:
                            char_path = str(mentor_paths[facing])

                        characters_info.append({
                            'character_name': char['name'],
                            'path': char_path,
                            'pose': char.get('pose', 'neutral_standing'),
                            'facing_direction': facing
                        })
                        print(f"      👁️  {char['name']}: facing {facing} → {Path(char_path).name}")
                print(f"   📝 {len(characters_info)} Charaktere aus Extraction")
            else:
                # Fallback: Nur Toshi + Mentor
                characters_info = [
                    {
                        'character_name': 'Toshi',
                        'path': str(toshi_path) if toshi_path else None,
                        'pose': 'neutral_standing',
                        'facing_direction': 'forward'
                    },
                    {
                        'character_name': mentor,
                        'path': str(mentor_path) if mentor_path else None,
                        'pose': 'teaching',
                        'facing_direction': 'forward'
                    }
                ]

            scene_info = {
                'scene_name': f"{concept}_post_{i}",
                'path': str(scene_path_post) if scene_path_post else None,
                'setting': f"{setting} - {part.get('title', '')}"
            }

            story_moment = f"{part['title']}: {part['text']}"

            # Use regeneration loop if enabled
            if composed_regen_loop and i > 1:  # Regenerate ab Post 2
                print(f"   🔄 Mit Auto-Regeneration (Ziel: 0.7)")
                result = composed_regen_loop.regenerate_composed_until_consistent(
                    characters_info=characters_info,
                    scene_info=scene_info,
                    story_moment=story_moment,
                    panel_type=f"post_{i}",
                    output_name=f"story_{story_id}_post_{i}",
                    existing_composed=composed_images_for_check
                )

                composed_path = result.get('path')
                if composed_path:
                    print(f"   ✅ Post {i}: {Path(composed_path).name} (Score: {result['final_score']:.2f}, Versuche: {result['attempts']})")
                    assets['composed'].append({
                        'post_number': i,
                        'path': str(composed_path),
                        'title': part['title'],
                        'consistency_score': result['final_score'],
                        'attempts': result['attempts']
                    })
                    composed_images_for_check.append(Path(composed_path))
            else:
                # Standard composition without regeneration
                # NUR den Post mit Kodexkarte-Erwähnung bekommt die Karte!
                kodex_card_path = None
                if kodex_card_path_global and i == kodex_post_number:
                    kodex_card_path = kodex_card_path_global
                    print(f"      🎴 Kodexkarte wird in Post {i} eingeblendet")

                composed_path = compose_scene(
                    characters_info=characters_info,
                    scene_info=scene_info,
                    story_moment=story_moment,
                    panel_type=f"post_{i}",
                    output_name=f"story_{story_id}_post_{i}",
                    kodex_card_path=kodex_card_path
                )

                if composed_path:
                    print(f"   ✅ Post {i}: {Path(composed_path).name}")
                    assets['composed'].append({
                        'post_number': i,
                        'path': str(composed_path),
                        'title': part['title']
                    })
                    composed_images_for_check.append(Path(composed_path))

        # 4. Style-Konsistenz analysieren (NEUER SCHRITT!)
        print(f"\n   ━━━ STEP 2.4: Style-Konsistenz prüfen ━━━")

        try:
            analyzer = ImageConsistencyAnalyzer()

            # 4.1 Analysiere neu generierte Reference Assets (Charaktere + Szenen)
            new_images = []
            for char in assets['characters']:
                if char['path']:
                    new_images.append(Path(char['path']))
            for scene in assets['scenes']:
                if scene['path']:
                    new_images.append(Path(scene['path']))

            if new_images:
                print(f"\n   🔍 Analysiere {len(new_images)} Reference Assets (Charaktere + Szenen)...")

                # Extrahiere Farbpaletten
                for img_path in new_images:
                    palette = analyzer.extract_color_palette(img_path)
                    print(f"   🎨 {img_path.name}: {len(palette)} Hauptfarben")

                # Style-Vergleich
                comparison = analyzer.compare_styles(new_images)
                assets['consistency_references'] = comparison

                if comparison['consistent']:
                    print(f"   ✅ Reference Assets konsistent (Score: {comparison['consistency_score']:.2f})")
                else:
                    print(f"   ⚠️  Reference Assets inkonsistent (Score: {comparison['consistency_score']:.2f})")

            # 4.2 Analysiere finale Post-Bilder (NEUE FUNKTION!)
            composed_images = []
            for composed in assets['composed']:
                if composed.get('path'):
                    composed_images.append(Path(composed['path']))

            if composed_images:
                print(f"\n   🔍 Analysiere {len(composed_images)} finale Post-Bilder...")

                # Extrahiere Farbpaletten der finalen Posts
                for img_path in composed_images:
                    palette = analyzer.extract_color_palette(img_path)
                    print(f"   🎨 {img_path.name}: {len(palette)} Hauptfarben")

                # Style-Vergleich der finalen Posts
                composed_comparison = analyzer.compare_styles(composed_images)
                assets['consistency_posts'] = composed_comparison

                if composed_comparison['consistent']:
                    print(f"   ✅ Post-Bilder konsistent (Score: {composed_comparison['consistency_score']:.2f})")
                else:
                    print(f"   ⚠️  Post-Bilder inkonsistent (Score: {composed_comparison['consistency_score']:.2f})")
                    print(f"   💡 Tipp: Prüfe die finalen Post-Bilder auf Style-Unterschiede")

                # Gesamtbewertung
                overall_score = (comparison.get('consistency_score', 0.0) + composed_comparison.get('consistency_score', 0.0)) / 2
                assets['consistency_overall'] = overall_score

                print(f"\n   📊 GESAMTBEWERTUNG:")
                print(f"      Reference Assets: {comparison.get('consistency_score', 0.0):.2f}")
                print(f"      Post-Bilder: {composed_comparison.get('consistency_score', 0.0):.2f}")
                print(f"      Overall: {overall_score:.2f}")

                if overall_score >= 0.7:
                    print(f"   ✅ Gesamtkonsistenz erreicht!")
                else:
                    print(f"   ⚠️  Gesamtkonsistenz noch nicht optimal (Ziel: ≥0.7)")

        except Exception as e:
            print(f"   ⚠️  Konsistenz-Analyse fehlgeschlagen: {e}")

        print(f"\n   ━━━ Asset-Generierung abgeschlossen ━━━")
        print(f"   ✅ {len(assets['characters'])} Charaktere (REFERENZEN)")
        print(f"   ✅ {len(assets['scenes'])} Szenen (REFERENZEN)")
        print(f"   ✅ {len(assets['composed'])} finale Bilder")

        # SPEECH BUBBLES - Automatisch hinzufügen (NEU!)
        if SPEECH_BUBBLE_AVAILABLE and self.add_speech_bubbles:
            print(f"\n   ━━━ STEP 2.5: Sprechblasen hinzufügen ━━━")
            try:
                from PIL import Image
                bubble = SpeechBubble()

                for composed in assets['composed']:
                    post_num = composed['post_number']
                    image_path = Path(composed['path'])

                    # Hole Story-Text für diesen Post
                    story_text = ""
                    for i, part in enumerate(story_parts, 1):
                        if i == post_num:
                            story_text = part.get('text', part.get('story', ""))[:150]  # Max 150 Zeichen
                            break

                    if not story_text:
                        print(f"   ⚠️  Post {post_num}: Kein Text gefunden, überspringe...")
                        continue

                    # Öffne Bild
                    img = Image.open(image_path)

                    # Füge Sprechblase hinzu (oben, zentriert)
                    img_with_bubble = bubble.add_speech_bubble(
                        image=img,
                        text=story_text,
                        character_position=(img.width // 2, img.height - 100),  # Unten Mitte
                        max_width=min(600, int(img.width * 0.8)),
                        position="above",
                        with_tail=True
                    )

                    # Speichere mit _speech Suffix
                    output_path = image_path.parent / f"{image_path.stem}_speech{image_path.suffix}"
                    img_with_bubble.save(output_path)

                    print(f"   ✅ Post {post_num}: Sprechblase hinzugefügt → {output_path.name}")

                    # Füge zur assets list hinzu
                    composed['speech_bubble_path'] = str(output_path)

                print(f"   ✅ {len(assets['composed'])} Sprechblasen erstellt")
            except Exception as e:
                print(f"   ❌ Sprechblasen-Generierung fehlgeschlagen: {e}")

        # VIDEOS - Nur für Post 3 generieren (kosteneffizient!)
        if FAL_VIDEO_AVAILABLE and self.generate_videos and os.getenv('FAL_KEY'):
            print(f"\n   ━━━ STEP 2.6: Video generieren (fal.ai) ━━━")
            print(f"   🎯 Nur Post 3 wird als Video generiert")
            print(f"   ⏳ Hinweis: Video-Generierung braucht ~30-60s")

            try:
                generator = FalVideoGenerator()
                video_dir = PROJECT_ROOT / "05_assets/videos/fal_animations"
                video_dir.mkdir(parents=True, exist_ok=True)

                videos_created = 0

                # Finde den Post mit der Kodexkarte
                kodex_post_num = None
                for i, part in enumerate(story_parts, 1):
                    part_text = part.get('text', part.get('story', "")).lower()
                    if 'kodex' in part_text or 'karte' in part_text:
                        kodex_post_num = i
                        print(f"   🎴 Kodexkarte gefunden in Post {i}")
                        break

                # Fallback: Wenn keine Kodexkarte gefunden, nutze Post 3
                if kodex_post_num is None:
                    kodex_post_num = 3
                    print(f"   ℹ️  Keine Kodexkarte erkannt, nutze Post {kodex_post_num} als Video")

                for composed in assets['composed']:
                    post_num = composed['post_number']

                    # NUR der Post mit der Kodexkarte wird als Video generiert!
                    if post_num != kodex_post_num:
                        print(f"   📷 Post {post_num}: Bleibt als Bild (kein Video)")
                        continue

                    image_path = Path(composed['path'])

                    # Hole Story-Text, Kodex-Karte und Sprechblasen-Text
                    story_text = ""
                    speech_text = None
                    for i, part in enumerate(story_parts, 1):
                        if i == post_num:
                            story_text = part.get('text', part.get('story', ""))
                            speech_text = part.get('speech', None)  # Falls Sprechblasen-Text vorhanden
                            break

                    # Kodex-Karte aus Story extrahieren (falls vorhanden)
                    kodex_karte = None
                    if 'kodex_karten' in story_output:
                        kodex_karten = story_output.get('kodex_karten', [])
                        if kodex_karten:
                            kodex_karte = kodex_karten[0] if isinstance(kodex_karten, list) else kodex_karten

                    # Output-Pfad
                    output_path = video_dir / f"story_{story_id}_post_{post_num}_video.mp4"

                    # Generiere Video mit erweitertem Prompt
                    print(f"\n   🎬 Post {post_num}: Generiere Video...")
                    if kodex_karte:
                        print(f"      🎴 Kodex-Karte: {kodex_karte}")
                    if speech_text:
                        print(f"      💬 Sprechblase: {speech_text[:40]}...")

                    from fal_video_generator import generate_video_from_composed_image

                    video_path = generate_video_from_composed_image(
                        image_path=image_path,
                        story_text=story_text,
                        motion_type="subtle",
                        output_path=output_path,
                        kodex_karte=kodex_karte,
                        speech_text=speech_text
                    )

                    print(f"   ✅ Post {post_num}: Video generiert → {output_path.name}")

                    # Füge zur assets list hinzu
                    composed['video_path'] = str(video_path)
                    videos_created += 1

                print(f"\n   ✅ {videos_created} Video erstellt (Post 3)")
            except Exception as e:
                print(f"   ❌ Video-Generierung fehlgeschlagen: {e}")
                print(f"   💡 Prüfe ob FAL_KEY gesetzt ist: export FAL_KEY='your-api-key'")
        elif FAL_VIDEO_AVAILABLE and self.generate_videos and not os.getenv('FAL_KEY'):
            print(f"\n   ⚠️  Video-Generierung aktiviert, aber FAL_KEY nicht gesetzt!")
            print(f"   💡 Setze mit: export FAL_KEY='your-fal-ai-api-key'")

        return {"success": True, "assets": assets}
    
    def optimize_posts(self, story_output):
        """Optimiert Posts für Social Media"""
        optimizer = SocialMediaOptimizer()

        print("\n🎨 Social Media Optimization")
        print("━"*80)

        # Nutze die optimize_posts (plural) Methode - gibt hashtags zurück!
        result = optimizer.optimize_posts(story_output)

        if result['success']:
            print(f"✅ {len(result['optimized_parts'])} Posts optimiert")

            # Konvertiere Format
            optimized = []
            for part in result['optimized_parts']:
                optimized.append({
                    "part": part['part'],
                    "title": part['title'],
                    "original_text": part['original_text'],
                    "optimized_text": part['optimized_text'],
                    "hashtags": part['hashtags'],
                    "success": True
                })

            return {"success": True, "optimized": True, "posts": optimized}
        else:
            print(f"❌ Optimization fehlgeschlagen")
            return {"success": False, "optimized": False, "posts": []}
    
    def publish(self, result):
        """Veröffentlicht Posts"""
        if self.dry_run:
            print("   🧪 DRY RUN - Kein echter Post")
            return {"success": True, "dry_run": True}

        # Async wrapper für alle Posts
        import asyncio
        return asyncio.run(self._publish_async(result))

    async def _publish_async(self, result):
        """Async Publish - sendet alle Posts sequentiell"""
        publisher = TelegramPoster()
        results = []

        # Poste jeden Teil
        for i, post in enumerate(result['optimized_posts']['posts'], 1):
            text = post['optimized_text']
            hashtags = " ".join(post['hashtags'])
            caption = f"{text}\n\n{hashtags}"

            # Prüfe ob Video oder Bild gepostet werden soll
            video_path = None
            image_path = None

            if result['assets'].get('assets'):
                for composed in result['assets']['assets']['composed']:
                    if composed['post_number'] == i:
                        # Priorisiere Video wenn vorhanden
                        if 'video_path' in composed and composed['video_path']:
                            video_path = composed['video_path']
                        image_path = composed['path']
                        break

            # Video posten wenn vorhanden
            if video_path and Path(video_path).exists():
                print(f"   🎬 Post {i}/4: Sende Video...")
                try:
                    message = await publisher.post_video(video_path, caption)
                    if message:
                        print(f"   ✅ Post {i}/4 Video gesendet (Message ID: {message.message_id})")
                        results.append({"post_number": i, "message_id": message.message_id, "success": True, "type": "video"})
                    else:
                        print(f"   ❌ Post {i}/4 Video fehlgeschlagen (kein Message-Objekt)")
                        results.append({"post_number": i, "success": False, "error": "No message returned"})
                except Exception as e:
                    print(f"   ❌ Post {i}/4 Video Fehler: {e}")
                    results.append({"post_number": i, "success": False, "error": str(e)})

            # Fallback: Bild posten
            elif image_path and Path(image_path).exists():
                print(f"   📷 Post {i}/4: Sende Bild...")
                try:
                    message = await publisher.post_image(image_path, caption)
                    if message:
                        print(f"   ✅ Post {i}/4 Bild gesendet (Message ID: {message.message_id})")
                        results.append({"post_number": i, "message_id": message.message_id, "success": True, "type": "image"})
                    else:
                        print(f"   ❌ Post {i}/4 Bild fehlgeschlagen (kein Message-Objekt)")
                        results.append({"post_number": i, "success": False, "error": "No message returned"})
                except Exception as e:
                    print(f"   ❌ Post {i}/4 Bild Fehler: {e}")
                    results.append({"post_number": i, "success": False, "error": str(e)})

            else:
                print(f"   ⚠️  Post {i}/4: Weder Video noch Bild gefunden, überspringe...")
                results.append({"post_number": i, "success": False, "error": "No video or image"})
                continue

            # Kleine Pause zwischen Posts
            if i < len(result['optimized_posts']['posts']):
                await asyncio.sleep(2)

        success_count = sum(1 for r in results if r.get('success'))
        return {"success": True, "posts_sent": success_count, "total": len(results), "results": results}
    
    def save_results(self, result):
        """Speichert Ergebnisse"""
        print("\n" + "━"*80)
        print("💾 STEP 6: Ergebnisse speichern")
        print("━"*80)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = PROJECT_ROOT / "05_outputs" / "storyrider_runs" / f"storyrider_{timestamp}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        result['timestamp'] = datetime.now().isoformat()
        result['settings'] = {
            'dry_run': self.dry_run,
            'skip_images': self.skip_images,
            'auto_approve': self.auto_approve
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {output_file.name}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Toshi StoryRider Pipeline")
    parser.add_argument('--dry-run', action='store_true', help='Test ohne Telegram')
    parser.add_argument('--skip-images', action='store_true', help='Bilder überspringen')
    parser.add_argument('--auto-approve', action='store_true', help='Automatisch approve')
    parser.add_argument('--auto-regenerate', action='store_true', help='Bilder automatisch regenerieren bis konsistent')
    parser.add_argument('--speech-bubbles', action='store_true', default=False, help='Sprechblasen hinzufügen')
    parser.add_argument('--generate-videos', action='store_true', default=True, help='Videos mit fal.ai generieren (Standard: AN, benötigt FAL_KEY)')
    parser.add_argument('--no-videos', action='store_false', dest='generate_videos', help='Keine Videos generieren')

    args = parser.parse_args()

    pipeline = StoryRiderPipeline(
        dry_run=args.dry_run,
        skip_images=args.skip_images,
        auto_approve=args.auto_approve,
        auto_regenerate=args.auto_regenerate,
        add_speech_bubbles=args.speech_bubbles,
        generate_videos=args.generate_videos
    )
    
    result = pipeline.run()
    
    # Summary
    print("\n" + "="*80)
    print("✅ STORYRIDER PIPELINE COMPLETE")
    print("="*80)
    print(f"📊 Story: {result['story_output']['title']}")
    print(f"🎨 Assets: {'Generiert' if result['assets']['success'] else 'Übersprungen'}")
    print(f"✨ Optimiert: {result['optimized_posts']['optimized']}")
    print(f"✅ Approved: {result['approval']['approved']}")
    print(f"📤 Posts: {'Gesendet' if result['publish']['success'] else 'Nicht gesendet'}")
    print("="*80)

if __name__ == "__main__":
    main()
