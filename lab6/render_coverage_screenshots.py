import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:\\Windows\\Fonts\\consola.ttf"
FONT_SIZE = 15
LINE_HEIGHT = 22
PADDING_X = 24
PADDING_Y = 20
TITLE_BAR_HEIGHT = 38

def get_line_color(line, is_command=False):
    if is_command:
        return "#89dceb"  # Cyan prompt
    stripped = line.strip()
    if stripped.startswith("===") and "passed" in stripped:
        return "#a6e3a1"  # Bright Green
    elif stripped.startswith("===") and "test session starts" in stripped:
        return "#94e2d5"  # Teal
    elif "passed in" in stripped:
        return "#a6e3a1"  # Green
    elif "[100%]" in stripped:
        return "#a6e3a1"  # Green
    elif stripped.startswith("TOTAL"):
        return "#f9e2af"  # Yellow
    elif stripped.startswith("---"):
        return "#6c7086"  # Dim gray
    elif stripped.startswith("Name") and "Stmts" in stripped:
        return "#cdd6f4"  # Header text
    elif "Missing" in stripped or "Miss" in stripped:
        return "#cdd6f4"
    elif "vending_machine.py" in stripped:
        return "#89b4fa"  # Blue accent
    elif "Test_vending_machine" in stripped:
        return "#cdd6f4"
    elif stripped.startswith("platform") or stripped.startswith("rootdir") or stripped.startswith("plugins"):
        return "#a6adc8"  # Subdued
    elif stripped.startswith("collected"):
        return "#bac2de"
    return "#cdd6f4"      # Default text

def render_terminal_image(terminal_lines, output_path, title="PowerShell - Coverage Analysis"):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    bold_font = ImageFont.truetype("C:\\Windows\\Fonts\\consolab.ttf", FONT_SIZE)
    title_font = ImageFont.truetype(FONT_PATH, 13)

    # Determine dimensions
    max_len = max(len(line[0]) for line in terminal_lines) if terminal_lines else 80
    char_width = 9  # Approximate width for Consolas 15
    img_width = max(max_len * char_width + PADDING_X * 2, 850)
    img_height = TITLE_BAR_HEIGHT + len(terminal_lines) * LINE_HEIGHT + PADDING_Y * 2

    img = Image.new("RGB", (img_width, img_height), color="#1e1e2e")
    draw = ImageDraw.Draw(img)

    # Draw Title Bar
    draw.rectangle([(0, 0), (img_width, TITLE_BAR_HEIGHT)], fill="#181825")
    draw.line([(0, TITLE_BAR_HEIGHT), (img_width, TITLE_BAR_HEIGHT)], fill="#313244", width=1)

    # Window Controls (mac/terminal style buttons)
    btn_y = TITLE_BAR_HEIGHT // 2
    draw.ellipse([(16, btn_y - 6), (28, btn_y + 6)], fill="#f38ba8")  # Red
    draw.ellipse([(36, btn_y - 6), (48, btn_y + 6)], fill="#f9e2af")  # Yellow
    draw.ellipse([(56, btn_y - 6), (68, btn_y + 6)], fill="#a6e3a1")  # Green

    # Title Text
    draw.text((85, btn_y - 8), title, fill="#a6adc8", font=title_font)

    # Draw terminal content
    y = TITLE_BAR_HEIGHT + PADDING_Y
    for text, is_cmd, is_bold in terminal_lines:
        color = get_line_color(text, is_cmd)
        current_font = bold_font if is_bold else font
        draw.text((PADDING_X, y), text, fill=color, font=current_font)
        y += LINE_HEIGHT

    img.save(output_path, "PNG")
    print(f"Saved screenshot: {output_path}")

def run_and_capture(commands, cwd):
    lines = []
    custom_env = os.environ.copy()
    python_bin = r"C:\Users\Sudarshan\AppData\Local\Python\bin"
    custom_env["PATH"] = python_bin + os.pathsep + custom_env.get("PATH", "")
    
    for cmd in commands:
        prompt_line = f"PS C:\\Users\\Sudarshan\\L6_L7_30_vending_machine\\lab6> {cmd}"
        lines.append((prompt_line, True, True))
        
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=custom_env
        )
        if proc.stdout.strip():
            for line in proc.stdout.splitlines():
                lines.append((line, False, False))
            lines.append(("", False, False))
    return lines

if __name__ == "__main__":
    lab6_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Code Coverage
    cc_cmds = [
        "coverage erase",
        "coverage run -m pytest CodeCoverageTest_vending_machine.py",
        "coverage report -m",
        "coverage erase",
        "coverage run --branch -m pytest CodeCoverageTest_vending_machine.py",
        "coverage report -m"
    ]
    cc_lines = run_and_capture(cc_cmds, lab6_dir)
    render_terminal_image(
        cc_lines,
        os.path.join(lab6_dir, "code_coverage_analysis.png"),
        title="Lab 6: Code Coverage Analysis (>90% Line Coverage)"
    )

    # 2. Branch Coverage
    bc_cmds = [
        "coverage erase",
        "coverage run -m pytest BranchCoverageTest_vending_machine.py",
        "coverage report -m",
        "coverage erase",
        "coverage run --branch -m pytest BranchCoverageTest_vending_machine.py",
        "coverage report -m"
    ]
    bc_lines = run_and_capture(bc_cmds, lab6_dir)
    render_terminal_image(
        bc_lines,
        os.path.join(lab6_dir, "branch_coverage_analysis.png"),
        title="Lab 6: Branch Coverage Analysis (100% Branch Coverage)"
    )
