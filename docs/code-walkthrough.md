# Code Walkthrough — Penjelasan Kode per Baris Mengikuti Alur Sistem

Urutan penjelasan mengikuti jalannya data, bukan per file. Tiap bagian
menyebut file, nomor baris, lalu arti tiap baris. Nomor baris sesuai kondisi
kode saat dokumen ini ditulis; kalau file diedit, nomornya bisa bergeser.

Peta alur:

```text
[0] Parameter dan penyimpanan state          app.py
[0.5] Alasan pemilihan p = 467 dan g = 2
[1] Prepare EHR                              app.py
[2] Diffie-Hellman                           app.py -> diffie_hellman.py -> math_utils.py (mod_exp)
[3] ElGamal: buat kunci dan enkripsi         app.py -> elgamal.py -> ehr_data.py
[4] Transmisi                                app.py
[5] Dekripsi                                 app.py -> elgamal.py -> ehr_data.py
[6] Reset                                    app.py
[7] Fungsi math lain (extended_gcd dst)      math_utils.py
[8] Versi CLI                                main.py
```

Catatan jujur yang perlu diingat: dari `math_utils.py`, hanya `mod_exp` yang
dipanggil oleh alur web dan CLI (dipakai DH). `extended_gcd`, `mod_inverse`,
dan `is_prime` belum dipanggil modul lain; ElGamal memakai `pow()` bawaan
Python. Ketiganya tetap diuji di `tests/test_math.py`.

Dokumen ini fokus pada alur data di backend. Untuk sisi browser (klik apa,
`fetch` ke mana, UI berubah bagaimana), lihat
[web-flow.md](./web-flow.md).

---

## [0] Parameter dan penyimpanan state

### `app.py` baris 1-13 (persiapan)

- **1** `import secrets` — modul acak aman secara kriptografi (lebih baik dari `random`).
- **2-5** mengimpor Flask: `Flask` (aplikasi), `render_template` (menampilkan HTML),
  `request` (data masuk), `jsonify` (membuat response JSON), `session` (cookie sesi).
- **7** `app = Flask(__name__)` membuat aplikasi web.
- **8** `app.secret_key = secrets.token_bytes(32)` — kunci untuk menandatangani
  cookie sesi. Dibuat acak tiap server start, jadi cookie lama tidak valid
  setelah restart.
- **11-13** `P = 467`, `G = 2`, dan `DEMO_STATES = {}`. Dua yang pertama adalah
  modulus prima dan generator untuk DH dan ElGamal; ini pilihan kita sendiri
  untuk demo, bukan standar, dan alasannya dibahas di bagian [0.5].
  `DEMO_STATES` adalah dict di memori yang menyimpan state semua pengguna:
  kuncinya id sesi, nilainya state simulasi.

### `app.py` baris 16-36 (state per pengguna)

- **16-25** `empty_state()` mengembalikan dict awal dengan 7 slot:
  - `ehr` teks rekam medis
  - `dh` hasil handshake
  - `public_key` dan `private_key` kunci ElGamal rumah sakit
  - `ciphertext` hasil enkripsi
  - `transmitted` flag sudah "dikirim"
  - `recovered` hasil dekripsi
- **28** `get_state()` dipanggil di awal hampir semua endpoint.
- **29** `sid = session.get("demo_id")` — ambil id dari cookie; `None` jika baru pertama.
- **31** `if sid not in DEMO_STATES` — benar jika id belum ada di dict
  (termasuk `None`).
- **32** `secrets.token_urlsafe(24)` membuat id acak yang tidak bisa ditebak.
- **33** `session["demo_id"] = sid` menyimpan id ke cookie browser.
- **34** `DEMO_STATES[sid] = empty_state()` membuat state kosong.
- **36** `return DEMO_STATES[sid]` mengembalikan dict yang sama (bukan salinan),
  sehingga perubahan di endpoint langsung tersimpan.

### `app.py` baris 39-60 (fungsi pembantu)

- **39-44** `api_error(message, code=400, kind="error")` membuat response error
  seragam: `{"success": False, "message": ..., "kind": ...}` plus kode HTTP.
  Frontend membaca field `message` ini untuk toast.
- **47-60** `summary(state)` mengubah state menjadi ringkasan aman untuk browser:
  - **51** `prepared` benar jika `ehr` sudah ada
  - **52** `connected` benar jika `dh` sudah ada
  - **53** `encrypted` benar jika `ciphertext` sudah ada
  - **54** `transmitted` langsung dari flag
  - **55** `decrypted` benar jika `recovered` sudah ada
  - **56** `block_count` jumlah pasangan ciphertext, 0 jika belum ada
  - Private key tidak pernah masuk ke ringkasan ini.

### `app.py` baris 67-98 (halaman dan status)

- **67-84** empat route halaman (`/`, `/clinic`, `/cryptography`, `/hospital`),
  masing-masing hanya `render_template` ke file HTML terkait.
- **91-98** `GET /api/status` memanggil `get_state()` lalu mengembalikan
  `summary(state)`. Inilah panggilan pertama yang membuat sesi lahir.

---

## [0.5] Mengapa `p = 467` dan `g = 2`

Pertanyaan ini hampir pasti muncul saat presentasi. Jawaban singkatnya: angka
ini **pilihan proyek**, bukan standar internasional, tetapi tidak sembarang
angka — 467 memenuhi empat syarat sekaligus.

### Empat syarat parameter

| # | Syarat | Kalau dilanggar | Di mana dicek |
|---|---|---|---|
| 1 | `p > 256` | byte dipetakan ke `1..256`; `p ≤ 256` membuat sebagian byte tidak bisa dienkripsi | `elgamal.py` baris 61-62 |
| 2 | `p` prima | invers `s^(-1) mod p` belum tentu ada, sehingga dekripsi gagal | `elgamal.py` baris 61-62 lewat `_is_probable_prime` |
| 3 | `1 < g < p` | `g = 0`, `1`, atau `p` membuat public key selalu 0 atau 1 | `diffie_hellman.py` baris 30-31, `elgamal.py` baris 63-64 |
| 4 | `g` berorde besar | public key hanya menempati sedikit nilai, mudah ditebak | tidak divalidasi kode; dijamin oleh pemilihan angka |

Syarat 1 dan 2 adalah **wajib** (dicek kode). Syarat 3 juga dicek. Syarat 4
tidak dicek kode sama sekali — ini yang membuat pemilihan angka jadi penting.

### Fakta 467 yang sudah diverifikasi

```text
467 prima                                   -> syarat 2 terpenuhi
467 = 2 × 233 + 1, dan 233 prima            -> 467 adalah SAFE PRIME
2^233 mod 467 = 466 = -1 (mod 467)          -> orde 2 mod 467 = 466 = p-1
                                            -> 2 adalah PRIMITIVE ROOT
```

Karena orde 2 adalah 466, nilai `2^a mod 467` untuk `a = 1..466` menjelajahi
**seluruh** rentang `1..466` tanpa pengulangan. Inilah sebabnya `g = 2` bagus:
public key tersebar merata, tidak menumpuk di beberapa angka saja.

Konsekuensi tambahan: karena ordonya penuh, **tepat satu** nilai `a` yang
memetakan ke `p-1`, yaitu `a = (p-1)/2 = 233` (karena `2^233 ≡ -1`).
Kalau `p` lebih kecil, proporsi private key "bermasalah" bisa jauh lebih besar:
untuk `p=7, g=3` (juga safe prime dengan primitive root), `a = 3` memetakan ke
`6`, yaitu 1 dari 4 kemungkinan (25%). Dengan `p = 467`, angkanya 1 dari 464.

### Kenapa bukan angka lain

Prima terkecil di atas 256 adalah **257**, tetapi 257 = `2^8 + 1` (Fermat
prime) dan orde 2 modulo 257 hanya **16**. Artinya `2^a mod 257` hanya
menghasilkan 16 nilai berbeda — public key sangat mudah ditebak.

Kalau syarat "safe prime" dan "2 primitive root" diterapkan sekaligus,
kandidat di atas 256 adalah:

| `p` | Safe prime? | Orde 2 | 2 primitive root? |
|---|---|---|---|
| 347 | ya | 346 | ya |
| 467 | ya | 466 | ya |
| 479 | ya | 239 | tidak |

Jadi **347 juga memenuhi semua syarat dan lebih kecil**. Tidak ada rumus yang
memaksa angka 467 dibanding 347. 467 adalah keputusan proyek; yang bisa
dipertanggungjawabkan secara matematis adalah bahwa 467 memenuhi semua syarat.
Angka ini dipilih karena masih cukup kecil sehingga hasil pemangkatannya bisa
diperiksa manual saat demo, dan `p - 1 = 466` mudah divisualisasikan saat
menjelaskan kasus `p-1` di bawah.

### Konsekuensi: bug 0,43% yang kita perbaiki

Karena orde 2 penuh (466) dan private key diambil dari rentang `2..465`
(464 nilai), hanya `a = 233` yang menghasilkan public key `466 = p-1`, dan
`compute_shared_secret` menolak nilai itu. Peluang satu pihak kena:

```text
1/464 ≈ 0,22%
```

Handshake melibatkan dua pihak, jadi peluang minimal satu pihak kena:

```text
1 - (463/464)^2 ≈ 0,43%
```

Pengukuran **sebelum** perbaikan, dari 20.000 handshake, memberi 74 kegagalan
(0,37%), konsisten dengan hitungan teoretis. **Sesudah** perbaikan, 20.000
handshake menghasilkan 0 kegagalan. Perbaikannya ada di `generate_dh_keys`
baris 33-41.

Catatan penting: penyebabnya **bukan** 467 sebagai safe prime, melainkan
validasi `compute_shared_secret` yang menolak `p-1`. Kalau `g` berorde kecil,
kasus seperti ini akan jauh lebih sering karena lebih banyak private key
memetakan ke `1` atau `p-1`.

### Kenapa bukan angka besar seperti di dunia nyata

| Konteks | Ukuran `p` | Catatan |
|---|---|---|
| Demo ini | 467 (9 bit) | hasil pangkat bisa dihitung manual |
| Minimum aman modern | 2048 bit | sekitar 617 digit desimal |
| Rekomendasi umum | 3072 bit | |
| Grup standar | RFC 3526 group 14-16 | dipakai TLS/VPN |

Kalau `p` diperbesar ke 2048 bit, ElGamal yang bekerja per byte membuat tiap
pasangan `(c1, c2)` menjadi sekitar 512 byte. Satu teks EHR 119 byte akan
menghasilkan puluhan kilobyte ciphertext, dan panel terminal di web menjadi
tidak terbaca. Untuk demonstrasi, 467 adalah kompromi yang tepat.

> Kalimat transisi: "Setelah state dan parameter dijelaskan, tahap pertama alur
> sistem adalah menyiapkan data rekam medis."

---

## [1] Prepare EHR

### `app.py` baris 105-167

- **105** `@app.post("/api/ehr/prepare")` — hanya menerima POST.
- **107** ambil state sesi.
- **108** `request.get_json(silent=True)` membaca body JSON; `silent=True`
  membuatnya mengembalikan `None` (bukan error) bila body rusak.
- **110-111** jika bukan dict, tolak dengan "Invalid JSON request.".
- **113-119** daftar lima field wajib: `patient_id`, `patient_name`, `age`,
  `diagnosis`, `treatment`.
- **121** `values = {}` penampung nilai yang sudah dibersihkan.
- **123** loop tiap field.
- **124** `str(data.get(field, "")).strip()` — ambil nilai, ubah ke string,
  buang spasi pinggir; kalau field tidak ada jadi string kosong.
- **126-129** kosong berarti error "Field '...' is required.".
- **131-134** lebih dari 200 karakter berarti error "too long".
- **136** simpan ke `values`.
- **138-141** `int(values["age"])` — jika bukan angka, `ValueError` ditangkap
  dan dijawab "Age must be a number.".
- **143-144** umur harus `0..130`.
- **146-152** merangkai satu string EHR lima baris (`Patient ID`, `Name`,
  `Age`, `Diagnosis`, `Treatment`) dipisah `\n`.
- **154** `state["ehr"] = ehr` menyimpan teks di server.
- **156-159** ciphertext, flag transmit, dan hasil dekripsi dikosongkan,
  karena data baru membuat enkripsi lama tidak berlaku. `dh` dan kunci
  ElGamal tidak dihapus.
- **161-167** response: `preview` (teks EHR), `bytes` (jumlah byte UTF-8,
  misalnya 119), dan `data` (ringkasan).

> Kalimat transisi: "Teks EHR sudah tersimpan. Sebelum mengenkripsi, kedua
> pihak melakukan pertukaran kunci Diffie-Hellman."

---

## [2] Diffie-Hellman

### `app.py` baris 174-219 (endpoint)

- **174** `@app.post("/api/crypto/handshake")`.
- **176** ambil state.
- **178** `try` supaya error modul bisa ditangkap.
- **179** `from crypto.diffie_hellman import perform_handshake` — impor di
  dalam fungsi (lazy import) agar kegagalan modul tidak menjatuhkan seluruh server.
- **181** `perform_handshake(P, G)` — jalankan simulasi DH dengan 467 dan 2.
- **183-184** jika `success` tidak benar, kirim error.
- **186** `state["dh"] = result` simpan hasil.
- **188-193** kunci ElGamal, ciphertext, flag transmit, dan hasil dekripsi
  dikosongkan: sesi kripto baru, data lama dibuang.
- **195-209** response berisi `p`, `g`, public key klinik dan rumah sakit, dan
  boolean `shared_secret_match` (hasil bandingan `clinic_secret == hospital_secret`).
  Nilai shared secret sendiri tidak dikirim ke browser.
- **211-216** `ImportError` atau `NotImplementedError` dijawab kode 409
  `module_pending`.
- **218-219** `ValueError` atau `RuntimeError` dijawab 400 dengan pesan error.

### `crypto/diffie_hellman.py` baris 8-9

- **8** `import secrets` untuk bilangan acak.
- **9** `from crypto.math_utils import mod_exp` — DH memakai `mod_exp` buatan sendiri.

### `crypto/diffie_hellman.py` baris 12-40 `generate_dh_keys(p, g)`

- **12-15** fungsi menerima `p` dan `g`, mengembalikan tuple `(private, public)`.
- **26-27** `p` harus lebih dari 3, kalau tidak `ValueError`.
- **29-30** `g` harus di antara 1 dan `p`, kalau tidak `ValueError`.
- **32** `for _ in range(1000)` — coba paling banyak 1000 kali.
- **33** `secrets.randbelow(p - 3) + 2` — `randbelow(n)` menghasilkan `0..n-1`,
  jadi hasilnya `2..p-2`. Private key tidak boleh 0, 1, atau `p-1`.
- **34** `public_key = mod_exp(g, private_key, p)` — rumus `A = g^a mod p`.
- **36-38** jika `2 <= public_key <= p-2`, kembalikan pasangan kunci.
  Pengecekan ini ada karena `compute_shared_secret` menolak public key
  di luar rentang itu. Untuk `p=467, g=2`, private key 233 menghasilkan
  public key 466 (= `p-1`); tanpa perulangan ini, handshake gagal acak
  sekitar 0,37%. Ini bug yang kita perbaiki.
- **40** jika 1000 percobaan gagal semua, `ValueError`.

### `crypto/diffie_hellman.py` baris 43-57 `compute_shared_secret`

- **43-47** menerima public key lawan, private key sendiri, dan `p`.
- **51-52** public key lawan harus `2..p-2`, kalau tidak `ValueError("Invalid peer public key.")`.
- **54-55** private key sendiri harus `2..p-2`.
- **57** `mod_exp(peer_public_key, private_key, p)` — rumus `S = B^a mod p`.

### `crypto/diffie_hellman.py` baris 60-93 `perform_handshake`

- **68** klinik membuat pasangan kunci (`clinic_private`, `clinic_public`).
- **70** rumah sakit membuat pasangan kunci.
- **72-76** klinik menghitung `clinic_secret` dari public key rumah sakit dan
  private key klinik.
- **78-82** rumah sakit menghitung `hospital_secret` dari public key klinik
  dan private key rumah sakit.
- **84-85** jika keduanya berbeda, `RuntimeError("DH shared secret mismatch.")`.
- **87-93** mengembalikan dict berisi dua public key, dua secret, dan `success: True`.

Contoh angka dengan `a=5`, `b=7`: `A = 32`, `B = 128`, keduanya menghitung
`S = 416`. Secara matematis `(g^b)^a = g^(ab) = (g^a)^b`.

### `crypto/math_utils.py` baris 10-31 `mod_exp` (dipakai oleh baris 34 dan 57 DH)

- **10** `mod_exp(base, exponent, modulus)` menghitung `base^exponent mod modulus`.
- **16-17** semua argumen harus `int` murni (bool ditolak), kalau tidak `TypeError`.
- **18-19** eksponen tidak boleh negatif.
- **20-21** modulus harus positif.
- **23** `result = 1 % modulus` — hasil awal 1; `% modulus` menangani kasus
  modulus 1 (hasilnya 0).
- **24** `base %= modulus` — kecilkan basis dulu supaya angka tidak membesar.
- **25** `while exponent > 0` — ulangi sampai eksponen habis.
- **26-27** jika bit terendah eksponen 1 (eksponen ganjil), kalikan hasil dengan basis saat ini.
- **28** `base = base * base % modulus` — kuadratkan basis.
- **29** `exponent //= 2` — geser eksponen satu bit ke kanan.
- **31** kembalikan `result`.

Contoh `mod_exp(2, 5, 467)`:

| Putaran | exponent awal | ganjil? | result | base | exponent akhir |
|---|---|---|---|---|---|
| 1 | 5 | ya | 2 | 4 | 2 |
| 2 | 2 | tidak | 2 | 16 | 1 |
| 3 | 1 | ya | 32 | 256 | 0 |

Hasil 32. Putarannya hanya sekitar `log2(exponent)` kali.

> Kalimat transisi: "Setelah kedua pihak sepakat, rumah sakit membuat kunci
> ElGamal dan klinik mengenkripsi rekam medis."

---

## [3] ElGamal: buat kunci dan enkripsi

### `app.py` baris 226-285 (endpoint)

- **226** `@app.post("/api/crypto/encrypt")`.
- **230-231** EHR belum disiapkan berarti error "Prepare EHR data first.".
- **233-236** DH belum dilakukan berarti error "Complete the DH demonstration first.".
- **239** lazy import `generate_keys` dan `encrypt`.
- **242** `generate_keys(P, G)` membuat pasangan kunci rumah sakit.
- **244-247** `encrypt(state["ehr"], public_key)` mengenkripsi teks EHR.
- **249-252** hasil harus berupa list.
- **254-262** tiap item harus pasangan (list atau tuple) berisi dua integer.
- **264-268** simpan `public_key`, `private_key`, `ciphertext`; flag
  transmit dan hasil dekripsi direset.
- **270-275** response: pesan sukses dan `block_count`.
- **277-282** modul belum siap dijawab 409.
- **284-285** `ValueError` atau `TypeError` dijawab 400.

### `crypto/elgamal.py` baris 71-82 `generate_keys(p, g)`

- **73-74** `p` dan `g` harus `int` murni.
- **75-76** `p` harus lebih dari 2 dan lolos `_is_probable_prime`.
- **77-78** `g` harus di antara 1 dan `p`.
- **80** `private_key = secrets.randbelow(p - 2) + 1` — hasilnya `1..p-2`.
- **81** `public_value = pow(g, private_key, p)` — rumus `y = g^x mod p`.
- **82** mengembalikan public key `(p, g, y)` dan private key `(p, g, x)`.
  Private key menyimpan `x`, bukan `y`.

### `crypto/elgamal.py` baris 8-49 `_is_probable_prime` (uji Miller-Rabin)

Tujuannya memeriksa apakah `p` prima, karena kalau `p` bukan prima,
invers modular tidak dijamin ada.

- **9-10** angka kurang dari 2 bukan prima.
- **12-17** cek pembagi prima kecil (2 sampai 37). Jika sama dengan prima
  itu, benar prima; jika habis dibagi, bukan prima.
- **19-23** menguraikan `number - 1 = odd_part × 2^powers_of_two`. Untuk 467:
  `466 = 233 × 2`, jadi `odd_part = 233`, `powers_of_two = 1`.
- **25-26** untuk angka di bawah `2^64`, memakai 7 basis tetap yang terbukti
  menghasilkan jawaban pasti.
- **27-31** untuk angka lebih besar, memakai 32 basis acak.
- **33** loop tiap basis.
- **34-36** basis dikecilkan modulo `number`; basis 0 atau 1 dilewati karena tidak informatif.
- **38** `value = pow(base, odd_part, number)`.
- **39-40** jika `value` 1 atau `number-1`, basis ini lolos; lanjut ke basis berikut.
- **42-45** kuadratkan `value` hingga `powers_of_two - 1` kali; jika muncul
  `number-1`, lolos (`break`).
- **46-47** `for ... else`: bagian `else` jalan hanya jika loop tidak pernah `break`,
  artinya basis ini membuktikan angka itu komposit, maka `return False`.
- **49** semua basis lolos berarti `True` (prima).

Untuk 467: basis 2 menghasilkan `2^233 mod 467 = 466 = n-1`, jadi lolos di
baris 39-40.

### `crypto/elgamal.py` baris 52-68 `_validate_public_key`

- **55-56** public key harus tuple atau list berisi 3 elemen.
- **58** unpack `p, g, y`.
- **59-60** ketiganya `int` murni.
- **61-62** `p` harus lebih dari 256 **dan** prima. Lebih dari 256 karena
  byte dipetakan ke 1..256.
- **63-64** `1 < g < p`.
- **65-66** `1 <= y < p`.
- **68** mengembalikan `(p, g, y)`.

### `crypto/elgamal.py` baris 85-104 `encrypt`

- **90** validasi kunci sekaligus unpack.
- **91-92** `plaintext` harus string.
- **93-94** `validate_ehr` harus benar (tidak kosong).
- **96** `ciphertext = []`.
- **97** `for byte in text_to_bytes(plaintext)` — teks diubah ke bytes UTF-8, lalu
  diproses satu byte (angka 0..255) per putaran.
- **98** `ephemeral_key = secrets.randbelow(p - 2) + 1` — `k` acak baru untuk
  tiap byte, `1..p-2`.
- **99** `c1 = pow(g, ephemeral_key, p)` — rumus `c1 = g^k mod p`.
- **100** `message = byte + 1` — dipetakan ke 1..256 supaya tidak pernah 0.
- **101** `c2 = message * pow(public_value, ephemeral_key, p) % p` — rumus
  `c2 = m · y^k mod p`.
- **102** simpan pasangan `(c1, c2)`.
- **104** kembalikan list pasangan; panjangnya sama dengan jumlah byte.

### `utils/ehr_data.py` baris 10-26

- **10-12** `validate_ehr(text)` benar jika `text` string dan tidak kosong
  setelah `strip()`.
- **15-19** `text_to_bytes(text)`: tolak non-string (`TypeError`), lalu
  `text.encode("utf-8")`.
- **22-26** `bytes_to_text(data)`: tolak non-bytes, lalu `data.decode("utf-8")`.

UTF-8 membuat satu karakter bisa lebih dari satu byte (emoji 4 byte), jadi
jumlah blok ciphertext mengikuti jumlah byte, bukan jumlah karakter.

> Kalimat transisi: "Ciphertext sudah jadi. Selanjutnya dikirim dan
> ditampilkan sebagai apa yang bisa dilihat penyadap."

---

## [4] Transmisi dan tampilan ciphertext

### `app.py` baris 292-330 `GET /api/crypto/details`

- **296-297** ambil `dh` dan `ciphertext` dari state.
- **299-305** siapkan hasil awal dengan `p`, `g`, dan tiga slot kosong.
- **307-315** jika DH sudah jalan, isi public key klinik, public key rumah
  sakit, dan boolean cocok. Tidak ada secret.
- **317-320** jika kunci ElGamal ada, isi public key saja `(p, g, y)`.
- **322-325** jika ciphertext ada, ubah tiap pasangan menjadi list agar bisa di-JSON.
- **327-330** kirim response.

Private key tidak pernah dikirim; ini poin keamanan yang bisa disebut.

### `app.py` baris 337-353 `POST /api/ehr/transmit`

- **341-342** jika ciphertext belum ada, error "Encrypt EHR first.".
- **344** `state["transmitted"] = True` — satu-satunya yang terjadi. Transmisi
  hanya mengubah flag, bukan komunikasi jaringan nyata.
- **346-353** response sukses dengan ringkasan baru.

> Kalimat transisi: "Sekarang rumah sakit menerima ciphertext dan
> mendekripsinya dengan private key."

---

## [5] Dekripsi

### `app.py` baris 360-401

- **364-365** belum transmit berarti error "Transmit ciphertext first.".
- **367-368** private key tidak ada berarti error "Private key unavailable.".
- **371** lazy import `decrypt`.
- **373-376** `decrypt(state["ciphertext"], state["private_key"])`.
- **378-381** hasil harus string.
- **383** simpan ke `state["recovered"]`.
- **385-391** response: `recovered`, dan `verified` dengan nilai
  `recovered == state["ehr"]` (perbandingan teks penuh).
- **393-398** modul belum siap dijawab 409.
- **400-401** `ValueError`, `TypeError`, atau `UnicodeError` dijawab 400.

### `crypto/elgamal.py` baris 107-148 `decrypt`

- **112-113** private key harus tuple atau list isi 3 elemen.
- **115** unpack `p, g, private_value` (private_value adalah `x`).
- **116-117** ketiganya `int` murni.
- **118-119** `p` harus lebih dari 256 dan prima.
- **120-121** `1 < g < p`.
- **122-123** `1 <= x < p-1`.
- **124-125** ciphertext harus berupa list.
- **127** `plaintext_bytes = bytearray()` penampung byte hasil.
- **128** loop tiap pasangan ciphertext.
- **129-134** pasangan harus list atau tuple berisi 2 integer.
- **136** unpack `c1, c2`.
- **137-140** keduanya harus di `1..p-1`.
- **142** `shared_secret = pow(c1, private_value, p)` — rumus `s = c1^x mod p`.
  Nilainya sama dengan `y^k` pada saat enkripsi, karena `c1^x = g^(kx) = (g^x)^k`.
- **143** `message = c2 * pow(shared_secret, -1, p) % p` — rumus
  `m = c2 · s^(-1) mod p`. `pow(s, -1, p)` adalah invers modular bawaan
  Python. Faktor `y^k` di `c2` saling menghilangkan, tersisa `m`.
- **144-145** `m` harus di 1..256; kalau tidak, ciphertext rusak atau kunci salah,
  `ValueError("Ciphertext contains an invalid byte value.")`.
- **146** `plaintext_bytes.append(message - 1)` — membalik pemetaan `byte + 1`.
- **148** `bytes_to_text(bytes(plaintext_bytes))` — susun byte dan decode UTF-8
  menjadi teks asli.

Contoh angka untuk huruf `A` (`m = 66`) dengan `x=127`, `k=53`, `p=467`, `g=2`:

```text
y   = 2^127 mod 467 = 132
c1  = 2^53  mod 467 = 399
s   = 132^53 mod 467 = 358
c2  = 66 · 358 mod 467 = 278
dekripsi: s = 399^127 mod 467 = 358 ; invers 358 = 437
          278 · 437 mod 467 = 66 ; 66 - 1 = 65 = 'A'
```

> Kalimat transisi: "Untuk mengulang demo, ada fitur reset."

---

## [6] Reset dan menjalankan server

### `app.py` baris 408-422

- **408** `@app.post("/api/reset")`.
- **410** ambil state.
- **411** `state.clear()` kosongkan dict.
- **412** `state.update(empty_state())` isi lagi dengan nilai awal.
- **414-418** response sukses dengan ringkasan.
- **421-422** `app.run(debug=True, host="127.0.0.1", port=5000)` — hanya jalan
  jika file dijalankan langsung; alamat lokal, port 5000.

---

## [7] Fungsi matematika lain (`crypto/math_utils.py`)

Bagian ini jelaskan setelah alur utama, dengan jujur bahwa belum dipanggil
oleh DH atau ElGamal, tetapi merupakan bagian yang diuji dan didokumentasikan.

### `extended_gcd(a, b)` baris 34-57

Tujuan: menemukan `gcd` dan koefisien `x, y` sehingga `a·x + b·y = gcd`.

- **39-40** `a` dan `b` harus `int` murni.
- **42** `old_r, r = abs(a), abs(b)` — sisa bagi, dimulai dari nilai mutlak.
- **43** `old_x, x = 1, 0` dan **44** `old_y, y = 0, 1` — koefisien awal.
- **46** `while r != 0` — ulangi sampai sisa 0.
- **47** `quotient = old_r // r`.
- **48** `old_r, r = r, old_r - quotient * r` — langkah Euclid biasa.
- **49-50** koefisien `x` dan `y` diperbarui dengan rumus yang sama.
- **52-55** jika input negatif, balikkan tanda koefisien terkait.
- **57** kembalikan `(gcd, x, y)`.

Contoh `extended_gcd(3, 11)`:

| Putaran | quotient | old_r | r | old_x | x | old_y | y |
|---|---|---|---|---|---|---|---|
| awal | | 3 | 11 | 1 | 0 | 0 | 1 |
| 1 | 0 | 11 | 3 | 0 | 1 | 1 | 0 |
| 2 | 3 | 3 | 2 | 1 | -3 | 0 | 1 |
| 3 | 1 | 2 | 1 | -3 | 4 | 1 | -1 |
| 4 | 2 | 1 | 0 | 4 | -11 | -1 | 3 |

Hasil `(1, 4, -1)`, benar karena `3·4 + 11·(-1) = 1`.

### `mod_inverse(a, modulus)` baris 60-74

- **65-66** `a` dan `modulus` harus `int` murni.
- **67-68** `modulus` harus lebih dari 1.
- **70** `gcd, x, _ = extended_gcd(a, modulus)` — hanya koefisien `x` yang dipakai.
- **71-72** jika `gcd != 1`, invers tidak ada, `ValueError`.
- **74** `x % modulus` — normalisasi ke `0..modulus-1`.

`mod_inverse(3, 11) = 4` karena `3·4 = 12 ≡ 1 (mod 11)`.

### `is_prime(n)` baris 77-99

- **83-84** `n` harus `int`.
- **85-86** kurang dari 2 bukan prima.
- **87-88** 2 dan 3 prima.
- **89-90** kelipatan 2 atau 3 bukan prima.
- **93** `divisor = 5` — pembagi pertama yang dicek.
- **94** `while divisor * divisor <= n` — cukup sampai akar kuadrat `n`.
- **95-96** cek `divisor` (bentuk `6k-1`) dan `divisor + 2` (bentuk `6k+1`);
  kalau habis dibagi, bukan prima.
- **97** `divisor += 6` — lompat ke pasangan berikutnya.
- **99** tidak ada pembagi ditemukan berarti prima.

---

## [8] Versi CLI (`main.py`)

Logika kripto sama persis dengan web; yang beda hanya cara menyimpan state
(variabel lokal di fungsi `main()`, bukan `DEMO_STATES`).

- **16-19** `P = 467`, `G = 2` (terpisah dari `app.py`).
- **90-133** `perform_connection()`; **105** memanggil `perform_handshake(P, G)`.
- **136-172** `input_ehr()` menanyakan 5 field lalu menyusun string EHR yang
  formatnya sama dengan di `app.py`.
- **175-200** `encrypt_ehr()`; **191** memanggil `encrypt(ehr, public_key)`.
- **203-233** `show_transmission()` mencetak tiap blok `(c1, c2)`.
- **236-259** `decrypt_ehr()`; **246** memanggil `decrypt(ciphertext, private_key)`.
- **262** `main()` berisi loop menu:
  - **280** menu `1`: handshake; **287** `generate_keys(P, G)` membuat kunci
    ElGamal di sini (berbeda dari web yang membuatnya saat enkripsi).
  - **305** menu `2`: input dan enkripsi.
  - **325** menu `3`: lihat transmisi.
  - **336** menu `4`: dekripsi dan bandingkan dengan plaintext asli.
  - **362** menu `5`: reset semua variabel.
  - **375** menu `0`: keluar.

---

## Rumus yang perlu dihafal

```text
DH       A = g^a mod p      B = g^b mod p      S = B^a = A^b mod p
ElGamal  y  = g^x mod p
         c1 = g^k mod p     c2 = m · y^k mod p
         s  = c1^x mod p    m  = c2 · s^(-1) mod p
Pemetaan m = byte + 1       (karena itu p > 256)
```
