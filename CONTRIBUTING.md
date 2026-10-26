# Contributing Guidelines — Team Erdoza

## Branch Strategy

Gunakan branch terpisah untuk setiap anggota:

| Branch | Developer | Scope |
|---|---|---|
| `feature/dh-cli` | Oryza | Diffie-Hellman, CLI & Integration |
| `feature/math-engine` | Aldo | Mathematical Utilities |
| `feature/elgamal` | Erlinda | ElGamal & EHR Data Processing |

## Development Rules

1. Jangan langsung melakukan push ke branch `main`.
2. Kerjakan modul sesuai pembagian jobdesk.
3. Pertahankan nama fungsi, parameter, dan format return.
4. Tambahkan unit test untuk fungsi yang diimplementasikan.
5. Jangan mengunggah data pasien asli, private key, atau file `.env`.
6. Buat Pull Request setelah fitur selesai.
7. Lakukan code review sebelum merge ke `main`.

## Function Contracts

### Mathematical Utilities — Aldo

- `mod_exp(base, exponent, modulus) -> int`
- `extended_gcd(a, b) -> tuple[int, int, int]`
- `mod_inverse(a, modulus) -> int`
- `is_prime(n) -> bool`

### ElGamal — Erlinda

- `generate_keys(p, g) -> (public_key, private_key)`
- `encrypt(plaintext, public_key) -> list[tuple[int, int]]`
- `decrypt(ciphertext, private_key) -> str`

### Diffie-Hellman — Oryza

- `generate_dh_keys(p, g) -> (private_key, public_key)`
- `compute_shared_secret(peer_public_key, private_key, p) -> int`

## Testing

Jalankan seluruh unit test dengan:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Pastikan setiap modul berhasil diuji sebelum integrasi.

## Commit Convention

Contoh:

```bash
git commit -m "feat: implement modular exponentiation"
git commit -m "feat: implement elgamal encryption"
git commit -m "feat: add diffie hellman handshake"
git commit -m "test: add elgamal unit tests"
git commit -m "docs: update project documentation"
```

## Integration

Integrasi akhir dilakukan setelah setiap modul siap dan telah melalui pengujian. Semua perubahan yang memengaruhi kontrak fungsi harus disepakati bersama.