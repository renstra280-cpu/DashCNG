import streamlit as st
import pandas as pd
# Buat model ANOVA
import statsmodels.api as sm
from statsmodels.formula.api import ols

#load layout, data, prepdata
from utils.data_source import get_data_source
from utils.prep_data import PrepData
from utils.stats_test import StatsTest
StatsTest()
from utils.layout import load_layout
load_layout()

# ==========================================
# PAGE CONFIG
# ==========================================
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
if st.button("🏠︎ HOME"):
    st.switch_page("HOME.py")

st.subheader("ANALISIS ANOVA")

#CONTOH FORMAT DATA ANOVA
with st.expander("Klik untuk melihat contoh format data ANOVA"):
        st.image("assets/format_data_anova.png",caption="Contoh Format Data Anova",width=200)
#TARUH CONTOH FORMAT DATA DISINI
#klik button ("klik untuk melihat contoh format data")

# ==========================================
# LOAD DATA
# ==========================================
#MASUK KE ANOVA
df_raw = get_data_source("anova")

# Kalau user upload / input data baru
if df_raw is not None:
    
    # Buat signature data
    new_signature = (
        df_raw.shape,
        tuple(df_raw.columns)
    )

    # Kalau belum pernah ada data
    if "df_anova" not in st.session_state:
        st.session_state["df_anova"] = df_raw.copy()
        st.session_state["data_signature_anova"] = new_signature

    # Kalau sudah ada data → cek apakah beda
    else:
        old_signature = st.session_state.get("data_signature_anova")

        if new_signature != old_signature:
            # 🚨 DATA BERUBAH → RESET SEMUA
            keys_to_reset = [
                "anova_results",
                "kruskal_results",
                "assumption_checked",
                "assumption_passed",
                "anova_posthoc",
                "kruskal_posthoc",
                "anova_final",
                "kruskal_final"
            ]

            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]

            # Update data baru
            st.session_state["df_anova"] = df_raw.copy()
            st.session_state["data_signature_anova"] = new_signature

            st.success("Sumber data berubah → hasil analisis direset ✅")

# Kalau belum pernah upload sama sekali
if "df_anova" not in st.session_state:
    st.info("Silakan upload atau masukkan data terlebih dahulu.")
    st.stop()

df = st.session_state["df_anova"]

#MENGUBAH SPASI MENJADI _
df.columns = df.columns.str.strip().str.replace(" ","_")

with st.expander("Klik untuk melihat preview data upload"):
    st.dataframe(df.head(20))

# =============================
# PILIH KOLOM UNTUK ANOVA
# =============================

numeric_cols = df.select_dtypes(include="number").columns.tolist()
category_cols = df.select_dtypes(exclude="number").columns.tolist()

if not category_cols:
    st.error("Tidak ada kolom kategori untuk ANOVA ❌")
    st.stop()

if not numeric_cols:
    st.error("Tidak ada kolom numerik untuk ANOVA ❌")
    st.stop()

group_col = st.selectbox("Pilih Kolom Kelompok (Kategori)", category_cols)
value_col = st.selectbox("Pilih Kolom Nilai (Numerik)", numeric_cols)

#panggil anova df
anova_df,error_msg = PrepData.anova(df, value_col, group_col)

jml_ktgr=len(df[group_col].unique())

if error_msg:
    st.error(error_msg)
    st.stop()
st.success(f"Data memenuhi jumlah kategori ({jml_ktgr}) ✅ (minimal terdiri 2 kategori/kelompok/treatment/group)")

# =============================
# VALIDASI JUMLAH KELOMPOK
# =============================
jml_kategori=anova_df[group_col].nunique()
if jml_kategori < 2:
    st.error("Jumlah kategori harus memiliki minimal 2 ❌")
    st.stop()

# =============================
# VALIDASI UKURAN TIAP KELOMPOK
# =============================
group_sizes = anova_df[group_col].value_counts()

# Temukan kelompok yang terlalu kecil
too_small_groups = group_sizes[group_sizes < 3]

if not too_small_groups.empty:
    excluded_groups=too_small_groups.index.tolist()
    max_display=10
    total_rows = len(df)
    if len(excluded_groups)>max_display:
        tampil= excluded_groups[:max_display]
        sisa=len(excluded_groups)-max_display
        sisa_kategori=total_rows-len(excluded_groups)

        st.warning(
            f"{len(excluded_groups)} kategori dari kolom {group_col} dikeluarkan dari analisis karena jumlah groupsize kategori (n)<3:\n\n"
            f"diantaranya: {', '.join(map(str, tampil))}... dan {sisa} kategori lainnya, tersisa {sisa_kategori} kategori ⚠")
    else:
        st.warning(
            f"Kategori berikut dikeluarkan dari analisis karena jumlah data (n)<3:\n\n"
            f"{', '.join(map(str, excluded_groups))} ⚠")


    # EXCLUDE kategori n<3 otomatis
    anova_df = anova_df[
        ~anova_df[group_col].isin(excluded_groups)
        ].copy()

#CEK ULANG SETELAH ADA VARIABEL YANG DIEXCLUDEKAN
jml_kategori_after_fil=anova_df[group_col].nunique()
if jml_kategori_after_fil<2:
    st.error(
        "Setelah mengeluarkan kategori groupsize dengan n < 3, "
        "jumlah kategori tersisa kurang dari 2 ❌"
    )
    st.stop()

# Kalau lolos semua, lanjut
st.success("Data siap untuk uji ANOVA ✅")    

#ANALISIS ANOVA
#pengecekan asumsi
if "assumption_checked" not in st.session_state:
    st.session_state["assumption_checked"] = False

if "assumption_passed" not in st.session_state:
    st.session_state["assumption_passed"] = None

#tombol jalankan asumsi
if st.button("Jalankan Uji Asumsi"):
    try:
        results = StatsTest.run_anova(anova_df, value_col, group_col)
    except Exception as e:
        st.error(f"Gagal menjalankan asumsi: {e}, pastikan data sesuai dengan format data serta memiliki nama kolom")
        results=None
    if results:
        st.session_state["assumption_checked"] = True
        st.session_state["anova_results"] = results

        if results["p_norm"] > 0.05 and results["p_lev"] > 0.05:
            st.session_state["assumption_passed"] = True
        else:
            st.session_state["assumption_passed"] = False

#ASUMSI
if st.session_state["assumption_checked"]:

    results = st.session_state["anova_results"]

    hasil_asumsi=pd.DataFrame({
        "Uji": ["Normalitas (Shapiro-Wilk)", "Homogenitas (Levene Test)"],
        "Statistik": [results["stat_norm"], results["stat_lev"]],
        "P-Value": [results["p_norm"], results["p_lev"]],
    })

    st.markdown("Hasil Uji Asumsi Anova")

    st.dataframe(hasil_asumsi.round(4))

#JIKA MEMENUHI ASUMSI --> JALANKAN ANOVA
if st.session_state["assumption_passed"] == True:

    st.success("Data memenuhi asumsi ANOVA ✅")

    if st.button("Hitung ANOVA"):
        st.session_state["anova_final"]=True

        #TAMPILKAN HASIL JIKA SUDAH PERNAH DIHITUNG
    if st.session_state.get("anova_final", False):
        st.markdown("Uji ANOVA")

        #hipotesis
        st.markdown("**Hipotesis**")
        st.write("H₀ : Tidak terdapat perbedaan rata-rata antar kelompok.")
        st.write("H₁ : Terdapat minimal satu kelompok yang memiliki rata-rata berbeda.")
        st.write("α : 0.05")
        st.write("Daerah kritis : Tolak H₀ jika P-Value < 0.05")
        st.dataframe(
            st.session_state["anova_results"]["anova_table"].round(4)
        )
        
#JIKA TIDAK MEMENUHI ASUMSI--> STOP ATAU LANJUT KRUSKAL WALLIS
elif st.session_state["assumption_passed"] == False:

    st.error("Data tidak memenuhi asumsi ANOVA ❌")

    pilihan = st.radio(
        "Pilih tindakan:",
        ["Stop Analisis", "Lanjut dengan Kruskal-Wallis"],
        key="kruskal_choice"
    )

    if pilihan == "Lanjut dengan Kruskal-Wallis":
        st.info("Kruskal-Wallis (statistika non parametrik) tidak memerlukan asumsi normalitas dan homogenitas varians.")

        if st.button("Hitung Kruskal-Wallis"):
            #panggil fungsi kruskal wallis
            results=StatsTest.run_kruskal(anova_df, value_col, group_col)
            st.session_state["kruskal_results"]=results
            st.session_state["kruskal_final"]=True

        if st.session_state.get("kruskal_final",False):

            hasil_kruskal = pd.DataFrame({
                "statistik": [st.session_state["kruskal_results"]["stat_krus"]],
                "P-value": [st.session_state["kruskal_results"]["p_krus"]]
            })

            st.markdown("Hasil Kruskal-Wallis")
            # Hipotesis
            st.markdown("**Hipotesis**")
            st.write("H₀ : Tidak terdapat perbedaan median antar kelompok.")
            st.write("H₁ : Terdapat minimal satu kelompok dengan median berbeda.")
            st.write("α : 0.05")
            st.write("Tolak H₀ jika P-Value < 0.05")
            st.dataframe(hasil_kruskal.round(4))
