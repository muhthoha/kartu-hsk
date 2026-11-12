# Product lens

Score: 4/10 | Vote: FUND IF

Catatan dasar: dinilai dari fitur "contoh soal HSK ala kertas resmi" di situs Zenta (Rp30.000 per bulan), bukan dari bisnisnya secara keseluruhan. Dari repo: sudah ada "Simulasi ujian kosakata" (pilihan ganda acak, timer, koreksi, analisis kesalahan, tersimpan di perangkat), 1.434 kata, 191 pola tata bahasa (belum ada HSK 1, 5, 6), data goresan hanzi, dan folder audio kecil.

## What is strong
- Pengalaman belajar sudah punya kerangka yang cocok: timer, koreksi per soal, dan daftar kata yang sering salah sudah ada. Soal ujian bisa menyambung ke sana ("salah di soal ini, ini kartu kata yang perlu diulang"). Itu yang tidak dimiliki PDF mentah.
- Pelajar Indonesia mendapat satu tempat untuk belajar dan menguji diri, dengan antarmuka dan terjemahan berbahasa Indonesia.
- Sifat fitur jelas dan bisa dijelaskan dalam satu kalimat: "latihan ujian HSK lengkap, dikoreksi, lalu diarahkan ke kata yang lemah".
- Berkas H31003 sudah menunjukkan bentuk soal (gambar A-F, benar/salah, susun kalimat, tulis hanzi dari pinyin), jadi bentuk antarmukanya bisa dirancang dari kebutuhan nyata.

## What would kill it (the top 3, most dangerous first)
1. Hak atas soal. Berkas H31003 tertulis disusun oleh Hanban / Kantor Pusat Institut Konfusius. Menjual ulang atau menampilkan kertas itu dalam langganan berbayar tanpa izin adalah produk yang dibangun di atas barang milik orang lain. Pembeli, pesaing, atau pemilik hak bisa menghentikannya kapan saja, dan situs ikut tercemar. Status izin penggunaan: belum diketahui, harus diperiksa sebelum satu baris kode ditulis. Alternatif yang bersih adalah soal buatan sendiri dengan format yang sama, tetapi itu pekerjaan konten besar yang butuh orang yang benar-benar menguasai HSK.
2. Pengalaman yang rusak di sambungannya. Berkas yang ada tidak punya kunci jawaban dan tidak punya audio. Ujian mendengar tanpa audio adalah 40 soal yang tidak bisa dikerjakan, dan tanpa kunci jawaban tidak ada koreksi, padahal koreksi adalah inti nilai fitur ini. Soal bergambar butuh gambar yang jelas di ponsel. Jika dikirim setengah jadi (hanya Membaca, tanpa kunci, tanpa audio), lima menit pertama pelanggan adalah kekecewaan. Siapa yang menulis kunci dan merekam audio, dan seberapa teliti: belum diketahui.
3. Ketinggalan zaman. HSK 3.0 diujikan di seluruh dunia mulai 13 Desember 2026, sekitar satu bulan dari sekarang, dengan format berbeda (Level 3: 70 soal, bukan 80). Konten HSK 2.0 yang dibuat sekarang bisa terasa usang begitu pelanggan pertama masuk. Pesaing sudah menawarkan simulasi HSK 3.0. Dan fitur ini tidak menyentuh soal fokus: situs sudah luas (kartu, tata bahasa, bacaan, latihan, menulis), dan menambah kertas ujian penuh untuk satu level adalah satu lagi hal yang harus dijaga, padahal bisnis belum punya satu pelanggan berbayar.

## The questions I would ask the founder
- Apakah Anda punya izin tertulis untuk memakai soal Hanban/Institut Konfusius di produk berbayar? Kalau tidak, siapa yang akan menulis soal sendiri?
- Siapa yang membuat kunci jawaban, dan siapa yang merekam audio? Berapa jam dan berapa biaya? Angkanya belum ada.
- Apakah Anda mau mengirim satu level dulu atau semua HSK 1-6? Level mana yang paling banyak dicari calon pelanggan Anda? (Data permintaan: belum ada.)
- HSK 2.0 atau 3.0? Kalau pelajar Anda mendaftar ujian setelah Desember 2026, mereka butuh format yang mana?
- Mengapa pelanggan membayar Rp30.000 per bulan untuk ini padahal paket pesaing mulai Rp459 ribu per tahun dan ada materi gratis di tempat lain? Apa yang hanya Zenta lakukan (misalnya menyambungkan kesalahan ke kartu kosakata)?
- Satu kalimat: apa yang pelanggan lakukan dengan Zenta setiap hari, dan apakah contoh soal membuatnya lebih jelas atau lebih berantakan?
- Apakah ada satu orang yang sudah mau membayar untuk fitur ini hari ini? Jumlah calon pengguna: belum diketahui.

## If FUND IF: the conditions
1. Hak jelas dulu: izin tertulis untuk soal resmi, atau putuskan membuat soal sendiri (berformat sama, bukan salinan). Tanpa salah satunya, jangan jual.
2. Kirim hanya yang lengkap: satu paket yang punya soal, kunci jawaban, audio, dan koreksi yang menyambung ke kartu kosakata. Tidak ada paket setengah jadi, tidak ada ujian mendengar tanpa suara.
3. Pilih satu format dan satu level untuk rilis pertama, dengan keputusan HSK 2.0 vs 3.0 berdasarkan apa yang dihadapi pelanggan pertama, bukan berdasarkan berkas yang kebetulan ada.
4. Uji dulu pada 5-10 pelajar nyata (pra-jual atau daftar tunggu dengan harga asli) sebelum membangun lebih banyak paket. Cari tahu dulu apakah mereka menyebut fitur ini sebagai alasan membayar.
5. Pasang batas ruang lingkup: fitur ini boleh ditambahkan tanpa mengorbankan inti situs (kartu harian dan kosakata) dan tanpa menambah ketergantungan pada n8n yang belum teruji untuk pelanggan berbayar.
