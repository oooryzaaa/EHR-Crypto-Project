# Walkthrough Fitur Documentation Viewer

Penjelasan per baris untuk lima file yang membentuk halaman `/docs` — fitur
yang membuat dokumen Markdown bisa dibuka dari HP saat presentasi. Formatnya
sama dengan [code-walkthrough.md](./code-walkthrough.md): setiap baris
dijelaskan beserta **alasan kenapa ditulis begitu**.

Nomor baris sesuai kondisi kode saat dokumen ini ditulis.

Peta:

```text
[1] app.py                    route + whitelist dokumen      (baris 1-134)
[2] utils/markdown_lite.py    parser Markdown sendiri         (254 baris)
[3] templates/docs.html       template halaman docs
[4] static/css/docs.css       styling, termasuk responsif HP
[5] templates/base.html       menu sidebar + blok extra_head
```

Alur satu request:

```text
GET /docs/cheatsheet
  -> docs_viewer("cheatsheet")            app.py
  -> read_doc("cheatsheet")               cek whitelist, baca docs/cheatsheet.md
  -> render_markdown(teks)                markdown_lite.render
       -> _inline / _table / _list_block  ubah Markdown jadi HTML
  -> Markup(html)                         tandai sudah aman untuk Jinja
  -> render_template("docs.html")         docs.html + base.html
  -> browser menampilkan artikel
```

---

## [1] `app.py` — route dan whitelist

### Import — baris 1-10

- **1** `import secrets` — sudah ada sebelumnya, untuk `secret_key` dan id sesi.
- **2** `from pathlib import Path` — **kenapa ditambahkan?** Untuk membentuk
  path folder `docs/` secara relatif terhadap lokasi `app.py`, bukan relatif
  terhadap direktori kerja. Kalau memakai string relatif biasa, aplikasi akan
  gagal menemukan dokumen ketika dijalankan dari folder lain.
- **4-7** `from flask import (...)` — **`redirect` dan `url_for` ditambahkan**
  supaya dokumen yang tidak dikenal bisa dialihkan ke halaman default.
- **8** `from markupsafe import Markup` — **ini bagian paling penting.**
  Jinja meng-escape semua variabel yang dirender dengan `{{ }}` secara default.
  Tanpa `Markup`, HTML hasil parser akan tampil sebagai teks mentah
  (`&lt;h1&gt;`), bukan heading. Ini bug yang benar-benar terjadi saat
  pengujian pertama.
- **10** `from utils.markdown_lite import render as render_markdown` —
  **kenapa diberi alias?** Supaya nama `render` yang sangat umum tidak bentrok
  dengan `render_template` Flask dan jelas asalnya saat dibaca.

### Konstanta folder dan daftar dokumen — baris 92-105

- **96** `DOCS_DIR = Path(__file__).resolve().parent / "docs"`
  - `__file__` adalah path `app.py`; `.resolve()` membuatnya absolut.
  - `.parent` adalah folder project.
  - **Kenapa dihitung sekali di module level, bukan di dalam fungsi?** Karena
    nilainya tidak pernah berubah; menghitung ulang setiap request hanya
    membuang waktu.
- **98-105** `DOCS_PAGES` — tuple pasangan `(slug, label)`.
  - **Kenapa tuple, bukan dict?** Urutan tab di UI mengikuti urutan di sini,
    dan `cheatsheet` sengaja ditaruh pertama supaya jadi halaman default.
  - **Kenapa ini merangkap jadi whitelist?** Karena `read_doc` memeriksa nama
    terhadap daftar ini. Efeknya: satu sumber kebenaran untuk "dokumen apa saja
    yang boleh dibuka", jadi tidak ada dua daftar yang bisa berbeda.
  - **Kenapa penting untuk keamanan?** Ini mencegah path traversal. Tanpa
    whitelist, `/docs/../../app` bisa dipakai membaca file di luar `docs/`.

### `read_doc(name)` — baris 108-116

- **109** docstring menyebut "whitelisted", menandai bahwa fungsinya bukan
  sekadar membaca file.
- **110-111** `if name not in {slug for slug, _ in DOCS_PAGES}: return None`
  - **Kenapa set, bukan list?** Pencarian pada set O(1), sedangkan list O(n).
    Perbedaannya kecil di sini, tetapi set menyatakan niat: ini uji keanggotaan,
    bukan urutan.
  - **Kenapa `return None`, bukan lempar exception?** Karena pemanggilnya
    (route) sudah punya perilaku yang diinginkan untuk kasus ini: redirect ke
    halaman default. Exception akan menghasilkan error 500 yang tidak ramah.
- **113-116** `try: ... except OSError: return None`
  - **Kenapa `OSError`?** `read_text` melempar `FileNotFoundError` (turunan
    `OSError`) bila file hilang, dan `PermissionError` bila tidak bisa dibaca.
    Keduanya ditangani sama: anggap tidak ada.
  - **Kenapa tidak dipisah `FileNotFoundError`?** Karena bagi pengguna
    hasilnya sama — halaman dialihkan. Menambah cabang tidak menambah manfaat.

### Route `/docs` — baris 119-134

- **119-120** dua decorator bertumpuk:
  ```python
  @app.get("/docs")
  @app.get("/docs/<name>")
  ```
  **Kenapa dua?** Agar `/docs` (tanpa nama) tetap bekerja dan memakai nilai
  default parameter. Decorator yang lebih dekat ke fungsi dipasang lebih dulu.
- **121** `def docs_viewer(name="cheatsheet"):` — **kenapa default di
  parameter, bukan `if name is None`?** Flask mengisi `<name>` hanya bila ada di
  URL; untuk `/docs`, parameternya tidak dikirim, sehingga nilai default dipakai
  langsung.
- **122** `content = read_doc(name)`.
- **124-125** `if content is None: return redirect(url_for("docs_viewer", name="cheatsheet"))`
  - **Kenapa redirect, bukan `abort(404)`?** Karena pengguna yang salah ketik
    lebih baik diantar ke dokumen utama daripada melihat halaman error.
  - **Kenapa `url_for(...)`, bukan string `"/docs/cheatsheet"`?** Kalau nanti
    URL berubah, hanya definisi route yang perlu diubah. `url_for` juga menangani
    pembentukan URL dengan benar.
- **127-134** `render_template("docs.html", active=name, pages=DOCS_PAGES, content=Markup(...))`
  - **`active=name`** dipakai template untuk menandai tab yang sedang dibuka.
  - **`pages=DOCS_PAGES`** dipakai template untuk membuat daftar tab, sehingga
    menambah dokumen baru cukup mengubah satu tuple di atas.
  - **`Markup(...)`** — komentar di baris 131-132 menjelaskan alasannya: parser
    sudah meng-escape setiap teks yang dibacanya (lihat `html.escape` di
    `markdown_lite.py`), jadi hasilnya aman ditandai sebagai HTML tepercaya.
    **Penting:** `Markup` hanya boleh dipakai untuk string yang kita sendiri
    sudah escape. Kalau dipakai untuk input pengguna mentah, itu celah XSS.

> Kalimat transisi: "Route selesai. Sekarang bagian yang benar-benar mengubah
> Markdown menjadi HTML."

---

## [2] `utils/markdown_lite.py` — parser Markdown (255 baris)

**Kenapa file ini ada.** `requirements.txt` tidak memuat library Markdown, dan
menambah dependency untuk satu halaman dokumentasi tidak sepadan. Parser ini
hanya mendukung konstruksi yang benar-benar dipakai folder `docs/`, memakai
standard library (`html`, `re`).

### Docstring dan import — baris 1-11

- **1-6** docstring menyebut daftar konstruksi yang didukung **dan**
  batasannya. Ini penting supaya orang berikutnya tidak mengira ini parser
  Markdown lengkap.
- **8** `from __future__ import annotations` — membuat anotasi tipe seperti
  `list[dict]` tidak dievaluasi saat runtime, sehingga kompatibel dengan Python
  versi lebih lama tanpa mengubah kode.
- **10** `import html` — untuk `html.escape`. **Ini inti keamanannya:** semua
  teks dari file di-escape sebelum disisipkan ke HTML.
- **11** `import re` — pola baris dikenali dengan regex.

### Pola regex — baris 13-17

- **13** `_FENCE = re.compile(r"^```(\w*)\s*$")` — blok kode, menangkap nama
  bahasa (```python). **Kenapa `re.compile` di module level?** Regex yang sudah
  dikompilasi disimpan kustom, jadi tidak dikompilasi ulang setiap baris.
- **14** `_HEADING = re.compile(r"^(#{1,4})\s+(.*)$")` — heading 1-4.
  **Kenapa hanya sampai 4?** Dokumen di `docs/` tidak memakai `#####`, dan
  membatasi level membuat percabangan di `render` lebih sederhana.
- **15** `_LIST_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")` — tiga
  kelompok: indentasi, penanda (`-`, `*`, atau `1.`), dan isi. Indentasi
  ditangkap karena dipakai untuk menentukan kedalaman nesting.
- **16** `_RULE = re.compile(r"^-{3,}\s*$")` — garis horizontal `---`.
  **Kenapa minimal 3 tanda hubung?** Supaya tidak bentrok dengan tanda minus di
  awal baris biasa.
- **17** `_MD_LINK = re.compile(r"\]\(\.?/?([\w\-]+)\.md(#[^)]*)?\)")` —
  menangkap nama file `.md` dan anchor opsional.

### `_slug(text)` — baris 20-24

- **20** signature, menerima judul heading.
- **22** `re.sub(r"[`*_]", "", text)` — buang penanda format. Tanpa ini,
  heading `` ## `mod_exp` `` akan menghasilkan anchor yang mengandung backtick.
- **23** `re.sub(r"[^\w\s-]", "", text)` — buang tanda baca. **Inilah yang
  membuat `p = 467` menjadi `p-467`**, bukan `p--467`: tanda `=` dibuang
  seluruhnya, bukan diganti tanda hubung.
- **24** `re.sub(r"\s+", "-", text)` — spasi jadi tanda hubung.
- **Kenapa perlu mendekati perilaku GitHub?** Karena anchor di dokumen lain
  (misalnya `[0.5]` di `code-walkthrough.md`) ditulis mengikuti aturan GitHub.
  Kalau slug di sini berbeda, tautan antar dokumen akan meleset.

### `_rewrite_links(text)` — baris 27-34

- **27** signature.
- **30-32** fungsi dalam `replace(match)` — **kenapa fungsi bersarang?**
  `re.sub` membutuhkan callable untuk transformasi dinamis. Nested function
  membuatnya bisa mengakses `match.group` tanpa variabel global.
- **31** `anchor = match.group(2) or ""` — anchor opsional; `None` diganti
  string kosong supaya bisa langsung dipakai di f-string.
- **32** `return f"](/docs/{match.group(1)}{anchor})"` — mengganti
  `](./web-flow.md)` menjadi `](/docs/web-flow)`. **Kenapa perlu?** Karena di
  dalam aplikasi web, file `.md` tidak bisa dibuka langsung; tautan harus
  diarahkan ke viewer.
- **34** `_MD_LINK.sub(replace, text)`.

### `_inline(text)` — baris 37-55

Fungsi ini mengubah markup dalam satu baris. **Kontraknya: `text` sudah
di-escape oleh pemanggil**, jadi fungsi ini hanya menambahkan tag.

- **38** docstring singkat menyatakan kontrak tersebut.
- **39** `spans: dict[str, str] = {}` — penyimpanan sementara.
- **41-44** `def stash(match)` membuat placeholder `\x00N\x00` dan menyimpan
  HTML `<code>` yang sebenarnya.
  **Kenapa perlu trik ini?** Karena inline code harus dilindungi dari
  transformasi berikutnya. Tanpa ini, `` `**bukan bold**` `` akan berubah
  menjadi bold di dalam blok kode. `\x00` dipilih sebagai penanda karena tidak
  mungkin muncul di dokumen biasa.
- **46** `re.sub(r"`([^`]+)`", stash, text)` — **urutan penting:** inline code
  diproses **paling awal**, sebelum bold/italic/link.
- **47** `_rewrite_links(text)` — tautan `.md` diarahkan ke viewer.
- **48** `\*\*([^*]+)\*\*` → `<strong>`. Bold diproses sebelum italic karena
  `**` harus dikenali lebih dulu; kalau tidak, `**x**` akan dibaca sebagai dua
  italic kosong.
- **49** `(?<![\w*])\*([^*\n]+)\*(?![\w*])` → `<em>`.
  - **Kenapa lookbehind `(?<![\w*])` dan lookahead `(?![\w*])`?** Untuk
    memastikan tanda bintang itu benar-benar pembuka/penutup italic, bukan
    bagian dari kata atau bagian dari `**`. Tanpa ini, `a*b` akan berubah jadi
    italic yang salah.
  - **Kenapa `[^*\n]`?** Italic tidak boleh melintasi baris baru.
- **50** `\[([^\]]+)\]\(([^)]+)\)` → `<a href>`. Dijalankan **setelah**
  bold/italic supaya teks tautan yang mengandung bold tetap benar.
- **52-53** mengembalikan placeholder menjadi HTML `<code>` aslinya.
- **55** `return text`.

### `_table(block)` — baris 58-81

- **59-62** memecah tiap baris menjadi sel dengan `strip("|").split("|")`.
  **Kenapa `strip("|")` dulu?** Karena baris tabel Markdown diawali dan
  diakhiri `|`; tanpa dibuang, akan ada sel kosong di kedua ujung.
- **64-67** menentukan baris header: tabel Markdown punya baris pemisah
  (`|---|---|`) di baris kedua. `re.fullmatch(r":?-{2,}:?", ...)` mengenali
  bentuk itu, termasuk varian perataan `:---:`.
  - **Kenapa `len(rows) >= 2`?** Supaya tabel dua baris tanpa pemisah tidak
    salah dibaca.
- **69-72** `cells_html(cells, tag)` — helper untuk membuat `<th>`/`<td>`.
  Setiap sel di-escape lalu lewat `_inline`, sehingga tabel boleh berisi
  inline code dan bold.
- **74** `<div class='table-wrap'>` — **kenapa dibungkus div?** Supaya CSS bisa
  memberi `overflow-x: auto` sehingga tabel lebar bisa digeser di HP tanpa
  merusak layout halaman.
- **75-80** menyusun `<thead>` (bila ada header), `<tbody>`, lalu menutup.

### `_collect_list(lines, start)` — baris 84-126

Tugasnya mengumpulkan item daftar. Ini bagian paling rumit, dan sumber bug
yang saya temukan saat pengujian.

- **85** docstring menyebut "folding indented continuation lines" — baris
  lanjutan yang lebih menjorok dianggap bagian dari item sebelumnya.
- **86** `items = []`, **87** `i = start`.
- **89-91** berhenti bila baris berikutnya bukan item daftar.
- **94-96** menangkap indentasi, penanda, dan teks; lalu maju satu baris.
- **98-112** menyerap baris lanjutan:
  - **100-105** bila ada baris kosong, cari baris tidak kosong berikutnya.
    **Kenapa?** Markdown mengizinkan satu baris kosong di antara item.
  - **107-111** bila baris berikutnya lebih menjorok, lanjutkan; bila item
    daftar baru atau sama indentasinya, berhenti.
  - **114-115** item daftar baru berarti item ini selesai.
  - **117-120** baris yang lebih menjorok digabung ke teks item, dipisah spasi.
    **Kenapa digabung, bukan dijadikan paragraf baru?** Karena di dokumen
    `docs/` baris lanjutan adalah penjelasan lanjutan dari satu poin.
- **122** `break` — baris yang indentasinya tidak lebih dalam menandai akhir item.
- **124** `items.append({"indent": indent, "marker": marker, "text": text})` —
  **kenapa dict, bukan tuple?** Supaya saat pohon dibentuk, tiap node punya
  `children` yang bisa diisi tanpa mengubah struktur data.
- **126** `return items, i` — **kenapa ikut mengembalikan `i`?** Karena
  pemanggil (`render`) perlu tahu sampai baris berapa daftar ini habis.

### `_nest_items(items)` — baris 152-164

- **153** docstring.
- **154** `root = []` — daftar level teratas.
- **155** `stack: list[tuple[int, list[dict]]] = [(-1, root)]` — **kuncinya di
  sini.** Stack berisi pasangan `(indentasi, daftar_anak)`. Nilai awal `-1`
  menjamin item pertama (indentasi ≥ 0) selalu masuk ke `root`.
- **157-159** `for item in items:` lalu
  `while len(stack) > 1 and stack[-1][0] >= item["indent"]: stack.pop()`
  — naik satu level selama indentasi di stack tidak lebih kecil dari item baru.
  Inilah yang membuat daftar bersarang jadi pohon.
- **160-162** membuat node, menempelkannya ke daftar anak teratas, lalu
  mendorong `(indent, node["children"])` ke stack.
  **Kenapa mendorong `children` yang masih kosong?** Karena list di Python
  adalah referensi. Item berikutnya yang lebih menjorok akan menempel ke list
  yang sama, sehingga otomatis menjadi anak node ini.

### `_render_list_tree(nodes)` — baris 129-149

- **131** `parts = []`, **132** `index = 0`.
- **134-136** menentukan tag dari penanda: angka → `<ol>`, selain itu `<ul>`.
- **137-144** loop mengelompokkan node bertipe sama. **Kenapa perlu
  mengelompokkan?** Karena daftar berurut dan tidak berurut bisa berdampingan;
  masing-masing butuh tag pembungkusnya sendiri.
- **140-142** `<li>teks</li>`; bila ada anak, render rekursif dan sisipkan
  **di dalam** `<li>`, yang merupakan struktur HTML yang benar untuk nesting.
- **146** menutup tag.
- **Kenapa rekursif di sini aman?** Karena kedalaman daftar di dokumen hanya
  dua sampai tiga level, jauh dari batas rekursi Python.

### `_list_block(lines, start)` — baris 167-169

Hanya dua baris: kumpulkan item, lalu bentuk pohon dan render.
**Kenapa dipisah jadi fungsi kecil?** Supaya `render` tetap terbaca sebagai
pemindai baris, dan detail daftar tidak mengganggunya.

### `render(markdown)` — baris 172-254

Ini alur utama: memindai baris dari atas ke bawah.

- **174-176** pecah teks jadi baris, siapkan `out` dan indeks `i`.
- **178** `while i < len(lines)` — satu putaran = satu blok.
- **181-182** `_FENCE` cocok? Ini blok kode. **Kenapa blok kode dicek
  pertama?** Supaya isi blok kode tidak dianggap heading atau daftar. Ini yang
  membuat ``` di dalam dokumen tidak mengacaukan struktur.
- **183-194** kumpulkan baris sampai ``` penutup, escape seluruh isinya, lalu
  emit `<pre data-lang='...'><code>...</code></pre>`.
  **Kenapa `html.escape` di sini wajib?** Karena isi blok kode bisa berisi `<`,
  `>`, atau `&` yang kalau tidak di-escape akan merusak HTML.
- **196-197** baris kosong dilewati — pemisah blok.
- **199-208** heading: level dari jumlah `#`, `id` dari `_slug`, isi lewat
  `_inline`. **Kenapa `id` dipakai?** Supaya anchor seperti
  `#05-mengapa-p-467-dan-g-2` bisa bekerja.
- **210-212** `---` jadi `<hr>`.
- **214-219** baris mulai `|` berarti tabel; kumpulkan seluruh blok lalu
  serahkan ke `_table`.
- **221-228** baris mulai `>` berarti kutipan. **Kenapa semua baris digabung
  dengan spasi?** Karena di `docs/` kutipan dipakai untuk kalimat transisi yang
  memang satu paragraf.
- **230-235** item daftar → `_list_block`, yang juga memajukan `i`.
- **237-252** sisa kasus diperlakukan sebagai paragraf. Loop menyerap baris
  berikutnya sampai menemukan baris kosong atau awal blok lain.
  **Kenapa harus memeriksa semua jenis blok di dalam loop paragraf?** Karena
  Markdown tidak mewajibkan baris kosong sebelum heading atau daftar.
- **254** `return "\n".join(out)`.

> Kalimat transisi: "Parser selesai. Sekarang template yang menampilkannya."

---

## [3] `templates/docs.html` — 34 baris

- **1** `{% extends "base.html" %}` — memakai kerangka yang sama dengan halaman
  lain, jadi sidebar, topbar, dan footer otomatis ikut.
- **3** `{% block title %}` — judul tab browser.
- **5-8** `{% block extra_head %}` memuat `docs.css`.
  **Kenapa tidak langsung dimasukkan ke `base.html`?** Karena CSS docs hanya
  dibutuhkan satu halaman. Blok ini juga yang saya tambahkan di `base.html`
  baris 19.
- **10** `{% block content %}`.
- **12-20** `page-heading` — judul halaman dan chip, sama seperti halaman lain
  supaya tampilan konsisten.
- **21-26** `<nav class="docs-tabs">` dengan loop:
  ```jinja
  {% for slug, label in pages %}
  <a href="{{ url_for('docs_viewer', name=slug) }}"
     class="docs-tab {% if active == slug %}active{% endif %}">{{ label }}</a>
  {% endfor %}
  ```
  - **Kenapa `pages` dikirim dari `app.py`?** Agar daftar tab tidak ditulis
    ulang di template. Menambah dokumen cukup mengubah `DOCS_PAGES`.
  - **`active == slug`** memberi class `active` pada tab yang sedang dibuka.
- **28-32** `<article class="panel docs-panel"><div class="docs-content">{{ content }}</div></article>`
  - **Kenapa dibungkus `.docs-content`?** Semua aturan CSS bertumpu pada kelas
    ini, sehingga gaya docs tidak bocor ke halaman lain.
  - **`{{ content }}`** di sini adalah `Markup`, jadi dirender sebagai HTML.
    Kalau lupa `Markup`, seluruh halaman akan tampil sebagai teks mentah.

---

## [4] `static/css/docs.css` — 196 baris

- **5-33** `.docs-tabs` dan `.docs-tab`
  - **`flex-wrap: wrap`** — supaya enam tab turun ke baris berikutnya di HP,
    bukan memaksa layar melebar.
  - **`border-radius: 999px`** — membuat tab berbentuk pil.
  - **`.docs-tab.active`** memberi latar biru, penanda halaman aktif.
- **35-37** `.docs-panel { overflow-x: hidden; }` — mencegah panel melebar
  karena isi panjang.
- **39-45** `.docs-content` — dasar tipografi, plus
  `overflow-wrap: anywhere` **untuk memastikan kata panjang seperti path file
  tidak merusak layout di layar sempit.**
- **47-74** heading h1-h4 — ukuran bertingkat, h1 dan h2 diberi garis bawah
  sebagai pemisah bagian.
- **76-89** paragraf, `strong`, dan link.
- **91-99** daftar dengan indentasi kiri.
- **101-112** `blockquote` diberi latar biru muda dan batang kiri.
  Ini yang membuat kalimat transisi dan peringatan mudah terlihat.
- **114-139** blok kode dan inline code
  - blok `pre` berlatar gelap (`#0f1a2e`) dengan `overflow-x: auto`, jadi
    baris panjang bisa digeser.
  - `pre code` mereset latar, supaya tidak dobel dengan `code` biasa.
- **141-145** garis pemisah.
- **147-171** `.table-wrap` dengan `overflow-x: auto` dan
  `-webkit-overflow-scrolling: touch` — **kunci tampilan di HP**: tabel lebar
  bisa digeser dengan jari tanpa menggeser seluruh halaman.
- **174-190** `@media (max-width: 760px)` — di layar kecil, font mengecil
  (15px → 14px), heading mengecil, tab lebih rapat, dan `pre` lebih kecil.
  **Kenapa 760px?** Supaya tablet kecil dan HP sama-sama masuk.

---

## [5] `templates/base.html` — dua tambahan kecil

- **19** `{% block extra_head %}{% endblock %}`
  **Kenapa ini perlu?** Tanpa blok ini, template anak tidak punya tempat
  menyisipkan `<link>` tambahan. `docs.html` memakainya di baris 5-8.
  Blok ini sengaja ditaruh **setelah** `style.css`, supaya CSS khusus halaman
  bisa menimpa aturan umum bila perlu.
- **62-66** tautan menu di sidebar:
  ```jinja
  <a href="{{ url_for('docs_viewer') }}"
     class="nav-link-custom {% if request.endpoint == 'docs_viewer' %}active{% endif %}">
      <span class="nav-icon">✎</span>
      Documentation
  </a>
  ```
  - **`request.endpoint == 'docs_viewer'`** — Flask mengisi `request.endpoint`
    dengan nama fungsi view. Dipakai untuk menandai menu aktif.
  - **Kenapa ditaruh paling bawah?** Dokumentasi adalah halaman pendukung,
    bukan bagian alur demo, jadi tidak boleh mengganggu urutan Dashboard →
    Clinic → Cryptography → Hospital.

---

## Bug yang ditemukan saat pengujian

Ada dua bug nyata, dan keduanya layak diketahui kalau penguji bertanya
"apa kendala saat mengerjakan fitur ini".

### 1. Jinja meng-escape HTML hasil parser

**Gejala.** Halaman `/docs` menampilkan teks mentah
`&lt;h1 id=&#39;script-demo...&#39;&gt;` alih-alih heading sungguhan.

**Penyebab.** Jinja meng-escape semua variabel `{{ }}` secara default — fitur
keamanan, bukan bug. Parser sudah meng-escape isi file, tetapi HTML hasilnya
masih dianggap teks biasa oleh Jinja.

**Perbaikan.** Kirim hasilnya sebagai `Markup(...)` di `app.py` baris 127-134,
dengan komentar yang menjelaskan **kenapa itu aman**: karena
`markdown_lite` sudah memanggil `html.escape` pada setiap teks sebelum
disisipkan.

**Verifikasi.** Sebelum perbaikan: 0 elemen `<h1>` asli, 4 `&lt;h2`.
Sesudah: 6 `<h1>`, 4 `<h2>`, 15 `<h3>`, 0 sisa ter-escape.

### 2. Daftar berurut dan bersarang salah struktur

**Gejala.** `1. satu` menghasilkan `</ul>` alih-alih `</ol>`, dan daftar
bersarang menghasilkan `<ul><li>a<ul> b</li></ul></ul>` — tag tidak seimbang.

**Penyebab.** Versi pertama memakai satu loop datar yang melacak level dengan
counter. Pendekatan itu rapuh: menutup dan membuka tag di loop yang sama
mudah menghasilkan urutan salah saat jenis daftar berganti atau indentasi
turun lebih dari satu level.

**Perbaikan.** Dipecah jadi tiga langkah kecil:
`_collect_list` (kumpulkan item) → `_nest_items` (bentuk pohon via stack) →
`_render_list_tree` (render rekursif). Satu langkah satu tanggung jawab.

**Verifikasi.** `1. satu\n2. dua` → `<ol><li>satu</li><li>dua</li></ol>`, dan
`- a\n  - b` → `<ul><li>a<ul><li>b</li></ul></li></ul>`.

---

## Kalau ditanya penguji

**"Kenapa tidak pakai library Markdown seperti `markdown` atau `mistune`?"**
Karena `requirements.txt` tidak memuatnya, dan menambah dependency untuk satu
halaman dokumentasi tidak sepadan. Parser ini hanya 255 baris dan hanya
mendukung konstruksi yang dipakai folder `docs/`.

**"Kenapa menambahkan fitur docs, padahal tidak diminta?"**
Dokumen demo sudah banyak jumlahnya, dan saat presentasi lebih praktis
membukanya dari HP daripada mengingat isinya. Fitur ini tidak mengubah alur
kriptografi sama sekali — sudah diverifikasi bahwa prepare → handshake →
encrypt → transmit → decrypt tetap menghasilkan `verified: True`.

**"Apakah aman?"**
Tiga lapis. Pertama, nama dokumen di-whitelist lewat `DOCS_PAGES`, sehingga
path traversal seperti `/docs/../app` menghasilkan 404 atau redirect. Kedua,
setiap teks di-escape dengan `html.escape` sebelum disisipkan, jadi file
Markdown tidak bisa menyuntikkan `<script>`. Ketiga, `Markup` hanya dipakai
untuk hasil parser yang sudah di-escape, bukan untuk input mentah.

**"Bagaimana menambah dokumen baru?"**
Buat file di `docs/`, lalu tambahkan satu baris `(slug, label)` ke
`DOCS_PAGES` di `app.py` baris 98-105. Tab dan routing menyesuaikan otomatis.

**"Kenapa nomor baris di dokumen lain bisa meleset?"**
Karena setiap kali file kode diedit, nomor baris bergeser. Contoh nyata:
penghapusan satu baris kosong di `crypto/diffie_hellman.py` menggeser seluruh
referensi di dokumen lain, dan itu sudah diperbaiki. Sebaiknya nomor baris
disinkronkan ulang setelah edit terakhir sebelum demo.
