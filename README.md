# Erdoza HealthCrypt

### Secure Electronic Health Record Transfer Simulation Using Diffie-Hellman and ElGamal

**Erdoza HealthCrypt** merupakan proyek simulasi pertukaran data Rekam Medis Elektronik (*Electronic Health Record/EHR*) antara Klinik dan Rumah Sakit Rujukan menggunakan algoritma kriptografi **Diffie-Hellman** dan **ElGamal**.

Proyek ini dikembangkan menggunakan Python dengan implementasi algoritma kriptografi secara manual (*from scratch*), tanpa menggunakan library kriptografi eksternal. Sistem dilengkapi antarmuka berbasis web menggunakan Flask, HTML, CSS, dan JavaScript, serta Command Line Interface (CLI) untuk demonstrasi teknis.

Proyek dikembangkan sebagai sarana pembelajaran untuk memahami proses pertukaran kunci, enkripsi, dekripsi, dan representasi data terenkripsi dalam komunikasi antarinstansi kesehatan.

> **Disclaimer:** Sistem ini dibuat khusus untuk keperluan akademis dan demonstrasi algoritma kriptografi. Sistem tidak ditujukan untuk penggunaan produksi atau pemrosesan data medis pasien sebenarnya.

---

## 1. Project Objectives

Tujuan utama pengembangan Erdoza HealthCrypt adalah:

- Mengimplementasikan algoritma Diffie-Hellman untuk mensimulasikan pertukaran kunci antara dua pihak.
- Mengimplementasikan algoritma ElGamal untuk melakukan enkripsi dan dekripsi data EHR.
- Memahami operasi matematika kriptografi, seperti modular exponentiation, Extended Euclidean Algorithm, dan modular inverse.
- Mensimulasikan pengiriman data EHR terenkripsi dari Klinik ke Rumah Sakit Rujukan.
- Mengembangkan antarmuka berbasis web untuk memvisualisasikan proses kriptografi secara interaktif.
- Melakukan pengujian fungsional dan memverifikasi kesesuaian hasil dekripsi dengan plaintext asli.

## 2. Technology Stack

| Komponen | Teknologi | Kegunaan |
|---|---|---|
| Programming Language | Python 3 | Implementasi algoritma dan backend |
| Web Framework | Flask | Routing, API, dan integrasi sistem |
| Frontend | HTML5, CSS3, JavaScript | Antarmuka aplikasi web |
| UI Framework | Bootstrap 5 | Komponen antarmuka |
| Cryptography | Diffie-Hellman & ElGamal | Pertukaran kunci dan enkripsi |
| Testing | Python unittest | Pengujian algoritma |
| Version Control | Git & GitHub | Kolaborasi dan manajemen kode |

## 3. System Architecture

Sistem menggunakan arsitektur berbasis web yang menghubungkan antarmuka frontend dengan backend Flask dan modul kriptografi Python.

```text
             ERDOZA HEALTHCRYPT
                     |
               Web Interface
                     |
        +------------+------------+
        |            |            |
   Clinic Portal   Crypto      Hospital
                   Monitor      Portal
        |            |            |
        +------------+------------+
                     |
                Flask API
                     |
          Cryptography Modules
                     |
       +-------------+-------------+
       |             |             |
 Diffie-Hellman  Math Engine    ElGamal
       |             |             |
       +-------------+-------------+
                     |
             EHR Data Processing
```

**Frontend** digunakan untuk memasukkan data EHR fiktif, memulai proses simulasi, dan menampilkan hasil operasi kriptografi.

**Flask Backend** menangani request dari frontend dan menghubungkannya dengan modul Python.

**Cryptography Modules** menjalankan perhitungan matematika, pertukaran kunci Diffie-Hellman, serta operasi enkripsi dan dekripsi ElGamal.

## 4. System Workflow

### Phase 1 — EHR Data Preparation

1. Pengguna membuka halaman Clinic Portal.
2. Pengguna memasukkan informasi pasien fiktif, seperti ID pasien, nama, usia, diagnosis, dan tindakan.
3. Sistem melakukan validasi input.
4. Data disusun menjadi representasi EHR yang siap diproses.

### Phase 2 — Diffie-Hellman Key Exchange

1. Klinik dan Rumah Sakit menyepakati parameter publik berupa bilangan prima `p` dan generator `g`.
2. Kedua pihak menghasilkan private key masing-masing.
3. Kedua pihak menghitung dan bertukar public key.
4. Masing-masing pihak menghitung shared secret.
5. Sistem memverifikasi apakah kedua shared secret menghasilkan nilai yang sama.

Rumus dasar:

\[
A = g^a \bmod p
\]

\[
B = g^b \bmod p
\]

\[
S_A = B^a \bmod p
\]

\[
S_B = A^b \bmod p
\]

Hasil yang diharapkan:

\[
S_A = S_B
\]

**Catatan:** Diffie-Hellman pada implementasi awal digunakan untuk demonstrasi pembentukan shared secret. Belum tersedia autentikasi identitas atau penggunaan shared secret sebagai kunci enkripsi kanal.

### Phase 3 — ElGamal Key Generation

1. Rumah Sakit menghasilkan pasangan public key dan private key ElGamal.
2. Public key digunakan oleh Klinik untuk mengenkripsi data.
3. Private key digunakan oleh Rumah Sakit untuk mendekripsi ciphertext.

Pembentukan public key:

\[
y = g^x \bmod p
\]

Keterangan:

- `p`: modulus prima
- `g`: generator
- `x`: private key
- `y`: komponen public key
- Pasangan kunci direpresentasikan sebagai public key `(p, g, y)` dan private key `(p, g, x)`.

### Phase 4 — EHR Encryption

1. Data EHR dikonversi menjadi representasi byte UTF-8.
2. Setiap byte dipetakan ke angka `1..256` (`byte + 1`), sehingga modulus harus memenuhi `p > 256`.
3. Sistem menghasilkan bilangan acak `k` untuk operasi enkripsi.
4. Setiap blok data dienkripsi menggunakan public key Rumah Sakit.
5. Sistem menghasilkan ciphertext dalam bentuk pasangan `(c1, c2)`.

Rumus enkripsi:

\[
c_1 = g^k \bmod p
\]

\[
c_2 = m \cdot y^k \bmod p
\]

Nilai `m` harus berada dalam rentang yang didukung modulus `p`.

### Phase 5 — Simulated Transmission

Ciphertext ditampilkan pada Cryptography Monitor melalui *Network Transmission Observer*.

Fitur ini mensimulasikan data yang dapat diamati selama transmisi. Pada versi pengembangan lokal, proses transmisi merupakan perubahan status di backend Flask, bukan komunikasi nyata antara dua server terpisah.

### Phase 6 — EHR Decryption

1. Rumah Sakit menerima ciphertext hasil simulasi.
2. Sistem menggunakan private key ElGamal untuk proses dekripsi.
3. Nilai ciphertext dikembalikan menjadi byte.
4. Byte dikonversi kembali menjadi teks UTF-8.
5. Sistem membandingkan hasil dekripsi dengan data EHR asli.

Rumus dasar dekripsi:

\[
s = c_1^x \bmod p
\]

\[
m = c_2 \cdot s^{-1} \bmod p
\]

Keberhasilan verifikasi menunjukkan bahwa data berhasil dipulihkan dengan benar pada proses simulasi.

---

## 5. Application Features

### Dashboard

- System overview
- Status pertukaran kunci
- Status enkripsi dan transmisi
- Jumlah ciphertext blocks
- Visualisasi transfer workflow
- Navigasi menuju modul simulasi

### Clinic Portal

- Form input data pasien fiktif
- Validasi data EHR
- Sample patient data
- Preview dokumen EHR
- Persiapan data sebelum enkripsi

### Cryptography Monitor

- Diffie-Hellman handshake
- Visualisasi parameter publik
- Tampilan public key Klinik dan Rumah Sakit
- Status perbandingan shared secret
- Proses ElGamal encryption
- Ciphertext block viewer
- Simulated network transmission

### Hospital Portal

- Status penerimaan ciphertext
- Informasi jumlah blok terenkripsi
- Proses dekripsi menggunakan private key
- Preview hasil dekripsi
- Verifikasi kesesuaian plaintext

### Command Line Interface

- Demonstrasi pertukaran kunci
- Input EHR melalui terminal
- Proses enkripsi dan dekripsi
- Tampilan ciphertext
- Pengujian hasil pemulihan data

Beberapa fitur kriptografi masih memerlukan penyelesaian dan integrasi modul anggota tim.

---

## 6. Team Erdoza — Jobdesk

Pengembangan proyek dibagi berdasarkan tanggung jawab modul dan integrasi sistem.

| Nama Anggota | NRP | Modul Fokus | Tanggung Jawab |
|---|---|---|---|
| **Oryza Qiara Ramadhani** | 5027241084 | System Integration, Diffie-Hellman & Web Development | Implementasi Diffie-Hellman, pengembangan CLI, Flask backend, frontend, visualisasi kriptografi, API, error handling, dan integrasi keseluruhan sistem. |
| **Christiano Ronaldo** | 5027241025 | Core Cryptography & Math Engine | Implementasi modular exponentiation, Extended Euclidean Algorithm, modular inverse, validasi bilangan prima, serta pengujian operasi matematika. |
| **Erlinda Annisa Zahra** | 5027241108 | ElGamal & EHR Data Processing | Implementasi pembangkitan kunci, enkripsi dan dekripsi ElGamal, konversi data UTF-8, serta pengujian pemulihan EHR. |

Setiap anggota bertanggung jawab terhadap pengujian dan dokumentasi modul masing-masing. Integrasi akhir dilakukan secara bersama.

## 7. Repository Structure

```text
EHR-Crypto-Project/
├── app.py
├── main.py
│
├── crypto/
│   ├── __init__.py
│   ├── diffie_hellman.py
│   ├── math_utils.py
│   └── elgamal.py
│
├── utils/
│   ├── __init__.py
│   └── ehr_data.py
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── clinic.html
│   ├── cryptography.html
│   └── hospital.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── tests/
│   ├── test_math.py
│   ├── test_dh.py
│   └── test_elgamal.py
│
├── requirements.txt
├── .gitignore
├── CONTRIBUTING.md
└── README.md
```

## 8. Installation & Setup

### Prerequisites

- Python 3.10 atau lebih baru
- Git
- Web browser
- Visual Studio Code (opsional)

### Clone Repository

```bash
git clone https://github.com/USERNAME/EHR-Crypto-Project.git
cd EHR-Crypto-Project
```

Ganti `USERNAME` dengan username atau organisasi pemilik repository GitHub.

### Create Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell memblokir aktivasi:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Run Web Application

```bash
python app.py
```

Buka browser dan akses:

`http://127.0.0.1:5000`

### Run CLI Application

```bash
python main.py
```

### Run Unit Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Pengujian dan fungsi kriptografi yang masih berupa placeholder belum dapat dianggap selesai sampai implementasinya tersedia dan seluruh pengujian berhasil.

---

## 9. Development Workflow

Setiap anggota mengembangkan modul masing-masing menggunakan branch Git.

| Branch | Penanggung Jawab |
|---|---|
| `feature/web-interface` | Oryza |
| `feature/dh-cli` | Oryza |
| `feature/math-engine` | Aldo |
| `feature/elgamal` | Erlinda |

### Collaboration Guidelines

1. Pertahankan struktur folder dan kontrak fungsi yang sudah disepakati.
2. Hindari mengubah modul milik anggota lain tanpa koordinasi.
3. Gunakan commit message yang jelas.
4. Tambahkan pengujian untuk setiap implementasi algoritma.
5. Lakukan code review sebelum menggabungkan perubahan ke branch `main`.
6. Gunakan Pull Request untuk integrasi fitur.

Panduan lengkap dapat dilihat pada `CONTRIBUTING.md`.

## 10. Project Status

**Current Stage: Web Development & Cryptographic Integration**

| Komponen | Status |
|---|---|
| Repository Structure | Prepared |
| Flask Web Application | Initial implementation available |
| Dashboard UI | Implemented |
| Clinic Portal UI | Implemented |
| Cryptography Monitor UI | Implemented |
| Hospital Portal UI | Implemented |
| Diffie-Hellman | Implementation written, testing pending |
| Mathematical Utilities | Implemented with unit tests; used by Diffie-Hellman |
| ElGamal Encryption & Decryption | Implemented and unit tested |
| EHR Data Processing | Implemented and unit tested |
| End-to-End Testing | Pending |

Status dapat berubah seiring kontribusi anggota dan hasil pengujian.

Dokumentasi modul matematika Christiano Ronaldo, hasil review integrasi, dan
kontrak validasi tersedia di [Math Engine](docs/math-engine.md).

## 11. Security Limitations

Erdoza HealthCrypt merupakan implementasi kriptografi untuk keperluan pembelajaran dengan beberapa batasan:

- Parameter kriptografi yang digunakan pada demonstrasi berukuran kecil dan tidak aman untuk penggunaan produksi.
- Diffie-Hellman tidak menyediakan autentikasi secara otomatis sehingga tidak mencegah serangan Man-in-the-Middle tanpa mekanisme tambahan.
- Shared secret Diffie-Hellman belum digunakan untuk membangun kanal komunikasi terenkripsi.
- Implementasi ElGamal dasar belum menyediakan autentikasi, integritas pesan, atau perlindungan terhadap modifikasi ciphertext.
- Transmisi jaringan merupakan simulasi lokal.
- Status simulasi disimpan sementara di memori backend, bukan sistem penyimpanan medis persisten.
- Sistem belum menerapkan autentikasi pengguna, kontrol akses berbasis peran, maupun audit keamanan produksi.
- Seluruh demonstrasi menggunakan data pasien fiktif.

**Aplikasi tidak boleh digunakan untuk menyimpan atau mengirimkan informasi kesehatan pasien sebenarnya.**

---

## 12. Project Credits

**Developed by Team Erdoza**

- Oryza Qiara Ramadhani
- Christiano Ronaldo
- Erlinda Annisa Zahra

Information Technology — Institut Teknologi Sepuluh Nopember (ITS)

*Academic Project — 2026*
