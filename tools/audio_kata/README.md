# Audio kata (suara sintetis MeloTTS)

Pembuat MP3 untuk **setiap kata** di situs: HSK 2.0, HSK 3.0, dan kosakata teknis (keuangan, pertambangan dan smelter, bandara).
Hasilnya ada di `audio/kata/`, satu berkas per kata (hanzi + pinyin).

## Lisensi dan asal suara
- Model suara: **MeloTTS zh_en** dari MyShell.ai, lisensi **MIT** (bebas dipakai, termasuk komersial), dalam format ONNX dari proyek sherpa-onnx (`vits-melo-tts-zh_en`).
- Hasil suara dibuat sendiri di mesin lokal, tidak memakai layanan daring dan tidak menyalin rekaman siapa pun.
- Pemeriksa otomatis (SenseVoice, hanya untuk mengecek, tidak ikut terbit): `sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17`.
- Suaranya sintetis, bukan penutur asli. Nada kata satu suku (terutama nada 2 dan 3) bisa terdengar kurang tegas. Disarankan ditinjau guru/penutur asli.

## Cara kerja singkat
1. Bacaan diambil dari **pinyin di situs** (bukan ditebak dari hanzi), jadi kata berbacaan ganda (还 hái / huán) selalu benar. Sandhi nada ketiga diterapkan.
2. Kata diucapkan dalam konteks ("kata, kata.") lalu satu salinan dipotong tepat memakai durasi per token dari model, karena kata pendek yang diucapkan sendirian sering terdengar lemah.
3. Hasil dikenali ulang dengan SenseVoice dan dibandingkan dengan pinyin; bila tidak cocok, dicoba kandidat lain (mode dan seed berbeda). Nada 1 dan 4 pada kata satu suku juga dicek lewat pitch (F0).
4. Entri dua bacaan ("cháng / zhǎng", "不能 / 不可以") diucapkan berurutan dengan jeda.
5. Dikodekan mono, 22,05 kHz, 40 kbps, kenyaringan disamakan (sekitar 2 sampai 4 KB per kata).

## Nama berkas
`audio/kata/<kode>.mp3`, kode = `kah(hanzi + "|" + pinyin)` (hash 53-bit, base 36; lihat `kah.py`, harus sama dengan `kaH()` di `index.html`).
Dengan cara ini tidak ada daftar kata di berkas publik (isi HSK 3.0 dan teknis baru dikunci di server).
Kunci memakai pinyin persis seperti di data kartu: bila pinyin sebuah kata diubah, audionya harus dibuat ulang.

## Menjalankan ulang
```
pip install numpy scipy onnxruntime        # ffmpeg juga dibutuhkan (libmp3lame)
# unduh dan ekstrak dua model dari rilis k2-fsa/sherpa-onnx di GitHub:
#   tts-models/vits-melo-tts-zh_en.tar.bz2
#   asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2
python3 tools/audio_kata/buat_audio_kata.py --daftar kata.json \
    --model <folder>/vits-melo-tts-zh_en --asr <folder>/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17 \
    --keluar audio/kata --bagian 0 --dari 2      # jalankan juga --bagian 1 secara paralel
```
`kata.json` = `[[hanzi, pinyin], ...]` (isi penuh HSK 3.0 dan teknis ada di server, bukan di repo; minta berkasnya ke pemilik).
Proses dapat dilanjutkan; kata yang MP3-nya sudah ada dilewati. Kecepatan sekitar 1,5 detik per kata per proses di CPU biasa.

## Di situs
Tombol "Dengar" pada kartu kata memutar `audio/kata/<kode>.mp3`; bila berkas tidak ada atau gagal dimuat, memakai suara bawaan peramban (`kwPlay` di `index.html`).
Tombol kalimat contoh HSK 3.0 (`h3Sen`) memutar `audio/kalimat/<kode>.mp3` bila kodenya ada di `audio/kalimat/index.json`; bila tidak, memakai audio kalimat lama (`AU`, audio HSK 2.0) bila ada, lalu suara peramban. MeloTTS didahulukan dari `AU` atas keputusan pemilik (23 Nov 2026).
Latihan 练习 > Dengar & pilih untuk HSK 5 (`lDe`, kode level 7) memutar MP3 yang sama dan hanya membuat soal dari kalimat yang kodenya ada di indeks. Daftar kode dimuat sekali oleh `ksMuat()` (dipakai juga HSK 3.0). Bila daftar gagal dimuat, soal HSK 5 kembali memakai suara Mandarin perangkat; tanpa suara itu tampil catatan.

## Audio kalimat contoh (HSK 3.0 dan HSK 5)
Status: 3.600 dari 3.600 kalimat HSK 3.0 (semua level) punya MP3. 18 di antaranya tidak lolos pemeriksa otomatis, lalu didengarkan pemilik dan disetujui (23 Nov 2026), jadi ikut dimasukkan. HSK 5 (1.258 kalimat contoh yang dipakai Dengar & pilih, 6 sampai 16 hanzi): 917 memakai MP3 HSK 3.0 yang sudah ada (kalimat sama), 341 dibuat baru. 4 dari yang baru tidak lolos pemeriksa otomatis, lalu didengarkan pemilik dan disetujui (23 Nov 2026). Jadi `audio/kalimat/` berisi 3.941 MP3 dan semua 1.258 kalimat HSK 5 punya rekaman. Kalimat kosakata teknis belum.
Kode berkas = `kah("s|" + hanzi kalimat)`, jadi situs tidak perlu pinyin kalimat dan tidak ada daftar kalimat di berkas publik.
```
# 1. pinyin kalimat: kata utama dari pinyin kartu, sisanya otomatis; CSV tinjauan berisi yang ditandai ragu
python3 tools/audio_kata/pinyin_kalimat.py --data /jalur/hsk3-penuh.json --model <folder>/vits-melo-tts-zh_en \
    --keluar kalimat.json --tinjau tinjau.csv
# (opsional) isi kolom "p2" di kalimat.json untuk kalimat yang pinyinnya dikoreksi; p2 dipakai bila ada
# 2. audio (boleh paralel dengan --bagian 0/1 --dari 2)
python3 tools/audio_kata/buat_audio_kalimat.py --daftar kalimat.json --model <folder>/vits-melo-tts-zh_en \
    --asr <folder>/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17 --keluar audio/kalimat
# 2b. coba lagi yang belum lolos dengan variasi suara tambahan (berkas diganti hanya bila hasil baru lolos)
python3 tools/audio_kata/buat_audio_kalimat.py --daftar kalimat.json --model <folder>/vits-melo-tts-zh_en \
    --asr <folder>/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17 --keluar audio/kalimat --ulangi
# 2c. kalimat yang pinyinnya dikoreksi manusia (koreksi_pinyin_kalimat.json): buat ulang, berkas lama ditimpa
python3 tools/audio_kata/buat_audio_kalimat.py --koreksi tools/audio_kata/koreksi_pinyin_kalimat.json \
    --model <folder>/vits-melo-tts-zh_en --asr <folder>/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17 --keluar audio/kalimat
# 3. indeks, lalu naikkan angka ?v= pada fetch("audio/kalimat/index.json?v=5") di index.html (ksMuat)
python3 tools/audio_kata/buat_audio_kalimat.py --keluar audio/kalimat --indeks
```
Hasil 3.600 kalimat: 3.553 lolos pada percobaan pertama (3 variasi suara per kalimat), 29 pulih lewat `--ulangi` (8 variasi tambahan), 18 tetap belum lolos otomatis; kedelapan belas itu didengarkan pemilik dan disetujui. ±1,6 detik per kalimat per proses, ±11 KB per MP3, total ±40 MB. Penyebab gagalnya terutama salah dengar oleh pemeriksa (儿 ditulis 而, misalnya). Pinyin otomatis: 147 kalimat (4%) ditandai ragu di CSV tinjauan, terutama kata berbunyi ganda seperti 种 教 长 当 得 少; pemilik menyatakan semuanya sudah sesuai, tetapi pemeriksaan ulang saat membuat audio HSK 5 (23 Nov 2026) menemukan 46 kalimat yang bacaannya keliru (34 HSK 3.0, 12 HSK 5): 只 sebagai penggolong harus zhī, 长 "panjang" cháng, 得 pelengkap de, 为 dalam 称为/选为/为止 wéi, 种 "menanam" zhòng, 假 jià, 教 jiāo, 切 qiē, 量 liáng, 系 jì, 相 xiàng, 撒 sǎ, 铺 pū, 地 sebagai partikel de. Semuanya dikoreksi di `koreksi_pinyin_kalimat.json` dan MP3-nya dibuat ulang. Pemeriksa SenseVoice membandingkan hanzi, bukan bacaan, jadi tidak bisa menangkap kesalahan jenis ini; hanya kalimat yang ditandai ragu yang diperiksa ulang satu per satu, huruf berbunyi ganda lain di luar daftar tanda belum diaudit. Pemeriksa hanya memastikan suara cocok dengan pinyin yang diberikan; ia tidak membuktikan bacaan itu benar menurut konteks, dan nada kalimat tidak diperiksa dari suara. Daftar nada netral di `pinyin_kalimat.py` (`NETRAL_2`) disusun tangan dan tidak lengkap. Belum ditinjau guru atau penutur asli.
