# Walkthrough Oryza & Aldo — Penjelasan Kode per Baris

Dokumen ini memakai format yang sama dengan [code-walkthrough.md](./code-walkthrough.md):
setiap baris kode dijelaskan beserta **alasan kenapa ditulis begitu**. Isinya
dibatasi pada bagian Oryza (Diffie-Hellman, Flask, frontend, CLI, integrasi) dan
bagian Aldo (math engine), karena Aldo tidak bisa ikut demo.

Nomor baris sesuai kondisi kode saat dokumen ini ditulis. Kalau file diedit,
nomornya bisa bergeser.

Peta:

```text
[1] Aldo  — crypto/math_utils.py        (fondasi matematika)
[2] Oryza — crypto/diffie_hellman.py    (pertukaran kunci)
[3] Oryza — app.py                      (backend web)
[4] Oryza — static/js/app.js            (logika frontend)
[5] Oryza — main.py                     (CLI)
[6] Oryza — templates/                  (tampilan)
[7] Kalau penguji bertanya bagian Aldo
```

Satu kalimat yang perlu diingat: bagian Aldo dan Oryza hanya tersambung lewat
**satu fungsi**, yaitu `mod_exp`. Tidak ada ketergantungan lain.

---

## [1] Aldo — `crypto/math_utils.py` (99 baris)

Modul ini berisi empat fungsi matematika. Yang benar-benar dipakai alur sistem
hanya `mod_exp` (oleh DH milik Oryza). Tiga lainnya adalah utilitas bersama yang
diuji ketat.

### `mod_exp(base, exponent, modulus)` — baris 10-31

**Kenapa fungsi ini ada.** DH dan ElGamal butuh `g^a mod p` dengan eksponen yang
bisa ratusan. Menghitung `2**465` dulu baru dimodulo akan membentuk bilangan
raksasa; `mod_exp` menghitung sambil terus memotong modulo supaya angkanya tetap
kecil.

- **10** `def mod_exp(base: int, exponent: int, modulus: int) -> int:` — tanda
  tipe `int` dipakai supaya pemanggil tahu kontraknya, dan supaya salah tipe
  ketahuan lebih awal.
- **11-15** docstring yang menyebut aturan main: eksponen non-negatif, modulus
  positif, modulus 1 menghasilkan 0, basis negatif dikecilkan dulu. Alasannya:
  perilaku batas (edge case) lebih baik ditulis di dekat fungsinya daripada
  hanya diuji.
- **16-17**
  ```python
  if any(type(value) is not int for value in (base, exponent, modulus)):
      raise TypeError("Base, exponent, and modulus must be integers.")
  ```
  **Kenapa `type(value) is not int`, bukan `not isinstance(value, int)`.**
  Karena di Python `bool` adalah turunan `int`: `isinstance(True, int)` bernilai
  `True`. Kalau memakai `isinstance`, `mod_exp(True, 2, 467)` akan lolos dan
  diam-diam dihitung sebagai `1`. Dengan `type(...) is not int`, `True` ditolak.
  Kasus ini diuji di `test_rejects_non_integer_arguments`.
- **18-19** `if exponent < 0: raise ValueError(...)` — eksponen negatif berarti
  invers; itu tugas `mod_inverse`, bukan fungsi ini. Menolak lebih jujur daripada
  mengembalikan hasil yang tidak dijanjikan.
- **20-21** `if modulus <= 0: raise ValueError(...)` — modulo 0 tidak
  terdefinisi. Modulus 1 sengaja diizinkan dan menghasilkan 0, sesuai sifat
  aritmetika modular.
- **23** `result = 1 % modulus` — hasil awal 1 (identitas perkalian). Ditulis
  `% modulus` supaya modulus 1 langsung menghasilkan 0, tanpa `if` tambahan.
- **24** `base %= modulus` — mengecilkan basis lebih dulu. Tanpa ini, basis
  negatif atau basis besar akan membuat perhitungan berikutnya membengkak.
- **25** `while exponent > 0` — ulangi selama masih ada bit.
- **26-27** `if exponent % 2 == 1: result = result * base % modulus` — bit
  terendah 1 berarti basis ikut dikalikan.
- **28** `base = base * base % modulus` — kuadratkan basis untuk bit berikutnya.
- **29** `exponent //= 2` — geser eksponen satu bit ke kanan.
- **31** `return result` — hasil akhir.

**Trace `mod_exp(2, 5, 467)`** (5 = biner `101`):

| Putaran | exponent | ganjil? | result | base |
|---|---|---|---|---|
| 1 | 5 | ya | 2 | 4 |
| 2 | 2 | tidak | 2 | 16 |
| 3 | 1 | ya | 32 | 256 |

Hasil 32. **Kenapa penting:** putarannya `log2(exponent)`, bukan `exponent`.
Untuk eksponen 465, ini hanya 9 putaran, bukan 465.

### `extended_gcd(a, b)` — baris 34-57

**Kenapa ada.** Untuk mencari invers modular, kita butuh koefisien Bezout:
bilangan `x, y` sehingga `a·x + b·y = gcd(a, b)`. Kalau `gcd = 1`, maka `x`
adalah invers dari `a` modulo `b`.

- **34** signature, mengembalikan `tuple[int, int, int]` = `(gcd, x, y)`.
- **35-38** docstring: gcd selalu non-negatif, input negatif dan nol didukung,
  `(0, 0)` menghasilkan `(0, 1, 0)`.
- **39-40** `if type(a) is not int or type(b) is not int` — alasan sama dengan
  `mod_exp`: menolak `bool` dan tipe lain.
- **42** `old_r, r = abs(a), abs(b)` — **kenapa `abs`?** Supaya sisa pembagian
  selama loop selalu non-negatif, sehingga satu-satunya penyesuaian tanda cukup
  dilakukan sekali di akhir (baris 52-55). Kalau tidak, tanda bisa berubah di
  tengah loop dan sulit dilacak.
- **43-44** `old_x, x = 1, 0` dan `old_y, y = 0, 1` — nilai awal koefisien,
  dipilih supaya identitas `a·1 + b·0 = a` dan `a·0 + b·1 = b` berlaku.
- **46** `while r != 0` — berhenti saat sisa nol; saat itu `old_r` adalah gcd.
- **47** `quotient = old_r // r` — pembagian bulat, langkah Euclid.
- **48** `old_r, r = r, old_r - quotient * r` — algoritma Euclid biasa.
- **49-50** `old_x, ...` dan `old_y, ...` diperbarui dengan rumus yang sama.
  **Kenapa iterative, bukan rekursif?** Input bisa ribuan bit; rekursi berisiko
  melebihi batas kedalaman Python.
- **52-55** `if a < 0: old_x = -old_x` dan `if b < 0: old_y = -old_y` —
  mengembalikan tanda koefisien sesuai tanda input, karena sebelumnya dipaksa
  positif oleh `abs`.
- **57** `return old_r, old_x, old_y`.

**Trace `extended_gcd(3, 11)`:**

| Putaran | quotient | old_r | r | old_x | x | old_y | y |
|---|---|---|---|---|---|---|---|
| awal | | 3 | 11 | 1 | 0 | 0 | 1 |
| 1 | 0 | 11 | 3 | 0 | 1 | 1 | 0 |
| 2 | 3 | 3 | 2 | 1 | -3 | 0 | 1 |
| 3 | 1 | 2 | 1 | -3 | 4 | 1 | -1 |
| 4 | 2 | 1 | 0 | 4 | -11 | -1 | 3 |

Hasil `(1, 4, -1)`, benar karena `3·4 + 11·(-1) = 12 - 11 = 1`.

### `mod_inverse(a, modulus)` — baris 60-74

**Kenapa ada.** Rumus dekripsi ElGamal butuh `s^(-1) mod p`, dan invers modular
hanya ada kalau `gcd(a, modulus) = 1`.

- **65-66** cek tipe murni `int`.
- **67-68** `if modulus <= 1: raise ValueError` — modulus 1 tidak punya grup
  perkalian yang bermakna; modulus 0 tidak terdefinisi.
- **70** `gcd, x, _ = extended_gcd(a, modulus)` — **kenapa memakai
  `extended_gcd`, bukan `pow(a, -1, modulus)`?** Tugas matematika ini
  mensyaratkan implementasi manual. `pow` baru dipakai ElGamal (modul lain),
  bukan di sini.
- **71-72** `if gcd != 1: raise ValueError(...)` — kalau tidak koprima, invers
  tidak ada. Lebih baik gagal jelas daripada mengembalikan angka salah.
- **74** `return x % modulus` — **kenapa `% modulus`?** Karena koefisien Bezout
  bisa negatif; `%` menormalkannya ke rentang `0..modulus-1`.

Contoh: `mod_inverse(3, 11) = 4` karena `3·4 = 12 ≡ 1 (mod 11)`.

### `is_prime(n)` — baris 77-99

**Kenapa ada.** Untuk memeriksa apakah kandidat modulus benar-benar prima,
karena ElGamal butuh modulus prima agar invers selalu ada.

- **82-83** docstring jujur: trial division hanya cocok untuk parameter
  demonstrasi kecil, **tidak** untuk bilangan seukuran kriptografi nyata.
- **83-84** `if type(n) is not int: raise TypeError` — konsisten dengan dua
  fungsi sebelumnya.
- **85-86** `if n < 2: return False` — 0 dan 1 bukan prima.
- **87-88** `if n in (2, 3): return True` — dua prima terkecil, ditangani
  langsung.
- **89-90** `if n % 2 == 0 or n % 3 == 0: return False` — membuang semua
  kelipatan 2 dan 3 sekaligus.
- **92** komentar: setiap prima > 3 berbentuk `6k-1` atau `6k+1`.
- **93** `divisor = 5` — pembagi pertama yang perlu diuji setelah 2 dan 3.
- **94** `while divisor * divisor <= n` — **kenapa sampai akar kuadrat?** Kalau
  `n = a × b` dengan `a ≤ b`, maka `a ≤ √n`. Jadi bila tidak ada pembagi sampai
  `√n`, `n` pasti prima.
- **95-96** `if n % divisor == 0 or n % (divisor + 2) == 0: return False` —
  menguji pasangan `6k-1` dan `6k+1`.
- **97** `divisor += 6` — lompat ke pasangan berikutnya. Efeknya hanya 2 dari
  setiap 6 angka yang diuji, bukan semua.
- **99** `return True` — tidak ada pembagi ditemukan, berarti prima.

**Kenapa tidak dipakai DH maupun ElGamal?** `crypto/elgamal.py` (Erlinda)
memakai `_is_probable_prime` (Miller-Rabin) miliknya sendiri. DH milik Oryza
belum memvalidasi primalitas `p` sama sekali. Ini tercatat sebagai tindak lanjut
di `docs/math-engine.md`, dan `is_prime` tetap dipakai pada
`test_manual_elgamal_round_trip_with_math_engine`.

> Kalimat transisi: "Modul matematika selesai. Fungsi `mod_exp` dari Aldo
> sekarang dipakai DH milik Oryza."

---

## [2] Oryza — `crypto/diffie_hellman.py` (93 baris)

**Tujuan modul.** Dua pihak (klinik dan rumah sakit) menghasilkan nilai rahasia
yang sama tanpa pernah mengirimkannya.

### `generate_dh_keys(p, g)` — baris 12-40

- **12-15** signature, mengembalikan `(private_key, public_key)`. **Kenapa
  urutannya private dulu?** Karena pemanggil biasanya langsung memisahkan
  keduanya, dan urutan ini konsisten dengan kontrak di `CONTRIBUTING.md`.
- **16-25** docstring berisi format argumen dan return.
- **26-27** `if p <= 3: raise ValueError(...)` — modulus terlalu kecil membuat
  ruang nilai tidak bermakna.
- **29-30** `if not 1 < g < p: raise ValueError(...)` — generator harus elemen
  grup; `g = 0`, `1`, atau `p` membuat public key selalu 0 atau 1.
- **32** `for _ in range(1000):` — **kenapa ada perulangan?** Ini bagian dari
  perbaikan bug. Sebelumnya kunci dibuat sekali saja; kalau public key jatuh di
  `1` atau `p-1`, `compute_shared_secret` menolaknya dan handshake gagal.
- **33** `private_key = secrets.randbelow(p - 3) + 2` — `randbelow(n)`
  menghasilkan `0..n-1`, jadi hasil akhirnya `2..p-2`. **Kenapa `secrets`, bukan
  `random`?** `random` dapat diprediksi dari seed; `secrets` memakai sumber acak
  sistem yang dirancang untuk kriptografi.
- **34** `public_key = mod_exp(g, private_key, p)` — rumus `A = g^a mod p`.
  **Di baris inilah `mod_exp` milik Aldo dipakai.**
- **36-38** `if 2 <= public_key <= p - 2: return private_key, public_key` —
  hanya mengembalikan public key yang bisa diterima `compute_shared_secret`.
- **40** `raise ValueError(...)` — kalau 1000 percobaan gagal semua, berarti
  generator memang tidak menghasilkan nilai valid; lebih baik gagal jelas.

**Kisah bug ini, untuk diceritakan saat demo.** Dengan `p = 467, g = 2`, private
key `233` menghasilkan `public_key = 466 = p-1`. Dulu baris 32 tidak ada
(perulangan), jadi handshake gagal. Peluangnya sekitar 0,43% per handshake;
terukur 74 kegagalan dari 20.000 percobaan sebelum perbaikan, dan 0 dari 20.000
sesudahnya. Regression test ada di `tests/test_dh.py`.

### `compute_shared_secret(peer_public_key, private_key, p)` — baris 43-57

- **43-47** signature dan docstring.
- **51-52** `if not 2 <= peer_public_key <= p - 2: raise ValueError(...)` —
  **kenapa divalidasi lagi?** Karena di skenario nyata public key lawan datang
  dari jaringan dan bisa saja `1`, `p-1`, atau `0` (nilai yang mematikan sifat
  rahasia bersama). Fungsi ini adalah batas kepercayaan.
- **54-55** `if not 2 <= private_key <= p - 2: raise ValueError(...)` —
  melindungi dari pemanggilan langsung dengan private key di luar rentang.
- **57** `return mod_exp(peer_public_key, private_key, p)` — rumus
  `S = B^a mod p`. **Pemakaian `mod_exp` kedua.**

### `perform_handshake(p, g)` — baris 60-93

- **60-67** signature dan docstring.
- **68** `clinic_private, clinic_public = generate_dh_keys(p, g)` — pihak klinik.
- **70** `hospital_private, hospital_public = generate_dh_keys(p, g)` — pihak
  rumah sakit. **Kenapa digabung dalam satu fungsi?** Karena ini simulasi;
  memisahkan dua proses hanya akan menyulitkan demo tanpa menambah pemahaman.
- **72-76** klinik menghitung `clinic_secret` dari public key rumah sakit.
- **78-82** rumah sakit menghitung `hospital_secret` dari public key klinik.
- **84-85** `if clinic_secret != hospital_secret: raise RuntimeError(...)` —
  **kenapa `RuntimeError`, bukan `ValueError`?** Karena ini bukan kesalahan
  input, melainkan kegagalan proses yang seharusnya mustahil secara matematis.
  Kalau terjadi, ada bug implementasi.
- **87-93** mengembalikan dict berisi kedua public key, kedua secret, dan
  `success`. **Kenapa secret ikut dikembalikan padahal rahasia?** Supaya demo
  bisa membandingkan keduanya dan membuktikan `S_A = S_B`. Di `app.py` baris
  203-206, nilai secret tidak dikirim ke browser — hanya boolean hasil
  bandingannya.

Contoh angka: `a=5, b=7` → `A=32`, `B=128`, keduanya menghasilkan `S=416`.
Dasarnya `(g^b)^a = g^(ab) = (g^a)^b`.

> Kalimat transisi: "DH siap. Sekarang bagian Oryza yang paling besar: backend
> Flask yang menghubungkan semua modul dan melayani browser."

---

## [3] Oryza — `app.py` (422 baris)

### Persiapan — baris 1-13

- **1** `import secrets` — dipakai untuk `secret_key` dan id sesi.
- **2-5** `from flask import (Flask, render_template, request, jsonify, session)` —
  lima alat: aplikasi, render HTML, baca request, buat JSON, simpan cookie sesi.
- **7** `app = Flask(__name__)` — objek aplikasi.
- **8** `app.secret_key = secrets.token_bytes(32)` — **kenapa dibuat acak tiap
  start, bukan string tetap?** Karena kunci ini menandatangani cookie sesi;
  kalau tetap dan bocor, orang bisa memalsukan sesi. Efek sampingnya: setelah
  server restart, cookie lama tidak valid dan pengguna otomatis mendapat sesi
  kosong — justru membantu saat demo.
- **11-12** `P = 467`, `G = 2` — parameter demo. Alasan lengkapnya di
  [code-walkthrough.md bagian 0.5](./code-walkthrough.md#05-mengapa-p-467-dan-g-2):
  467 prima, `> 256`, safe prime, dan 2 primitive root berorde penuh 466.
- **13** `DEMO_STATES = {}` — **kenapa dict di memori, bukan database?** Karena
  ini simulasi satu mesin. Konsekuensinya harus disebut jujur: tidak persisten,
  hilang saat restart, dan tidak cocok untuk banyak worker.

### State per pengguna — baris 16-36

- **16-25** `empty_state()` mengembalikan tujuh slot: `ehr`, `dh`,
  `public_key`, `private_key`, `ciphertext`, `transmitted`, `recovered`.
  **Kenapa dipisah jadi fungsi, bukan literal berulang?** Supaya reset di baris
  412 punya satu sumber kebenaran.
- **28** `def get_state():` — dipanggil di awal hampir semua endpoint.
- **29** `sid = session.get("demo_id")` — ambil id dari cookie; `None` jika baru.
- **31** `if sid not in DEMO_STATES:` — **kenapa cek ke dict, bukan langsung
  percaya cookie?** Karena isi cookie hanya ditandatangani, bukan dienkripsi.
  Kalau id valid secara tanda tangan tapi tidak ada di server (misal setelah
  restart), state baru harus dibuat.
- **32-34** buat id acak, simpan ke cookie, buat state kosong.
- **36** `return DEMO_STATES[sid]` — **mengembalikan dict yang sama, bukan
  salinan.** Ini disengaja: endpoint mengubah dict itu langsung sehingga
  perubahannya tersimpan tanpa perlu `save()`.

### Fungsi pembantu — baris 39-60

- **39-44** `api_error(message, code=400, kind="error")` — **kenapa pakai
  pembantu?** Supaya semua error punya bentuk sama
  (`success/message/kind`), dan frontend bisa menampilkan `message` apa adanya.
- **47-60** `summary(state)` — mengubah state menjadi ringkasan.
  **Kenapa ada?** Browser tidak perlu (dan tidak boleh) tahu isi state penuh.
  - **51-55** lima boolean status
  - **56** `block_count`
  - **57-59** metadata algoritma
  - **Private key tidak pernah masuk ringkasan ini.** Ini keputusan keamanan
    yang bisa disebut saat presentasi.

### Empat halaman — baris 67-84

- **67-84** `dashboard()`, `clinic()`, `cryptography()`, `hospital()` —
  masing-masing hanya `render_template`. **Kenapa logika tidak ditaruh di
  sini?** Supaya halaman tetap ringan dan semua logika ada di API; halaman
  cukup jadi kerangka yang diisi `app.js`.

### `GET /api/status` — baris 91-98

- **93** `state = get_state()` — panggilan pertama inilah yang melahirkan sesi
  saat browser pertama kali membuka aplikasi.
- **95-98** mengembalikan `summary(state)`.

### `POST /api/ehr/prepare` — baris 105-167

- **108** `data = request.get_json(silent=True)` — **kenapa `silent=True`?**
  Supaya body JSON rusak menghasilkan `None` yang bisa dijawab rapi, bukan
  exception 400 bawaan Flask dengan halaman HTML.
- **110-111** bukan dict → tolak.
- **113-119** daftar lima field wajib.
- **123** loop tiap field.
- **124** `str(data.get(field, "")).strip()` — **kenapa `str(...)`?** Supaya
  angka atau `None` dari JSON tidak membuat `.strip()` gagal.
- **126-129** kosong → tolak. **131-134** lebih dari 200 karakter → tolak
  (membatasi ukuran ciphertext dan mencegah input aneh).
- **138-141** `int(values["age"])` dengan `try` (baris 138 adalah `try:`,
  baris 139 yang memanggil `int`) — **kenapa tidak `str.isdigit()`?** Karena
  `isdigit()` menerima angka unicode seperti `²`, sedangkan `int()` menolak
  dengan jelas.
- **143-144** rentang umur `0..130` — validasi wajar untuk data pasien.
- **146-152** menyusun satu string lima baris. **Kenapa digabung jadi satu
  teks, bukan disimpan sebagai dict?** Karena yang dienkripsi adalah dokumen;
  mempertahankan bentuk dokumen membuat demo mudah dibaca dan verifikasi cukup
  membandingkan string penuh.
- **154** `state["ehr"] = ehr`.
- **156-159** mengosongkan `ciphertext`, `transmitted`, `recovered` —
  **kenapa?** Data baru membuat enkripsi lama tidak berlaku. `dh` dan kunci
  ElGamal sengaja tidak dihapus agar pengguna tidak perlu handshake ulang.
- **161-167** response: `preview`, `bytes`, `data`.

### `POST /api/crypto/handshake` — baris 174-219

- **179** `from crypto.diffie_hellman import perform_handshake` — **kenapa
  impor di dalam fungsi?** Supaya kalau modul kripto belum siap,
  `ImportError`/`NotImplementedError` bisa ditangkap (baris 214-219) dan
  dijawab `409 module_pending`, bukan membuat seluruh server gagal start.
- **181** `result = perform_handshake(P, G)`.
- **183-184** cek `success`.
- **186** `state["dh"] = result`.
- **188-193** mengosongkan kunci ElGamal, ciphertext, `transmitted`,
  `recovered` — sesi kripto baru berarti semua turunan lama dibuang.
- **195-212** response. **Perhatikan baris 206-209:** yang dikirim hanya
  `shared_secret_match` (boolean), bukan nilai secret. Ini yang membedakan
  demo edukasi dari kebocoran.
- **214-219** `ImportError`/`NotImplementedError` → 409.
- **221-222** `ValueError`/`RuntimeError` → 400.

### `POST /api/crypto/encrypt` — baris 226-285

- **230-231** HTTP 400 "Prepare EHR data first." — **kenapa dicek di backend,
  padahal tombol sudah dinonaktifkan?** Karena tombol di browser bisa diakali
  lewat DevTools atau `curl`. Backend adalah penjaga sebenarnya.
- **233-236** DH harus sudah dilakukan.
- **239** lazy import `generate_keys` dan `encrypt` (modul Erlinda).
- **242** `generate_keys(P, G)` — kunci dibuat di sini, **beda dengan CLI yang
  membuatnya di menu 1**.
- **244-247** `encrypt(state["ehr"], public_key)`.
- **249-252** hasil harus `list`. **255-262** tiap item harus pasangan dua
  `int`. **Kenapa diperiksa lagi?** Karena `encrypt` adalah modul milik anggota
  lain; kontraknya perlu dijaga di batas modul.
- **264-268** simpan `public_key`, `private_key`, `ciphertext`; reset
  `transmitted` dan `recovered`.
- **270-275** response berisi `block_count`.
- **277-282** modul belum siap → 409. **284-285** `ValueError`/`TypeError` → 400.

### `GET /api/crypto/details` — baris 292-330

- **296-297** ambil `dh` dan `ciphertext`.
- **299-305** kerangka hasil.
- **307-315** isi data DH **tanpa secret**.
- **317-320** `if state["public_key"] is not None: ...` — hanya public key
  `(p, g, y)`. **Private key tidak pernah keluar**; ini alasan endpoint ini
  aman dipanggil kapan saja.
- **322-325** ciphertext diubah ke list supaya bisa di-JSON.
- **327-330** response.

### `POST /api/ehr/transmit` — baris 337-353

- **341-342** wajib sudah enkripsi.
- **344** `state["transmitted"] = True` — **satu-satunya yang terjadi.**
  **Kenapa tidak ada jaringan sungguhan?** Karena ini simulasi lokal; README
  dan UI menyebutnya eksplisit agar tidak menyesatkan.
- **346-353** response dengan ringkasan baru.

### `POST /api/ehr/decrypt` — baris 360-401

- **364-365** wajib sudah transmit — **ini yang membuat urutan demo tidak bisa
  dilompati**.
- **367-368** private key harus ada.
- **371** lazy import `decrypt`.
- **373-376** `decrypt(state["ciphertext"], state["private_key"])`.
- **378-381** hasil harus `str`.
- **383** simpan `recovered`.
- **385-391** response, dengan **389** `"verified": recovered == state["ehr"]`.
  **Kenapa membandingkan string penuh?** Karena itu bukti round-trip berhasil:
  teks yang sama persis, bukan sekadar mirip.
- **393-398** modul belum siap → 409. **400-401** `ValueError`/`TypeError`/
  `UnicodeError` → 400. **Kenapa `UnicodeError` ikut ditangkap?** Karena byte
  hasil dekripsi bisa tidak valid sebagai UTF-8 bila ciphertext diubah.

### `POST /api/reset` dan menjalankan server — baris 408-422

- **411-412** `state.clear()` lalu `state.update(empty_state())` — **kenapa
  tidak `state = empty_state()`?** Karena `get_state()` mengembalikan referensi
  dict yang sama; mengganti variabel lokal tidak akan mengubah isi
  `DEMO_STATES`. `clear()` + `update()` mengubah dict di tempat.
- **414-418** response.
- **421-422** `app.run(debug=True, host="127.0.0.1", port=5000)` — hanya jalan
  bila file dieksekusi langsung. `debug=True` memudahkan saat demo, tetapi
  **tidak boleh** di produksi karena membocorkan detail error.

> Kalimat transisi: "Backend siap. Sekarang sisi browser yang memanggil API
> tersebut."

---

## [4] Oryza — `static/js/app.js` (570 baris)

### `apiRequest(url, method, data)` — baris 21-61

- **21** signature dengan nilai default `"GET"` dan `data = null`.
- **22-27** menyusun `options` dengan header `Accept`.
- **29-32** kalau ada data, tambahkan `Content-Type` dan `JSON.stringify`.
- **36-42** `try { response = await fetch(...) } catch` — **kenapa ditangkap
  terpisah?** Supaya pesan "tidak bisa konek ke server" (server mati) berbeda
  dari "respons tidak valid" (server hidup tapi balasannya aneh).
- **46-52** parsing JSON dengan `try/catch` sendiri.
- **54-58** `if (!response.ok || !result.success) throw new Error(result.message)` —
  **kenapa dua syarat?** `response.ok` menangkap kode HTTP 4xx/5xx, sedangkan
  `result.success` menangkap kegagalan logika yang dikirim dengan status 200.
- **60** `return result` — pemanggil menerima objek JSON yang sudah pasti sukses.

### `setText` dan `showToast` — baris 64-89

- **64-70** `setText(id, value)` — **kenapa ada pengecekan `if (element)`?**
  Karena satu file JS dipakai di empat halaman; elemen yang tidak ada harus
  dilewati, bukan bikin error.
- **73-89** `showToast` membuat `<div>`, mengisi `textContent`, memberi
  `role="status"` (aksesibilitas), lalu `setTimeout` menghapusnya setelah 4,5
  detik. **Kenapa `textContent`, bukan `innerHTML`?** Karena pesan bisa berasal
  dari server; `textContent` mencegah injeksi HTML.

### `runAction(button, action)` — baris 92-102

- **93** `button.disabled = true` — mencegah klik ganda saat menunggu respons.
- **95-98** `try { await action() } catch (error) { showToast(error.message, "error") }` —
  **titik pusat penanganan error**: setiap kegagalan API otomatis muncul sebagai
  toast.
- **99-101** `finally { button.disabled = false }` — **kenapa di `finally`?**
  Supaya tombol tetap menyala kembali walaupun aksinya gagal.

### `loadStatus` dan `renderStatus` — baris 109-241

- **109-116** `loadStatus()` memanggil `/api/status`, menyimpan ke `currentStatus`.
- **121-136** mengisi empat metrik dashboard.
- **139-163** workflow empat tahap. **Perhatikan baris 142-145:** tahap ketiga
  baru tercentang bila `encrypted && transmitted` — **kenapa digabung?** Karena
  di UI tahap 3 adalah "Encrypt & Transmit".
- **149-163** loop yang menambahkan class `completed` dan mengganti indikator
  `○`/`✓`.
- **222-240** aturan tombol. **Kenapa aturan ini ada di frontend juga, padahal
  backend sudah menjaga?** Karena frontend untuk kenyamanan (pengguna tidak
  mencoba hal mustahil), backend untuk keamanan. Dua lapis, bukan duplikasi
  yang sia-sia.

### `renderDocument(id, text)` — baris 248-262

- **253** `container.replaceChildren()` — membersihkan isi lama.
- **255-256** membuat `<pre>` baru.
- **259** `pre.textContent = text` — mencegah injeksi.
- **261** memasang ke container.

### `setupClinic()` — baris 269-320

- **270-273** ambil elemen; kalau tidak ada (bukan halaman clinic), berhenti.
- **275-283** tombol *Use Sample Data* mengisi lima field contoh, lalu toast.
- **285-286** `event.preventDefault()` — **kenapa?** Supaya submit tidak
  me-reload halaman; data dikirim lewat `fetch`.
- **288** `form.reportValidity()` — memakai validasi HTML5 bawaan browser.
- **292-318** `runAction` membungkus: kumpulkan nilai dengan `.trim()`, kirim
  POST, render preview, perbarui status, tampilkan toast berisi jumlah byte.

### `refreshCryptoDetails()` — baris 327-378

- **328** kalau elemen `ciphertextOutput` tidak ada, berarti bukan halaman
  cryptography — berhenti.
- **336-352** isi `p`, `g`, dan kedua public key; kalau DH belum jalan, isi `—`.
- **356-362** kalau belum ada ciphertext, tampilkan pesan menunggu.
- **364-377** menyusun header lalu satu baris per blok dengan
  `padStart(3, "0")` supaya nomornya rata.

### `setupCryptography()` — baris 381-433

- **382-386** ambil tiga tombol; berhenti kalau bukan halaman ini.
- **388-402** handshake → perbarui status → `refreshCryptoDetails()` → toast.
- **404-418** encrypt → sama, ditambah jumlah blok yang muncul di terminal.
- **420-432** transmit → hanya status dan toast. **Kenapa tidak memanggil
  `refreshCryptoDetails()`?** Karena ciphertext tidak berubah, hanya flag.

### `setupHospital()` — baris 440-485

- **447-450** `POST /api/ehr/decrypt`.
- **452-455** tampilkan teks hasil dekripsi.
- **457-472** label verifikasi: "Record Matches" atau "Record Mismatch",
  dengan class `success`/`error`. **Kenapa class dihapus dulu baru ditambah?**
  Supaya tidak menumpuk class dari percobaan sebelumnya.
- **474-482** perbarui status dan tampilkan toast sesuai hasil verifikasi.

### `setupNavigation()` — baris 492-547

- **493-498** tombol ☰ untuk membuka sidebar di layar kecil.
- **503-508** `confirm()` sebelum reset — mencegah klik tidak sengaja.
- **511-514** `POST /api/reset`.
- **519-542** membersihkan tampilan lokal: form, preview EHR, preview
  dekripsi, label verifikasi, dan panel ciphertext.

### Inisialisasi — baris 554-570

- **555-558** memasang empat `setup*` — **kenapa semua dipanggil?** Karena
  fungsi masing-masing sudah punya penjaga elemen, jadi aman dipanggil di
  halaman mana pun.
- **560-565** `loadStatus()` lalu `refreshCryptoDetails()` di dalam `try`,
  supaya kegagalan awal (misal server mati) muncul sebagai toast, bukan layar
  kosong.
- **567-569** log inisialisasi.

> Kalimat transisi: "Web selesai. Versi terminal memakai logika kripto yang
> sama."

---

## [5] Oryza — `main.py` (406 baris)

- **16-19** `# Educational parameters only.` lalu `P = 467`, `G = 2`.
  **Kenapa didefinisikan ulang, bukan diimpor dari `app.py`?** Supaya CLI bisa
  jalan tanpa memuat Flask. Konsekuensinya: kalau parameter diubah, harus
  diubah di dua tempat — ini keterbatasan yang perlu disebut.
- **22-29** `class Colors` berisi kode ANSI. **Kenapa?** Agar tahapan demo
  mudah dibedakan warna di terminal.
- **32-33** `colorize(text, color)` membungkus teks dengan kode warna lalu
  `RESET` — **kenapa `RESET` penting?** Tanpa itu, warna akan bocor ke teks
  berikutnya.
- **36-37** `divider()` mencetak 65 tanda `-`.
- **40-51** `show_header()` mencetak judul aplikasi.
- **54-78** `show_menu(connected, encrypted)` menerima dua status supaya
  tampilan menu mencerminkan keadaan. **Kenapa parameter, bukan variabel
  global?** Supaya ketergantungan jelas.
- **81-83** `pause()` menunggu Enter agar pengguna sempat membaca output.
- **85-87** `simulate_loading(message)` mencetak lalu `time.sleep(0.6)` —
  **kenapa ada jeda buatan?** Supaya tahapan terasa berurutan saat presentasi.
  Ini murni kosmetik, bukan bagian kriptografi.
- **90-133** `perform_connection()`:
  - **105** `result = perform_handshake(P, G)` — memakai fungsi yang sama
    dengan web.
  - **118-125** menampilkan public key kedua pihak dan shared secret.
  - **127-130** mencetak peringatan bahwa DH tidak terautentikasi —
    **kejujuran ini penting**, karena DH tanpa autentikasi rentan MITM.
- **136-172** `input_ehr()`:
  - **144-148** menanyakan lima field.
  - **158-159** semua field wajib terisi.
  - **161-162** umur harus angka `0..130`.
  - **164-170** menyusun string dengan format **sama persis** seperti `app.py`,
    supaya hasil demo CLI dan web bisa dibandingkan.
- **175-200** `encrypt_ehr()`:
  - **187** `print(f"Original data size : {len(encoded)} bytes")` mencetak
    ukuran asli dalam byte.
  - **191** `ciphertext = encrypt(ehr, public_key)`.
  - **198** mencetak jumlah blok.
- **203-233** `show_transmission()` mencetak setiap blok `(c1, c2)` dengan
  nomor tiga digit, meniru "apa yang dilihat penyadap".
- **236-259** `decrypt_ehr()`:
  - **246** `recovered = decrypt(ciphertext, private_key)`.
  - **251-257** mencetak hasil.
- **262-380** `main()`:
  - **270-277** variabel state disimpan sebagai variabel lokal — **beda dengan
    web yang memakai dict**. Alasannya: CLI satu pengguna, satu proses.
  - **280** menu `1`: handshake, lalu **287** `generate_keys(P, G)` membuat
    kunci ElGamal. **Kenapa di menu 1?** Karena di CLI kunci disiapkan
    bersamaan dengan sesi, sedangkan di web kunci dibuat saat enkripsi.
  - **305** menu `2`: input dan enkripsi; state lama direset.
  - **325** menu `3`: tampilkan transmisi.
  - **336** menu `4`: dekripsi, lalu **352-358** membandingkan dengan plaintext
    asli dan mencetak `[VERIFIED]` atau `[WARNING]`.
  - **362** menu `5`: reset semua variabel.
  - **375** menu `0`: keluar.
  - **388-392** penanganan `NotImplementedError` (modul belum siap).
  - **394-398** penanganan `ValueError`/`UnicodeError` (input salah).
  - **400-402** `except KeyboardInterrupt` — **kenapa ditangkap?** Supaya Ctrl+C
    keluar rapi, bukan menampilkan traceback.

---

## [6] Oryza — `templates/` (5 file)

- **`base.html`** — kerangka: sidebar, topbar, footer, dan pemuatan `app.js`
  dengan `defer`. **Kenapa `defer`?** Supaya script dieksekusi setelah HTML
  selesai diparse, sehingga elemen sudah tersedia.
  - Body diberi `data-page="{{ request.endpoint }}"` — penanda halaman aktif.
  - Bootstrap dimuat dari CDN. **Risiko yang harus disebut:** tanpa internet,
    tampilan akan berantakan.
- **`dashboard.html`** — metrik (`metricConnection`, `metricBlocks`, dst.) dan
  workflow empat kartu (`workflowPrepared`, ...). Id ini harus cocok dengan
  yang dipakai `app.js` baris 121-163.
- **`clinic.html`** — form `ehrForm` dengan lima field, `maxlength="200"`,
  dan `min/max` umur. Id `prepareButton` dan `fillDemoData` dipakai `app.js`.
  Panel preview memakai `ehrPreview`.
- **`cryptography.html`** — panel DH (`dhPrime`, `clinicPublic`, `dhResult`),
  panel ElGamal (`encryptButton`, `encryptedBlockCount`), dan terminal
  `ciphertextOutput` + `transmitButton`.
- **`hospital.html`** — status (`hospitalTransmission`, `hospitalBlockCount`,
  `hospitalDecryption`), tombol `decryptButton`, panel `decryptedPreview`, dan
  label `verificationStatus`.

**Kenapa semua id ini penting?** `app.js` mengambil elemen berdasarkan id.
Salah ketik satu id berarti fitur itu diam-diam tidak jalan (karena penjaga
`if (!element) return`). Saat demo, kalau satu tombol tidak bereaksi, cek id-nya
di template dulu.

---

## [7] Kalau penguji bertanya bagian Aldo

Aldo tidak bisa ikut demo, jadi bagian ini yang mewakili. Jawaban singkat yang
bisa dipakai:

**"Apa yang dikerjakan Aldo?"**
`crypto/math_utils.py`: `mod_exp` (square-and-multiply), `extended_gcd`,
`mod_inverse`, dan `is_prime` (trial division `6k±1`), plus pengujiannya di
`tests/test_math.py` dan dokumentasi `docs/math-engine.md`.

**"Bagaimana bagiannya tersambung dengan punyamu?"**
Lewat satu fungsi: `mod_exp`. `crypto/diffie_hellman.py` baris 9 mengimpornya,
lalu memakainya di baris 34 (public key) dan baris 57 (shared secret). Tidak ada
ketergantungan lain.

**"Kenapa `mod_exp` penting?"**
Karena menghitung `g^a mod p` dengan eksponen ratusan secara langsung akan
membentuk bilangan raksasa. Square-and-multiply menekan jumlah operasi menjadi
`log2(eksponen)` dan menjaga angka tetap kecil dengan modulo di setiap langkah.

**"Kenapa ElGamal tidak memakai `mod_inverse` dan `is_prime` Aldo?"**
Karena `elgamal.py` milik Erlinda sudah lulus pengujian dengan `pow()` dan
Miller-Rabin sendiri. Mengubahnya butuh koordinasi sesuai aturan kepemilikan
modul di `CONTRIBUTING.md`. Ini dicatat di `docs/math-engine.md`.

**"Apa yang belum selesai dari math engine?"**
`is_prime` dan `mod_inverse` belum dipanggil alur produksi; keduanya utilitas
bersama yang diuji. DH juga belum memvalidasi primalitas `p` dan orde `g` —
itu tindak lanjut modul DH milik Oryza, bukan Aldo.

**"Kalau `mod_exp` salah, apa efeknya?"**
Seluruh DH dan setiap perhitungan ElGamal akan salah, karena keduanya memakai
eksponensiasi modular. Karena itu `tests/test_math.py` membandingkan `mod_exp`
dengan `pow()` Python untuk ratusan kombinasi, termasuk eksponen 2048 bit.
