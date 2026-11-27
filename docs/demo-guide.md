# Demo Guide — Erdoza HealthCrypt

Panduan demo dan penjelasan source code. Disusun urut: apa yang ditunjukkan,
lalu kode mana yang dijelaskan, lalu antisipasi pertanyaan.

**Dokumen pendamping:** [code-walkthrough.md](./code-walkthrough.md) (kode per
baris), [web-flow.md](./web-flow.md) (alur request di web),
[cheatsheet.md](./cheatsheet.md) (ringkasan satu halaman),
[walkthrough-oryza-aldo.md](./walkthrough-oryza-aldo.md) (bagian Oryza dan
Aldo, format per baris).

## Persiapan sebelum demo

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe app.py
```

Buka `http://127.0.0.1:5000`.

- Pastikan internet hidup sebelum demo. `templates/base.html` memuat Bootstrap
  dari CDN jsdelivr. Tanpa internet, tampilan akan berantakan.
- Parameter demo: `P = 467`, `G = 2` (didefinisikan di `app.py` dan `main.py`).
  Alasannya: 467 prima, lebih besar dari 256, **safe prime** (467 = 2×233+1,
  233 prima), dan **2 adalah primitive root** dengan orde penuh 466. Penjelasan
  lengkap ada di [code-walkthrough.md](./code-walkthrough.md) bagian [0.5].
- State simulasi disimpan di memori (`DEMO_STATES`), hilang jika server restart.
- Ukuran sampel EHR dari tombol **Use Sample Data** adalah 119 byte, sehingga
  menghasilkan 119 blok ciphertext.

## 1. Alur demo di web

| # | Halaman | Aksi | Yang terjadi di balik layar |
|---|---|---|---|
| 1 | Dashboard `/` | Tunjukkan semua status "Pending" | `app.js` memanggil `GET /api/status`, lalu `renderStatus()` mengisi kartu metrik |
| 2 | Clinic `/clinic` | Klik **Use Sample Data**, lalu **Prepare EHR** | `POST /api/ehr/prepare`. Backend memvalidasi input, lalu menyusun 5 field menjadi satu string EHR |
| 3 | Cryptography | Klik **Generate DH Handshake** | `POST /api/crypto/handshake` memanggil `perform_handshake(467, 2)` |
| 4 | Cryptography | Klik **Encrypt Prepared EHR** | `POST /api/crypto/encrypt` membuat kunci ElGamal rumah sakit, lalu mengenkripsi teks EHR |
| 5 | Cryptography | Lihat panel terminal, lalu klik **Simulate Transmission** | Panel menampilkan pasangan `(c1, c2)`. Transmit hanya mengubah flag `transmitted = True` |
| 6 | Hospital `/hospital` | Klik **Decrypt with Hospital Private Key** | `POST /api/ehr/decrypt` memanggil `decrypt()`, lalu membandingkan hasilnya dengan EHR asli |

Poin yang perlu ditekan saat presentasi:

- Yang terlihat penyadap di jaringan hanya angka `(c1, c2)`, bukan teks asli.
- Private key ElGamal tidak pernah dikirim ke browser. `/api/crypto/details`
  hanya mengembalikan public key `(p, g, y)` dan ciphertext.
- Tombol dikunci sesuai urutan status, jadi tidak bisa decrypt sebelum transmit.
- Tombol **Reset** di pojok kanan atas mengosongkan seluruh state.

## 2. Alur demo CLI (opsional, 1-2 menit)

```powershell
.\.venv\Scripts\python.exe main.py
```

Menu `1` handshake, `2` input dan enkripsi EHR, `3` lihat transmisi, `4`
dekripsi, `5` reset, `0` keluar. Pada CLI, kunci ElGamal dibuat di menu `1`
(bersamaan dengan handshake), sedangkan di web dibuat saat proses enkripsi.

## 3. Peta source code

Urutan penjelasan yang enak diikuti: fondasi matematika, lalu protokol, lalu
aplikasi.

```text
crypto/math_utils.py     fondasi: mod_exp, extended_gcd, mod_inverse, is_prime
crypto/diffie_hellman.py pertukaran kunci
crypto/elgamal.py        enkripsi dan dekripsi per byte
utils/ehr_data.py        validasi dan konversi UTF-8
app.py                   Flask: routing, validasi, state sesi
static/js/app.js         fetch API dan render status
main.py                  CLI dengan alur yang sama
```

### 3.1 `crypto/math_utils.py`

**`mod_exp(base, exponent, modulus)`** menghitung `base^exponent mod modulus`
dengan square-and-multiply.

Contoh `mod_exp(2, 5, 467)`: 5 dalam biner adalah `101`.

| Langkah | Bit | `result` | `base` |
|---|---|---|---|
| awal | — | 1 | 2 |
| bit 0 (LSB) = 1 | ganjil | 2 | 4 |
| bit 1 = 0 | genap | 2 | 16 |
| bit 2 = 1 | ganjil | 32 | 256 |

Hasilnya 32. Tiap putaran `exponent //= 2`, jadi hanya butuh sekitar
`log2(exponent)` langkah. Ini kunci efisiensi seluruh sistem.

**`extended_gcd(a, b)`** mengembalikan `(gcd, x, y)` sehingga `a·x + b·y = gcd`.
Contoh dari unit test: `extended_gcd(240, 46) = (2, -9, 47)` karena
`240·(-9) + 46·47 = -2160 + 2162 = 2`.

**`mod_inverse(a, modulus)`** mencari `x` dengan `a·x ≡ 1 (mod modulus)`.
Caranya mengambil koefisien Bezout dari `extended_gcd`, lalu `% modulus`.
Contoh: `mod_inverse(3, 11) = 4` karena `3·4 = 12 ≡ 1 (mod 11)`.

**`is_prime(n)`** memakai trial division sampai `√n`, hanya mengecek pembagi
berbentuk `6k-1` dan `6k+1`. Fungsi ini belum dipanggil oleh modul DH atau
ElGamal; perannya sebagai utilitas matematika bersama yang diuji ketat, dan
sudah dipakai pada `test_manual_elgamal_round_trip_with_math_engine`. ElGamal
memakai `_is_probable_prime` (Miller-Rabin) untuk memvalidasi `p`.

Catatan untuk pertanyaan "kenapa `pow()` bawaan juga dipakai di ElGamal?":
`mod_exp` dipakai oleh `diffie_hellman.py`; `elgamal.py` memakai `pow()`.
Keduanya sudah dibuktikan menghasilkan nilai sama lewat
`test_mod_exp_matches_python_reference`. Detail ini ada di
[docs/math-engine.md](./math-engine.md).

### 3.2 `crypto/diffie_hellman.py`

Ide: dua pihak membangun nilai rahasia yang sama tanpa pernah mengirimkannya.

```text
p = 467, g = 2                         (parameter publik)
Klinik : a = 5  -> A = g^a mod p = 32
Hospital: b = 7  -> B = g^b mod p = 128
Klinik hitung  : B^a mod p = 128^5 mod 467 = 416
Hospital hitung: A^b mod p =  32^7 mod 467 = 416
```

Keduanya sama karena `(g^b)^a = g^(ab) = (g^a)^b`. Penyadap hanya melihat
`p, g, A, B`. Untuk mendapatkan `a` dari `A`, ia harus menyelesaikan
logaritma diskret, yang tidak praktis untuk `p` besar. Angka 416 di atas juga
sama dengan `2^35 mod 467`, sesuai `g^(ab)`.

Fungsi:

- `generate_dh_keys(p, g)` — private key acak `2..p-2`, public key
  `mod_exp(g, private, p)`. Di dalamnya ada perulangan yang mengulang
  pembangkitan bila public key jatuh di `1` atau `p-1`, karena
  `compute_shared_secret` menolak nilai tersebut.
- `compute_shared_secret(peer_public, private, p)` — `mod_exp(peer_public, private, p)`.
- `perform_handshake(p, g)` — menjalankan kedua sisi sekaligus, lalu
  memastikan `clinic_secret == hospital_secret`.

**Batasan yang harus disebut:** nilai DH pada demo ini hanya didemonstrasikan
sama di kedua sisi. Shared secret belum dipakai sebagai kunci enkripsi kanal.
Enkripsi data murni memakai ElGamal dengan pasangan kunci terpisah.

### 3.3 `crypto/elgamal.py`

Pembentukan kunci:

```text
private key x (acak)      -> (p, g, x)
public  key y = g^x mod p -> (p, g, y)
```

Enkripsi untuk satu nilai `m` dengan `k` acak baru setiap byte:

```text
c1 = g^k mod p
c2 = m · y^k mod p
```

Dekripsi:

```text
s = c1^x mod p          (karena c1^x = g^(kx) = y^k)
m = c2 · s^(-1) mod p   (faktor y^k saling menghilangkan)
```

Contoh terverifikasi dengan `p=467, g=2, x=127, k=53`, huruf `A` (`m = 66`):

```text
y   = 2^127 mod 467 = 132
c1  = 2^53  mod 467 = 399
s   = 132^53 mod 467 = 358      (dan 399^127 mod 467 = 358, sama)
invers dari 358 mod 467 = 437
c2  = 66 · 358 mod 467 = 278
dekripsi: 278 · 437 mod 467 = 66 -> 66 - 1 = 65 -> 'A'
```

Detail yang sering ditanyakan:

- **Kenapa `byte + 1`?** Byte bernilai `0..255`, tetapi `m = 0` membuat
  `c2 = 0` dan informasi hilang. Maka dipetakan ke `1..256`. Akibatnya `p`
  harus lebih besar dari 256, sesuai validasi `p <= 256` yang menolak.
- **Kenapa ciphertext berupa list pasangan?** Karena enkripsi per byte. Teks
  EHR 119 byte menghasilkan 119 pasangan `(c1, c2)`.
- **Kenapa `k` baru setiap byte?** Supaya byte yang sama menghasilkan
  ciphertext berbeda. Diuji oleh
  `test_encryption_uses_fresh_ephemeral_key_per_byte`.
- **`_is_probable_prime`** adalah Miller-Rabin untuk memvalidasi `p` sebelum
  enkripsi dan dekripsi.
- **`pow(s, -1, p)`** adalah invers modular bawaan Python, setara `mod_inverse`.

### 3.4 `utils/ehr_data.py`

Tiga fungsi kecil:

- `validate_ehr(text)` — benar jika string dan tidak kosong/hanya spasi.
- `text_to_bytes(text)` — `text.encode("utf-8")`.
- `bytes_to_text(data)` — `data.decode("utf-8")`.

UTF-8 dipilih karena teks Indonesia bisa memuat aksen dan emoji; satu emoji
bisa menjadi 4 byte, sehingga jumlah blok ciphertext mengikuti jumlah byte,
bukan jumlah karakter.

### 3.5 `app.py` (Flask)

- **State per sesi.** `DEMO_STATES` adalah dict di memori dengan kunci
  `session["demo_id"]`. `get_state()` membuat state baru bila belum ada.
  Bukan database, tidak persisten, dan tidak cocok untuk multi-worker.
- **Validasi input.** `prepare_ehr` mewajibkan lima field, masing-masing
  maksimal 200 karakter, dan umur `0..130`. Field disusun menjadi teks EHR
  dengan format `Patient ID / Name / Age / Diagnosis / Treatment`.
- **Urutan dijaga di backend.** `encrypt_ehr` menolak jika EHR atau DH belum
  ada; `transmit` menolak jika belum enkripsi; `decrypt_ehr` menolak jika
  belum transmit atau private key tidak ada.
- **Private key tidak keluar dari server.** Hanya `public_key` yang
  dikembalikan lewat `/api/crypto/details`.
- **Verifikasi.** `verified = recovered == state["ehr"]`.
- **Reset data.** Menyiapkan EHR baru atau handshake baru akan mengosongkan
  ciphertext dan hasil dekripsi sebelumnya.

### 3.6 `static/js/app.js`

- `apiRequest()` membungkus `fetch`, memeriksa `response.ok` dan
  `result.success`, lalu melempar `Error` dengan pesan dari backend.
- `renderStatus()` mengisi teks status dan mengatur `disabled` tombol
  berdasarkan data dari `/api/status`.
- `setupClinic`, `setupCryptography`, `setupHospital` memasang event listener
  sesuai halaman; halaman yang tidak punya elemen terkait akan dilewati
  (`if (!element) return`).
- Teks ditampilkan dengan `textContent` (bukan `innerHTML`) untuk mencegah XSS.

### 3.7 `main.py` (CLI)

Alur menu identik dengan web. Perbedaan utama: kunci ElGamal dibuat di menu
`1` (`generate_keys`), lalu disimpan di variabel lokal `hospital_public_key`
dan `hospital_private_key`. CLI memakai `perform_handshake` dan fungsi crypto
yang sama, jadi tidak ada duplikasi logika kriptografi.

## 4. Antisipasi pertanyaan

| Pertanyaan | Jawaban singkat |
|---|---|
| Shared secret DH dipakai untuk apa? | Hanya didemonstrasikan sama di kedua pihak; belum dipakai sebagai kunci enkripsi. Enkripsi data memakai ElGamal. |
| Kenapa ElGamal tidak memakai `mod_exp` buatan sendiri? | DH memakai `mod_exp`; ElGamal memakai `pow()`. Keduanya terbukti menghasilkan nilai sama lewat unit test. Dicatat di `docs/math-engine.md`. |
| Apakah sistem ini aman? | Tidak untuk produksi: `p = 467` terlalu kecil, DH tidak terautentikasi (rentan MITM), dan ElGamal dasar tidak menjamin integritas. |
| Kenapa ciphertext lebih besar dari plaintext? | Setiap byte menjadi dua angka `(c1, c2)`, sehingga 119 byte menjadi 119 pasangan. |
| Kenapa hasil enkripsi berubah setiap klik? | `k` dan kunci dibuat acak baru setiap proses, tetapi hasil dekripsi selalu sama. |
| Kenapa `p` harus > 256? | Karena byte dipetakan ke `1..256`; modulus lebih kecil membuat sebagian nilai tidak terwakili. |
| Kenapa memilih 467, bukan angka lain? | 467 memenuhi semua syarat: prima, > 256, safe prime, dan 2 primitive root berorde penuh 466 (jadi public key tersebar merata). 347 juga memenuhi syarat; 467 dipilih karena mudah dihitung manual saat demo. Bukan angka standar. |
| Apakah 467 aman? | Tidak. Hanya 9 bit, sedangkan minimum modern 2048 bit. Tujuannya supaya hasil pangkat bisa diperiksa manual. |
| Bug apa yang ditemukan saat pengujian? | Sebelum diperbaiki, public key DH bisa jatuh di `p-1` (peluang ~0,37% terukur dari 20.000 percobaan, ~0,43% teoretis), lalu ditolak validasi. Kini ditangani perulangan di `generate_dh_keys`: 0 kegagalan dari 20.000 percobaan, plus regression test. |
| Apa bedanya web dan CLI? | Logika kriptografi sama; beda pada tempat pembuatan kunci ElGamal dan cara penyimpanan state (Flask session vs variabel lokal). |
| Kenapa state hilang saat server restart? | State disimpan di dict memori (`DEMO_STATES`), bukan database. |

## 5. Pemecahan masalah saat demo

| Gejala | Penyebab umum | Solusi |
|---|---|---|
| Tampilan tanpa CSS | Bootstrap CDN tidak termuat | Sambungkan internet, atau muat Bootstrap lokal |
| "Prepare EHR data first" | Belum prepare EHR | Jalankan langkah 2 |
| "Complete the DH demonstration first" | Belum handshake | Klik **Generate DH Handshake** |
| "Transmit ciphertext first" | Belum klik transmit | Klik **Simulate Transmission** |
| Status kembali kosong | Server restart | Ulangi dari langkah 2 |
| Port 5000 terpakai | Proses lain berjalan | Hentikan proses lain, atau ubah `port` di `app.py` |
