# EHR-Crypto-Project

Proyek ini adalah simulasi sistem transfer data Rekam Medis Elektronik (EHR) antar institusi kesehatan (misal: Klinik ke Rumah Sakit Rujukan) menggunakan pengamanan kriptografi hibrida dari awal (from scratch) **tanpa library kriptografi eksternal**.

Sistem ini diimplementasikan menggunakan bahasa pemrograman Python murni untuk mendemonstrasikan algoritma **Diffie-Hellman** dan **ElGamal**.

## Arsitektur Keamanan
1. **Diffie-Hellman Key Exchange:** Digunakan untuk memvalidasi dan mengamankan jalur komunikasi (Handshake & Session Validation) antara server Klinik dan Rumah Sakit.
2. **ElGamal Asymmetric Encryption:** Digunakan untuk mengenkripsi data teks Rekam Medis Elektronik agar tetap rahasia dari pihak ketiga (Man-in-the-Middle) maupun jika terjadi kebocoran basis data.

## Fitur Utama
* **Pure Cryptographic Math:** Implementasi algoritma eksponensiasi modular dan *Extended Euclidean* secara manual.
* **Text-to-Ciphertext:** Konversi data medis (String) menjadi blok angka, dienkripsi menjadi pasangan ciphertext $(c_1, c_2)$.
* **Interactive CLI:** Antarmuka *Command Line* untuk menyimulasikan peran sebagai Dokter Pengirim dan Server Penerima.

##  Tim Pengembang (Kelompok X)
| Nama | NIM | Jobdesk |
|---|---|---|
| [Nama Anggota 1] | [NIM 1] | Core Cryptography & Math Engine |
| [Nama Anggota 2] | [NIM 2] | ElGamal Data Processor (Enkripsi/Dekripsi) |
| [Nama Anggota 3] | [NIM 3] | System Integration, DH Handshake, & CLI |

## Cara Menjalankan Program
Pastikan Anda memiliki Python 3.x terinstal di sistem Anda.
1. Clone repositori ini:
   ```bash
   git clone [https://github.com/oooryzaaa/EHR-Crypto-System.git]
   cd EHR-Crypto-System
