# Script Demo — Erdoza HealthCrypt

Naskah siap baca. Bagian **1** untuk menjelaskan web, bagian **2** untuk
menjelaskan kode. Isi ringkasan lama dipindahkan ke lampiran di bawah.

**Cara pakai:** teks normal = diucapkan apa adanya (boleh diubah gaya bahasanya).
`«...»` = aksi yang dilakukan, jangan diucapkan.

**Alokasi waktu (total ±13 menit):**

| Bagian | Isi | Waktu |
|---|---|---|
| 0 | Pembukaan | 1 menit |
| 1 | Penjelasan web | 5 menit |
| 2 | Code walkthrough | 6 menit |
| 3 | Penutup | 1 menit |

---

## BAGIAN 0 — Pembukaan

`«Buka terminal di folder project»`

Ucapkan:

> Selamat pagi. Kami tim Erdoza, terdiri dari tiga orang: saya Oryza di bagian
> integrasi sistem, Diffie-Hellman, dan web; Aldo di bagian matematika dasar;
> Erlinda di bagian ElGamal dan pengolahan data EHR. Hari ini kami
> mendemonstrasikan Erdoza HealthCrypt, yaitu simulasi pengiriman rekam medis
> elektronik dari klinik ke rumah sakit rujukan menggunakan Diffie-Hellman dan
> ElGamal. Seluruh algoritma kriptografi kami tulis sendiri, tanpa library
> kriptografi.

`«Jalankan: .\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"»`

Ucapkan:

> Sebelum mulai, kami pastikan dulu seluruh pengujian lulus. Ada 26 unit test
> yang mencakup operasi matematika, pertukaran kunci, enkripsi-dekripsi, dan
> konversi data. Semuanya lulus. Karena Aldo tidak bisa hadir, bagian
> matematika akan saya jelaskan mewakili beliau.

`«Jalankan: .\.venv\Scripts\python.exe app.py, lalu buka http://127.0.0.1:5000»`

---

## BAGIAN 1 — Penjelasan Web

### 1.1 Arsitektur — 40 detik

`«Tunjukkan halaman Dashboard»`

Ucapkan:

> Aplikasi ini punya empat halaman: Dashboard untuk ringkasan status, Clinic
> Portal untuk menyiapkan data pasien fiktif, Cryptography Monitor untuk
> menjalankan proses kriptografi, dan Hospital Portal untuk menerima dan
> mendekripsi. Semua halaman memanggil API di backend Flask. Perhitungan
> kriptografi seluruhnya terjadi di server; browser hanya menampilkan hasilnya.

`«Arahkan kursor ke sidebar»`

Ucapkan:

> Alurnya empat tahap: siapkan data, tukar kunci, enkripsi dan kirim, lalu
> dekripsi dan verifikasi.

### 1.2 Dashboard — 20 detik

Ucapkan:

> Saat ini semua status masih Pending, dan hanya tombol handshake yang aktif.
> Tombol lain terkunci karena urutan prosesnya belum terpenuhi. Ini bukan
> sekadar hiasan: backend juga menolak permintaan yang melompat urutan, jadi
> walaupun tombolnya diakali lewat developer tools, tetap gagal.

### 1.3 Clinic Portal — 50 detik

`«Klik Clinic Portal, lalu klik "Use Sample Data"»`

Ucapkan:

> Di sini klinik memasukkan data pasien fiktif: ID, nama, umur, diagnosis, dan
> tindakan. Saya pakai data contoh supaya cepat.

`«Klik "Prepare EHR →""»`

Ucapkan:

> Setelah disiapkan, kelima field digabung menjadi satu dokumen teks. Di panel
> kanan terlihat preview-nya, dan sistem melaporkan ukurannya 119 byte. Angka
> ini penting: nanti jumlah blok ciphertext akan sama dengan jumlah byte,
> karena ElGamal di sini bekerja per byte, bukan per karakter.
>
> Tombol Encrypt sekarang masih mati, karena kita belum melakukan pertukaran
> kunci.

### 1.4 Cryptography Monitor — Diffie-Hellman — 70 detik

`«Klik Cryptography, lalu "Generate DH Handshake →""»`

Ucapkan:

> Tahap kedua adalah pertukaran kunci Diffie-Hellman. Klinik dan rumah sakit
> masing-masing membuat kunci privat, lalu saling bertukar kunci publik.
> Klinik menghitung satu nilai rahasia dari kunci publik rumah sakit, dan
> rumah sakit menghitung dari kunci publik klinik.

`«Tunjuk angka Prime Modulus, Generator, dan dua public key»`

Ucapkan:

> Parameter publiknya adalah p sama dengan 467 dan g sama dengan 2. Nilai ini
> bukan angka standar internasional, tapi pilihan kami untuk demonstrasi, dan
> dipilih karena memenuhi empat syarat: prima, lebih besar dari 256, merupakan
> safe prime, dan 2 adalah primitive root dengan orde penuh.
>
> Di bawah terlihat "Shared Secrets Match", yang berarti kedua pihak
> menghasilkan nilai rahasia yang persis sama. Tapi perlu saya sampaikan jujur:
> nilai rahasia ini belum kami pakai sebagai kunci enkripsi kanal. Enkripsi
> datanya memakai pasangan kunci ElGamal yang terpisah. Ini tercatat sebagai
> batasan di README.

### 1.5 Encryption — 60 detik

`«Klik "Encrypt Prepared EHR →""»`

Ucapkan:

> Tahap ketiga, rumah sakit membuat pasangan kunci ElGamal: satu kunci publik
> dan satu kunci privat. Kunci publik dikirim ke klinik, kunci privat tetap
> disimpan di server dan tidak pernah dikirim ke browser.

`«Tunjuk jumlah blok dan panel terminal»`

Ucapkan:

> Klinik lalu mengenkripsi setiap byte dari dokumen tadi menggunakan kunci
> publik. Hasilnya 119 pasangan angka, masing-masing berisi c1 dan c2. Angka
> inilah yang terlihat oleh penyadap di jaringan, dan tanpa kunci privat,
> isinya tidak bisa dipulihkan.

### 1.6 Simulasi Transmisi — 30 detik

`«Klik "Simulate Transmission →""»`

Ucapkan:

> Tahap keempat hanya mensimulasikan pengiriman. Perlu saya tegaskan: ini bukan
> komunikasi jaringan sungguhan, hanya perubahan status di server yang
> menandai ciphertext sudah diterima. Kami sengaja menyebutkannya supaya tidak
> menyesatkan.

### 1.7 Hospital Portal — 60 detik

`«Klik Hospital Portal»`

Ucapkan:

> Di sisi penerima terlihat status transmisi sudah diterima, dengan jumlah blok
> yang sama, 119.

`«Klik "Decrypt with Hospital Private Key →""»`

Ucapkan:

> Rumah sakit mendekripsi dengan kunci privatnya. Setiap pasangan c1 dan c2
> dikembalikan menjadi satu byte, lalu seluruh byte disusun kembali dan dibaca
> sebagai teks UTF-8. Hasilnya keluar sebagai dokumen yang sama.

`«Tunjuk label "Record Matches"»`

Ucapkan:

> Sistem membandingkan hasil dekripsi dengan dokumen asli secara penuh, dan
> hasilnya cocok. Kalau saya kembali ke Dashboard, keempat tahap sekarang
> tercentang.

`«Kembali ke Dashboard, tunjuk workflow»`

Ucapkan:

> Sebagai catatan keamanan: kunci privat tidak pernah dikirim ke browser. Endpoint
> yang menampilkan detail kriptografi hanya mengembalikan kunci publik,
> ciphertext, dan status "cocok atau tidak". Itu sebabnya halaman ini aman
> dibuka kapan saja.

---

## BAGIAN 2 — Code Walkthrough

### 2.1 Urutan yang dibuka — 15 detik

Ucapkan:

> Saya akan menjelaskan kode mengikuti jalannya data, bukan urutan folder.
> Mulai dari matematika dasar, lalu pertukaran kunci, lalu enkripsi, lalu
> backend dan frontend. Ada satu benang merah: modul matematika dan modul DH
> hanya tersambung lewat satu fungsi, yaitu `mod_exp`.

### 2.2 `crypto/math_utils.py` — bagian Aldo — 90 detik

`«Buka crypto/math_utils.py, scroll ke baris 10»`

Ucapkan:

> File ini berisi empat fungsi matematika. Yang benar-benar dipakai sistem
> hanya `mod_exp`, di baris 10 sampai 31. Fungsinya menghitung nilai pangkat
> modulo, misalnya 2 pangkat a modulo 467.
>
> Kenapa tidak dihitung langsung? Karena eksponennya bisa ratusan digit.
> Menghitung 2 pangkat 465 dulu baru dimodulo akan membentuk bilangan raksasa.
> Metode square-and-multiply yang dipakai di sini mengalikan dan mengkuadratkan
> sambil terus memotong modulo, sehingga angkanya tetap kecil.

`«Tunjuk baris 25-29»`

Ucapkan:

> Inti algoritmanya hanya lima baris: selama eksponen masih ada, kalau bit
> terendahnya satu maka hasil dikalikan basis; basis dikuadratkan; lalu
> eksponen digeser satu bit. Jumlah putarannya sebanding dengan jumlah bit
> eksponen, jadi untuk eksponen 465 hanya sembilan putaran.

`«Tunjuk contoh di dokumen, atau hitung manual»`

Ucapkan:

> Contoh: 2 pangkat 5 modulo 467. Lima dalam biner adalah 101, jadi tiga
> putaran, hasilnya 32.

`«Tunjuk baris 16-17»`

Ucapkan:

> Satu detail yang saya anggap penting: pengecekan tipe di baris 16 memakai
> `type(value) is not int`, bukan `isinstance`. Alasannya, di Python boolean
> adalah turunan integer, jadi kalau memakai `isinstance`, nilai `True` akan
> lolos dan diam-diam dihitung sebagai angka satu. Dengan cara ini, boolean
> ditolak.

`«Scroll ke baris 34 dan 60»`

Ucapkan:

> Dua fungsi berikutnya: `extended_gcd` mencari koefisien Bezout, dan
> `mod_inverse` memakainya untuk mencari invers modular. Invers modular hanya
> ada kalau faktor persekutuan terbesarnya satu, dan itu diperiksa di baris 71.
>
> Keduanya diterapkan secara iteratif, bukan rekursif, karena input bisa
> ribuan bit dan rekursi berisiko melebihi batas kedalaman Python.

`«Scroll ke baris 77»`

Ucapkan:

> Fungsi terakhir, `is_prime`, memakai pembagian percobaan sampai akar kuadrat.
> Berhenti di akar kuadrat karena kalau n sama dengan a kali b dengan a lebih
> kecil atau sama dengan b, maka a pasti tidak lebih besar dari akar n. Jadi
> bila tidak ada pembagi sampai akar n, bilangan itu pasti prima. Pengecekannya
> juga hanya menguji bentuk 6k-1 dan 6k+1, sehingga hanya dua dari setiap enam
> angka yang diperiksa.
>
> Perlu saya sampaikan: fungsi ini belum dipanggil oleh DH maupun ElGamal.
> ElGamal memakai uji Miller-Rabin miliknya sendiri, sedangkan DH belum
> memvalidasi primalitas sama sekali. Ini tindak lanjut yang masih terbuka.

### 2.3 `crypto/diffie_hellman.py` — 90 detik

`«Buka crypto/diffie_hellman.py»`

Ucapkan:

> Baris 9 mengimpor `mod_exp` dari modul Aldo. Itu satu-satunya titik sambung
> antara bagian kami.

`«Tunjuk baris 12-40»`

Ucapkan:

> Fungsi pertama, `generate_dh_keys`, membuat kunci privat secara acak di
> baris 33. Hasilnya di antara 2 dan p dikurangi 2. Kunci publik dihitung di
> baris 34 dengan rumus g pangkat a modulo p, memakai fungsi Aldo tadi.
>
> Kenapa memakai modul `secrets`, bukan `random`? Karena `random` bisa
> diprediksi dari seed-nya, sedangkan `secrets` memakai sumber acak sistem yang
> memang dirancang untuk kriptografi.

`«Tunjuk baris 32 dan 36-40»`

Ucapkan:

> Di sini ada perbaikan bug yang saya temukan saat pengujian. Awalnya kunci
> hanya dibuat sekali. Ternyata untuk p sama dengan 467 dan g sama dengan 2, ada
> satu kunci privat, yaitu 233, yang menghasilkan kunci publik 466, atau p
> dikurangi 1, dan nilai itu ditolak oleh fungsi berikutnya. Akibatnya
> handshake gagal secara acak sekitar nol koma empat tiga persen. Dari 20.000
> percobaan, terukur 74 kegagalan. Perbaikannya: pembuatan kunci diulang sampai
> mendapat nilai yang valid, dan sekarang nol kegagalan dari 20.000 percobaan.
> Ada regression test-nya di `tests/test_dh.py`.

`«Tunjuk baris 43-57, lalu 60-93»`

Ucapkan:

> Fungsi kedua menghitung nilai rahasia bersama, dan di baris 51 memvalidasi
> kunci publik lawan, karena di dunia nyata nilai itu datang dari jaringan dan
> bisa saja bernilai satu atau p dikurangi satu. Fungsi ketiga,
> `perform_handshake`, menjalankan kedua pihak sekaligus lalu memastikan kedua
> nilai rahasianya sama. Kalau berbeda, ia melempar `RuntimeError`, bukan
> `ValueError`, karena itu bukan kesalahan input melainkan kegagalan proses
> yang seharusnya mustahil.

### 2.4 `crypto/elgamal.py` — bagian Erlinda — 60 detik

`«Buka crypto/elgamal.py»`

Ucapkan:

> Bagian ini dikerjakan Erlinda. Saya jelaskan pokoknya. Di baris 71, kunci
> dibuat: kunci privat acak, lalu kunci publik dihitung dengan rumus y sama
> dengan g pangkat x modulo p.
>
> Baris 85 sampai 104 adalah enkripsi. Setiap byte diproses satu per satu, dan
> untuk setiap byte dipakai nilai k acak yang baru. Ini penting: kalau dua byte
> yang sama memakai k yang sama, ciphertext-nya akan identik, dan pola datanya
> bisa ditebak.

`«Tunjuk baris 100»`

Ucapkan:

> Satu detail yang sering ditanyakan: byte bernilai nol sampai 255, tapi di
> baris 100 nilainya ditambah satu. Alasannya, nilai nol akan membuat c2 selalu
> nol dan informasinya hilang. Karena itu modulus harus lebih besar dari 256.

`«Tunjuk baris 142-148»`

Ucapkan:

> Dekripsi ada di baris 107 sampai 148. Nilai rahasia dihitung dari c1 pangkat
> x, lalu c2 dikalikan inversnya. Faktor yang sama di kedua sisi saling
> menghilangkan, sehingga pesan aslinya kembali. Kalau hasilnya di luar rentang
> 1 sampai 256, sistem menolak, karena itu berarti ciphertext sudah diubah atau
> kuncinya salah.

### 2.5 `utils/ehr_data.py` — 20 detik

`«Buka utils/ehr_data.py»`

Ucapkan:

> File kecil ini hanya mengubah teks ke byte UTF-8 dan sebaliknya, plus
> validasi tidak kosong. UTF-8 dipakai supaya aksen dan emoji tetap bisa
> dienkripsi dan dipulihkan.

### 2.6 `app.py` — 100 detik

`«Buka app.py»`

Ucapkan:

> Ini bagian saya: backend Flask yang menyatukan semuanya.

`«Tunjuk baris 1-13»`

Ucapkan:

> Di baris 8, kunci sesi dibuat acak setiap kali server dinyalakan. Efek
> sampingnya, setelah restart cookie lama tidak berlaku dan pengguna otomatis
> mendapat sesi kosong. Di baris 11 dan 12 ada parameter 467 dan 2, dan di
> baris 13 ada tempat penyimpanan state di memori. Ini bukan database, jadi
> hilang kalau server restart, dan tidak cocok untuk banyak proses.

`«Tunjuk baris 28-36»`

Ucapkan:

> Fungsi `get_state` membuat atau mengambil state berdasarkan id sesi di
> cookie. Perhatikan baris 36: ia mengembalikan objek yang sama, bukan salinan.
> Ini sengaja, supaya perubahan di endpoint langsung tersimpan tanpa perlu
> fungsi simpan.

`«Tunjuk baris 47-60»`

Ucapkan:

> Fungsi `summary` mengubah state menjadi ringkasan yang aman dikirim ke
> browser. Kunci privat tidak pernah masuk ke ringkasan ini.

`«Tunjuk baris 105-167»`

Ucapkan:

> Endpoint persiapan data memvalidasi lima field, masing-masing wajib terisi
> dan maksimal 200 karakter, lalu umur antara nol sampai 130. Setelah itu
> kelima nilai digabung menjadi satu dokumen teks. Di baris 156 sampai 159,
> ciphertext lama dikosongkan karena data baru membuat enkripsi lama tidak
> berlaku. Tapi hasil handshake dan kunci lama sengaja tidak dihapus, supaya
> pengguna tidak perlu mengulang pertukaran kunci.

`«Tunjuk baris 179, lalu 181»`

Ucapkan:

> Di endpoint handshake, import modul kripto sengaja diletakkan di dalam
> fungsi, bukan di atas file. Tujuannya supaya kalau modul kripto belum siap,
> kesalahannya bisa ditangkap dan dijawab dengan kode 409, bukan membuat
> seluruh server gagal menyala.

`«Tunjuk baris 195-209»`

Ucapkan:

> Perhatikan response-nya: yang dikirim ke browser hanya status "cocok atau
> tidak" di baris 203, bukan nilai rahasianya. Nilai rahasianya tetap di server.

`«Tunjuk baris 230-236, 341-342, 364-365»`

Ucapkan:

> Tiga penjaga urutan ada di sini: enkripsi menolak kalau data atau handshake
> belum ada, transmisi menolak kalau belum enkripsi, dan dekripsi menolak kalau
> belum transmisi. Ini alasan demo kita tidak bisa dilompati.

`«Tunjuk baris 317-320»`

Ucapkan:

> Endpoint detail kriptografi hanya mengirim kunci publik, ciphertext, dan
> status. Kunci privat tidak pernah keluar dari server. Ini poin keamanan yang
> ingin kami tonjolkan.

`«Tunjuk baris 389»`

Ucapkan:

> Verifikasi dekripsi dilakukan dengan membandingkan teks hasil dekripsi
> dengan dokumen asli secara penuh. Bukan kemiripan, tapi kesamaan penuh.

`«Tunjuk baris 411-412»`

Ucapkan:

> Terakhir, reset. Dict-nya dikosongkan lalu diisi ulang, bukan diganti
> variabelnya, karena referensi dict ini yang disimpan di tempat penyimpanan
> state.

### 2.7 `static/js/app.js` — 60 detik

`«Buka static/js/app.js»`

Ucapkan:

> Sisi browser ada di file ini. Baris 21 sampai 61 membungkus `fetch`: kalau
> server mati, pesannya beda dengan kalau servernya membalas error. Perhatikan
> baris 54: pengecekan dilakukan dua kali, yaitu status HTTP dan field
> `success`, supaya kegagalan logika yang dikirim dengan status 200 tetap
> terdeteksi.

`«Tunjuk baris 92-102»`

Ucapkan:

> Fungsi `runAction` adalah pusat penanganan error: tombol dinonaktifkan
> sementara, kesalahan ditampilkan sebagai notifikasi, dan tombol dinyalakan
> lagi di blok `finally` supaya tidak pernah tertinggal mati.

`«Tunjuk baris 222-240, lalu 248-262»`

Ucapkan:

> Di baris 222 sampai 240, tombol diatur berdasarkan status dari server.
> Ini untuk kenyamanan; keamanan tetap di backend. Dan di baris 248 sampai 262,
> teks ditampilkan memakai `textContent`, bukan `innerHTML`, supaya isi dari
> server tidak bisa disisipi HTML.

### 2.8 `main.py` — 30 detik

`«Buka main.py»`

Ucapkan:

> Versi terminal memakai fungsi kriptografi yang sama, jadi tidak ada logika
> yang diduplikasi. Bedanya hanya dua: parameter 467 dan 2 didefinisikan ulang
> supaya CLI bisa jalan tanpa Flask, dan kunci ElGamal dibuat di menu satu
> bersamaan dengan handshake, sedangkan di web dibuat saat enkripsi.

---

## BAGIAN 3 — Penutup

Ucapkan:

> Sebagai kesimpulan, sistem ini berhasil melakukan pertukaran kunci
> Diffie-Hellman, enkripsi dan dekripsi ElGamal, serta memverifikasi bahwa
> dokumen yang diterima rumah sakit persis sama dengan yang dikirim klinik.
> Seluruh algoritma ditulis manual tanpa library kriptografi.
>
> Ada tiga batasan yang kami sadari dan kami cantumkan di README. Pertama,
> parameter 467 sangat kecil; implementasi produksi memakai modulus minimal
> 2048 bit. Kedua, Diffie-Hellman tanpa autentikasi rentan serangan
> man-in-the-middle, dan nilai rahasianya belum kami pakai untuk mengenkripsi
> kanal. Ketiga, transmisi hanya simulasi lokal. Sistem ini untuk pembelajaran,
> bukan untuk data pasien sungguhan.
>
> Terima kasih.

---

# Lampiran A — Angka kunci dan rumus

```text
p = 467      g = 2      (didefinisikan di app.py baris 11-12 dan main.py 18-19)
Sampel EHR   = 119 byte -> 119 blok ciphertext
Mapping byte = byte + 1  (1..256), karena itu p harus > 256
Private key DH = acak 2..p-2      Public key = g^private mod p
Private key ElGamal x             Public key y = g^x mod p
```

```text
Diffie-Hellman          ElGamal
A = g^a mod p           Enkripsi:  c1 = g^k mod p
B = g^b mod p                      c2 = m · y^k mod p
S = B^a = A^b mod p     Dekripsi:  s  = c1^x mod p
                                   m  = c2 · s^-1 mod p
```

Contoh terverifikasi:

```text
DH        a=5, b=7            -> A=32, B=128, S=416 (kedua sisi sama)
          cek: 2^35 mod 467 = 416
mod_exp   mod_exp(2, 5, 467)  -> 32
egcd      extended_gcd(3,11)  -> (1, 4, -1)   cek: 3·4 + 11·(-1) = 1
inverse   mod_inverse(3, 11)  -> 4            cek: 3·4 = 12 ≡ 1 (mod 11)
ElGamal   x=127, k=53, huruf A (m=66)
          y=132, c1=399, s=358, invers=437, c2=278
          dekripsi: 278 · 437 mod 467 = 66 -> 'A'
Miler-Rabin 467: 466 = 233 × 2, 2^233 mod 467 = 466 = n-1
```

Fakta parameter 467: prima, > 256, safe prime (467 = 2×233+1, 233 prima),
2 primitive root dengan orde penuh 466. Bukan angka standar.

---

# Lampiran B — Kalau ditanya (jawaban satu-dua kalimat)

| Pertanyaan | Jawaban |
|---|---|
| Kenapa 467? | Prima, > 256, safe prime, dan 2 primitive root orde penuh 466. Bukan standar; 347 juga memenuhi syarat. |
| Apakah aman? | Tidak untuk produksi. 9 bit vs minimum 2048 bit. |
| Shared secret DH dipakai apa? | Hanya didemonstrasikan sama; enkripsi data memakai ElGamal. |
| Kenapa ElGamal tidak pakai `mod_exp` Aldo? | ElGamal memakai `pow()` dan Miller-Rabin sendiri; `mod_exp` dipakai DH. Keduanya terbukti sama lewat unit test. |
| Kenapa ciphertext lebih besar? | Tiap byte jadi dua angka (c1, c2). |
| Kenapa hasil enkripsi berubah tiap klik? | k dan kunci dibuat acak baru; hasil dekripsi tetap sama. |
| State hilang setelah restart? | Disimpan di dict memori `DEMO_STATES`, bukan database. |
| Bug apa yang ditemukan? | Kunci publik DH bisa jatuh di p-1 → handshake gagal 0,43%; sudah diperbaiki dengan perulangan + regression test. |
| Bagian Aldo apa? | `math_utils.py`: `mod_exp`, `extended_gcd`, `mod_inverse`, `is_prime` + pengujiannya. |
| Bagian Erlinda apa? | `elgamal.py` dan `ehr_data.py`: kunci, enkripsi, dekripsi, konversi UTF-8. |

---

# Lampiran C — Perintah

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe app.py      # http://127.0.0.1:5000
.\.venv\Scripts\python.exe main.py     # CLI
```

Cek internet sebelum demo: Bootstrap dimuat dari CDN. Kalau status kosong,
server kemungkinan restart — ulangi dari Prepare EHR.

---

# Lampiran D — Rujukan dokumen lain

- [demo-guide.md](./demo-guide.md) — detail alur demo + tabel tanya-jawab
- [web-flow.md](./web-flow.md) — alur request web dari sisi browser
- [code-walkthrough.md](./code-walkthrough.md) — seluruh kode per baris
- [walkthrough-oryza-aldo.md](./walkthrough-oryza-aldo.md) — bagian Oryza & Aldo, per baris
- [math-engine.md](./math-engine.md) — dokumentasi math engine dari Aldo
