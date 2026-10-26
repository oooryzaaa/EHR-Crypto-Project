
"""
Core Mathematical Utilities
Developer: Christiano Ronaldo (Aldo)

Modular arithmetic functions for DH and ElGamal.
"""


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """Calculate base ** exponent modulo a positive modulus by squaring.

    Exponents must be non-negative. A modulus of 1 returns 0, including
    for exponent 0. Negative bases are reduced modulo the modulus first.
    """
    if any(type(value) is not int for value in (base, exponent, modulus)):
        raise TypeError("Base, exponent, and modulus must be integers.")
    if exponent < 0:
        raise ValueError("Exponent must be non-negative.")
    if modulus <= 0:
        raise ValueError("Modulus must be positive.")

    result = 1 % modulus
    base %= modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = result * base % modulus
        base = base * base % modulus
        exponent //= 2

    return result


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (gcd, x, y) with non-negative gcd and ax + by = gcd.

    Signed inputs and zeros are supported; (0, 0) returns (0, 1, 0).
    """
    if type(a) is not int or type(b) is not int:
        raise TypeError("a and b must be integers.")

    old_r, r = abs(a), abs(b)
    old_x, x = 1, 0
    old_y, y = 0, 1

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y

    if a < 0:
        old_x = -old_x
    if b < 0:
        old_y = -old_y

    return old_r, old_x, old_y


def mod_inverse(a: int, modulus: int) -> int:
    """Return the inverse in 0..modulus-1 using extended_gcd.

    Raise ValueError if modulus <= 1 or a and modulus are not coprime.
    """
    if type(a) is not int or type(modulus) is not int:
        raise TypeError("a and modulus must be integers.")
    if modulus <= 1:
        raise ValueError("Modulus must be greater than 1.")

    gcd, x, _ = extended_gcd(a, modulus)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist for these values.")

    return x % modulus


def is_prime(n: int) -> bool:
    """Check primality exactly by trial division through sqrt(n).

    Intended for the small educational parameters used by this project;
    trial division is not suitable for cryptographic-size primes.
    """
    if type(n) is not int:
        raise TypeError("n must be an integer.")
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Every prime greater than 3 has the form 6k - 1 or 6k + 1.
    divisor = 5
    while divisor * divisor <= n:
        if n % divisor == 0 or n % (divisor + 2) == 0:
            return False
        divisor += 6

    return True
