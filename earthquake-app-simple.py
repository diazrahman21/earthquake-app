import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import pytz

# Konfigurasi halaman
st.set_page_config(
    page_title="Deteksi Gempa Indonesia",
    page_icon="🌍",
    layout="wide"
)

# Fungsi untuk mengambil data gempa dari USGS area Indonesia
def fetch_usgs_indonesia_earthquakes():
    """Mengambil data gempa dari USGS dengan filter area Indonesia"""
    try:
        # Bounding box Indonesia (approximate)
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            'format': 'geojson',
            'starttime': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'endtime': datetime.now().strftime('%Y-%m-%d'),
            'minlatitude': -11,
            'maxlatitude': 6,
            'minlongitude': 95,
            'maxlongitude': 141,
            'minmagnitude': 2.5,
            'limit': 100
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        earthquakes = []
        
        for feature in data['features']:
            try:
                properties = feature['properties']
                geometry = feature['geometry']
                
                # Extract data
                magnitude = properties.get('mag', 0)
                place = properties.get('place', 'Unknown location')
                time_ms = properties.get('time', 0)
                depth = geometry['coordinates'][2] if len(geometry['coordinates']) > 2 else 0
                
                # Convert time
                utc_time = pd.to_datetime(time_ms, unit='ms')
                local_time = utc_time.tz_localize('UTC').tz_convert(pytz.timezone('Asia/Jakarta'))
                
                # Format untuk konsistensi
                earthquakes.append({
                    "tanggal": local_time.strftime("%d-%b-%Y"),
                    "jam": local_time.strftime("%H:%M:%S"),
                    "lintang": geometry['coordinates'][1],
                    "bujur": geometry['coordinates'][0],
                    "magnitudo": magnitude,
                    "kedalaman": int(depth),
                    "wilayah": place,
                    "potensi_tsunami": "Tidak berpotensi tsunami" if magnitude < 7.0 else "Berpotensi tsunami",
                    "waktu_kejadian": local_time
                })
                
            except Exception as e:
                print(f"Error parsing USGS data: {e}")
                continue
        
        return pd.DataFrame(earthquakes)
        
    except Exception as e:
        st.error(f"Error mengambil data dari USGS: {e}")
        return create_dummy_data()

# Fungsi untuk membuat data dummy
def create_dummy_data():
    """Membuat data dummy untuk testing"""
    dummy_data = [
        {
            "tanggal": "16-Jun-2025",
            "jam": "10:30:00",
            "lintang": -6.2088,
            "bujur": 106.8456,
            "magnitudo": 4.2,
            "kedalaman": 15,
            "wilayah": "Jakarta Selatan",
            "potensi_tsunami": "Tidak berpotensi tsunami",
            "waktu_kejadian": datetime.now(pytz.timezone('Asia/Jakarta'))
        },
        {
            "tanggal": "16-Jun-2025",
            "jam": "09:15:00",
            "lintang": -7.2575,
            "bujur": 112.7521,
            "magnitudo": 3.8,
            "kedalaman": 22,
            "wilayah": "Surabaya, Jawa Timur",
            "potensi_tsunami": "Tidak berpotensi tsunami",
            "waktu_kejadian": datetime.now(pytz.timezone('Asia/Jakarta'))
        },
        {
            "tanggal": "16-Jun-2025",
            "jam": "08:45:00",
            "lintang": -8.3405,
            "bujur": 115.0920,
            "magnitudo": 5.1,
            "kedalaman": 18,
            "wilayah": "Denpasar, Bali",
            "potensi_tsunami": "Tidak berpotensi tsunami",
            "waktu_kejadian": datetime.now(pytz.timezone('Asia/Jakarta'))
        },
        {
            "tanggal": "15-Jun-2025",
            "jam": "14:20:00",
            "lintang": -2.5489,
            "bujur": 118.0149,
            "magnitudo": 5.4,
            "kedalaman": 35,
            "wilayah": "Sulawesi Tengah",
            "potensi_tsunami": "Tidak berpotensi tsunami",
            "waktu_kejadian": datetime.now(pytz.timezone('Asia/Jakarta'))
        }
    ]
    return pd.DataFrame(dummy_data)

# Header aplikasi
st.title("🌍 Deteksi Gempa Bumi Indonesia")
st.markdown("Aplikasi monitoring gempa bumi real-time di wilayah Indonesia")

# Ambil data gempa
with st.spinner("📡 Mengambil data gempa..."):
    earthquake_data = fetch_usgs_indonesia_earthquakes()
    
    if earthquake_data.empty:
        st.warning("⚠️ Menggunakan data contoh")

# Informasi sumber data
if not earthquake_data.empty:
    sample_location = earthquake_data.iloc[0]['wilayah']
    if any(keyword in sample_location.lower() for keyword in ['km', 'of', 'near']):
        st.info("📊 **Sumber Data:** USGS - Data gempa area Indonesia (7 hari terakhir)")
    else:
        st.info("📊 **Sumber Data:** Data gempa Indonesia")

# Statistik ringkas
if not earthquake_data.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Gempa", len(earthquake_data))
    
    with col2:
        max_mag = earthquake_data['magnitudo'].max()
        st.metric("Magnitudo Tertinggi", f"{max_mag:.1f}")
    
    with col3:
        avg_depth = earthquake_data['kedalaman'].mean()
        st.metric("Kedalaman Rata-rata", f"{avg_depth:.0f} km")
    
    with col4:
        recent_count = len(earthquake_data[earthquake_data['magnitudo'] >= 4.0])
        st.metric("Gempa M ≥ 4.0", recent_count)

# Filter berdasarkan magnitudo
if not earthquake_data.empty:
    max_magnitude = float(earthquake_data['magnitudo'].max())
    min_magnitude = st.slider(
        "Magnitudo Minimum", 
        min_value=0.0, 
        max_value=max_magnitude, 
        value=min(2.5, max_magnitude), 
        step=0.1
    )
    filtered_data = earthquake_data[earthquake_data["magnitudo"] >= min_magnitude]
else:
    filtered_data = earthquake_data
    min_magnitude = 2.5

# Peta interaktif
if not filtered_data.empty:
    st.subheader("🗺️ Peta Gempa Bumi")
    
    fig = px.scatter_mapbox(
        filtered_data,
        lat="lintang",
        lon="bujur",
        size="magnitudo",
        color="magnitudo",
        hover_name="wilayah",
        hover_data={
            "tanggal": True, 
            "jam": True, 
            "magnitudo": True, 
            "kedalaman": True
        },
        zoom=4,
        center={"lat": -2.5, "lon": 118},
        height=600,
        title="Gempa Bumi di Indonesia",
        color_continuous_scale="Reds"
    )
    
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"📍 Tidak ada gempa dengan magnitudo ≥ {min_magnitude:.1f}")

# Tabel data
st.subheader("📋 Data Gempa Terkini")
if not filtered_data.empty:
    # Format tabel untuk tampilan
    display_data = filtered_data.copy()
    display_data = display_data.sort_values('waktu_kejadian', ascending=False)
    
    # Pilih kolom untuk ditampilkan
    columns_to_show = ['tanggal', 'jam', 'wilayah', 'magnitudo', 'kedalaman', 'potensi_tsunami']
    st.dataframe(
        display_data[columns_to_show],
        use_container_width=True,
        height=400
    )
    
    # Download data
    csv = display_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Data CSV",
        data=csv,
        file_name=f"gempa_indonesia_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
else:
    st.info("Tidak ada data untuk ditampilkan")

# Sidebar informasi
st.sidebar.header("📱 Tentang Aplikasi")
st.sidebar.info("""
**Deteksi Gempa Bumi Indonesia**

Aplikasi ini menampilkan data gempa bumi real-time di wilayah Indonesia.

**Fitur:**
- 🗺️ Peta interaktif
- 📊 Filter magnitudo
- 📋 Tabel data lengkap
- 📥 Download data CSV
- ⚠️ Peringatan gempa besar

**Sumber Data:**
- USGS (United States Geological Survey)
- Area: Indonesia
- Update: Real-time
""")

# Peringatan gempa besar
st.sidebar.subheader("⚠️ Peringatan")
if not filtered_data.empty:
    high_magnitude = filtered_data[filtered_data['magnitudo'] >= 6.0]
    if not high_magnitude.empty:
        st.sidebar.error(f"🚨 PERINGATAN: {len(high_magnitude)} gempa M ≥ 6.0!")
        for _, row in high_magnitude.head(3).iterrows():
            st.sidebar.warning(f"📍 M {row['magnitudo']:.1f} - {row['wilayah'][:50]}...")
    else:
        st.sidebar.success("✅ Tidak ada gempa besar (M ≥ 6.0)")

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** Data ini untuk tujuan informasi. Untuk informasi resmi, rujuk ke BMKG atau otoritas terkait.")
