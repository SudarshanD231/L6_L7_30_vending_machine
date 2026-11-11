# L6_L7_30 — Vending Machine

Software Engineering Laboratory coursework covering Code & Branch Coverage Analysis (Lab 6) and Property-Based Fuzz Testing & Input Validation Hardening (Lab 7).

---

## Repository Structure

```
L6_L7_30_vending_machine/
├── lab6/                               # Lab 6: Code and Branch Coverage Analysis
│   ├── vending_machine.py              # Vending machine implementation
│   ├── test_vending_machine.py         # Initial test suite
│   ├── CodeCoverageTest_vending_machine.py     # Statement coverage suite (>90%)
│   ├── BranchCoverageTest_vending_machine.py   # Branch coverage suite (100%)
│   ├── code_coverage_analysis.png      # Terminal execution screenshot
│   ├── branch_coverage_analysis.png    # Terminal execution screenshot
│   └── README.md                       # Lab 6 documentation & report
│
└── lab7/                               # Lab 7: Fuzzing for Input Validation Bugs
    ├── processor.py                    # Hardened vending machine application
    ├── test_processor.py               # Property-based fuzz test suite (Hypothesis)
    ├── processor_buggy.py              # Original buggy starter code (for reference)
    ├── processor_hardened.py           # Hardened implementation reference
    ├── vending_machine.py              # Backward compatibility module
    ├── render_lab7_screenshots.py      # Automated terminal screenshot generator
    ├── generate_pdf_report.py          # ReportLab formal PDF generator
    ├── Lab7_Fuzzing_Report.pdf         # Deliverable 1: Formal PDF report with screenshots
    ├── step2_buggy_processor_output.png        # Step 2 terminal screenshot
    ├── step4_test_processor_failing.png        # Step 4 terminal screenshot (fuzz failures)
    ├── step5_fixed_processor_output.png        # Step 5 terminal screenshot
    ├── step6_test_processor_passing.png        # Step 6 terminal screenshot (all pass)
    └── README.md                       # Lab 7 comprehensive documentation
```

---

## Lab Modules Overview

### [Lab 6: Code and Branch Coverage Analysis](lab6/README.md)
- **Objective:** Evaluate and maximize code statement and branch coverage on the vending machine module.
- **Results:** Achieved **93% line coverage** on initial targeted testing and **100% branch coverage** (18/18 branches, 100% line coverage) on final test suites.

### [Lab 7: Fuzzing for Input Validation Bugs](lab7/README.md)
- **Objective:** Apply dynamic property-based fuzz testing using **Hypothesis** to detect edge cases, unhandled crashes, and DoS loop vulnerabilities, followed by defensive programming to harden the application.
- **Results:**
  - Uncovered 5 distinct vulnerability classes (uncaught `ValueError`, `NoneType` `AttributeError`, unhashable type `TypeError`, algorithmic loop DoS, and mutation integrity flaws).
  - Hardened `processor.py` with defensive type assertions, safe lookups, $O(1)$ arithmetic change calculation, and bounded transactions.
  - Achieved **100% test pass rate** on all 6 Hypothesis fuzz test suites with hundreds of adversarial examples generated per property.
  - Generated formal PDF report: [`lab7/Lab7_Fuzzing_Report.pdf`](lab7/Lab7_Fuzzing_Report.pdf).
