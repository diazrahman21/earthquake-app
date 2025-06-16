# 🚀 Panduan Deployment Aplikasi Gempa Bumi Indonesia

## Platform Deployment yang Didukung

### 1. Streamlit Cloud (Recommended)
Deployment paling mudah dan gratis:

1. **Push code ke GitHub repository**
2. **Kunjungi** [share.streamlit.io](https://share.streamlit.io)
3. **Connect GitHub account** dan pilih repository
4. **Set main file:** `earthquake-app.py`
5. **Deploy!** - Aplikasi akan otomatis deploy dan update saat ada push baru

**File yang diperlukan:**
- `requirements.txt` ✅
- `earthquake-app.py` ✅
- `.streamlit/config.toml` ✅

### 2. Heroku
Deployment ke Heroku:

```bash
# Install Heroku CLI
# Login ke Heroku
heroku login

# Create app
heroku create your-earthquake-app-name

# Set buildpack Python
heroku buildpacks:set heroku/python

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

**File yang diperlukan:**
- `Procfile` ✅
- `requirements.txt` ✅
- `runtime.txt` ✅
- `setup.sh` ✅

### 3. Railway
Simple deployment:

1. **Kunjungi** [railway.app](https://railway.app)
2. **Connect GitHub** repository
3. **Deploy from repo** - otomatis detect Python
4. **Set start command:** `streamlit run earthquake-app.py --server.port=$PORT --server.address=0.0.0.0`

### 4. Render
Free hosting alternatif:

1. **Kunjungi** [render.com](https://render.com)
2. **New Web Service** dari GitHub
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `streamlit run earthquake-app.py --server.port=$PORT --server.address=0.0.0.0`

## 🔧 Troubleshooting Deployment Errors

### Error: "installer returned a non-zero exit code"

**Penyebab umum:**
1. **Version conflict** - dependencies tidak kompatibel
2. **Memory limit** - package terlalu besar untuk platform
3. **Build timeout** - proses install terlalu lama

**Solusi:**
1. **Gunakan requirements.txt yang sudah dioptimasi** ✅
2. **Gunakan Python 3.9** (lebih stabil untuk deployment) ✅
3. **Remove unused dependencies**

### Error: "Module not found"

**Solusi:**
- Pastikan semua import ada di `requirements.txt`
- Test lokal: `pip install -r requirements.txt`

### Error: "Port binding failed"

**Solusi:**
- Gunakan environment variable PORT
- Set address ke 0.0.0.0

## 📝 Checklist Pre-Deployment

- [x] `requirements.txt` dengan versi yang kompatibel
- [x] `runtime.txt` dengan Python 3.9
- [x] `Procfile` untuk Heroku
- [x] `.streamlit/config.toml` untuk konfigurasi
- [x] `.gitignore` untuk exclude file yang tidak perlu
- [x] Test lokal berhasil
- [x] No hardcoded paths atau credentials

## 🌟 Rekomendasi

**Untuk pemula:** Gunakan **Streamlit Cloud** - paling mudah dan gratis
**Untuk production:** Gunakan **Heroku** atau **Railway** - lebih powerful
**Untuk custom domain:** Gunakan **Render** atau **Railway**

## 📞 Support

Jika masih ada error deployment, cek:
1. **Logs platform** untuk error detail
2. **GitHub repository** sudah up to date
3. **File permissions** di Windows/Mac
4. **Internet connection** saat build

---

File ini sudah dioptimasi untuk deployment yang sukses! 🚀
