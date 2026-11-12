# Zenta 汉 (repo: kartu-hsk)

- What it is: sebuah situs belajar Mandarin harian (kartu kosakata HSK, tata bahasa, bacaan, latihan, latihan menulis hanzi) yang menjadi alat pendukung bagi bisnis tempat belajar Mandarin milik pendiri; bisnisnya sendiri belum berjalan, situs dan sistemnya sudah jadi.
- Who it is for: pelajar bahasa Mandarin berbahasa Indonesia yang tertarik belajar Mandarin dan menyiapkan HSK (antarmuka dan terjemahan dalam bahasa Indonesia).
- What it sells, at what price: akses web berlangganan, Rp30.000 per bulan.
- Where and how: online, di zenta.web.id. Masuk dengan akun email + password, verifikasi email, kode undangan saat daftar. Ada fitur pengumuman email dan berhenti berlangganan. Dipasang sebagai PWA (bisa di-install di ponsel).
- Budget and constraints: tidak diketahui (belum disebutkan pendiri). Situs sudah ada; bisnis belum berjalan dan belum ada pelanggan berbayar.

## Fakta dari repo (diperiksa langsung)
- Kosakata: 1.434 kata, HSK 1-6 (HSK 1: 150, HSK 2: 150, HSK 3: 300, HSK 4: 600, HSK 5: 183, HSK 6: 50), tiap kata ada pinyin, arti Indonesia, kalimat contoh.
- Tata bahasa: 191 pola (HSK 2: 44, HSK 3: 47, HSK 4: 100). Belum ada pola HSK 1, 5, 6.
- Ada data audio dan data goresan hanzi (Hanzi Writer / Make Me a Hanzi).
- Backend akun/verifikasi/pengumuman memakai webhook n8n di n8n.zenta.web.id.
## Yang belum diketahui
- Apakah ada kelas/guru (tempat belajar) di luar web, atau web adalah produk utamanya.
- Cara pembayaran, jumlah calon pengguna, biaya server/n8n, sumber pelanggan pertama.

## Fitur yang diusulkan (ronde dewan ke-2)
Pendiri ingin menambahkan **contoh soal HSK** ke situs, seperti berkas terlampir: kertas ujian resmi HSK level 3, kode H31003. Harga tetap Rp30.000 per bulan untuk akses web.

Fakta tentang berkas contoh (dibaca langsung dari PDF 20 halaman):
- Judul: 新汉语水平考试 HSK（三级）H31003. Tercantum "国家汉办/孔子学院总部 编制" (disusun oleh Hanban / Kantor Pusat Institut Konfusius). Format HSK 2.0 lama.
- Isi: Mendengar 40 soal (sekitar 35 menit), Membaca 30 soal (30 menit), Menulis 10 soal (15 menit); total sekitar 90 menit. Termasuk naskah lengkap rekaman mendengar (halaman 14-19).
- Tidak termasuk: kunci jawaban, dan berkas audio rekaman. Soal mendengar memakai gambar (pilih gambar A-F), benar/salah, dan pilihan ganda A-C. Soal membaca: mencocokkan kalimat, mengisi kata, memahami paragraf. Menulis: menyusun kata menjadi kalimat dan menulis hanzi dari pinyin.
- Halaman bergambar (foto) untuk soal mendengar bagian 1.

Fakta pembanding:
- Simulasi ujian yang sudah ada di Zenta, dari kode situs, adalah "Simulasi ujian kosakata": soal pilihan ganda acak dari kosakata (pilih level, 10/30/50 soal), bukan kertas ujian HSK asli.
- HSK 3.0 mulai diujikan di seluruh dunia pada 13 Desember 2026 (sumber: Study Chinese, mengutip pengumuman CLEC). Format HSK 3.0 level 3: mendengar 30, membaca 30, menulis 10 (total 70 soal). Ujian sebelum 13 Desember 2026 masih memakai HSK 2.0 (level 1-6).
- Pesaing yang sudah menawarkan soal ujian: SuperTest (soal ujian asli dan ujian tiruan HSK 1-6, paket berbayar mulai Rp459 ribu per tahun), KaKa Chinese (simulasi ujian, materi gratis tersedia), Study Chinese (simulasi ujian HSK 3.0 level 3-9 dan HSK 2.0 level 3-6 di paket Plus).
