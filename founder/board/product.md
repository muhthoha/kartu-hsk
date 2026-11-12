# Product lens

Score: 6/10 | Vote: FUND IF

Dasar penilaian: brief.md dan pemeriksaan langsung repo (index.html, data/). Tidak ada data pasar, kompetitor, atau biaya; hal-hal itu ditulis sebagai pertanyaan terbuka, bukan angka.

## What is strong

- Isi produknya nyata dan sudah jadi: 1.434 kata HSK 1-6 dengan pinyin, arti Indonesia, dan kalimat contoh; 191 pola tata bahasa; data goresan hanzi; audio. Ini kerja tangan yang membuat produk terasa dikurasi, bukan hasil tempel.
- Bahasa Indonesia sampai ke detail: antarmuka, arti kata, dan penjelasan pola ("Tidak hanya A, tetapi juga B") ditulis untuk pelajar Indonesia. Itu perbedaan pengalaman yang bisa dirasakan dalam lima menit pertama.
- Ada alur belajar, bukan sekadar daftar kata: kartu dengan penjadwalan ulang (SRS), simulasi ujian kosakata dengan timer, hitung mundur ujian dengan target harian, latihan menulis, latihan menjawab HSKK. Ini menjawab satu kebutuhan konkret: menyiapkan HSK.
- Dipasang sebagai PWA, jadi terasa seperti aplikasi di ponsel tanpa toko aplikasi.
- Detail yang tidak terlihat pembeli dikerjakan serius: CSP ketat, escape HTML, verifikasi email, halaman berhenti langganan. Pendiri tidak memotong sudut di bagian yang tidak dilihat pelanggan.

## What would kill it (the top 3, most dangerous first)

1. Tidak ada satu hal yang harus dilakukan dengan sangat baik. Produk melakukan banyak hal (kartu, tata bahasa, bacaan, latihan, menulis, ujian, HSKK) dan pitch satu kalimatnya belum ada. Brief sendiri belum bisa menjawab apakah web ini produk utama atau alat bantu kelas. Tanpa satu janji (misalnya "lulus HSK 3 dalam N bulan"), Rp30.000/bulan dibandingkan dengan semua yang gratis, dan pelajar tidak punya alasan memilih untuk membayar.
2. Pengalaman membayar dan masuk terputus-putus. Alur sekarang: kode undangan, daftar, verifikasi email, login, dan belum ada cara bayar yang diketahui. Setiap sambungan antar sistem (situs, webhook n8n, email) adalah titik patah, dan akun, verifikasi, serta sinkronisasi bergantung pada satu layanan n8n di n8n.zenta.web.id. Bila itu mati atau email verifikasi masuk spam, pelanggan berbayar pertama langsung kecewa. Juga: index.html sekitar 12,9 MB, sehingga muat pertama di ponsel dan kuota pelajar bisa menjadi lima menit pertama yang buruk. Apakah ini di-cache dengan baik di jaringan lambat belum teruji.
3. Isi belum utuh untuk janji "HSK 1-6". Tata bahasa hanya HSK 2-4 (tidak ada HSK 1, 5, 6); kosakata HSK 5 dan 6 hanya 183 dan 50 kata, jauh dari daftar resmi lengkap (angka resmi perlu diverifikasi pendiri). Pembeli HSK 1 atau 5-6 bisa menemukan lubang dalam seminggu, dan bulan kedua adalah saat langganan dibatalkan.

## The questions I would ask the founder

1. Dalam satu kalimat: untuk siapa, dan hasil apa dalam berapa lama? Kalau perlu satu paragraf, mana yang kamu buang?
2. Apa yang dilihat dan dirasakan pengguna baru di lima menit pertama, dari membuka zenta.web.id sampai menyelesaikan satu kartu? Berapa langkah dan berapa detik? Sudah ditonton langsung pada orang asli?
3. Web ini produk utama, atau pelengkap kelas/guru? Kalau pelengkap, apakah Rp30.000 membayar web saja, dan apakah guru bagian dari pengalaman yang sama?
4. Rp30.000/bulan: apa yang akan membuat orang terus membayar di bulan ke-3, bukan hanya bulan pertama? Fitur mana yang berbayar dan mana yang bisa dicoba gratis? Apakah ada uji gratis atau pembelian pertama dengan harga nyata?
5. Siapa pembayarnya (pelajar, orang tua, kantor), dan bagaimana mereka membayar? Metode pembayaran apa yang dipakai sekarang? (belum diketahui)
6. Mengapa kode undangan? Itu membatasi pertumbuhan atau menjadi alat uji? Dari mana 10 pengguna pertama datang?
7. Apa yang terjadi saat layanan n8n mati atau email tidak sampai? Siapa yang tahu, dan siapa yang membalas pelanggan?
8. Berapa biaya tetap bulanan (domain, server, n8n, email) dan berapa pelanggan berbayar agar impas? (belum diketahui; ini untuk CFO)

## If FUND IF: the conditions

Soal harga Rp30.000/bulan: Product lens tidak menilai angkanya sebagai mahal atau murah, karena tidak ada data pasar, harga pesaing, atau kemauan membayar yang diketahui (open question). Yang dinilai adalah apakah pengalamannya pantas ditagih. Rp30.000 (sekitar USD 1,9) adalah harga yang murah untuk dibayar tetapi tetap harga yang menuntut kepercayaan: produk yang menagih harus tidak pernah rusak dan harus punya satu janji jelas. Harga rendah juga memberi sedikit ruang untuk dukungan manual, jadi pengalaman harus berjalan sendiri. Jangan mengubah harga sebelum diuji; uji dulu dengan pembeli sungguhan (lihat syarat 4).

Dana layak diberikan bila:

1. Ada satu janji satu kalimat dan satu jalur utama (misalnya persiapan satu level HSK tertentu) yang ditampilkan paling depan; fitur lain diturunkan atau disembunyikan sampai jalur ini terasa tuntas.
2. Lima menit pertama diuji pada minimal beberapa pelajar baru (jumlahnya ditentukan pendiri) dengan ponsel biasa dan jaringan biasa; muat pertama dibuat jauh lebih ringan dari 12,9 MB, dan alur daftar-verifikasi-masuk-belajar tidak lagi memakai langkah yang tidak perlu.
3. Cara bayar nyata dipasang dan diuji ujung ke ujung (bayar, aktif, perpanjang, berhenti), termasuk apa yang dilihat pelanggan saat gagal, dan ada pemantauan serta cadangan untuk layanan n8n.
4. Uji harga dengan pembayaran sungguhan (pra-jual atau uji dengan harga Rp30.000 pada kelompok kecil), bukan pertanyaan "maukah kamu bayar". Hasilnya, bersama pesaing dan biaya, diteruskan ke pricing dan CFO.
5. Celah isi ditutup atau diakui terang-terangan: tata bahasa HSK 1, 5, 6 dan kosakata HSK 5-6, atau janji dipersempit ke level yang sudah lengkap.
