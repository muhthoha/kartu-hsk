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
Tombol kalimat contoh HSK 3.0 (`h3Sen`) memutar `audio/kalimat/<kode>.mp3` bila kodenya ada di `audio/kalimat/index.json`; bila tidak, memakai suara peramban. Audio kalimat lama (`AU`, audio HSK 2.0) tetap didahulukan bila kalimatnya sama.

## Audio kalimat contoh (HSK 3.0)
Status: baru 250 kalimat pratinjau (Set 1 tiap level, `data/hsk3.json`). Sisanya menunggu `hsk3-penuh.json`; kalimat kosakata teknis belum.
Kode berkas = `kah("s|" + hanzi kalimat)`, jadi situs tidak perlu pinyin kalimat dan tidak ada daftar kalimat di berkas publik.
```
# 1. pinyin kalimat: kata utama dari pinyin kartu, sisanya otomatis; CSV tinjauan berisi yang ditandai ragu
python3 tools/audio_kata/pinyin_kalimat.py --data /jalur/hsk3-penuh.json --model <folder>/vits-melo-tts-zh_en \
    --keluar kalimat.json --tinjau tinjau.csv
# (opsional) isi kolom "p2" di kalimat.json untuk kalimat yang pinyinnya dikoreksi; p2 dipakai bila ada
# 2. audio (boleh paralel dengan --bagian 0/1 --dari 2)
python3 tools/audio_kata/buat_audio_kalimat.py --daftar kalimat.json --model <folder>/vits-melo-tts-zh_en \
    --asr <folder>/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17 --keluar audio/kalimat
# 3. indeks, lalu naikkan angka ?v= pada fetch("audio/kalimat/index.json?v=1") di index.html (h3Load)
python3 tools/audio_kata/buat_audio_kalimat.py --keluar audio/kalimat --indeks
```
Hasil uji 250 kalimat: 249 lolos pemeriksa, ±1,7 detik per kalimat, ±11 KB per MP3 (3.600 kalimat kira-kira 40 MB). Pemeriksa hanya memastikan suara cocok dengan pinyin yang diberikan; ia tidak membuktikan bacaan itu benar menurut konteks, dan nada kalimat tidak diperiksa dari suara. Daftar nada netral di `pinyin_kalimat.py` (`NETRAL_2`) disusun tangan dan tidak lengkap. Belum ditinjau guru atau penutur asli.
