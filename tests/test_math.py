import math
import unittest

from crypto.math_utils import extended_gcd, is_prime, mod_exp, mod_inverse


class TestMathUtils(unittest.TestCase):

    def test_mod_exp_known_values(self):
        for base, exponent, modulus, expected in (
            (2, 5, 467, 32),
            (4, 13, 497, 445),
            (-2, 5, 13, 7),
            (467, 3, 467, 0),
            (0, 0, 467, 1),
            (2, 0, 1, 0),
        ):
            with self.subTest(base=base, exponent=exponent, modulus=modulus):
                self.assertEqual(mod_exp(base, exponent, modulus), expected)

    def test_mod_exp_matches_python_reference(self):
        for base in range(-10, 11):
            for exponent in range(12):
                for modulus in (1, 2, 7, 23, 467):
                    self.assertEqual(
                        mod_exp(base, exponent, modulus),
                        pow(base, exponent, modulus),
                    )
        self.assertEqual(mod_exp(123456789, 2**1024, 467),
                         pow(123456789, 2**1024, 467))

    def test_mod_exp_rejects_invalid_ranges(self):
        for values in ((2, -1, 467), (2, 5, 0), (2, 5, -7)):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    mod_exp(*values)

    def test_extended_gcd_known_value(self):
        self.assertEqual(extended_gcd(240, 46), (2, -9, 47))
        self.assertEqual(extended_gcd(0, 0), (0, 1, 0))

    def test_extended_gcd_bezout_identity_for_signed_inputs(self):
        for a in range(-25, 26):
            for b in range(-25, 26):
                gcd, x, y = extended_gcd(a, b)
                self.assertEqual(gcd, math.gcd(a, b))
                self.assertEqual(a * x + b * y, gcd)
        a, b = 2**2048, 2**1024 - 1
        gcd, x, y = extended_gcd(a, b)
        self.assertEqual(gcd, math.gcd(a, b))
        self.assertEqual(a * x + b * y, gcd)

    def test_mod_inverse_known_values(self):
        for a, modulus, expected in (
            (3, 11, 4), (17, 3120, 2753), (-3, 11, 7),
            (14, 11, 4), (1, 2, 1),
        ):
            with self.subTest(a=a, modulus=modulus):
                self.assertEqual(mod_inverse(a, modulus), expected)

    def test_mod_inverse_identity(self):
        for modulus in range(2, 50):
            for a in range(-50, 51):
                if math.gcd(a, modulus) == 1:
                    inverse = mod_inverse(a, modulus)
                    self.assertTrue(0 <= inverse < modulus)
                    self.assertEqual(a * inverse % modulus, 1)
                else:
                    with self.assertRaises(ValueError):
                        mod_inverse(a, modulus)

    def test_mod_inverse_rejects_invalid_modulus(self):
        for modulus in (-11, 0, 1):
            with self.subTest(modulus=modulus):
                with self.assertRaises(ValueError):
                    mod_inverse(3, modulus)

    def test_is_prime_known_values(self):
        for n in (2, 3, 5, 7, 23, 257, 467, 65537, 104729):
            with self.subTest(n=n):
                self.assertTrue(is_prime(n))
        for n in (-7, 0, 1, 4, 9, 25, 49, 121, 467**2, 561, 1105, 1729):
            with self.subTest(n=n):
                self.assertFalse(is_prime(n))

    def test_is_prime_matches_sieve(self):
        limit = 2000
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for divisor in range(2, math.isqrt(limit) + 1):
            if sieve[divisor]:
                for multiple in range(divisor * divisor, limit + 1, divisor):
                    sieve[multiple] = False
        for n, expected in enumerate(sieve):
            self.assertEqual(is_prime(n), expected, msg=f"n={n}")

    def test_rejects_non_integer_arguments(self):
        for invalid in (True, False, 2.5, "2", None, 2 + 0j):
            for function, arguments in (
                (mod_exp, (invalid, 2, 467)),
                (mod_exp, (2, invalid, 467)),
                (mod_exp, (2, 2, invalid)),
                (extended_gcd, (invalid, 3)),
                (extended_gcd, (3, invalid)),
                (mod_inverse, (invalid, 467)),
                (mod_inverse, (3, invalid)),
                (is_prime, (invalid,)),
            ):
                with self.subTest(function=function.__name__, arguments=arguments):
                    with self.assertRaises(TypeError):
                        function(*arguments)

    def test_manual_elgamal_round_trip_with_math_engine(self):
        # Exercise all four utilities with the existing byte + 1 encoding.
        p, g, private_key, ephemeral_key = 467, 2, 127, 53
        self.assertTrue(is_prime(p))
        public_key = mod_exp(g, private_key, p)
        c1 = mod_exp(g, ephemeral_key, p)
        encryption_secret = mod_exp(public_key, ephemeral_key, p)
        decryption_secret = mod_exp(c1, private_key, p)
        inverse = mod_inverse(decryption_secret, p)
        for byte in range(256):
            c2 = (byte + 1) * encryption_secret % p
            self.assertEqual(c2 * inverse % p - 1, byte)


if __name__ == "__main__":
    unittest.main()
