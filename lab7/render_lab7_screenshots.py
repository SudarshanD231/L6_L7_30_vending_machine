"""
Screenshot Renderer for Lab 7 (Fuzz Testing for Input Validation Bugs)
Generates high-resolution terminal screenshots matching the course style.
"""

import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = "C:\\Windows\\Fonts\\consola.ttf"
BOLD_FONT_PATH = "C:\\Windows\\Fonts\\consolab.ttf"
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING_X = 22
PADDING_Y = 18
TITLE_BAR_HEIGHT = 36


def get_line_color(line, is_command=False):
    if is_command:
        return "#89dceb"  # Cyan prompt
    stripped = line.strip()
    if "PASSED" in stripped or (stripped.startswith("===") and "passed" in stripped):
        return "#a6e3a1"  # Bright Green
    elif "FAILED" in stripped or (stripped.startswith("===") and "failed" in stripped) or "FAILURES" in stripped:
        return "#f38ba8"  # Coral Red
    elif "ERROR" in stripped or "Traceback" in stripped or stripped.startswith("E "):
        return "#f38ba8"  # Red error
    elif stripped.startswith("===") and "test session starts" in stripped:
        return "#94e2d5"  # Teal
    elif stripped.startswith("==="):
        return "#f9e2af"  # Yellow divider
    elif stripped.startswith("---") or stripped.startswith("___"):
        return "#6c7086"  # Dim separator
    elif stripped.startswith("[Transaction") or stripped.startswith(" ->"):
        return "#b4befe"  # Light lavender
    elif stripped.startswith("platform") or stripped.startswith("rootdir") or stripped.startswith("plugins"):
        return "#a6adc8"  # Subdued
    elif stripped.startswith("collected") or stripped.startswith("cachedir"):
        return "#bac2de"
    return "#cdd6f4"      # Default text


def render_terminal_image(terminal_lines, output_path, title="PowerShell - Lab 7"):
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        bold_font = ImageFont.truetype(BOLD_FONT_PATH, FONT_SIZE)
        title_font = ImageFont.truetype(FONT_PATH, 12)
    except Exception:
        font = ImageFont.load_default()
        bold_font = font
        title_font = font

    max_len = max(len(line[0]) for line in terminal_lines) if terminal_lines else 80
    char_width = 8.5
    img_width = max(int(max_len * char_width + PADDING_X * 2), 900)
    img_height = TITLE_BAR_HEIGHT + len(terminal_lines) * LINE_HEIGHT + PADDING_Y * 2

    img = Image.new("RGB", (img_width, img_height), color="#1e1e2e")
    draw = ImageDraw.Draw(img)

    # Title Bar
    draw.rectangle([(0, 0), (img_width, TITLE_BAR_HEIGHT)], fill="#181825")
    draw.line([(0, TITLE_BAR_HEIGHT), (img_width, TITLE_BAR_HEIGHT)], fill="#313244", width=1)

    # Window Controls (mac/terminal style buttons)
    btn_y = TITLE_BAR_HEIGHT // 2
    draw.ellipse([(14, btn_y - 6), (26, btn_y + 6)], fill="#f38ba8")
    draw.ellipse([(34, btn_y - 6), (46, btn_y + 6)], fill="#f9e2af")
    draw.ellipse([(54, btn_y - 6), (66, btn_y + 6)], fill="#a6e3a1")

    # Title Text
    draw.text((80, btn_y - 7), title, fill="#a6adc8", font=title_font)

    # Content
    y = TITLE_BAR_HEIGHT + PADDING_Y
    for text, is_cmd, is_bold in terminal_lines:
        color = get_line_color(text, is_cmd)
        curr_font = bold_font if is_bold else font
        draw.text((PADDING_X, y), text, fill=color, font=curr_font)
        y += LINE_HEIGHT

    img.save(output_path, "PNG")
    print(f"Rendered: {output_path} ({img_width}x{img_height})")


def run_command_capture(cmd, prompt):
    lines = [(prompt, True, True)]
    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if proc.stdout:
        for l in proc.stdout.splitlines():
            lines.append((l, False, False))
    return lines


def main():
    print("Generating Lab 7 Screenshots...")
    lab_prompt = "PS C:\\Users\\Sudarshan\\L6_L7_30_vending_machine\\lab7> "

    # -------------------------------------------------------------
    # Screenshot 1: Step 2 - Run Buggy Application (python processor.py)
    # -------------------------------------------------------------
    print("[1/4] Running Buggy processor.py...")
    # Temporarily copy buggy to processor.py
    shutil.copyfile(os.path.join(SCRIPT_DIR, "processor_buggy.py"), os.path.join(SCRIPT_DIR, "processor.py"))
    step2_lines = run_command_capture("python processor.py", lab_prompt + "python processor.py")
    render_terminal_image(
        step2_lines,
        os.path.join(SCRIPT_DIR, "step2_buggy_processor_output.png"),
        title="PowerShell - Step 2: Run Buggy Application (python processor.py)"
    )

    # -------------------------------------------------------------
    # Screenshot 2: Step 4 - Run Fuzz Tests on Buggy (pytest test_processor.py)
    # -------------------------------------------------------------
    print("[2/4] Running pytest against buggy processor.py (expecting failures)...")
    step4_lines = run_command_capture("python -m pytest test_processor.py", lab_prompt + "pytest test_processor.py")
    render_terminal_image(
        step4_lines,
        os.path.join(SCRIPT_DIR, "step4_test_processor_failing.png"),
        title="PowerShell - Step 4: Fuzz Testing Failing Cases (pytest test_processor.py)"
    )

    # -------------------------------------------------------------
    # Screenshot 3: Step 5 - Run Fixed/Hardened processor.py
    # -------------------------------------------------------------
    print("[3/4] Running Fixed/Hardened processor.py...")
    # Restore hardened code
    shutil.copyfile(os.path.join(SCRIPT_DIR, "processor_hardened.py"), os.path.join(SCRIPT_DIR, "processor.py"))
    step5_lines = run_command_capture("python processor.py", lab_prompt + "python processor.py")
    render_terminal_image(
        step5_lines,
        os.path.join(SCRIPT_DIR, "step5_fixed_processor_output.png"),
        title="PowerShell - Step 5: Run Hardened Application (python processor.py)"
    )

    # -------------------------------------------------------------
    # Screenshot 4: Step 6 - Re-run Fuzz Tests on Fixed (pytest test_processor.py)
    # -------------------------------------------------------------
    print("[4/4] Running pytest against hardened processor.py (expecting all pass)...")
    step6_lines = run_command_capture("python -m pytest test_processor.py -v", lab_prompt + "pytest test_processor.py -v")
    render_terminal_image(
        step6_lines,
        os.path.join(SCRIPT_DIR, "step6_test_processor_passing.png"),
        title="PowerShell - Step 6: Fuzz Testing All Passing (pytest test_processor.py -v)"
    )

    print("\nAll 4 screenshots generated successfully!")


if __name__ == "__main__":
    main()
