"""
Legal Compass — Full Automated Boundary & Edge-Case Test Suite
Runs comprehensive test cases across all legal provisions, boundaries, and input variations.
"""
import sys
import json
import nlp_engine

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding="utf-8")

def run_tests():
    print("=" * 65)
    print("  LEGAL COMPASS — COMPREHENSIVE BOUNDARY & EDGE-CASE TEST SUITE")
    print("=" * 65)

    engine = nlp_engine.LegalNLPEngine()

    test_categories = {
        "1. Constitutional Boundaries (Articles 1 to 395)": [
            ("article 1", "Lower bound Art 1", lambda r: "Article 1" in r["answer"]),
            ("article 395", "Upper bound Art 395", lambda r: "Article 395" in r["answer"]),
            ("article 0", "Out of bound below (Art 0)", lambda r: "does not exist" in r["answer"]),
            ("article 396", "Out of bound above (Art 396)", lambda r: "does not exist" in r["answer"]),
            ("article 9999", "Extreme out of bound (Art 9999)", lambda r: "does not exist" in r["answer"]),
            ("article 21A", "Alpha suffix Art 21A", lambda r: "21A" in r["answer"] or "Education" in r["answer"]),
            ("article 39A", "Alpha suffix Art 39A", lambda r: "39A" in r["answer"] or "Free legal aid" in r["answer"]),
            ("article 51A", "Alpha suffix Art 51A", lambda r: "51A" in r["answer"] or "Fundamental Duties" in r["answer"]),
            ("article 300A", "Alpha suffix Art 300A", lambda r: "300A" in r["answer"] or "Property" in r["answer"]),
            ("article 370", "Abrogated Art 370", lambda r: "370" in r["answer"] or "Jammu" in r["answer"]),
        ],
        "2. IPC Section Boundaries (Sections 1 to 511)": [
            ("IPC 1", "Lower bound IPC 1", lambda r: "IPC Section 1" in r["answer"]),
            ("IPC 511", "Upper bound IPC 511", lambda r: "IPC Section 511" in r["answer"]),
            ("IPC 512", "Out of bound IPC 512", lambda r: "512" in r["answer"]),
            ("section 300", "IPC 300 Murder Definition", lambda r: "300" in r["answer"]),
            ("section 302", "IPC 302 Murder Punishment", lambda r: "302" in r["answer"]),
            ("section 498A", "Alpha suffix IPC 498A", lambda r: "498A" in r["answer"]),
            ("section 120B", "Alpha suffix IPC 120B", lambda r: "120" in r["answer"] or "conspiracy" in r["answer"].lower()),
            ("section 295A", "Alpha suffix IPC 295A", lambda r: "295" in r["answer"] or "religious" in r["answer"].lower()),
        ],
        "3. CrPC Section Boundaries (Sections 1 to 484)": [
            ("CrPC 1", "Lower bound CrPC 1", lambda r: "CrPC Section 1" in r["answer"]),
            ("CrPC 484", "Upper bound CrPC 484", lambda r: "CrPC Section 484" in r["answer"]),
            ("CrPC 41", "CrPC 41 Arrest", lambda r: "41" in r["answer"] and "arrest" in r["answer"].lower()),
            ("CrPC 125", "CrPC 125 Maintenance", lambda r: "125" in r["answer"] and "maintenance" in r["answer"].lower()),
            ("CrPC 144", "CrPC 144 Prohibitory Orders", lambda r: "144" in r["answer"]),
            ("CrPC 154", "CrPC 154 FIR", lambda r: "154" in r["answer"] or "FIR" in r["answer"]),
            ("CrPC 438", "CrPC 438 Anticipatory Bail", lambda r: "438" in r["answer"] or "bail" in r["answer"].lower()),
            ("CrPC 482", "CrPC 482 Inherent Powers", lambda r: "482" in r["answer"] or "inherent" in r["answer"].lower()),
        ],
        "4. Formatting, Casing & Short Forms": [
            ("ARTICLE 21", "Uppercase query", lambda r: "Article 21" in r["answer"]),
            ("  article   21  ", "Extra spaces", lambda r: "Article 21" in r["answer"]),
            ("art 21", "Short form 'art'", lambda r: "Article 21" in r["answer"]),
            ("sec 302", "Short form 'sec'", lambda r: "302" in r["answer"]),
            ("ipc 302", "Short form 'ipc'", lambda r: "302" in r["answer"]),
            ("crpc 438", "Short form 'crpc'", lambda r: "438" in r["answer"]),
            ("what is art. 21???", "Punctuation included", lambda r: "Article 21" in r["answer"]),
        ],
        "5. New Laws (BNS, BNSS, BSA 2023)": [
            ("BNS 2023", "Bharatiya Nyaya Sanhita", lambda r: "BNS" in r["answer"] or "Nyaya" in r["answer"]),
            ("BNSS 2023", "Bharatiya Nagarik Suraksha Sanhita", lambda r: "BNSS" in r["answer"] or "Nagrik" in r["answer"] or "Suraksha" in r["answer"]),
            ("BSA 2023", "Bharatiya Sakshya Adhiniyam", lambda r: "BSA" in r["answer"] or "Sakshya" in r["answer"]),
        ],
        "6. Conversational & Edge-Case Queries": [
            ("hello", "Greeting test", lambda r: "Legal Compass" in r["answer"]),
            ("thank you", "Farewell test", lambda r: "informational" in r["answer"].lower()),
            ("How do I file an FIR?", "Situational FIR query", lambda r: "FIR" in r["answer"] or "154" in r["answer"]),
            ("What is anticipatory bail?", "Situational Bail query", lambda r: "bail" in r["answer"].lower() or "438" in r["answer"]),
        ],
    }

    total_tests = 0
    total_passed = 0
    total_failed = 0

    for cat_name, tests in test_categories.items():
        print(f"\n▶ {cat_name}")
        print("-" * 65)
        for query, desc, validator in tests:
            total_tests += 1
            res = engine.answer(query)
            ans = res.get("answer", "")
            
            try:
                passed = validator(res)
            except Exception as e:
                passed = False
            
            if passed:
                total_passed += 1
                print(f"  [PASS] '{query}' — {desc}")
            else:
                total_failed += 1
                print(f"  [FAIL] '{query}' — {desc}")
                print(f"         Result excerpt: {ans[:100]}...")

    print("\n" + "=" * 65)
    print(f"  FINAL SUMMARY: {total_passed}/{total_tests} PASSED ({round(total_passed/total_tests*100, 1)}%)")
    print(f"  FAILED: {total_failed}")
    print("=" * 65 + "\n")

    return total_failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
