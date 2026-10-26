# Math Engine — Christiano Ronaldo

Modul `crypto/math_utils.py` mengimplementasikan operasi matematika secara
manual tanpa library kriptografi. Nama fungsi, parameter, dan format return
mengikuti kontrak pada `CONTRIBUTING.md`.

| Fungsi | Algoritma dan hasil | Batas input |
|---|---|---|
| `mod_exp(base, exponent, modulus)` | Square-and-multiply, hasil `0..modulus-1` | `exponent >= 0`, `modulus > 0` |
| `extended_gcd(a, b)` | Extended Euclidean Algorithm iteratif, tuple `(gcd, x, y)` dengan `a*x + b*y == gcd` | Mendukung negatif dan nol; `gcd >= 0` |
| `mod_inverse(a, modulus)` | Koefisien Bezout dari `extended_gcd`, dinormalisasi dengan modulo | `modulus > 1` dan `gcd(a, modulus) == 1` |
| `is_prime(n)` | Trial division, menguji faktor `6k-1` dan `6k+1` sampai akar kuadrat | Nilai di bawah 2 menghasilkan `False` |

Semua argumen harus bertipe `int`; termasuk `bool` ditolak dengan `TypeError`,
selaras dengan validasi integer pada modul ElGamal. Rentang yang tidak valid
atau invers yang tidak tersedia menghasilkan `ValueError`.

`mod_exp(0, 0, p)` menghasilkan `1` untuk `p > 1`; modulus 1 selalu menghasilkan
`0`. `extended_gcd(0, 0)` menghasilkan `(0, 1, 0)`.

Square-and-multiply membutuhkan O(log exponent) iterasi dan Extended Euclidean
Algorithm O(log min(|a|, |b|)) untuk input nonzero. Pemeriksaan prima bersifat
eksak, dengan O(sqrt(n)) iterasi sebagai batas atas, dan ditujukan untuk parameter
demonstrasi kecil seperti `p = 467`.

## Review integrasi sebelum implementasi

- Empat fungsi matematika masih berupa placeholder dan `tests/test_math.py`
  kosong. Baseline: 13 pengujian dijalankan, tiga error pada Diffie-Hellman
  karena `mod_exp` belum diimplementasikan.
- Kode Oryza pada `crypto/diffie_hellman.py` sudah mengimpor `mod_exp`.
  Implementasi ini langsung memenuhi dependensi tersebut tanpa mengubah
  kontrak maupun kode DH, CLI, dan Flask.
- Kode Erlinda pada `crypto/elgamal.py` sudah lulus pengujian. Modul tersebut
  memakai `pow` untuk eksponensiasi/invers dan `_is_probable_prime` untuk
  pemeriksaan prima. Mengalihkan pemanggilannya ke math engine memerlukan
  koordinasi terpisah sesuai aturan kepemilikan modul di `CONTRIBUTING.md`;
  perubahan ini hanya menyediakan dan menguji fungsi matematika bersama.
- DH saat ini belum memvalidasi primalitas `p`. Selain itu, generator dengan
  orde kecil dapat menghasilkan public key `1` atau `p-1` yang kemudian ditolak
  `compute_shared_secret`. Parameter demo `p=467, g=2` tidak mengalami kasus
  tersebut untuk rentang private key yang digunakan. Validasi parameter DH
  merupakan tindak lanjut pada modul Oryza.

## Pengujian

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Pengujian math mencakup vektor hasil yang diketahui, perbandingan `mod_exp`
dengan `pow` Python, identitas Bezout dengan `math.gcd`, identitas invers,
primalitas terhadap sieve, bilangan komposit Carmichael, input negatif/nol,
integer besar, serta penolakan input tidak valid. Fungsi referensi bawaan hanya
digunakan di pengujian.

Satu pengujian tambahan melakukan round-trip rumus ElGamal untuk seluruh
256 nilai byte menggunakan math engine dan pemetaan `byte + 1` milik Erlinda.
Ini memverifikasi kompatibilitas rumus tanpa mengubah implementasi ElGamal.

Hasil verifikasi setelah implementasi:

- Seluruh 25 unit test lulus, termasuk DH, ElGamal, EHR, dan math engine.
- Smoke test dengan Flask test client: empat halaman dapat dirender; persiapan
  EHR, handshake, enkripsi, transmisi, dan dekripsi berhasil dengan
  `verified == True`.
- Smoke test CLI melalui input menu: handshake, input pasien fiktif, enkripsi,
  tampilan transmisi, dan dekripsi menghasilkan pesan verifikasi yang sesuai.
- `git diff --check` lulus. Pemeriksaan web memakai test client, belum mencakup
  interaksi JavaScript di browser.
