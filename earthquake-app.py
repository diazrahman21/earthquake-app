import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import pytz
import xml.etree.ElementTree as ET

# Fungsi untuk mengambil data gempa bumi dari BMKG
def fetch_bmkg_earthquake_data():
    try:
        # URL API BMKG untuk data gempa terkini
        url = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.xml"
          # Headers untuk menghindari error 403 dan handle compression
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/xml, text/xml, */*',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
            # Hapus Accept-Encoding untuk menghindari compression
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Debug: periksa content type dan isi response
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        print(f"Response length: {len(response.content)}")
        print(f"First 200 chars: {response.text[:200]}")
        
        # Periksa apakah response adalah XML
        if 'xml' not in content_type.lower() and not response.text.strip().startswith('<?xml'):
            raise Exception(f"Response bukan XML. Content-Type: {content_type}")
        
        # Parse XML data
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            print(f"Response content: {response.text[:500]}")
            raise Exception(f"XML tidak valid: {e}")
        
        earthquakes = []
        
        # Cari semua element gempa
        gempa_elements = root.findall('.//gempa')  # Cari di semua level
        if not gempa_elements:
            gempa_elements = root.findall('gempa')  # Fallback ke level pertama
        
        print(f"Found {len(gempa_elements)} gempa elements")
        
        for gempa in gempa_elements:
            try:
                # Extract data dari XML dengan berbagai kemungkinan struktur
                tanggal = ""
                jam = ""
                
                # Coba berbagai format field
                if gempa.find('Tanggal') is not None:
                    tanggal = gempa.find('Tanggal').text or ""
                elif gempa.find('tanggal') is not None:
                    tanggal = gempa.find('tanggal').text or ""
                
                if gempa.find('Jam') is not None:
                    jam = gempa.find('Jam').text or ""
                elif gempa.find('jam') is not None:
                    jam = gempa.find('jam').text or ""
                
                # Koordinat
                coordinates = ""
                if gempa.find('point/coordinates') is not None:
                    coordinates = gempa.find('point/coordinates').text or "0,0"
                elif gempa.find('.//coordinates') is not None:
                    coordinates = gempa.find('.//coordinates').text or "0,0"
                
                # Lintang dan bujur alternatif
                lintang_str = ""
                bujur_str = ""
                if gempa.find('Lintang') is not None:
                    lintang_str = gempa.find('Lintang').text or "0"
                if gempa.find('Bujur') is not None:
                    bujur_str = gempa.find('Bujur').text or "0"
                
                # Magnitude
                magnitude_str = ""
                if gempa.find('Magnitude') is not None:
                    magnitude_str = gempa.find('Magnitude').text or "0"
                elif gempa.find('magnitude') is not None:
                    magnitude_str = gempa.find('magnitude').text or "0"
                
                # Kedalaman
                kedalaman_str = ""
                if gempa.find('Kedalaman') is not None:
                    kedalaman_str = gempa.find('Kedalaman').text or "0"
                elif gempa.find('kedalaman') is not None:
                    kedalaman_str = gempa.find('kedalaman').text or "0"
                
                # Wilayah
                wilayah = ""
                if gempa.find('Wilayah') is not None:
                    wilayah = gempa.find('Wilayah').text or "Tidak diketahui"
                elif gempa.find('wilayah') is not None:
                    wilayah = gempa.find('wilayah').text or "Tidak diketahui"
                
                # Potensi tsunami
                potensi = ""
                if gempa.find('Potensi') is not None:
                    potensi = gempa.find('Potensi').text or "Tidak berpotensi tsunami"
                elif gempa.find('potensi') is not None:
                    potensi = gempa.find('potensi').text or "Tidak berpotensi tsunami"
                
                # Parse koordinat
                lintang = 0.0
                bujur = 0.0
                
                if coordinates and coordinates != "0,0":
                    coords = coordinates.split(',')
                    if len(coords) >= 2:
                        try:
                            bujur = float(coords[0])
                            lintang = float(coords[1])
                        except ValueError:
                            continue
                elif lintang_str and bujur_str:
                    try:
                        # Parse lintang bujur dengan cleaning
                        lintang_clean = lintang_str.replace('°', '').replace(' LS', '').replace(' LU', '').replace(',', '.')
                        bujur_clean = bujur_str.replace('°', '').replace(' BT', '').replace(' BB', '').replace(',', '.')
                        
                        lintang = float(lintang_clean)
                        bujur = float(bujur_clean)
                        
                        # Konversi koordinat berdasarkan arah
                        if 'LS' in lintang_str:
                            lintang = -abs(lintang)
                        if 'BB' in bujur_str:
                            bujur = -abs(bujur)
                    except ValueError:
                        continue
                else:
                    continue  # Skip jika tidak ada koordinat
                
                # Parse magnitude
                try:
                    magnitude = float(magnitude_str.replace(',', '.')) if magnitude_str else 0.0
                except ValueError:
                    magnitude = 0.0
                
                if magnitude == 0.0:
                    continue  # Skip jika magnitude tidak valid
                
                # Parse kedalaman
                try:
                    kedalaman_clean = kedalaman_str.replace(' Km', '').replace(' km', '').replace(',', '.')
                    kedalaman = int(float(kedalaman_clean)) if kedalaman_clean else 0
                except ValueError:
                    kedalaman = 0
                
                # Buat datetime object
                waktu_kejadian = datetime.now(pytz.timezone('Asia/Jakarta'))
                if tanggal and jam:
                    try:
                        datetime_str = f"{tanggal} {jam}"
                        # Coba berbagai format tanggal
                        for date_format in ["%d-%b-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
                            try:
                                waktu_kejadian = datetime.strptime(datetime_str, date_format)
                                waktu_kejadian = waktu_kejadian.replace(tzinfo=pytz.timezone('Asia/Jakarta'))
                                break
                            except ValueError:
                                continue
                    except:
                        pass
                
                earthquakes.append({
                    "tanggal": tanggal,
                    "jam": jam,
                    "lintang": lintang,
                    "bujur": bujur,
                    "magnitudo": magnitude,
                    "kedalaman": kedalaman,
                    "wilayah": wilayah,
                    "potensi_tsunami": potensi,
                    "waktu_kejadian": waktu_kejadian
                })
                
            except Exception as e:
                print(f"Error parsing gempa data: {e}")
                continue
        
        print(f"Successfully parsed {len(earthquakes)} earthquakes")
        return pd.DataFrame(earthquakes)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error koneksi ke BMKG: {e}")
        return create_dummy_earthquake_data()
    except Exception as e:
        st.error(f"Error mengambil data dari BMKG: {e}")
        return create_dummy_earthquake_data()

# Fungsi untuk mengambil data gempa M 5.0+ dari BMKG
def fetch_bmkg_major_earthquakes():    try:
        url = "https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.xml"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/xml, text/xml, */*',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
            # Hapus Accept-Encoding untuk menghindari compression
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Debug: periksa content type dan isi response
        content_type = response.headers.get('content-type', '')
        print(f"Major earthquakes Content-Type: {content_type}")
        print(f"Major earthquakes Response length: {len(response.content)}")
        
        # Periksa apakah response adalah XML
        if 'xml' not in content_type.lower() and not response.text.strip().startswith('<?xml'):
            raise Exception(f"Response bukan XML. Content-Type: {content_type}")
        
        # Parse XML data
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            print(f"Response content: {response.text[:500]}")
            raise Exception(f"XML tidak valid: {e}")
        
        earthquakes = []
        
        # Cari semua element gempa
        gempa_elements = root.findall('.//gempa')  # Cari di semua level
        if not gempa_elements:
            gempa_elements = root.findall('gempa')  # Fallback ke level pertama
        
        print(f"Found {len(gempa_elements)} major gempa elements")
        
        for gempa in gempa_elements:
            try:
                # Extract data dengan berbagai kemungkinan format
                tanggal = ""
                jam = ""
                
                if gempa.find('Tanggal') is not None:
                    tanggal = gempa.find('Tanggal').text or ""
                elif gempa.find('tanggal') is not None:
                    tanggal = gempa.find('tanggal').text or ""
                
                if gempa.find('Jam') is not None:
                    jam = gempa.find('Jam').text or ""
                elif gempa.find('jam') is not None:
                    jam = gempa.find('jam').text or ""
                
                # Koordinat
                coordinates = ""
                if gempa.find('point/coordinates') is not None:
                    coordinates = gempa.find('point/coordinates').text or "0,0"
                elif gempa.find('.//coordinates') is not None:
                    coordinates = gempa.find('.//coordinates').text or "0,0"
                
                # Magnitude
                magnitude_str = ""
                if gempa.find('Magnitude') is not None:
                    magnitude_str = gempa.find('Magnitude').text or "0"
                elif gempa.find('magnitude') is not None:
                    magnitude_str = gempa.find('magnitude').text or "0"
                
                # Kedalaman
                kedalaman_str = ""
                if gempa.find('Kedalaman') is not None:
                    kedalaman_str = gempa.find('Kedalaman').text or "0"
                elif gempa.find('kedalaman') is not None:
                    kedalaman_str = gempa.find('kedalaman').text or "0"
                
                # Wilayah
                wilayah = ""
                if gempa.find('Wilayah') is not None:
                    wilayah = gempa.find('Wilayah').text or "Tidak diketahui"
                elif gempa.find('wilayah') is not None:
                    wilayah = gempa.find('wilayah').text or "Tidak diketahui"
                
                # Dirasakan
                dirasakan = ""
                if gempa.find('Dirasakan') is not None:
                    dirasakan = gempa.find('Dirasakan').text or "Tidak dirasakan"
                elif gempa.find('dirasakan') is not None:
                    dirasakan = gempa.find('dirasakan').text or "Tidak dirasakan"
                
                # Parse koordinat
                lintang = 0.0
                bujur = 0.0
                
                if coordinates and coordinates != "0,0":
                    coords = coordinates.split(',')
                    if len(coords) >= 2:
                        try:
                            bujur = float(coords[0])
                            lintang = float(coords[1])
                        except ValueError:
                            continue
                else:
                    continue  # Skip jika tidak ada koordinat
                
                # Parse magnitude
                try:
                    magnitude = float(magnitude_str.replace(',', '.')) if magnitude_str else 0.0
                except ValueError:
                    magnitude = 0.0
                
                if magnitude == 0.0:
                    continue  # Skip jika magnitude tidak valid
                
                # Parse kedalaman
                try:
                    kedalaman_clean = kedalaman_str.replace(' Km', '').replace(' km', '').replace(',', '.')
                    kedalaman = int(float(kedalaman_clean)) if kedalaman_clean else 0
                except ValueError:
                    kedalaman = 0
                
                # Buat datetime object
                waktu_kejadian = datetime.now(pytz.timezone('Asia/Jakarta'))
                if tanggal and jam:
                    try:
                        datetime_str = f"{tanggal} {jam}"
                        # Coba berbagai format tanggal
                        for date_format in ["%d-%b-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
                            try:
                                waktu_kejadian = datetime.strptime(datetime_str, date_format)
                                waktu_kejadian = waktu_kejadian.replace(tzinfo=pytz.timezone('Asia/Jakarta'))
                                break
                            except ValueError:
                                continue
                    except:
                        pass
                
                earthquakes.append({
                    "tanggal": tanggal,
                    "jam": jam,
                    "lintang": lintang,
                    "bujur": bujur,
                    "magnitudo": magnitude,
                    "kedalaman": kedalaman,
                    "wilayah": wilayah,
                    "dirasakan": dirasakan,
                    "waktu_kejadian": waktu_kejadian
                })
                
            except Exception as e:
                print(f"Error parsing major earthquake data: {e}")
                continue
        
        print(f"Successfully parsed {len(earthquakes)} major earthquakes")
        return pd.DataFrame(earthquakes)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error koneksi ke BMKG: {e}")
        return create_dummy_major_earthquake_data()
    except Exception as e:
        st.error(f"Error mengambil data gempa besar dari BMKG: {e}")
        return create_dummy_major_earthquake_data()

# Fungsi alternatif mengambil data gempa Indonesia dari USGS
def fetch_usgs_indonesia_earthquakes():
    """Mengambil data gempa dari USGS dengan filter area Indonesia"""
    try:
        # Bounding box Indonesia (approximate)
        # minlatitude=-11, maxlatitude=6, minlongitude=95, maxlongitude=141
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            'format': 'geojson',
            'starttime': (datetime.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d'),
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
                
                # Format untuk konsistensi dengan data BMKG
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
        
        print(f"Successfully fetched {len(earthquakes)} earthquakes from USGS")
        return pd.DataFrame(earthquakes)
        
    except Exception as e:
        print(f"Error fetching from USGS: {e}")
        return pd.DataFrame()

# Fungsi untuk membuat data dummy untuk testing
def create_dummy_earthquake_data():
    """Membuat data dummy ketika API BMKG tidak dapat diakses"""
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
        }
    ]
    return pd.DataFrame(dummy_data)

def create_dummy_major_earthquake_data():
    """Membuat data dummy untuk gempa besar"""
    dummy_data = [
        {
            "tanggal": "15-Jun-2025",
            "jam": "14:20:00",
            "lintang": -2.5489,
            "bujur": 118.0149,
            "magnitudo": 5.4,
            "kedalaman": 35,
            "wilayah": "Sulawesi Tengah",
            "dirasakan": "II-III Palu",
            "waktu_kejadian": datetime.now(pytz.timezone('Asia/Jakarta'))
        },
        {
            "tanggal": "14-Jun-2025",
            "jam": "21:10:00",
            "lintang": -0.7893,
            "bujur": 127.8014,
            "magnitudo": 5.8,
            "kedalaman": 42,
            "wilayah": "Maluku Utara",
            "dirasakan": "III-IV Ternate",
            "waktu_kejadian": datetime.now(pytz.timezone('Asia/Jakarta'))
        }
    ]
    return pd.DataFrame(dummy_data)

# Ambil data gempa bumi terkini dari BMKG
with st.spinner("📡 Mengambil data gempa Indonesia..."):
    # Prioritaskan USGS karena lebih reliable
    st.info("🔄 Mengambil data dari USGS (area Indonesia)...")
    recent_earthquake_data = fetch_usgs_indonesia_earthquakes()
    
    if not recent_earthquake_data.empty:
        major_earthquake_data = recent_earthquake_data[recent_earthquake_data['magnitudo'] >= 5.0]
        st.success("✅ Data berhasil diambil dari USGS")
    else:
        # Fallback ke BMKG jika USGS gagal
        st.info("🔄 Mencoba BMKG sebagai alternatif...")
        recent_earthquake_data = fetch_bmkg_earthquake_data()
        major_earthquake_data = fetch_bmkg_major_earthquakes()
        
        if not recent_earthquake_data.empty:
            st.success("✅ Data berhasil diambil dari BMKG")
        else:
            st.warning("⚠️ Menggunakan data contoh")

# Layout aplikasi Streamlit
st.title("🌍 Deteksi Gempa Bumi Indonesia - BMKG")
st.markdown("Aplikasi ini memvisualisasikan data gempa bumi real-time di Indonesia dari Badan Meteorologi, Klimatologi, dan Geofisika (BMKG).")

# Informasi sumber data
if not recent_earthquake_data.empty or not major_earthquake_data.empty:
    # Deteksi sumber data berdasarkan format wilayah
    if not recent_earthquake_data.empty:
        sample_location = recent_earthquake_data.iloc[0]['wilayah']
        if any(keyword in sample_location.lower() for keyword in ['km', 'of', 'near']):
            st.info("📊 **Sumber Data:** USGS (United States Geological Survey) - Data gempa area Indonesia")
        else:
            st.info("📊 **Sumber Data:** BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) - Data resmi Indonesia")
    else:
        st.info("📊 **Sumber Data:** Data gempa Indonesia dari sumber terpercaya")
else:
    st.warning("⚠️ **Status:** Menggunakan data contoh karena tidak dapat mengakses API saat ini")

# Statistik ringkas
if not recent_earthquake_data.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Gempa", len(recent_earthquake_data))
    
    with col2:
        max_mag = recent_earthquake_data['magnitudo'].max()
        st.metric("Magnitudo Tertinggi", f"{max_mag:.1f}")
    
    with col3:
        avg_depth = recent_earthquake_data['kedalaman'].mean()
        st.metric("Kedalaman Rata-rata", f"{avg_depth:.0f} km")
    
    with col4:
        recent_count = len(recent_earthquake_data[recent_earthquake_data['magnitudo'] >= 4.0])
        st.metric("Gempa M ≥ 4.0", recent_count)

# Tentukan nilai default untuk slider
if not recent_earthquake_data.empty:
    max_magnitude = float(recent_earthquake_data['magnitudo'].max())
    default_magnitude = min(1.0, max_magnitude)
else:
    max_magnitude = 10.0
    default_magnitude = 1.0

# Filter berdasarkan magnitudo
min_magnitude = st.slider("Magnitudo Minimum", 
                         min_value=0.0, 
                         max_value=max_magnitude, 
                         value=default_magnitude, 
                         step=0.1)

# Filter data berdasarkan magnitudo
if not recent_earthquake_data.empty:
    filtered_recent_data = recent_earthquake_data[recent_earthquake_data["magnitudo"] >= min_magnitude]
else:
    filtered_recent_data = pd.DataFrame()

if not major_earthquake_data.empty:
    filtered_major_data = major_earthquake_data[major_earthquake_data["magnitudo"] >= min_magnitude]
else:
    filtered_major_data = pd.DataFrame()

# Buat peta Plotly untuk gempa bumi terkini
if not filtered_recent_data.empty:
    fig_recent = px.scatter_mapbox(
        filtered_recent_data,
        lat="lintang",
        lon="bujur",
        size="magnitudo",
        color="magnitudo",
        hover_name="wilayah",
        hover_data={
            "tanggal": True, 
            "jam": True, 
            "magnitudo": True, 
            "kedalaman": True, 
            "potensi_tsunami": True
        },
        zoom=4,
        center={"lat": -2.5, "lon": 118},  # Fokus ke Indonesia
        height=600,
        title="🚨 Gempa Bumi Terkini di Indonesia",
        color_continuous_scale="Reds"    )
    
    fig_recent.update_layout(
        mapbox_style="open-street-map",
        title_font_size=20,
        title_x=0.5
    )
    
    st.plotly_chart(fig_recent, use_container_width=True)
else:
    st.info("📍 Tidak ada data gempa terkini dengan magnitudo >= {:.1f} untuk ditampilkan".format(min_magnitude))

# Buat peta Plotly untuk gempa bumi yang dirasakan
if not filtered_major_data.empty:
    fig_major = px.scatter_mapbox(
        filtered_major_data,
        lat="lintang",
        lon="bujur",
        size="magnitudo",
        color="kedalaman",
        hover_name="wilayah",
        hover_data={
            "tanggal": True, 
            "jam": True, 
            "magnitudo": True, 
            "kedalaman": True, 
            "dirasakan": True
        },
        zoom=4,
        center={"lat": -2.5, "lon": 118},  # Fokus ke Indonesia
        height=600,
        title="📊 Gempa Bumi yang Dirasakan (M ≥ 5.0)",
        color_continuous_scale="Viridis"    )
    
    fig_major.update_layout(
        mapbox_style="open-street-map",
        title_font_size=20,
        title_x=0.5
    )
    
    st.plotly_chart(fig_major, use_container_width=True)
else:
    st.info("📊 Tidak ada data gempa besar dengan magnitudo >= {:.1f} untuk ditampilkan".format(min_magnitude))

# Tampilkan data dalam bentuk tabel
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Data Gempa Bumi Terkini")
    if not filtered_recent_data.empty:
        # Format data untuk ditampilkan
        display_recent = filtered_recent_data.copy()
        display_recent = display_recent.sort_values('waktu_kejadian', ascending=False)
        
        # Tampilkan tabel dengan styling
        st.dataframe(
            display_recent[['tanggal', 'jam', 'wilayah', 'magnitudo', 'kedalaman', 'potensi_tsunami']],
            use_container_width=True,
            height=300
        )
        
        # Statistik singkat
        st.metric("Total Gempa Terkini", len(filtered_recent_data))
        if filtered_recent_data['magnitudo'].max() > 0:
            st.metric("Magnitudo Tertinggi", f"{filtered_recent_data['magnitudo'].max():.1f}")
    else:
        st.info("Tidak ada data gempa terkini untuk ditampilkan")

with col2:
    st.subheader("📊 Data Gempa yang Dirasakan")
    if not filtered_major_data.empty:
        # Format data untuk ditampilkan
        display_major = filtered_major_data.copy()
        display_major = display_major.sort_values('waktu_kejadian', ascending=False)
        
        # Tampilkan tabel dengan styling
        st.dataframe(
            display_major[['tanggal', 'jam', 'wilayah', 'magnitudo', 'kedalaman', 'dirasakan']],
            use_container_width=True,
            height=300
        )
        
        # Statistik singkat
        st.metric("Total Gempa Besar", len(filtered_major_data))
        if filtered_major_data['magnitudo'].max() > 0:
            st.metric("Magnitudo Tertinggi", f"{filtered_major_data['magnitudo'].max():.1f}")
    else:
        st.info("Tidak ada data gempa besar untuk ditampilkan")

# Informasi Tambahan di Sidebar
st.sidebar.subheader("📱 Tentang Aplikasi")
st.sidebar.info(
    """
    **Deteksi Gempa Bumi Indonesia**
    
    Aplikasi ini mengambil data gempa bumi real-time dari BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) Indonesia.
    
    **Fitur:**
    - 🚨 Data gempa terkini di Indonesia
    - 📊 Gempa yang dirasakan (M ≥ 5.0)
    - 🗺️ Visualisasi peta interaktif
    - 📋 Tabel data lengkap
    - 🔍 Filter berdasarkan magnitudo
    
    **Sumber Data:** 
    - data.bmkg.go.id
    - Diperbarui secara real-time
    """
)

# Peringatan gempa bumi
st.sidebar.subheader("⚠️ Peringatan Gempa")
if not filtered_recent_data.empty:
    high_magnitude = filtered_recent_data[filtered_recent_data['magnitudo'] >= 6.0]
    if not high_magnitude.empty:
        st.sidebar.error(f"🚨 PERINGATAN: Terdapat {len(high_magnitude)} gempa dengan magnitudo ≥ 6.0!")
        for _, row in high_magnitude.iterrows():
            st.sidebar.warning(f"📍 M {row['magnitudo']:.1f} - {row['wilayah']} ({row['tanggal']} {row['jam']})")
    else:
        st.sidebar.success("✅ Tidak ada gempa besar (M ≥ 6.0) dalam data terkini")

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()
