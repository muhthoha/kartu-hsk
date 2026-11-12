# Ringkasan dewan, ronde 2: fitur "contoh soal HSK" (seperti berkas H31003)

Ronde 1 (bisnis secara keseluruhan) ada di `founder/archive/round1-bisnis/`. Ronde ini menilai satu usulan: menambahkan contoh soal HSK ke Zenta, seperti kertas ujian HSK level 3 terlampir.

## Suara
**2 PASS, 1 FUND IF.** Skor rata-rata: **3,3/10** (Offers 3 PASS, Monopoly 3 PASS, Product 4 FUND IF).

PASS di sini berarti: **untuk fitur dalam bentuk yang diusulkan** (memasang kertas ujian itu apa adanya). Ketiganya sepakat fitur ini bisa menjadi FUND IF kalau diubah bentuknya (lihat paragraf terakhir). Ini hasil yang jelas, bukan kegagalan.

## Risiko yang disebut ketiganya (urut paling berbahaya)
1. **Hak atas soalnya.** Berkas H31003 tertulis "国家汉办/孔子学院总部 编制" (disusun oleh Hanban / Kantor Pusat Institut Konfusius), jadi bukan milik Anda. Menampilkan atau menjual akses ke salinannya dalam langganan berbayar tanpa izin atau lisensi bisa membuat konten diturunkan dan mencemari seluruh situs. Status izin pemakaiannya belum diketahui; saya tidak memeriksa ketentuan penggunaan berkas itu. Ini harus dijawab sebelum satu baris kode ditulis.
2. **Produknya tidak lengkap dan formatnya hampir usang.**
   - Berkas tidak memuat kunci jawaban dan tidak ada audio, padahal 40 dari 80 soal adalah mendengar. Tanpa kunci tidak ada koreksi, dan tanpa audio separuh ujian tidak bisa dikerjakan.
   - Itu format HSK 2.0 (80 soal untuk level 3). HSK 3.0 mulai diujikan 13 Desember 2026 dengan format baru (level 3: 70 soal).
3. **Tidak ada pembeda dan belum ada bukti permintaan.** SuperTest, KaKa Chinese, dan Study Chinese sudah menawarkan soal atau simulasi ujian. Belum ada pelanggan berbayar, dan soal ujian tidak mendatangkan pelanggan pertama.

## Perbedaan pendapat
- **Product (4, FUND IF)** paling positif: kerangka belajar sudah ada (timer, koreksi, daftar kata yang sering salah), jadi soal bisa disambungkan ke kartu ulang. Syaratnya paket harus lengkap.
- **Monopoly (3, PASS)** paling keras: satu kertas ujian tanpa kunci dan tanpa audio hanya barang pelengkap yang bisa dijiplak dalam sebulan. Satu-satunya pembeda yang mungkin hidup: soal yang terhubung ke kosakata dan tata bahasa Zenta sendiri.
- **Offers (3, PASS)** melihat sisi baiknya: ada urgensi jujur karena peralihan ke HSK 3.0, dan soal berformat ujian paling dekat dengan hasil yang dibeli. Tetapi penawarannya harus "hasil bernama + jaminan", bukan "akses soal", dan harganya mungkin perlu di atas Rp30.000 untuk paket persiapan ujian.

## Daftar syarat (untuk dicentang skill lain)
- [ ] **Hak jelas dulu:** izin tertulis dari pemegang hak, **atau** tulis soal sendiri bergaya HSK (bukan salinan kertas Hanban). Tanpa salah satunya, jangan jual.
- [ ] **Kirim hanya paket lengkap:** soal, kunci jawaban, skor otomatis, audio untuk bagian mendengar, dan pembahasan singkat dalam bahasa Indonesia. Tidak ada ujian mendengar tanpa suara. (ops, launch)
- [ ] **Sambungkan ke aset Zenta:** salah di soal = kartu kosakata dan pola tata bahasa yang perlu diulang. Ini pembeda yang sulit dijiplak. (offer)
- [ ] **Pilih satu level dan satu format:** disarankan HSK 3.0 level 3, atau dua format dengan label jelas, ditentukan dari kebutuhan pelanggan pertama, bukan dari berkas yang kebetulan ada. (consumer)
- [ ] **Uji permintaan sebelum membangun:** daftar tunggu atau pra-penjualan dengan harga nyata ke 5-10 pelajar. Batas jumlah pendaftar untuk lanjut harus Anda tentukan lebih dulu; datanya belum ada. (consumer, pricing)
- [ ] **Penawaran, bukan fitur:** beri nama, hasil terukur (skor kesiapan), jaminan yang sanggup ditanggung CFO, dan uji harga di atas Rp30.000 untuk paket persiapan ujian dengan batas waktu jujur. (offer, pricing, cfo)
- [ ] **Jalur 100 pelanggan pertama tertulis,** dengan biaya per pelanggan. (marketing)
- [ ] **Jangan mengorbankan inti situs** dan jangan menambah ketergantungan pada n8n yang belum teruji untuk pelanggan berbayar. (ops)
- [ ] **Hitung biaya:** jam kerja dan biaya kunci jawaban, rekaman audio, server, dan n8n; margin Rp30.000. (cfo)

## Versi terkuat fitur ini
Bukan "kertas ujian HSK resmi di dalam situs". Versi terkuat yang dilihat dewan: **set latihan HSK 3.0 level 3 yang Anda tulis sendiri**, berformat ujian, lengkap dengan kunci jawaban, audio, dan pembahasan berbahasa Indonesia, dan setiap kesalahan otomatis menjadi kartu kosakata atau pola tata bahasa untuk diulang. Soalnya milik Zenta, jadi bisa dilindungi, dan terhubung ke 1.434 kata dan 191 pola Anda, sesuatu yang tidak dimiliki pesaing yang hanya menjual PDF. Berkas H31003 tetap berguna sebagai **contoh bentuk soal** untuk menulis soal sendiri, selama isinya tidak disalin.

## Koreksi untuk panel pembeli sebelumnya
Pitch di panel 20 pembeli menyebut "simulasi", dan kelima pembeli menyebutnya sebagai alasan membeli. Setelah memeriksa kode situs, simulasi yang ada saat ini adalah **"Simulasi ujian kosakata"**: soal pilihan ganda acak dari kosakata dengan timer dan koreksi, bukan kertas ujian HSK. Jadi alasan beli di panel itu bersandar pada janji yang lebih besar dari produknya. Hasil panel (25% beli) sebaiknya dibaca dengan catatan ini; ulangi panel dengan pitch yang tepat sebelum memakainya untuk keputusan harga.

## Pertanyaan terbuka dan skill yang menjawabnya
- Pemegang hak dan izin soal, atau biaya menulis soal sendiri: dijawab Anda; biayanya `/founder-cfo`
- Berapa pelajar yang menanti latihan soal, dan mau bayar berapa: `/founder-consumer`, lalu `/founder-pricing`
- Apakah ini penawaran tersendiri dengan harga di atas Rp30.000: `/founder-offer`
