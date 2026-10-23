# Erdoza-EHR-Project 

Proyek ini adalah simulasi sistem transfer data Rekam Medis Elektronik (EHR) antar institusi kesehatan (misal: Klinik ke Rumah Sakit Rujukan) menggunakan pengamanan kriptografi hibrida dari nol (*from scratch*) **tanpa menggunakan library kriptografi eksternal**.

Proyek ini dibangun menggunakan Python murni untuk mendemonstrasikan implementasi algoritma **Diffie-Hellman** dan **ElGamal** secara matematis dan fungsional.

---

## Alur Kerja Sistem (Cara Kerja)

Sistem ini menggabungkan Diffie-Hellman (DH) untuk mengamankan *jalur komunikasi* dan ElGamal untuk mengamankan *data rekam medis*.

1. **Fase 1: Inisiasi Jalur Aman (Diffie-Hellman Handshake)**
   * Komputer Klinik (Pengirim) dan Server Rumah Sakit (Penerima) menyepakati parameter publik (bilangan prima $p$ dan generator $g$).
   * Keduanya menghasilkan kunci privat masing-masing dan bertukar kunci publik di jaringan.
   * Keduanya menghitung *Shared Secret* (Kunci Sesi) untuk memastikan jalur komunikasi aman dari serangan *Man-in-the-Middle* (MitM).

2. **Fase 2: Persiapan Kunci Enkripsi (ElGamal Key Generation)**
   * Server Rumah Sakit membuat pasangan kunci asimetris (*Public Key* & *Private Key*) menggunakan algoritma ElGamal.
   * Rumah Sakit mengirimkan Kunci Publik ElGamal-nya ke Klinik, sementara Kunci Privat disimpan di basis data Rumah Sakit.

3. **Fase 3: Pemrosesan & Enkripsi Data EHR (Di sisi Klinik)**
   * Dokter di Klinik memasukkan data EHR pasien berupa teks (Misal: `ID: 001 | Pasien: Budi | Diagnosa: Kanker Paru`).
   * Sistem mengubah teks menjadi deretan blok angka menggunakan konversi nilai ASCII.
   * Sistem mengenkripsi angka tersebut menggunakan Kunci Publik ElGamal milik Rumah Sakit, menghasilkan ciphertext (pasangan $c_1, c_2$) yang bentuknya acak, lalu mengirimkannya melalui jaringan.

4. **Fase 4: Dekripsi & Pemulihan Data (Di sisi Rumah Sakit)**
   * Server Rumah Sakit menerima ciphertext.
   * Sistem mendekripsi angka-angka acak tersebut menggunakan Kunci Privat ElGamal milik Rumah Sakit.
   * Hasil dekripsi dikonversi kembali menjadi teks ASCII sehingga rekam medis pasien dapat dibaca dengan utuh.

---

## Pembagian Jobdesk Tim Erdoza

Untuk memastikan beban kerja seimbang, pengembangan proyek dibagi menjadi 3 modul fungsional:

| Nama Anggota | NRP | Modul Fokus | Tanggung Jawab Utama |
|---|---|---|---|
| **Oryza Qiara Ramadhani** | 5027241084 | **System Integration & CLI** | Menyatukan kode ke dalam `main.py`. Membangun antarmuka CLI interaktif, menangani logika Diffie-Hellman *handshake*, *error handling*, serta memastikan alur presentasi sistem berjalan lancar. |
| **??** | [Isi NRP] | **Core Cryptography Math** | Membangun fondasi matematika murni di `math_utils.py`. Membuat fungsi `mod_exp` untuk eksponensial modular, algoritma *Extended Euclidean* untuk `mod_inverse`, serta pencarian bilangan prima yang aman. |
| **??** | [Isi NRP] | **ElGamal Data Processor** | Mengelola manipulasi data di `elgamal.py`. Membuat fungsi konversi Teks-ke-ASCII, serta menulis logika enkripsi (pemecahan pesan ke blok) dan dekripsi algoritma ElGamal. |

---

---

## Struktur Repositori

```text
Erdoza-EHR-Project/
├── math_utils.py         # Fungsi matematika dasar (Eksponensial, Invers Modular)
├── elgamal.py            # Logika enkripsi, dekripsi, & konversi teks ASCII
├── main.py               # Program utama (CLI Menu & DH Handshake)
└── README.md             # Dokumentasi proyek
