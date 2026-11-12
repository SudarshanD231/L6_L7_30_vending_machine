# L6_L7_30 — Vending Machine

## Lab 7: Fuzzing for Input Validation Bugs

### About
Property-based fuzz testing and defensive software hardening for the coin-operated vending machine application (`processor.py`), developed using the **Hypothesis** fuzzing framework and `pytest` for Lab 7 (Fuzzing for Input Validation Bugs).

---

### Deliverables Summary

| Deliverable | File / Artifact | Description | Result |
|-------------|-----------------|-------------|--------|
| **1. PDF Document with Screenshots** | [`Lab7_Fuzzing_Report.pdf`](Lab7_Fuzzing_Report.pdf) | Formal report containing all 4 execution screenshots, vulnerability analysis, and methodology | Complete & Generated |
| **2. Fixed Application Python Script** | [`processor.py`](processor.py) (and [`vending_machine.py`](vending_machine.py)) | Hardened application with strict defensive input validation, type guarding, and DoS loop prevention | 100% Passing Fuzz Tests |
| **3. Updated Test Code (Hypothesis)** | [`test_processor.py`](test_processor.py) | Comprehensive property-based fuzz testing suite covering all 3 functions with Hypothesis | 6 test suites, hundreds of generated cases |
| **Terminal Screenshots (PNG)** | [`step2_buggy_processor_output.png`](step2_buggy_processor_output.png)<br>[`step4_test_processor_failing.png`](step4_test_processor_failing.png)<br>[`step5_fixed_processor_output.png`](step5_fixed_processor_output.png)<br>[`step6_test_processor_passing.png`](step6_test_processor_passing.png) | High-definition terminal captures corresponding to each step of the lab manual | Complete & Verified |

### Understanding Fuzzing with Hypothesis

- **Traditional Unit Testing:** Asserts behavior on known, hand-crafted inputs (e.g. testing `select_item("cola", stock, 200)`). It only tests what the engineer anticipates.
- **Property-Based Fuzz Testing (Hypothesis):** Formulates broad invariants (e.g., *"the function must never crash with an uncaught exception on any input type"* or *"sum(change) must equal credit - price"*), and generates hundreds of randomized, adversarial inputs (None, malformed strings, arbitrary types, boundary integers) to break those properties.
- When an invariant fails, Hypothesis automatically performs **shrink analysis** to discover the smallest, simplest reproducible test case causing the failure.

---

### The Three Core Functions & Fuzzed Bugs Uncovered

#### 1. `select_item(item, stock, credit)`
- **Bug 1 (AttributeError):** When `stock=None` or a non-dict type, calling `stock.get(item, 0)` raised `AttributeError: 'NoneType' object has no attribute 'get'`.
- **Bug 2 (TypeError):** When `item` is an unhashable type (e.g., `list`, `dict`), checking `item not in PRICES` raised `TypeError: unhashable type: 'list'`.
- **Bug 3 (TypeError / Logic Bug):** Non-integer or negative credit triggered unhandled comparison exceptions or allowed negative credit.
- **Fix / Hardening:** Guarded item lookup with `try/except TypeError`, strictly validated `isinstance(stock, dict)` and positive integer stock count, and validated non-negative numeric credit.

#### 2. `make_change(amount)`
- **Bug 1 (Unhandled ValueError):** When `amount < 0`, the starter code raised `raise ValueError("negative amount")`, crashing the host application.
- **Bug 2 (TypeError):** When `amount` was `None` or a non-numeric type, checking `amount < 0` raised `TypeError`.
- **Bug 3 (Algorithmic DoS Vulnerability):** Using linear repeated subtraction `while amount >= coin: amount -= coin` caused infinite loops on `float('inf')` and severe CPU stalls on large integers.
- **Fix / Hardening:** Validated non-negative integer amount, returned `None` gracefully on invalid inputs, replaced the while loop with $O(1)$ arithmetic division (`count = remaining // coin`, `remaining %= coin`), and enforced upper bounds.

#### 3. `purchase(item, stock, credit)`
- **Bug 1 (Cascading Crash):** Inherited all crash points from `select_item` and `make_change`.
- **Bug 2 (State Atomicity Failure):** If stock mutation occurred before or during incomplete transactions, stock was corrupted.
- **Fix / Hardening:** Guaranteed transactional atomicity: stock is only decremented if validation, stock availability, and exact change calculation all succeed.

---

### Terminal Screenshots & Step-by-Step Verification

#### Step 2: Running Buggy Application (`python processor.py`)
![Step 2 Buggy Output](step2_buggy_processor_output.png)

#### Step 4: Running Fuzz Tests Against Buggy Application (`pytest test_processor.py`)
Hypothesis automatically falsifies properties and discovers minimal failing inputs:
![Step 4 Fuzz Tests Failing](step4_test_processor_failing.png)

#### Step 5: Running Fixed/Hardened Application (`python processor.py`)
Demonstrating graceful handling of fuzz edge cases:
![Step 5 Fixed Output](step5_fixed_processor_output.png)

#### Step 6: Re-Running Fuzz Tests on Hardened Application (`pytest test_processor.py -v`)
All 6 property-based test suites pass across hundreds of fuzzed examples:
![Step 6 Fuzz Tests Passing](step6_test_processor_passing.png)

---

### How to Run

Navigate to the `lab7` directory:

```bash
cd lab7
```

#### 1. Install Dependencies:
```bash
pip install hypothesis pytest reportlab pillow
```

#### 2. Run the Hardened Application:
```bash
python processor.py
```

#### 3. Run Property-Based Fuzz Tests:
```bash
pytest test_processor.py -v
```

#### 4. Re-generate Screenshots:
```bash
python render_lab7_screenshots.py
```

#### 5. Re-generate PDF Report:
```bash
python generate_pdf_report.py
```
