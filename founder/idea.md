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
