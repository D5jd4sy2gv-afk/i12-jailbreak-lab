import unittest
from argparse import Namespace
from i12_jb_audit import DeviceInfo, assess, collect_device, TARGET_PRODUCT, TARGET_IOS, TARGET_BUILD

class AuditTests(unittest.TestCase):
    def test_exact_target_tuple(self):
        info = DeviceInfo(TARGET_PRODUCT, TARGET_IOS, TARGET_BUILD, "iPhone 12", "A14 Bionic", "D53gAP")
        result = assess(info)
        self.assertTrue(result["target_match"])
        self.assertEqual(result["overall"], "NO_VERIFIED_PUBLIC_FULL_JAILBREAK_FOR_THIS_TARGET")

    def test_wrong_build_is_not_exact_target(self):
        info = DeviceInfo(TARGET_PRODUCT, TARGET_IOS, "24A999", "iPhone 12", "A14 Bionic", "D53gAP")
        self.assertFalse(assess(info)["target_match"])

    def test_manual_device_profile(self):
        args = Namespace(product_type=TARGET_PRODUCT, ios_version=TARGET_IOS, build=TARGET_BUILD)
        info = collect_device(args)
        self.assertEqual(info.device_name, "iPhone 12")
        self.assertEqual(info.chip, "A14 Bionic")

if __name__ == "__main__":
    unittest.main()
