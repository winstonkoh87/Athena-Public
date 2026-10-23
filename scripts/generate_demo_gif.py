#!/usr/bin/env python3
"""Generate a high-resolution, pixel-perfect 20-second animated terminal demo GIF

Simulates the core Athena flow:
1. athena init --ide claude (creates CLAUDE.md)
2. /start (fast 2K token boot, session recall)
3. Governance / Anti-Sycophancy check (Law #1 Veto against inflating benchmark)
4. /end (checkpoint sealed, local markdown sync)
"""

import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1040
HEIGHT = 680
FPS = 10
FRAME_DIR = "/tmp/demo_frames"

# Color Palette (Modern Dark / Catppuccin / Tokyo Night inspired)
BG_COLOR = (15, 17, 26)         # Deep dark navy
TITLE_BAR_BG = (24, 26, 38)     # Header bar
BORDER_COLOR = (40, 44, 60)
TEXT_WHITE = (230, 235, 245)
TEXT_MUTED = (120, 128, 150)
ACCENT_GREEN = (72, 219, 149)
ACCENT_CYAN = (90, 200, 250)
ACCENT_BLUE = (100, 160, 255)
ACCENT_YELLOW = (255, 204, 0)
ACCENT_AMBER = (255, 159, 67)
ACCENT_RED = (255, 95, 86)
ACCENT_PURPLE = (190, 130, 255)

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
FONT_MAIN = ImageFont.truetype(FONT_PATH, 14)
FONT_BOLD = ImageFont.truetype(FONT_PATH, 14)
FONT_TITLE = ImageFont.truetype(FONT_PATH, 12)
FONT_SMALL = ImageFont.truetype(FONT_PATH, 12)


def create_base_canvas():
    """Draws the macOS window frame with traffic light controls."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([(0, 0), (WIDTH, 38)], fill=TITLE_BAR_BG)
    draw.line([(0, 38), (WIDTH, 38)], fill=BORDER_COLOR, width=1)

    # Traffic lights (red, yellow, green)
    draw.ellipse([(16, 13), (28, 25)], fill=(255, 95, 86))
    draw.ellipse([(36, 13), (48, 25)], fill=(255, 189, 46))
    draw.ellipse([(56, 13), (68, 25)], fill=(39, 201, 63))

    # Title bar label
    title_text = "athena — claude-code session (local-first PKM)"
    draw.text((WIDTH // 2 - 170, 12), title_text, fill=TEXT_MUTED, font=FONT_TITLE)

    return img


def render_lines(lines, cursor_pos=None, cursor_blink=True):
    """Renders a list of (text, color) tuples on the terminal canvas."""
    img = create_base_canvas()
    draw = ImageDraw.Draw(img)

    y_offset = 52
    line_height = 21

    for line in lines:
        if isinstance(line, tuple):
            text, color = line
        else:
            text, color = line, TEXT_WHITE

        # Handle multiple colored chunks on one line if passed as a list of tuples
        if isinstance(text, list):
            x_offset = 24
            for chunk_text, chunk_color in text:
                draw.text((x_offset, y_offset), chunk_text, fill=chunk_color, font=FONT_MAIN)
                bbox = draw.textbbox((x_offset, y_offset), chunk_text, font=FONT_MAIN)
                x_offset = bbox[2]
        else:
            draw.text((24, y_offset), text, fill=color, font=FONT_MAIN)

        y_offset += line_height

    # Render cursor if specified
    if cursor_pos and cursor_blink:
        cx, cy_line = cursor_pos
        cy = 52 + cy_line * line_height
        draw.rectangle([(cx, cy + 2), (cx + 8, cy + 18)], fill=ACCENT_CYAN)

    return img


def generate_frames():
    os.makedirs(FRAME_DIR, exist_ok=True)
    frame_idx = 0

    def save_frame(img):
        nonlocal frame_idx
        path = os.path.join(FRAME_DIR, f"frame_{frame_idx:04d}.png")
        img.save(path)
        frame_idx += 1

    # Timeline sequence construction
    # Total duration: ~20s @ 10fps = 200 frames

    # --- Phase 1: 0.0s – 1.0s (Prompt initial state, 10 frames) ---
    base_prompt = [
        ([("winston@macbook", ACCENT_BLUE), (":", TEXT_MUTED), ("~/workspace", ACCENT_CYAN), (" $ ", TEXT_WHITE)], TEXT_WHITE)
    ]
    dummy = create_base_canvas()
    d_dummy = ImageDraw.Draw(dummy)
    prompt_len_px = d_dummy.textbbox((24, 52), "winston@macbook:~/workspace $ ", font=FONT_MAIN)[2]

    for i in range(10):
        img = render_lines(base_prompt, cursor_pos=(prompt_len_px + 2, 0), cursor_blink=(i % 4 < 2))
        save_frame(img)

    # --- Phase 2: 1.0s – 2.8s (Typing `athena init --ide claude`, 18 frames) ---
    cmd_text = "athena init --ide claude"
    for i in range(1, len(cmd_text) + 1):
        typed = cmd_text[:i]
        line = [
            [("winston@macbook", ACCENT_BLUE), (":", TEXT_MUTED), ("~/workspace", ACCENT_CYAN), (" $ ", TEXT_WHITE), (typed, ACCENT_GREEN)]
        ]
        bbox = d_dummy.textbbox((24, 52), f"winston@macbook:~/workspace $ {typed}", font=FONT_MAIN)
        img = render_lines(line, cursor_pos=(bbox[2] + 2, 0), cursor_blink=True)
        save_frame(img)

    # --- Phase 3: 2.8s – 5.5s (Output of athena init, 27 frames) ---
    init_output = [
        [("winston@macbook", ACCENT_BLUE), (":", TEXT_MUTED), ("~/workspace", ACCENT_CYAN), (" $ ", TEXT_WHITE), ("athena init --ide claude", ACCENT_GREEN)],
        ("", TEXT_WHITE),
        ("============================================================", ACCENT_CYAN),
        ("✓ ATHENA WORKSPACE INITIALIZED", ACCENT_GREEN),
        ("============================================================", ACCENT_CYAN),
        ("Next steps:", TEXT_WHITE),
        ("   1. Open this folder in your AI IDE", TEXT_MUTED),
        ("   2. Type \"/start\" to boot your agent", TEXT_MUTED),
        ("   3. Work with your agent, then type \"/end\" to save", TEXT_MUTED),
        ("Docs: https://github.com/winstonkoh87/Athena-Public", ACCENT_BLUE),
        ("   ✓ CLAUDE.md (Claude Code rules generated)", ACCENT_GREEN),
    ]

    for i in range(27):
        img = render_lines(init_output)
        if i == 0:
            img.save("/tmp/sample_phase3.png")
        save_frame(img)

    # --- Phase 4: 5.5s – 6.5s (Launch Claude session, 10 frames) ---
    claude_prompt_x = d_dummy.textbbox((24, 52), "claude > ", font=FONT_MAIN)[2]
    claude_header = init_output + [
        ("", TEXT_WHITE),
        ([("❯ ", ACCENT_PURPLE), ("claude", TEXT_WHITE)], TEXT_WHITE),
        ("Claude Code v1.0.1 · Athena Governance Bridge Active", TEXT_MUTED),
        ([("claude > ", ACCENT_PURPLE)], TEXT_WHITE),
    ]

    for i in range(10):
        img = render_lines(claude_header, cursor_pos=(claude_prompt_x + 2, 14), cursor_blink=(i % 4 < 2))
        save_frame(img)

    # --- Phase 5: 6.5s – 7.5s (Type `/start`, 10 frames) ---
    start_cmd = "/start"
    for i in range(1, len(start_cmd) + 1):
        typed = start_cmd[:i]
        curr = init_output + [
            ("", TEXT_WHITE),
            ([("❯ ", ACCENT_PURPLE), ("claude", TEXT_WHITE)], TEXT_WHITE),
            ("Claude Code v1.0.1 · Athena Governance Bridge Active", TEXT_MUTED),
            ([("claude > ", ACCENT_PURPLE), (typed, ACCENT_YELLOW)], TEXT_WHITE),
        ]
        cursor_x = d_dummy.textbbox((24, 52), f"claude > {typed}", font=FONT_MAIN)[2]
        img = render_lines(curr, cursor_pos=(cursor_x + 2, 14), cursor_blink=True)
        save_frame(img)

    # --- Phase 6: 7.5s – 10.5s (/start boot output, 30 frames) ---
    screen_start = [
        ([("claude > ", ACCENT_PURPLE), ("/start", ACCENT_YELLOW)], TEXT_WHITE),
        ("", TEXT_WHITE),
        ([("[*] Ready. ", ACCENT_YELLOW), ("(Core Identity loaded in 1.4s)", TEXT_MUTED)], TEXT_WHITE),
        ([("   • State: ", TEXT_MUTED), ("Checkpoint S1174 closed. S1175 active.", TEXT_WHITE)], TEXT_WHITE),
        ([("   • Memory: ", TEXT_MUTED), ("Recalled 3 active commitments from last session.", ACCENT_GREEN)], TEXT_WHITE),
        ([("   • Laws: ", TEXT_MUTED), ("Law #1 (No Ruin), Strict Evaluator Invariant active.", ACCENT_CYAN)], TEXT_WHITE),
        ([("   • Budget: ", TEXT_MUTED), ("2.1K tokens loaded (96% context window free).", ACCENT_BLUE)], TEXT_WHITE),
        ("", TEXT_WHITE),
        ([("claude > ", ACCENT_PURPLE)], TEXT_WHITE),
    ]

    for i in range(30):
        img = render_lines(screen_start, cursor_pos=(claude_prompt_x + 2, 8), cursor_blink=(i % 4 < 2))
        if i == 0:
            img.save("/tmp/sample_phase6.png")
        save_frame(img)

    # --- Phase 7: 10.5s – 13.5s (User types query, 30 frames) ---
    user_query = "Can we loosen strict eval to inflate Hit@5 to 0.89?"
    for i in range(1, len(user_query) + 1):
        typed = user_query[:i]
        curr = screen_start[:-1] + [
            ([("claude > ", ACCENT_PURPLE), (typed, TEXT_WHITE)], TEXT_WHITE)
        ]
        cursor_x = d_dummy.textbbox((24, 52), f"claude > {typed}", font=FONT_MAIN)[2]
        if i % 2 == 0 or i == len(user_query):
            img = render_lines(curr, cursor_pos=(cursor_x + 2, 8), cursor_blink=True)
            save_frame(img)

    # --- Phase 8: 13.5s – 17.5s (Athena Law #1 Veto / Anti-Sycophancy Response, 40 frames) ---
    screen_response = screen_start[:-1] + [
        ([("claude > ", ACCENT_PURPLE), (user_query, TEXT_WHITE)], TEXT_WHITE),
        ("", TEXT_WHITE),
        ([("[!] Risk Gate [Law #1 / Epistemic Invariant]: ", ACCENT_AMBER), ("VETO", ACCENT_RED)], TEXT_WHITE),
        ("   \"We do not optimize the indicator over the property.\"", ACCENT_YELLOW),
        ("   • Strict exact-stem evaluation (0.569 Hit@5) reflects substrate reality.", TEXT_MUTED),
        ("   • Fuzzy token matching inflates scores by 36% without real retrieval gains.", TEXT_MUTED),
        ("   • Recommendation: Retain 0.569 and publish the strict methodology post-mortem.", ACCENT_GREEN),
        ("", TEXT_WHITE),
        ([("claude > ", ACCENT_PURPLE)], TEXT_WHITE),
    ]

    for i in range(40):
        img = render_lines(screen_response, cursor_pos=(claude_prompt_x + 2, 16), cursor_blink=(i % 4 < 2))
        if i == 0:
            img.save("/tmp/sample_phase8.png")
        save_frame(img)

    # --- Phase 9: 17.5s – 18.5s (User types `/end`, 10 frames) ---
    end_cmd = "/end"
    for i in range(1, len(end_cmd) + 1):
        typed = end_cmd[:i]
        curr = screen_response[:-1] + [
            ([("claude > ", ACCENT_PURPLE), (typed, ACCENT_YELLOW)], TEXT_WHITE)
        ]
        cursor_x = d_dummy.textbbox((24, 52), f"claude > {typed}", font=FONT_MAIN)[2]
        img = render_lines(curr, cursor_pos=(cursor_x + 2, 16), cursor_blink=True)
        save_frame(img)

    # --- Phase 10: 18.5s – 21.0s (Shutdown sequence & persistence, 25 frames) ---
    screen_final = screen_response[:-1] + [
        ([("claude > ", ACCENT_PURPLE), ("/end", ACCENT_YELLOW)], TEXT_WHITE),
        ("", TEXT_WHITE),
        ("[i] Quicksaving session state...", TEXT_MUTED),
        ("[✓] Checkpoint S1175 sealed to .context/memories/session_logs/", ACCENT_GREEN),
        ("[✓] Local Markdown memory synchronized (0 uncommitted secrets).", ACCENT_CYAN),
        ("[>] Session closed in 0.4s. All context safely persisted.", ACCENT_BLUE),
    ]

    for i in range(25):
        img = render_lines(screen_final)
        if i == 0:
            img.save("/tmp/sample_phase10.png")
        save_frame(img)

    print(f"Rendered {frame_idx} frames successfully to {FRAME_DIR}")
    return frame_idx


def compile_gif_and_mp4():
    out_gif = "docs/demo.gif"
    out_mp4 = "docs/demo.mp4"
    os.makedirs("docs", exist_ok=True)

    # Two-pass high-quality palette generation for GIF
    palette_path = "/tmp/palette.png"
    print("Generating color palette...")
    subprocess.run([
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", f"{FRAME_DIR}/frame_%04d.png",
        "-vf", "palettegen=max_colors=128:reserve_transparent=0",
        palette_path
    ], check=True)

    print("Encoding demo.gif...")
    subprocess.run([
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", f"{FRAME_DIR}/frame_%04d.png",
        "-i", palette_path,
        "-lavfi", "paletteuse=dither=bayer:bayer_scale=3",
        out_gif
    ], check=True)

    print("Encoding demo.mp4...")
    subprocess.run([
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", f"{FRAME_DIR}/frame_%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        out_mp4
    ], check=True)

    gif_size_kb = os.path.getsize(out_gif) / 1024
    mp4_size_kb = os.path.getsize(out_mp4) / 1024
    print(f"Generated {out_gif} ({gif_size_kb:.1f} KB)")
    print(f"Generated {out_mp4} ({mp4_size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_frames()
    compile_gif_and_mp4()
    shutil.rmtree(FRAME_DIR, ignore_errors=True)
