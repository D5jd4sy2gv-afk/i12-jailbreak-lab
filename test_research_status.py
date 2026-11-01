import unittest
from research_status import build_report, TARGET

class ResearchStatusTests(unittest.TestCase):
    def test_report_target_and_safety(self):
        report = build_report()
        self.assertEqual(report["target"], TARGET)
        self.assertIn("NO_PUBLIC_REPRODUCIBLE_A14_FULL_JAILBREAK_ESTABLISHED", report["overall"])
        self.assertTrue(any("does not contact or modify" in x for x in report["safety"]))

if __name__ == "__main__":
    unittest.main()
