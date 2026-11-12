---
description: Generate an upload-ready YouTube Short/Reel from a single topic prompt
created: 2026-02-25
last_updated: 2026-07-22
model: default
temperature: 0.7
tools:
  read: true
  write: true
  bash: true
  search: true
  generate_image: true
---

# /video — AI Video Factory

> **Input**: A topic string (e.g. "What happens if you daytrade without a stop loss")
> **Output**: `video.mp4` + `thumbnail.png` + `description.md`

## Phase 1: Script Generation

1. **Search Exocortex** for relevant context on the topic:

   ```bash
   python3 Athena-Public/examples/scripts/smart_search.py "<topic>" --limit 5 
   ```

2. **Write the script** using this structure:
   - **Hook** (0-3s): Curiosity question — "What happens to your portfolio if..."
   - **Escalation** (3-45s): Time-based or severity-based progression (After 1 trade → 1 week → 1 month → 1 year). Use real data from `.context/` when available.
   - **Payoff** (45-55s): The insight/framework/lesson. Reference a Protocol or Case Study if applicable.
   - **CTA** (55-60s): Subscribe + link to Athena-Public or website.
3. **Save** the script to `media-factory/scripts/<slug>.md`.

## Phase 2: Visual Generation

1. For each scene in the script, **generate an image** using the `generate_image` tool:
   - Style: Dark background, clean typography, vibrant accent colors, data visualizations
   - Resolution: Vertical (1080x1920 for Shorts/Reels)
   - Save to `media-factory/frames/<slug>/scene_XX.png`
2. **Generate thumbnail** — bold text overlay, high contrast, curiosity-inducing. Save as `media-factory/frames/<slug>/thumbnail.png`.

## Phase 3: Voiceover

1. Generate voiceover audio from the script:

   ```bash
   # Option A: Free (Google TTS)
   python3 -c "
   from gtts import gTTS
   tts = gTTS(open('media-factory/scripts/<slug>.md').read(), lang='en', slow=False)
   tts.save('media-factory/audio/<slug>.mp3')
   "
   ```

   ```bash
   # Option B: Premium (ElevenLabs — requires API key in .env)
   python3 -c "
   from elevenlabs import generate, save
   audio = generate(text=open('media-factory/scripts/<slug>.md').read(), voice='Adam', model='eleven_monolingual_v1')
   save(audio, 'media-factory/audio/<slug>.mp3')
   "
   ```

## Phase 4: Assembly

1. **Get audio duration** and calculate scene timing:

   ```bash
   ffprobe -v error -show_entries format=duration -of csv=p=0 media-factory/audio/<slug>.mp3
   ```

8. **Stitch frames + audio** into video:

   ```bash
   # Create input file list with duration per frame
   # Then assemble with ffmpeg
   ffmpeg -f concat -safe 0 -i media-factory/frames/<slug>/input.txt \
     -i media-factory/audio/<slug>.mp3 \
     -c:v libx264 -pix_fmt yuv420p -r 30 \
     -c:a aac -b:a 192k \
     -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
     -shortest \
     media-factory/output/<slug>.mp4
   ```

9. **Generate captions** (optional, if Whisper is available):

   ```bash
   whisper media-factory/audio/<slug>.mp3 --model base --output_format srt --output_dir media-factory/output/
   ```

10. **Burn captions into video** (optional):

    ```bash
    ffmpeg -i media-factory/output/<slug>.mp4 \
      -vf "subtitles=media-factory/output/<slug>.srt:force_style='FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=60'" \
      media-factory/output/<slug>_captioned.mp4
    ```

## Phase 5: SEO Package

1. **Generate description.md** with:
    - Title (3 options: curiosity, authority, controversy)
    - Description (SEO-optimized, 2-3 paragraphs + links)
    - Tags (15-20 relevant hashtags)
    - Suggested upload time (based on audience timezone)
2. Save to `media-factory/output/<slug>_seo.md`.

## Output Checklist

| Deliverable | Path |
|---|---|
| Script | `media-factory/scripts/<slug>.md` |
| Frames | `media-factory/frames/<slug>/scene_*.png` |
| Thumbnail | `media-factory/frames/<slug>/thumbnail.png` |
| Audio | `media-factory/audio/<slug>.mp3` |
| Video | `media-factory/output/<slug>.mp4` |
| Captioned Video | `media-factory/output/<slug>_captioned.mp4` |
| SEO Package | `media-factory/output/<slug>_seo.md` |

---

## Tagging

# workflow #video #content #media-factory #distribution
