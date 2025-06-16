# 🌍 Deteksi Gempa Bumi Indonesia - BMKG

Aplikasi web interaktif untuk memantau dan memvisualisasikan data gempa bumi real-time di Indonesia menggunakan data resmi dari BMKG (Badan Meteorologi, Klimatologi, dan Geofisika).

## ✨ Fitur Utama

- 🚨 **Data Gempa Terkini**: Menampilkan gempa bumi terkini di Indonesia
- 📊 **Gempa yang Dirasakan**: Fokus pada gempa bumi dengan magnitudo ≥ 5.0 yang dirasakan masyarakat
- 🗺️ **Peta Interaktif**: Visualisasi lokasi gempa pada peta Indonesia dengan Plotly
- 🔍 **Filter Magnitudo**: Filter berdasarkan magnitudo minimum
- 📋 **Data Lengkap**: Tabel data dengan informasi detail
- ⚠️ **Peringatan Gempa**: Alert untuk gempa besar (M ≥ 6.0)
- 🔄 **Real-time**: Data diperbarui secara otomatis dari BMKG

## 🛠️ Teknologi yang Digunakan

- **Python 3.10+**
- **Streamlit** - Framework web app
- **Plotly** - Visualisasi peta interaktif
- **Pandas** - Manipulasi data
- **PyTZ** - Penanganan zona waktu Indonesia
- **Requests** - HTTP requests ke API BMKG
- **XML ElementTree** - Parsing data XML dari BMKG

## 📊 Sumber Data

Data gempa bumi diambil dari API resmi BMKG:
- **Gempa Terkini**: `https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.xml`
- **Gempa Dirasakan**: `https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.xml`

Data mencakup:
- Lokasi gempa (wilayah)
- Magnitudo dan kedalaman
- Waktu kejadian (WIB/WITA/WIT)
- Koordinat (lintang, bujur)
- Potensi tsunami
- Dampak yang dirasakan

## 🚀 Cara Menjalankan

### Menjalankan Secara Lokal

1. **Clone repository:**
   ```bash
   git clone https://github.com/username/earthquake-app.git
   cd earthquake-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi:**
   ```bash
   streamlit run earthquake-app.py
   ```

4. **Buka browser** dan akses `http://localhost:8501`

### Deploy ke Cloud Platform

#### Streamlit Cloud
1. Push code ke GitHub repository
2. Kunjungi [share.streamlit.io](https://share.streamlit.io)
3. Connect repository dan deploy

#### Heroku
1. Install Heroku CLI
2. Login dan create app:
   ```bash
   heroku create earthquake-indonesia-app
   git push heroku main
   ```

## 📱 Cara Penggunaan

1. **Buka aplikasi** di browser
2. **Gunakan slider** untuk mengatur magnitudo minimum
3. **Lihat peta interaktif** - klik pada marker untuk detail
4. **Periksa tabel data** untuk informasi lengkap
5. **Pantau peringatan** di sidebar untuk gempa besar
6. **Klik refresh** untuk memperbarui data

## 🗺️ Visualisasi

### Peta Gempa Terkini
- Marker berukuran sesuai magnitudo
- Warna berdasarkan intensitas
- Hover untuk detail gempa
- Fokus pada wilayah Indonesia

### Peta Gempa yang Dirasakan
- Marker berukuran sesuai magnitudo
- Warna berdasarkan kedalaman
- Informasi dampak yang dirasakan

## 📋 Informasi Data

### Gempa Terkini
- Semua gempa yang tercatat BMKG
- Update real-time
- Informasi potensi tsunami

### Gempa yang Dirasakan
- Gempa dengan magnitudo ≥ 5.0
- Gempa yang berdampak pada masyarakat
- Laporan dampak dari berbagai wilayah

## 🚨 Fitur Peringatan

- **Alert otomatis** untuk gempa M ≥ 6.0
- **Notifikasi sidebar** untuk gempa berbahaya
- **Status keamanan** berdasarkan data terkini

## 📁 Struktur File

```
earthquake-app/
├── earthquake-app.py          # Main aplikasi Streamlit
├── requirements.txt           # Dependencies Python
├── README.md                 # Dokumentasi ini
└── .gitignore               # Git ignore file
```

## 🔧 Konfigurasi

### Zona Waktu
Default zona waktu adalah `Asia/Jakarta` (WIB). Data dari BMKG sudah dalam waktu lokal Indonesia.

### Refresh Data
Data diperbarui otomatis setiap kali halaman dimuat ulang atau tombol refresh ditekan.

## 🤝 Kontribusi

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- [BMKG](https://www.bmkg.go.id/) untuk menyediakan API data gempa bumi Indonesia
- [Streamlit](https://streamlit.io/) untuk framework web app yang mudah digunakan
- [Plotly](https://plotly.com/) untuk visualisasi peta interaktif

## 📞 Kontak

**Developer:** Your Name
- GitHub: [@username](https://github.com/username)
- Email: your.email@example.com

## ⚠️ Disclaimer

Data gempa bumi dalam aplikasi ini bersumber dari BMKG untuk tujuan informasi dan edukasi. Untuk informasi resmi dan tindakan darurat, selalu merujuk ke pengumuman resmi BMKG dan otoritas terkait.

---

⭐ **Jika project ini bermanfaat, jangan lupa berikan star!** ⭐
