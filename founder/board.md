# Ringkasan dewan: Zenta 汉 (akses web Rp30.000/bulan)

## Suara
**3 FUND IF, 0 FUND, 0 PASS.** Skor rata-rata: **4,3/10** (Offers 4, Monopoly 3, Product 6).

Tidak ada anggota yang menolak, dan tidak ada yang mendanai begitu saja. Produknya dinilai nyata, tetapi bisnisnya belum terbukti.

## Risiko yang disebut lebih dari satu anggota (urut paling berbahaya)
1. **Tidak ada satu janji hasil yang jelas, jadi penawaran hanya "akses isi" (komoditas).** (Offers, Monopoly, Product) Tanpa bukti orang lulus/naik tingkat HSK dan tanpa satu kalimat "untuk siapa, hasil apa, berapa lama", Rp30.000 dibandingkan dengan semua materi gratis.
2. **Belum ada jalur menjangkau pembeli.** (Offers, Monopoly) Sumber 100 pelanggan pertama belum diketahui; belum ada pelanggan berbayar; kode undangan membatasi pertumbuhan.
3. **Harga Rp30.000 (sekitar USD 1,9) terbaca sebagai harga komoditas.** (Offers, Monopoly, Product) Dewan sepakat: boleh jadi **harga uji awal, bukan harga akhir**. Margin tidak bisa dihitung karena biaya server, n8n, email, dan pembayaran belum diketahui.
4. **Satu titik gagal: akun, verifikasi, dan pengumuman bergantung pada satu webhook n8n.** (Monopoly, Product) Belum ada cara bayar yang diketahui.
5. **Celah isi.** (Offers, Product) Tata bahasa hanya HSK 2-4; kosakata HSK 5 dan 6 hanya 183 dan 50 kata. Jangan menjanjikan "HSK 1-6" sebelum ini ditutup atau diakui.

Risiko dari satu anggota: tidak ada pembeda yang bertahan (Monopoly, bahan HSK tersedia umum); `index.html` sekitar 12,9 MB, berat untuk ponsel dan kuota (Product).

## Perbedaan pendapat
- **Product (6/10)** paling positif: isi dikurasi, alur belajar lengkap (SRS, simulasi ujian, menulis hanzi), kerja di bagian tak terlihat serius. Bagi lensa ini masalahnya fokus dan kehandalan, bukan produk.
- **Monopoly (3/10)** paling keras: tanpa distribusi dan tanpa rahasia yang tak bisa disalin, ini komoditas. Menetapkan batas: jika 30 pembayar nyata tidak tercapai dalam 60 hari, suaranya menjadi **PASS**.
- **Harga:** Offers dan Monopoly condong menguji harga yang lebih tinggi (mis. Rp60.000-Rp90.000) dengan hasil yang dijanjikan; Product menolak menilai angkanya sebelum ada uji pembayaran nyata. Semua sepakat harus diuji dengan pembayaran sungguhan, bukan pertanyaan "maukah kamu bayar".

## Daftar syarat (untuk dicentang oleh skill lain)
- [ ] **Satu janji satu kalimat** + satu jalur utama (mis. persiapan satu level HSK), fitur lain diturunkan. (consumer, offer)
- [ ] **Pilih satu pasar kecil dulu** (mis. pelajar HSK 1-4 berbahasa Indonesia, satu komunitas/kelas pendiri) lewat kode undangan. (consumer, marketing)
- [ ] **Tulis rahasia dalam satu kalimat** dan satu hal yang tak bisa disalin (metode, data, komunitas, kelas tatap muka). (competitors, offer)
- [ ] **Peta pesaing termasuk yang gratis** dan apa yang pengguna keluhkan, sebelum harga final. (competitors)
- [ ] **Uji harga dengan pembayaran nyata** pada beberapa titik (mis. Rp30.000, Rp60.000, Rp90.000) ke 20-30 calon pembeli. (consumer, pricing)
- [ ] **Hitung ekonomi satuan**: biaya tetap bulanan, biaya per pelanggan, jumlah pelanggan impas. (cfo)
- [ ] **Satu saluran yang terbukti**: 30 pembayar nyata dalam 60 hari dengan biaya per pelanggan tercatat. (marketing, launch)
- [ ] **Bukti hasil**: 5-10 pengguna awal, kemajuan terukur (mis. skor tes tiruan sebelum/sesudah), testimoni. (launch)
- [ ] **Ubah dari akses menjadi hasil** dengan nama, bonus jujur, dan jaminan yang terjangkau setelah biaya diketahui. (offer, cfo)
- [ ] **Alur bayar ujung ke ujung** (bayar, aktif, perpanjang, berhenti) + pemantauan dan cadangan di luar n8n. (ops)
- [ ] **Lima menit pertama diuji ke pelajar nyata**; muat pertama jauh lebih ringan dari 12,9 MB. (ops, launch)
- [ ] **Tutup celah isi** (tata bahasa HSK 1/5/6, kosakata HSK 5-6) atau jual hanya level yang lengkap. (ops, offer)

## Versi terkuat bisnis ini
Bukan "situs kartu HSK seharga Rp30.000". Versi terkuat yang dilihat dewan: **jalur persiapan satu level HSK (misalnya HSK 3 atau 4) untuk pelajar Indonesia, dengan hasil yang dinamai, tes tiruan, bukti kemajuan dari pengguna pertama, dan jaminan**, dijual awalnya ke satu komunitas atau murid tempat belajar pendiri, dan memakai harga Rp30.000 hanya sebagai harga uji sambil menguji harga yang lebih tinggi. Ini berbeda dari yang diajukan: produknya sama, tetapi yang dijual adalah hasil dan jalurnya, bukan akses ke isi. Pertanyaan yang belum terjawab dan menentukan banyak hal: apakah web ini produk utama, atau pelengkap kelas/guru? Jika tempat belajar punya murid, itu bisa menjadi saluran dan pembeda terkuat.

## Pertanyaan terbuka dan skill yang menjawabnya
- Pesaing, termasuk yang gratis, dan harganya: `/founder-competitors`
- Apakah pelajar mau membayar dan pada harga berapa: `/founder-consumer`, lalu `/founder-pricing`
- Biaya tetap dan jumlah pelanggan impas: `/founder-cfo`
