/# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Toshi - Quest for Truth** is an automated Bitcoin education content generation system that creates Instagram-optimized learning stories in a retro 16-bit SNES RPG style. The system generates stories with consistent pixel art characters, composes multi-character scenes, and publishes to social media (primarily Telegram).

### Key Technologies
- **Story Generation**: OpenAI GPT-4o-mini
- **Image Generation**: Google Imagen 3 (characters, NPCs, scenes, Kodex cards)
- **Video Generation**: fal.ai (optional, for post 4 only)
- **Image Processing**: PIL/Pillow (local composition, ground detection)
- **Database**: SQLite (local), PostgreSQL (production on Proxmox)
- **Publishing**: python-telegram-bot

## Running the Pipeline

### Quick Start Commands

**Standard Pipeline (Fixed Scenes 1-4):**
```bash
./start_full.sh --scene N                    # LIVE: Generate all assets + auto-approve + post to Telegram
./start_full.sh --scene N --dry-run          # Test without posting (assets are generated)
./start_full.sh --scene N --skip-images      # Fast test without image generation
./start_full.sh --scene N --manual-review    # Require manual approval before posting
```

**V1/StoryRider Pipeline (Dynamic/Unlimited Bitcoin Concepts):**
```bash
./start_full.sh --v1                         # LIVE: New story with dynamic concept generation
./start_full.sh --storyrider                 # Alias for --v1
./start_full.sh --v1 --dry-run              # Test without posting
./start_full.sh --v1 --skip-images          # Fast test without images
./start_full.sh --v1 --skip-videos          # Skip video generation
./start_full.sh --v1 --auto-regenerate      # Auto-regenerate until consistency score ≥0.7
./start_full.sh --v1 --publish              # Enable Telegram posting
```

**Direct Python Execution:**
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run StoryRider pipeline directly
python3 START_PIPELINE_STORYRIDER.py --auto-approve --dry-run
```

### Environment Setup

1. Copy `.env.template` to `.env` and configure:
   - `TELEGRAM_BOT_TOKEN` - From @BotFather
   - `TELEGRAM_CHANNEL_ID` - Target channel (-1002919626367 for production)
   - `OPENAI_API_KEY` - For story generation
   - `GOOGLE_API_KEY` - For Imagen 3 image generation
   - `HF_API_TOKEN` - For Hugging Face models (optional)

2. Install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Initialize database (if needed):
```bash
sqlite3 04_database/local_cache.sqlite < 04_database/db_schema.sql
```

## Architecture & Pipeline Flow

### Pipeline Execution Flow (V1/StoryRider Mode)

```
start_full.sh → START_PIPELINE.py → START_PIPELINE_STORYRIDER.py
    ↓
1. Story Request Generation (Dynamic)
   - Query DB for used concepts
   - Generate NEW Bitcoin concept (GPT-4o-mini)
   - Generate NEW mentor character (GPT-4o-mini)
   - Save to story_requests table
    ↓
2. Story Generation (00_system_core/scripts/generate_daily_story.py)
   - NPC/Object-Lock system (consistent pixel art)
   - Word limits: Part 1: 45-55, Part 2: 50-60, Part 3: 65-75, Part 4: 40-50
   - Hook at start, mini-cliffhanger at end
   - Fact-checklist validation (mechanism, numbers, consequences)
   - Quality Guard prevents bad outputs
   - Output: 4-post structure (Introduction, Problem, Mentor, Resolution)
    ↓
3. Asset Generation (if not --skip-images)
   a. Character Generation (character_generator.py)
      - Toshi (main character) - reuses existing if found
      - Mentor character - generates with description from GPT
      - Optional: Auto-regeneration until consistency ≥0.7
   b. NPC Extraction & Generation (character_extractor.py + npc_generator.py)
      - AI extracts NPCs from story text
      - Generates transparent PNG sprites
      - Auto background removal
   c. Scene Background (scene_background_generator.py)
      - NPCs painted INTO background (not separate sprites)
      - Detailed pixel art scenes
   d. Image Composition (scene_composer.py + image_compositor.py)
      - Ground Detection (ground_detector.py) - CV-based positioning
      - Multi-character support (up to 4 characters)
      - Facing Direction system (characters look at each other)
      - Output: 1024x1024 PNG per post
   e. Kodex Card (kodex_card_generator.py)
      - Only for Post 4 (Resolution)
      - SNES 16-bit pixel art style
   f. Video Generation (fal_video_generator.py) - Optional
      - Only for Post 4 (with Kodex card)
      - 7.5 seconds, 30fps
    ↓
4. Social Media Optimization (social_media_optimizer.py)
   - Add hashtags: #Bitcoin, #BitcoinEducation, #Toshi, #QuestForTruth
   - Format captions
    ↓
5. Quality Review
   - Auto-approve (default) or manual review (--manual-review)
    ↓
6. Publishing (telegram_poster.py)
   - Posts to Telegram channel (if not --dry-run)
   - Video for Post 4, images for Posts 1-3
   - Returns message IDs
    ↓
7. Results Saved
   - JSON output: 05_outputs/storyrider_runs/storyrider_TIMESTAMP.json
   - DB updates: story_requests.status = 'completed'
```

### Key Pipeline Scripts

**Entry Points:**
- `START_PIPELINE.py` - Unified router (detects --v1 flag and routes)
- `START_PIPELINE_STORYRIDER.py` - Main V1/StoryRider pipeline orchestrator
- `START_PIPELINE_FULL.py` - Fixed scenes (1-4) pipeline

**Core Systems (00_system_core/):**
- `character_generator.py` - Imagen 3 character generation
- `character_extractor.py` - AI-based NPC detection from story text
- `npc_generator.py` - NPC sprite generation with auto background removal
- `scene_background_generator.py` - Scene background with integrated NPCs
- `scene_composer.py` - Final scene composition orchestrator
- `image_compositor.py` - Low-level PIL composition
- `ground_detector.py` - Computer vision ground position detection
- `positioning_strategies.py` - Multi-character positioning logic
- `kodex_card_generator.py` - Concept card generation
- `fal_video_generator.py` - Video animation generation

**Story Generation (00_system_core/scripts/):**
- `generate_daily_story.py` - V4.0 story generator with guardrails
  - Instagram optimization (word limits, hooks, fact-checklist)
  - NPC/Object-Lock system for consistency
  - Quality Guard validation
  - Template fallback system
- `telegram_poster.py` - Telegram Bot API posting
- `social_media_optimizer.py` - Caption & hashtag optimization
- `image_consistency_analyzer.py` - Character consistency scoring
- `image_regeneration_loop.py` - Auto-regenerate until consistent

## Database Schema

**Local Development:** `04_database/local_cache.sqlite`
**Production:** PostgreSQL on Proxmox (192.168.178.37)

### Key Tables

**Pipeline Tables:**
- `story_requests` - Input data for story generation
  - Stores: concept, mentor, mentor_gender, mentor_appearance, setting, challenge, learning_goal
  - Status tracking: pending → completed
  - Flag: story_generated (0/1)

- `story_outputs` - Generated stories
  - Links to: story_requests.id (request_id)
  - Contains: title, story JSON, post_plan JSON

- `social_media_posts` - Individual posts (4 per story)
  - Links to: story_outputs.id (story_output_id)
  - Contains: post_number (1-4), caption, image_path, telegram_message_id

**Content Tables:**
- `kapitel` - Story chapters (thematic grouping)
- `szenen` - Scenes (1-4, fixed pipeline only)
- `charaktere` - Mentor characters
- `konzepte` - Bitcoin concepts

**Query Examples:**
```sql
-- Check pipeline status
SELECT sr.id, sr.concept, sr.mentor, sr.status, sr.story_generated
FROM story_requests sr
ORDER BY sr.created_at DESC LIMIT 10;

-- View recent posts
SELECT smp.post_number, smp.caption, smp.telegram_message_id
FROM social_media_posts smp
JOIN story_outputs so ON smp.story_output_id = so.id
ORDER BY smp.created_at DESC LIMIT 20;

-- Track used concepts (avoid repetition)
SELECT DISTINCT concept FROM story_requests WHERE story_generated = 1;
```

## Project Structure

```
Bitcoin-Toshi/
├── 00_system_core/          # Core modules
│   ├── scripts/             # Story generation & utilities
│   ├── character_*.py       # Character-related modules
│   ├── scene_*.py          # Scene composition modules
│   └── *_detector.py       # Vision systems (ground detection)
├── 02_models/              # Model configs (if needed)
├── 04_database/            # SQLite database + schema
│   ├── local_cache.sqlite  # Active DB
│   ├── db_schema.sql       # Schema definition
│   └── migrations/         # DB migrations
├── 05_assets/              # Generated & reference assets
│   ├── images/
│   │   ├── 00_reference/   # Master character references
│   │   │   ├── characters/ # Toshi, mentors (reusable)
│   │   │   └── scenes/     # Background scenes
│   │   ├── 01_npcs/        # Generated NPC sprites
│   │   ├── 02_kodex_cards/ # Concept cards
│   │   └── 03_generated/   # Final composed images
│   │       └── composed/   # story_N_post_M.png
│   └── videos/
│       └── fal_animations/ # Generated videos (Post 4 only)
├── 05_outputs/             # Pipeline run outputs
│   └── storyrider_runs/    # JSON results per run
├── 07_logs/                # Execution logs
├── .claude/skills/         # Claude Code skills
│   ├── bitcoin-story-generator/
│   ├── toshi-pipeline/
│   ├── toshi-assets/
│   └── social-publisher/
├── START_PIPELINE.py       # Unified entry point
├── START_PIPELINE_STORYRIDER.py  # V1/StoryRider pipeline
├── START_PIPELINE_FULL.py  # Fixed scenes pipeline
├── start_full.sh           # Main shell wrapper
└── requirements.txt        # Python dependencies
```

## Development Guidelines

### Story Generation Guardrails (v4.0)

When working on story generation, respect these strict requirements:

**Word Limits (STRICT):**
- Part 1 (Introduction): 45-55 words
- Part 2 (Problem): 50-60 words
- Part 3 (Mentor/Lesson): 65-75 words (contains fact-checklist!)
- Part 4 (Resolution): 40-50 words

**Instagram Optimization:**
- First sentence = HOOK (engage immediately)
- Last sentence = Mini-cliffhanger (next post tease)
- 70% Bitcoin facts, 30% storytelling

**Fact-Checklist (Part 3 REQUIRED):**
1. MECHANISM - How does it work technically?
2. NUMBERS/RULES - Specific values (21M cap, 10 min blocks, etc.)
3. CONSEQUENCES - What happens? Why does it matter?

**NPC/Object-Lock:**
- Selected NPCs & objects from predefined pools (forest, city, temple, etc.)
- NO inventing new NPCs/objects beyond the pool
- Ensures consistent pixel art generation

### Image Asset Reuse

The system is optimized for cost reduction through asset reuse:

- **Characters**: Generated once, reused across stories (60-99% savings)
- **File naming**: `{character}_{pose}_{facing}_{version}_{timestamp}.png`
- **Facing directions**: forward, left, right
- **Transparency**: All character sprites have transparent backgrounds
- **Ground detection**: Auto-positions characters on detected ground level

**When adding new character generation:**
1. Check `05_assets/images/00_reference/characters/{name}/` first
2. Only generate if not found or consistency score < 0.7
3. Save with proper naming convention
4. Update character references in DB if needed

### Multi-Character System

**Character Extraction (character_extractor.py):**
- Uses GPT-4o-mini to analyze story text
- Extracts: name, description, gender, facing_direction
- Filters out Toshi + Mentor (main characters only)
- NPCs are separate sprites or painted into background

**Ground Detection (ground_detector.py):**
- Computer vision analysis of scene background
- Detects horizon line and ground level
- Returns Y-position for character placement
- Ensures characters "stand" on ground, not float

**Positioning Strategies (positioning_strategies.py):**
- 2 characters: Balanced left/right
- 3+ characters: Visual hierarchy (size, depth)
- Facing directions: Characters look at each other in dialog
- Overlap handling: Z-ordering based on Y-position

## Common Development Tasks

### Add New Bitcoin Concept (V1 Mode)
No manual editing needed! The system auto-generates concepts via GPT-4o-mini. But if you want to influence:
- Edit prompts in `generate_daily_story.py` line ~100-150
- Concept generation prompt controls topic selection

### Debug Story Generation Issues
```bash
# Run with dry-run to see output without posting
./start_full.sh --v1 --dry-run

# Check logs
tail -f 07_logs/story_generation/*.log

# Inspect database
sqlite3 04_database/local_cache.sqlite
> SELECT * FROM story_requests ORDER BY created_at DESC LIMIT 1;
```

### Test Image Generation Only
```bash
# Generate story + images but don't post
./start_full.sh --v1 --dry-run

# Skip images entirely (fast test)
./start_full.sh --v1 --skip-images
```

### Check Telegram Bot Status
```bash
python3 00_system_core/scripts/get_bot_info.py
python3 00_system_core/scripts/find_channel_id.py
```

### View Generated Assets
```bash
# Latest composed images
ls -lt 05_assets/images/03_generated/composed/ | head -5

# Latest videos (if generated)
ls -lt 05_assets/videos/fal_animations/ | head -3

# Open latest story images
open 05_assets/images/03_generated/composed/story_*_post_*.png
```

### Database Queries
```bash
sqlite3 04_database/local_cache.sqlite

# View story pipeline status
SELECT sr.id, sr.concept, sr.mentor, sr.status, so.title
FROM story_requests sr
LEFT JOIN story_outputs so ON sr.id = so.request_id
ORDER BY sr.created_at DESC LIMIT 10;

# Check published posts
SELECT COUNT(*) FROM social_media_posts WHERE telegram_message_id IS NOT NULL;
```

## Cost Estimates

**Per Story Run (V1 Mode with all features):**
- Story generation (GPT-4o-mini): $0.002
- Concept generation (GPT-4o-mini): $0.002
- Mentor generation (GPT-4o-mini): $0.002
- Toshi character (Imagen 3): $0.10 (or $0 if reused)
- Mentor character (Imagen 3): $0.10
- NPCs (2-3, Imagen 3): $0.20-$0.30
- Scene background (Imagen 3): $0.10
- Kodex card (Imagen 3): $0.10
- Video (fal.ai, optional): $0.02
- **Total: ~$0.64** per story (without video: $0.62)
- **With asset reuse: ~$0.50** (Toshi reused, some NPCs reused)

**Cost Optimization Strategies:**
- Enable `--auto-regenerate` only when quality issues occur
- Reuse Toshi character across all stories (saves $0.10/story)
- Skip videos with `--skip-videos` (saves $0.02/story)
- Use fixed scenes mode for testing (skips concept/mentor generation)

## Important Files to Review

**For Story Logic:**
- `00_system_core/scripts/generate_daily_story.py` - Core story generator v4.0
- `START_PIPELINE_STORYRIDER.py` - Pipeline orchestration

**For Image Generation:**
- `00_system_core/character_generator.py` - Imagen 3 character creation
- `00_system_core/scene_background_generator.py` - Scene backgrounds
- `00_system_core/image_compositor.py` - Final composition logic

**For Publishing:**
- `00_system_core/scripts/telegram_poster.py` - Telegram API integration
- `00_system_core/scripts/social_media_optimizer.py` - Caption formatting

**For Understanding Flow:**
- `PIPELINE_EXECUTION_FLOW_V1.md` - Detailed step-by-step execution
- `.claude/skills/toshi-pipeline/SKILL.md` - Pipeline skill documentation
- `.claude/skills/bitcoin-story-generator/SKILL.md` - Story generation skill

## Troubleshooting

**"No module named X" errors:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**"API key not found" errors:**
- Check `.env` file exists (copy from `.env.template`)
- Verify API keys are correctly set
- Run: `cat .env | grep API_KEY` to verify

**Image generation fails:**
- Check Google API key: `echo $GOOGLE_API_KEY`
- Verify Imagen 3 API is enabled in Google Cloud Console
- Check quota/billing in Google Cloud

**Telegram posting fails:**
- Verify bot token: `python3 00_system_core/scripts/get_bot_info.py`
- Check channel ID is correct (should be negative number for private channels)
- Ensure bot is admin in the channel

**Database locked errors:**
- Close any open `sqlite3` sessions
- Check for zombie Python processes: `ps aux | grep python3`

**Character consistency issues:**
- Use `--auto-regenerate` flag to retry until consistency ≥0.7
- Check reference images in `05_assets/images/00_reference/characters/`
- Review `image_regeneration_loop.py` logs

## Bitcoin Content Guidelines

**Allowed Topics:**
- Bitcoin fundamentals (blockchain, proof-of-work, mining)
- Network concepts (nodes, consensus, difficulty adjustment)
- Security (private keys, multisig, time locks)
- Economics (halving, supply cap, incentives)
- Technical features (SegWit, Taproot, Lightning Network)

**Forbidden Topics:**
- Altcoins or "crypto" in general
- Trading strategies or financial advice
- Price predictions or speculation
- Get-rich-quick narratives
- Non-Bitcoin blockchain projects

**Tone & Style:**
- Educational, warm, adventurous
- Retro-RPG aesthetic (16-bit SNES style)
- Age-appropriate (family-friendly)
- Respectful, no hype or FUD
- Focus on learning, not profit

## Testing Workflow

**Before committing changes:**
```bash
# 1. Test story generation only (fast)
./start_full.sh --v1 --skip-images --dry-run

# 2. Test full pipeline without posting
./start_full.sh --v1 --dry-run

# 3. Review generated assets
open 05_assets/images/03_generated/composed/story_*_post_*.png

# 4. Check database state
sqlite3 04_database/local_cache.sqlite "SELECT * FROM story_requests ORDER BY created_at DESC LIMIT 1;"

# 5. Only then run live (if approved)
./start_full.sh --v1 --manual-review
```
