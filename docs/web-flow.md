# Web Flow — Cara Kerja Aplikasi Web Erdoza HealthCrypt

Dokumen ini menjelaskan alur web dari sisi request: kamu klik apa, browser
memanggil apa, backend menjalankan apa, state berubah jadi apa, lalu UI update
bagaimana. Nomor baris `app.py` dan `static/js/app.js` sesuai kondisi kode saat
dokumen ini ditulis.

Untuk penjelasan kode per baris bagian kripto, lihat
[code-walkthrough.md](./code-walkthrough.md).

---

## Peta singkat

```text
Browser (app.js)                       Server (Flask)
----------------                       --------------
GET  /api/status            -------->
                                        get_state() -> buat sesi bila baru
                                        summary(state)
                            <--------    JSON: prepared/connected/...

POST /api/ehr/prepare       -------->   validasi -> state["ehr"]
POST /api/crypto/handshake  -------->   perform_handshake(467,2) -> state["dh"]
POST /api/crypto/encrypt    -------->   generate_keys + encrypt -> ciphertext
GET  /api/crypto/details    -------->   public key + ciphertext (tanpa private)
POST /api/ehr/transmit      -------->   state["transmitted"] = True
POST /api/ehr/decrypt       -------->   decrypt -> state["recovered"]
POST /api/reset             -------->   state <- empty_state()
```

---

## Tahap 0 — Saat server dinyalakan

`python app.py` menyiapkan tiga hal di memori (`app.py` baris 1-13):

```python
app.secret_key = secrets.token_bytes(32)   # kunci tanda tangan cookie, acak tiap start
P = 467                                     # modulus prima demo
G = 2                                       # generator
DEMO_STATES = {}                            # "database" sesi
```

`DEMO_STATES` adalah tempat penyimpanan state. Isinya satu entry per browser,
kuncinya `demo_id` acak. Karena `secret_key` dibuat baru tiap start, cookie lama
tidak valid setelah restart, jadi kamu otomatis mendapat sesi kosong.

Alasan `p = 467` dibahas di
[code-walkthrough.md bagian 0.5](./code-walkthrough.md#05-mengapa-p-467-dan-g-2).

---

## Tahap 1 — Buka Dashboard (`/`)

1. `GET /` → `dashboard()` (`app.py` baris 67-68) → `render_template("dashboard.html")`.
2. Template `extends "base.html"`, jadi sidebar, topbar, dan `app.js` ikut termuat.
3. `app.js` baris 554-569 berjalan saat `DOMContentLoaded`: memasang empat
   fungsi setup, lalu `loadStatus()` dan `refreshCryptoDetails()`.
4. `loadStatus()` (`app.js` baris 109-116) memanggil `GET /api/status`.
5. Di server, `status()` (`app.py` baris 91-98) memanggil `get_state()`
   (baris 28-36). Di sinilah sesi lahir:

```python
sid = session.get("demo_id")        # pertama kali: None
if sid not in DEMO_STATES:          # None tidak ada di dict -> True
    sid = secrets.token_urlsafe(24) # bikin id acak
    session["demo_id"] = sid        # simpan di cookie browser
    DEMO_STATES[sid] = empty_state()
```

State awal dari `empty_state()` (`app.py` baris 16-25):

```python
{"ehr": None, "dh": None, "public_key": None, "private_key": None,
 "ciphertext": None, "transmitted": False, "recovered": None}
```

6. `summary(state)` (`app.py` baris 47-60) mengubah state jadi ringkasan aman:
   `prepared`, `connected`, `encrypted`, `transmitted`, `decrypted`,
   `block_count`. Private key tidak pernah masuk sini.
7. `renderStatus()` (`app.js` baris 119-241) mengisi metrik dan **mengunci tombol**:

| Tombol | Aktif kalau (baris `app.js`) |
|---|---|
| Handshake | selalu (baris 222-224) |
| Encrypt | `prepared && connected` (baris 226-230) |
| Transmit | `encrypted && !transmitted` (baris 232-236) |
| Decrypt | `transmitted` (baris 238-240) |

Jadi saat pertama dibuka, semua status "Pending" dan hanya Handshake yang aktif.

---

## Tahap 2 — Clinic: Prepare EHR

**Aksi:** klik *Use Sample Data* → form terisi (`app.js` baris 275-283);
klik *Prepare EHR*.

1. `submit` ditangkap, `event.preventDefault()` mencegah reload
   (`app.js` baris 285-286).
2. `form.reportValidity()` mengecek validasi HTML5: `required`, `maxlength=200`,
   umur `0-130` (baris 288).
3. `runAction()` (baris 92-102) men-disable tombol supaya tidak dobel klik, lalu
   menyalakannya lagi di `finally`.
4. `POST /api/ehr/prepare` dengan body 5 field yang sudah `trim()` (baris 301-305).

**Di backend `prepare_ehr()` (`app.py` baris 105-167):**

1. `request.get_json(silent=True)` (baris 108); bukan dict → 400 "Invalid JSON request.".
2. Lima field wajib dicek satu per satu (baris 123-136): kosong → 400
   "Field '...' is required."; lebih dari 200 karakter → 400 "too long".
3. `int(age)` (baris 138-144): gagal → "Age must be a number."; di luar `0..130` → 400.
4. Menyusun satu string (baris 146-152):

```text
Patient ID: EHR-2026-001
Name: Pasien Simulasi A
Age: 45
Diagnosis: Hipertensi (data fiktif)
Treatment: Terapi simulasi
```

5. `state["ehr"] = ehr` (baris 154), lalu ciphertext, `transmitted`, dan
   `recovered` dikosongkan (baris 156-159). **`dh` dan kunci lama tidak dihapus**
   — ganti EHR tidak memaksa handshake ulang.

**Response:** `preview`, `bytes` (119), dan `data` (summary baru).

**Di frontend:** `renderDocument()` (`app.js` baris 248-262) membuat `<pre>`
baru dan mengisi `textContent` — bukan `innerHTML`, jadi aman dari XSS.
`renderStatus` dipanggil ulang, tapi Encrypt masih mati karena `connected`
belum true. Toast: "EHR prepared successfully (119 bytes)."

---

## Tahap 3 — Cryptography: DH Handshake

**Aksi:** klik *Generate DH Handshake* (`app.js` baris 388-402).

1. `POST /api/crypto/handshake`.
2. Backend melakukan **lazy import** (`app.py` baris 179):

```python
from crypto.diffie_hellman import perform_handshake
```

   Kenapa di dalam fungsi? Supaya `ImportError`/`NotImplementedError` bisa
   ditangkap dan dijawab `409 module_pending`, bukan membuat server crash.
3. `perform_handshake(467, 2)` (baris 181) menjalankan **dua pihak sekaligus**:
   - Klinik: private `a` acak, public `A = 2^a mod 467`.
   - Hospital: private `b` acak, public `B = 2^b mod 467`.
   - Klinik hitung `B^a`, hospital hitung `A^b`.
   - Beda → `RuntimeError`; sama → return dict berisi kedua public key dan kedua secret.
4. `state["dh"] = result` (baris 186), lalu kunci ElGamal, ciphertext,
   `transmitted`, dan `recovered` dikosongkan (baris 188-193). Sesi kripto
   baru = data lama dibuang.
5. Response hanya memuat `p`, `g`, `clinic_public`, `hospital_public`, dan
   `shared_secret_match: true`. **Nilai shared secret tidak dikirim ke browser.**

**Di frontend:** `renderStatus` membuat `connected = true` sehingga tombol
Encrypt aktif. `refreshCryptoDetails()` (`app.js` baris 327-378) memanggil
`GET /api/crypto/details` dan mengisi angka public key di panel DH.

---

## Tahap 4 — Cryptography: Encrypt EHR

**Aksi:** klik *Encrypt Prepared EHR* (`app.js` baris 404-418).

**Guard di backend (`app.py` baris 230-236):**

```python
if state["ehr"] is None:  return 400 "Prepare EHR data first."
if state["dh"] is None:   return 400 "Complete the DH demonstration first."
```

Ini yang membuat urutan tidak bisa dilompati, walaupun tombolnya diakali lewat
DevTools.

1. `generate_keys(467, 2)` (baris 242): `x` acak, `y = 2^x mod 467`.
2. `encrypt(state["ehr"], public_key)` (baris 244-247). Untuk tiap byte:
   - `k` **baru** acak, `c1 = g^k mod p`
   - `m = byte + 1`, `c2 = m · y^k mod p`
   - Hasilnya 119 pasangan `(c1, c2)`.
3. Backend memeriksa bentuk hasil: harus `list`, tiap item pasangan dua `int`
   (baris 249-262).
4. `public_key`, `private_key`, `ciphertext` disimpan; `transmitted` dan
   `recovered` direset (baris 264-268).
5. Response: `block_count: 119`.

**Di frontend:** `refreshCryptoDetails()` menampilkan semua pasangan di panel
terminal (`app.js` baris 364-377):

```text
Block 001: (c1, c2)
Block 002: (c1, c2)
...
```

Inilah "yang dilihat penyadap". Tombol Transmit sekarang aktif.

---

## Tahap 5 — Cryptography: Simulate Transmission

**Aksi:** klik *Simulate Transmission* (`app.js` baris 420-432).

1. Guard: `ciphertext is None` → 400 "Encrypt EHR first." (`app.py` baris 341-342).
2. `state["transmitted"] = True` (baris 344). **Itu saja.** Tidak ada socket,
   tidak ada HTTP antar server — transmisi hanya perubahan flag, sesuai
   disclaimer di README.
3. UI mengganti label jadi "Transmission Completed", dan di dashboard kartu
   workflow ke-3 baru tercentang karena syaratnya `encrypted && transmitted`
   (`app.js` baris 142-145).

---

## Tahap 6 — Hospital: Decrypt

**Aksi:** klik *Decrypt with Hospital Private Key* (`app.js` baris 445-484).

**Guard:** belum transmit → 400 "Transmit ciphertext first."; private key `None`
→ 400 "Private key unavailable." (`app.py` baris 364-368).

1. `decrypt(ciphertext, private_key)` (baris 373-376). Untuk tiap pasangan:
   - `s = c1^x mod p` → sama dengan `y^k` saat enkripsi.
   - `m = c2 · s^(-1) mod p`.
   - `m` harus `1..256`; kalau tidak, ciphertext rusak/kunci salah.
   - `byte = m - 1`, dikumpulkan, lalu `.decode("utf-8")`.
2. Backend cek hasilnya `str`, simpan `state["recovered"] = recovered` (baris 383).
3. `verified = recovered == state["ehr"]` (baris 389) — perbandingan string penuh.

**Di frontend:** teks EHR muncul di panel kanan, label verifikasi jadi
**"Record Matches"** dengan class `success` (`app.js` baris 460-472), toast
hijau. Di dashboard, kartu workflow ke-4 ikut tercentang.

---

## Tahap 7 — Reset

Klik **↻ Reset** (`app.js` baris 500-546):

1. `confirm()` browser dulu (baris 503-508).
2. `POST /api/reset` → `state.clear()` + `state.update(empty_state())`
   (`app.py` baris 411-412).
3. Frontend mereset form, preview EHR, preview dekripsi, dan label verifikasi
   (baris 519-542).

---

## Siapa mengosongkan apa

| Aksi | `ehr` | `dh` | kunci ElGamal | `ciphertext` | `transmitted` | `recovered` |
|---|---|---|---|---|---|---|
| Prepare EHR | **diisi** | tetap | tetap | **kosong** | **False** | **kosong** |
| Handshake | tetap | **diisi** | **kosong** | **kosong** | **False** | **kosong** |
| Encrypt | tetap | tetap | **diisi** | **diisi** | **False** | **kosong** |
| Transmit | tetap | tetap | tetap | tetap | **True** | tetap |
| Decrypt | tetap | tetap | tetap | tetap | tetap | **diisi** |
| Reset | kosong | kosong | kosong | kosong | False | kosong |

---

## Kalau ada yang gagal

`apiRequest()` (`app.js` baris 21-61) memeriksa dua hal: `response.ok` dan
`result.success`. Kalau salah satu gagal, ia `throw new Error(result.message)`
(baris 54-58). `runAction()` menangkapnya, memunculkan toast merah berisi pesan
dari backend, lalu menyalakan lagi tombolnya (baris 97-101).

Artinya, setiap error yang kamu lihat di UI adalah **teks asli dari backend**,
bukan pesan generik browser. Itu sebabnya pesan seperti "Transmit ciphertext
first." bisa langsung dipakai untuk debugging saat demo.

---

## Dua hal yang sering ditanyakan

**"State-nya per browser atau per aplikasi?"**
Per browser. Buka Chrome dan Edge → dua `demo_id` berbeda → dua simulasi
terpisah. Tapi dua tab di browser yang sama berbagi satu state karena
cookie-nya sama.

**"Di mana private key disimpan?"**
Hanya di memori server, di `DEMO_STATES`. Browser cuma menerima public key
`(p, g, y)`, ciphertext, dan boolean "match". Endpoint `/api/crypto/details`
secara eksplisit tidak menyertakan private key (`app.py` baris 317-320).

---

## Ringkasan endpoint

| Method | Path | Fungsi di `app.py` | Baris |
|---|---|---|---|
| GET | `/api/status` | `status()` | 91-98 |
| POST | `/api/ehr/prepare` | `prepare_ehr()` | 105-167 |
| POST | `/api/crypto/handshake` | `handshake()` | 174-219 |
| POST | `/api/crypto/encrypt` | `encrypt_ehr()` | 226-285 |
| GET | `/api/crypto/details` | `crypto_details()` | 292-330 |
| POST | `/api/ehr/transmit` | `transmit()` | 337-353 |
| POST | `/api/ehr/decrypt` | `decrypt_ehr()` | 360-401 |
| POST | `/api/reset` | `reset()` | 408-422 |
