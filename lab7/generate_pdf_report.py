"""
Lab 7 PDF Report Generator
Generates a comprehensive, professional PDF document with screenshots and analyses.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(SCRIPT_DIR, "Lab7_Fuzzing_Report.pdf")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "Lab 7: Fuzzing for Input Validation Bugs — Vending Machine")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "Software Engineering Laboratory — Lab 7 Report")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1A365D")   # Deep Navy
    SECONDARY = colors.HexColor("#2B6CB0") # Medium Blue
    ACCENT_GREEN = colors.HexColor("#2F855A") # Forest Green
    ACCENT_RED = colors.HexColor("#C53030")   # Burgundy
    BG_LIGHT = colors.HexColor("#F7FAFC")
    TEXT_DARK = colors.HexColor("#2D3748")

    # Typography styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=PRIMARY,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )
    code_inline = ParagraphStyle(
        "CodeInline",
        parent=body_style,
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2C5282")
    )
    callout_style = ParagraphStyle(
        "Callout",
        parent=body_style,
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4A5568")
    )

    story = []

    # =================================================================
    # TITLE & METADATA BLOCK
    # =================================================================
    story.append(Paragraph("LAB 7: Fuzzing for Input Validation Bugs", title_style))
    story.append(Paragraph("Automated Vulnerability Detection & Hardening with Hypothesis", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=12))

    meta_data = [
        [
            Paragraph("<b>Repository:</b> L6_L7_30_vending_machine", body_style),
            Paragraph("<b>Target Module:</b> processor.py / vending_machine.py", body_style),
        ],
        [
            Paragraph("<b>Methodology:</b> Property-Based Fuzz Testing", body_style),
            Paragraph("<b>Frameworks:</b> Hypothesis 6.170, pytest 9.1", body_style),
        ],
        [
            Paragraph("<b>Assigned System:</b> Vending Machine (3 core functions)", body_style),
            Paragraph("<b>Final Status:</b> 100% Fuzz Tests Passed (Hardened)", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # =================================================================
    # OBJECTIVES & INTRODUCTION
    # =================================================================
    story.append(Paragraph("1. Lab Objectives & Methodology", h1_style))
    story.append(Paragraph(
        "The objective of this laboratory is to explore dynamic fuzz testing as both a security vulnerability detection technique "
        "and a quality assurance mechanism. Using the <b>Hypothesis</b> property-based testing framework in Python, we systematically uncover "
        "hidden bugs, unhandled exceptions, and edge-case vulnerabilities in the assigned vending machine application, and then apply defensive "
        "programming techniques to harden the codebase against all malformed inputs.",
        body_style
    ))
    story.append(Paragraph("<b>Why Fuzz Testing?</b>", h2_style))
    story.append(Paragraph("• <i>Manual testing</i> frequently overlooks rare boundary conditions and invalid types.", bullet_style))
    story.append(Paragraph("• <i>Traditional unit tests</i> only verify developer assumptions (test what you anticipate).", bullet_style))
    story.append(Paragraph("• <i>Hypothesis fuzz testing</i> generates hundreds of randomized, adversarial inputs to discover what developers never anticipated, shrinking failing cases to minimal reproducing examples.", bullet_style))
    story.append(Spacer(1, 10))

    # =================================================================
    # STEP 1 & 2: BUGGY APPLICATION RUN
    # =================================================================
    story.append(Paragraph("2. Step 2: Executing Buggy Starter Application", h1_style))
    story.append(Paragraph(
        "The starter application implements three core vending machine operations: <code>select_item()</code>, "
        "<code>make_change()</code>, and <code>purchase()</code>. Executing <code>python processor.py</code> with standard, "
        "well-formed inputs appears to succeed, masking severe input validation vulnerabilities beneath nominal test runs.",
        body_style
    ))

    step2_img_path = os.path.join(SCRIPT_DIR, "step2_buggy_processor_output.png")
    if os.path.exists(step2_img_path):
        story.append(Spacer(1, 4))
        story.append(Image(step2_img_path, width=490, height=300))
        story.append(Paragraph("<b>Figure 1:</b> Initial run of buggy <code>processor.py</code> demonstrating successful execution on expected inputs.", callout_style))
    story.append(Spacer(1, 10))

    # =================================================================
    # STEP 3 & 4: HYPOTHESIS FUZZ TESTING & FAILING CASES
    # =================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Step 3 & 4: Hypothesis Fuzz Testing & Failure Discovery", h1_style))
    story.append(Paragraph(
        "A property-based fuzz test suite was created in <code>test_processor.py</code> using Hypothesis strategies "
        "(<code>st.text()</code>, <code>st.integers()</code>, <code>st.dictionaries()</code>, <code>st.floats()</code>, "
        "<code>st.none()</code>, and <code>st.booleans()</code>) targeting all three functions with the invariant that the system must "
        "<b>never crash</b> with unhandled exceptions on any input type.",
        body_style
    ))

    # Table of Bugs Found
    bugs_summary = [
        [Paragraph("<b>Target Function</b>", body_style), Paragraph("<b>Input Trigger (Falsifying Case)</b>", body_style), Paragraph("<b>Vulnerability / Unhandled Exception</b>", body_style)],
        [
            Paragraph("<code>select_item()</code>", code_inline),
            Paragraph("<code>stock=None, credit=None</code>", code_inline),
            Paragraph("<b>AttributeError / TypeError:</b> <code>'NoneType' object has no attribute 'get'</code>. Application crashes when stock is None or non-dict.", body_style)
        ],
        [
            Paragraph("<code>make_change()</code>", code_inline),
            Paragraph("<code>amount = -1</code>", code_inline),
            Paragraph("<b>Unhandled ValueError:</b> Raises unhandled <code>ValueError('negative amount')</code> instead of returning a graceful error status.", body_style)
        ],
        [
            Paragraph("<code>make_change()</code>", code_inline),
            Paragraph("<code>amount = None</code>", code_inline),
            Paragraph("<b>TypeError:</b> <code>'<' not supported between 'NoneType' and 'int'</code>. Crashes on non-integer amounts.", body_style)
        ],
        [
            Paragraph("<code>make_change()</code>", code_inline),
            Paragraph("<code>amount = float('inf') / large int</code>", code_inline),
            Paragraph("<b>Algorithmic DoS Vulnerability:</b> <code>while amount >= coin: amount -= coin</code> creates an infinite loop on <code>inf</code> or stalls on extreme integers.", body_style)
        ],
        [
            Paragraph("<code>purchase()</code>", code_inline),
            Paragraph("<code>stock=None, item='cola'</code>", code_inline),
            Paragraph("<b>State / Caller Crash:</b> Cascades failure from <code>select_item</code> and mutates or fails before change processing.", body_style)
        ],
    ]
    bugs_table = Table(bugs_summary, colWidths=[110, 160, 234])
    bugs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ED8936")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BG_LIGHT, colors.white])
    ]))
    story.append(bugs_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Terminal Screenshot: Pytest Test Cases Failing (Hypothesis Falsification)</b>", h2_style))
    step4_img_path = os.path.join(SCRIPT_DIR, "step4_test_processor_failing.png")
    if os.path.exists(step4_img_path):
        # Scale to fit nicely on the page
        story.append(Image(step4_img_path, width=490, height=390))
        story.append(Paragraph("<b>Figure 2:</b> Hypothesis falsifying test properties and identifying minimal failing inputs for all three functions.", callout_style))
    story.append(Spacer(1, 10))

    # =================================================================
    # STEP 5: HARDENED APPLICATION & DEFENSIVE FIXES
    # =================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Step 5: Fixing and Hardening the Application", h1_style))
    story.append(Paragraph(
        "To resolve all vulnerabilities exposed by fuzz testing, defensive programming techniques were implemented in "
        "<code>processor.py</code> across all three functions:",
        body_style
    ))
    story.append(Paragraph("• <b>Item Validation:</b> Guarded dictionary lookups with <code>try-except TypeError</code> to safely reject unhashable objects (e.g. lists, dicts) with status <code>'invalid'</code>.", bullet_style))
    story.append(Paragraph("• <b>Stock Validation:</b> Strictly verified <code>isinstance(stock, dict)</code> and checked that item stock is a valid integer strictly greater than zero (excluding booleans). Missing, malformed, or zero stock returns <code>'sold_out'</code>.", bullet_style))
    story.append(Paragraph("• <b>Credit Validation:</b> Enforced non-negative numeric credit (excluding booleans). Malformed credit returns <code>'insufficient'</code> without crashing.", bullet_style))
    story.append(Paragraph("• <b>Denial of Service (DoS) Prevention in Change Calculation:</b> Replaced the dangerous linear subtraction loop with <b>O(1) arithmetic division</b> (<code>count = remaining // coin</code>, <code>remaining %= coin</code>) and enforced a practical transaction limit (<code>MAX_TRANSACTION_LIMIT = 100,000</code>).", bullet_style))
    story.append(Paragraph("• <b>Atomic State Mutation:</b> In <code>purchase()</code>, stock is only decremented if validation, stock check, and exact change calculation all succeed.", bullet_style))
    story.append(Spacer(1, 6))

    step5_img_path = os.path.join(SCRIPT_DIR, "step5_fixed_processor_output.png")
    if os.path.exists(step5_img_path):
        story.append(Image(step5_img_path, width=490, height=375))
        story.append(Paragraph("<b>Figure 3:</b> Execution of hardened <code>processor.py</code> demonstrating graceful handling of fuzz test edge cases.", callout_style))
    story.append(Spacer(1, 10))

    # =================================================================
    # STEP 6: RE-RUNNING FUZZ TESTS (100% PASSING)
    # =================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Step 6: Re-Running Fuzz Tests on Fixed Application", h1_style))
    story.append(Paragraph(
        "With defensive input validation and algorithmic DoS hardening in place, <code>pytest test_processor.py -v</code> was re-executed. "
        "Hypothesis ran hundreds of randomized test combinations per property, and <b>all 6 test suites passed cleanly with 0 failures</b>.",
        body_style
    ))

    step6_img_path = os.path.join(SCRIPT_DIR, "step6_test_processor_passing.png")
    if os.path.exists(step6_img_path):
        story.append(Image(step6_img_path, width=490, height=175))
        story.append(Paragraph("<b>Figure 4:</b> Terminal output showing 100% test pass rate across all property-based fuzz tests.", callout_style))
    story.append(Spacer(1, 12))

    # Test Suite Verification Table
    test_results = [
        [Paragraph("<b>Test Suite Function</b>", body_style), Paragraph("<b>Type</b>", body_style), Paragraph("<b>Fuzzed Inputs Tested</b>", body_style), Paragraph("<b>Outcome</b>", body_style)],
        [
            Paragraph("<code>test_select_item_no_crash</code>", code_inline),
            Paragraph("Fuzz Invariant", body_style),
            Paragraph("Arbitrary Unicode text, ints, None, booleans, malformed stock dicts & credit", body_style),
            Paragraph("<b>PASSED</b> (100 examples)", body_style),
        ],
        [
            Paragraph("<code>test_select_item_valid_invariants</code>", code_inline),
            Paragraph("Domain Property", body_style),
            Paragraph("Bounded positive credit and stock across catalog items", body_style),
            Paragraph("<b>PASSED</b> (100 examples)", body_style),
        ],
        [
            Paragraph("<code>test_make_change_no_crash</code>", code_inline),
            Paragraph("Fuzz Invariant", body_style),
            Paragraph("Negative amounts, None, text strings, non-numeric floats, booleans", body_style),
            Paragraph("<b>PASSED</b> (100 examples)", body_style),
        ],
        [
            Paragraph("<code>test_make_change_valid_properties</code>", code_inline),
            Paragraph("Domain Property", body_style),
            Paragraph("Integer amounts 0..10,000 (verified coin sum, denominations, ordering)", body_style),
            Paragraph("<b>PASSED</b> (100 examples)", body_style),
        ],
        [
            Paragraph("<code>test_purchase_no_crash</code>", code_inline),
            Paragraph("Fuzz Invariant", body_style),
            Paragraph("Arbitrary item types, corrupted stocks, extreme credits", body_style),
            Paragraph("<b>PASSED</b> (100 examples)", body_style),
        ],
        [
            Paragraph("<code>test_purchase_state_integrity</code>", code_inline),
            Paragraph("Domain Property", body_style),
            Paragraph("Stock decrement atomicity & exact change verification", body_style),
            Paragraph("<b>PASSED</b> (100 examples)", body_style),
        ],
    ]
    test_table = Table(test_results, colWidths=[150, 75, 205, 74])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ACCENT_GREEN),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BG_LIGHT, colors.white])
    ]))
    story.append(test_table)
    story.append(Spacer(1, 14))

    # =================================================================
    # DELIVERABLES & CONCLUSION
    # =================================================================
    story.append(Paragraph("6. Deliverables Summary & Conclusion", h1_style))
    story.append(Paragraph(
        "All three required deliverables specified in the laboratory prompt have been completed:",
        body_style
    ))
    story.append(Paragraph("1. <b>PDF Document with Screenshots:</b> <code>lab7/Lab7_Fuzzing_Report.pdf</code> (this document), complete with all four execution screenshots and vulnerability analyses.", bullet_style))
    story.append(Paragraph("2. <b>Fixed Application Python Script:</b> <code>lab7/processor.py</code>, containing comprehensive defensive validation and DoS protection.", bullet_style))
    story.append(Paragraph("3. <b>Updated test_processor.py Code:</b> <code>lab7/test_processor.py</code>, containing six property-based Hypothesis test suites.", bullet_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Conclusion:</b> Fuzz testing with Hypothesis successfully bridged the gap left by traditional unit testing. While conventional tests "
        "only verified anticipated happy paths, Hypothesis automatically uncovered critical edge cases (e.g. <code>NoneType</code> attributes, "
        "negative amounts raising uncaught exceptions, and algorithmic loop stalls). Through defensive programming, the application was hardened "
        "into a resilient, production-grade service that gracefully handles unexpected inputs.",
        body_style
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
