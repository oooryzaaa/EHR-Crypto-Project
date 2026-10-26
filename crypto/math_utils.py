
"""
Core Mathematical Utilities
Developer: Aldo

Modular arithmetic functions for DH and ElGamal.
"""


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """Calculate (base ** exponent) % modulus."""
    # TODO (Aldo): Implement modular exponentiation.
    raise NotImplementedError("Implement mod_exp")


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (gcd, x, y) such that ax + by = gcd."""
    # TODO (Aldo): Implement Extended Euclidean Algorithm.
    raise NotImplementedError("Implement extended_gcd")


def mod_inverse(a: int, modulus: int) -> int:
    """Return modular multiplicative inverse of a."""
    # TODO (Aldo): Use extended_gcd.
    raise NotImplementedError("Implement mod_inverse")


def is_prime(n: int) -> bool:
    """Check whether n is prime."""
    # TODO (Aldo): Implement primality checking.
    raise NotImplementedError("Implement is_prime")
