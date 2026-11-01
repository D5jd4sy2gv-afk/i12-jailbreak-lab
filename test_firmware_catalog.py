import unittest
from firmware_catalog import lookup, DEVICE, TARGET_BUILD

class CatalogTests(unittest.TestCase):
    def test_exact_build_found(self):
        def fake(url):
            return [{"identifier": DEVICE, "version": "27.0", "buildid": TARGET_BUILD,
                     "signed": False, "filesize": 123456}]
        r = lookup(fake)
        self.assertEqual(r["status"], "found")
        self.assertEqual(r["device"], DEVICE)
        self.assertEqual(r["build"], TARGET_BUILD)
        self.assertFalse(r["signed"])
        self.assertFalse(r["binary_downloaded"])

    def test_missing_build(self):
        r = lookup(lambda url: [{"identifier": DEVICE, "version": "27.1", "buildid": "OTHER", "signed": True}])
        self.assertEqual(r["status"], "not_found")

    def test_fallback_source(self):
        calls = []
        def fake(url):
            calls.append(url)
            if len(calls) == 1:
                raise OSError("offline")
            return {"firmwares": [{"identifier": DEVICE, "version": "27.0", "buildid": TARGET_BUILD, "signed": False}]}
        r = lookup(fake)
        self.assertEqual(r["status"], "found")
        self.assertEqual(r["source"], "ipsw.me")
        self.assertEqual(len(calls), 2)

if __name__ == "__main__":
    unittest.main()
