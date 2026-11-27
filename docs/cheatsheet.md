# Cheatsheet — Erdoza HealthCrypt

Satu halaman untuk dibaca ulang sebelum demo.

## Angka kunci

```text
p = 467      g = 2      (parameter demo, di app.py dan main.py)
Sampel EHR   = 119 byte -> 119 blok ciphertext
Mapping byte = byte + 1  (1..256), karena itu p harus > 256
Private key DH = acak 2..p-2      Public key = g^private mod p
Private key ElGamal x           Public key y = g^x mod p
```

## Urutan demo web

```text
Dashboard  -> lihat status Pending
Clinic     -> Use Sample Data -> Prepare EHR
Crypto     -> Generate DH Handshake
Crypto     -> Encrypt Prepared EHR
Crypto     -> Simulate Transmission  (panel terminal menampilkan (c1, c2))
Hospital   -> Decrypt with Hospital Private Key -> "Record Matches"
```

Tombol terkunci sesuai urutan. Reset ada di kanan atas.

## Rumus

```text
Diffie-Hellman          ElGamal
A = g^a mod p           Enkripsi:  c1 = g^k mod p
B = g^b mod p                      c2 = m · y^k mod p
S = B^a = A^b mod p     Dekripsi:  s  = c1^x mod p
                                   m  = c2 · s^-1 mod p
```

## Contoh angka terverifikasi

```text
DH      a=5, b=7            -> A=32, B=128, S=416 (kedua sisi sama)
        cek: 2^35 mod 467 = 416
mod_exp mod_exp(2, 5, 467)  -> 32
egcd    extended_gcd(240,46) -> (2, -9, 47)
inverse mod_inverse(3, 11)  -> 4
ElGamal x=127, k=53, huruf A (m=66)
        y=132, c1=399, s=358, invers=437, c2=278
        dekripsi: 278 · 437 mod 467 = 66 -> 'A'
```

## File dan tanggung jawab

| File | Isi | Developer |
|---|---|---|
| `crypto/math_utils.py` | `mod_exp`, `extended_gcd`, `mod_inverse`, `is_prime` | Aldo |
| `crypto/diffie_hellman.py` | `generate_dh_keys`, `compute_shared_secret`, `perform_handshake` | Oryza |
| `crypto/elgamal.py` | `generate_keys`, `encrypt`, `decrypt`, `_is_probable_prime` | Erlinda |
| `utils/ehr_data.py` | `validate_ehr`, `text_to_bytes`, `bytes_to_text` | Erlinda |
| `app.py` | 4 halaman + 8 API, state di `DEMO_STATES` | Oryza |
| `static/js/app.js` | `apiRequest`, `renderStatus`, setup per halaman | Oryza |
| `main.py` | CLI menu 1-5 | Oryza |

## Endpoint API

```text
GET  /api/status          status ringkas sesi
POST /api/ehr/prepare     validasi + susun teks EHR
POST /api/crypto/handshake perform_handshake(467, 2)
POST /api/crypto/encrypt  generate_keys + encrypt
GET  /api/crypto/details  p, g, public key, ciphertext (tanpa private key)
POST /api/ehr/transmit    set transmitted = True
POST /api/ehr/decrypt     decrypt + verified = (hasil == EHR asli)
POST /api/reset           kosongkan state
```

## Kalimat siap pakai

- "Diffie-Hellman menyepakati rahasia bersama, ElGamal memakainya untuk
  mengenkripsi rekam medis per byte."
- "Penyadap hanya melihat pasangan `(c1, c2)`; tanpa private key, isi rekam
  medis tidak bisa dipulihkan."
- "Private key tidak pernah dikirim ke browser; hanya public key yang
  ditampilkan."
- "Parameter 467 sengaja kecil untuk demonstrasi, bukan untuk produksi."
- "DH di sini belum terautentikasi, sehingga belum tahan man-in-the-middle."

## Perintah

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe app.py      # http://127.0.0.1:5000
.\.venv\Scripts\python.exe main.py     # CLI
```

## Jangan lupa

- Cek internet (Bootstrap dari CDN) sebelum mulai.
- Kalau status kosong, server kemungkinan restart: ulangi dari Prepare EHR.
- 26 unit test harus lulus: `Ran 26 tests ... OK`.
