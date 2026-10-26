import unittest

from utils.ehr_data import bytes_to_text, text_to_bytes, validate_ehr


class TestEHRData(unittest.TestCase):

    def test_validate_ehr(self):
        self.assertTrue(validate_ehr("Patient: Example"))
        self.assertFalse(validate_ehr(""))
        self.assertFalse(validate_ehr(" \t\n"))
        self.assertFalse(validate_ehr(None))

    def test_utf8_round_trip(self):
        text = "Pasien fiktif: Zoë 🩺"
        self.assertEqual(bytes_to_text(text_to_bytes(text)), text)

    def test_conversion_rejects_invalid_types_or_encoding(self):
        with self.assertRaises(TypeError):
            text_to_bytes(123)
        with self.assertRaises(TypeError):
            bytes_to_text("not bytes")
        with self.assertRaises(UnicodeDecodeError):
            bytes_to_text(b"\xff")


if __name__ == "__main__":
    unittest.main()
