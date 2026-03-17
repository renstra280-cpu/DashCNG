import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import chi2_contingency
from itertools import combinations

#load layout, data, prepdata
from utils.data_source import get_data_source
from utils.prep_data import PrepData
from utils.layout import load_layout
load_layout()

#HYPERLINK DARI MAIN_DASH
# Tombol kembali
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
if st.button("🏠︎ HOME"):
    st.switch_page("HOME.py")


st.subheader("VISUALISASI DATA")

#CONTOH FORMAT DATA ANOVA
with st.expander("Klik untuk melihat contoh format data VISUALISASI"):
        st.image("assets/format_data_visual.png",caption="Contoh Format Data Visualisasi",width=450)

# =======================
# AMBIL DATA DI DATA_SOURCE & PREP_DATA
# =======================
df = None   # <<< WAJIB inisialisasi dulu

df_raw = get_data_source("visual")

if df_raw is not None:
    df = PrepData.visual(df_raw)

# ======================
# TAMPILKAN DATAs
# ======================
if df is None:
    st.warning("Silakan upload data terlebih dahulu.")
    st.stop()

# ======================
# TAMPILKAN DATA
# ======================
st.success("Data berhasil dimuat")
with st.expander("Klik untuk melihat preview data upload"):
    st.dataframe(df.head(20))

# ======================
# MULAI DASHBOARD
# ======================
all_cols = df.columns.tolist()

time_col = st.selectbox(
    "Pilih Kolom Base Time-Line (rentang data yang digunakan)",
    options=all_cols,
    index=0
)
    # lanjut dashboard...
    # lanjut filter...
    # lanjut sidebar...
    # lanjut KPI...
    # lanjut charts...

# =======================
# FILTER DATA (TIME LINE) (FLEKSIBEL BERDASARKAN BEBERAPA FORMAT DATA)
# =======================
col_start, col_end = st.columns(2)

# Kalau kolom numerik
if pd.api.types.is_numeric_dtype(df[time_col]):

    min_val = int(df[time_col].min())
    max_val = int(df[time_col].max())

    with col_start:
        start_val = st.number_input(
            "Mulai",
            value=min_val,
            min_value=min_val,
            max_value=max_val
        )

    with col_end:
        end_val = st.number_input(
            "Selesai",
            value=max_val,
            min_value=min_val,
            max_value=max_val
        )

    if start_val > end_val:
        st.error("Nilai mulai tidak boleh lebih besar dari nilai selesai.")
        st.stop()

    df_filter = df[
        (df[time_col] >= start_val) &
        (df[time_col] <= end_val)
    ].copy()

# Kalau kolom datetime
elif pd.api.types.is_datetime64_any_dtype(df[time_col]):

    min_date = df[time_col].min()
    max_date = df[time_col].max()

    with col_start:
        start_date = st.date_input(
            "Tanggal Mulai",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with col_end:
        end_date = st.date_input(
            "Tanggal Selesai",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    df_filter = df[
        (df[time_col] >= pd.to_datetime(start_date)) &
        (df[time_col] <= pd.to_datetime(end_date))
    ].copy()

# Kalau kolom kategori / string
else:
    unique_vals = df[time_col].dropna().astype(str).drop_duplicates().tolist()

    with col_start:
        start_val = st.selectbox("Mulai", unique_vals, index=0, key="timeline_start")

    with col_end:
        end_val = st.selectbox("Selesai", unique_vals, index=len(unique_vals) - 1, key="timeline_end")

    # Ambil posisi index
    start_idx = unique_vals.index(start_val)
    end_idx = unique_vals.index(end_val)

    # Pastikan urutan benar
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx

    # Filter berdasarkan posisi
    allowed_vals = unique_vals[start_idx:end_idx + 1]

    df_filter = df[df[time_col].astype(str).isin(allowed_vals)].copy()

if df_filter.empty:
    st.warning(
        "⚠ Tidak ada data pada rentang yang dipilih.\n\n"
        "Coba:\n"
        "- Ubah nilai **Mulai / Selesai**\n"
        "- Atau pilih **kolom timeline lain**"
    )
    st.stop()

# =======================
# SETTINGAN SIDEBAR: PILIH VARIABEL
# =======================
kpi_opsi = df_filter.select_dtypes(include="number").columns.tolist()

st.sidebar.header("Pilih Variabel KPI & Chart")


# --- KPI ---
st.sidebar.markdown("## Metric 1&2 (Sum)")
#KPI 1&2
kpi_col1 = st.sidebar.selectbox("Metric 1 Sum", kpi_opsi, index=0, key="kpi_1")
kpi_col2 = st.sidebar.selectbox("Metric 2 Sum", kpi_opsi, index=1 if len(kpi_opsi) > 1 else 0, key="kpi_2")

#KPI 3&4
#KPI3
st.sidebar.markdown("## Metric 3 (Persentase)")

persen_col = st.sidebar.selectbox(
    "Pilih Variabel Persentase",
    df_filter.columns,
    key="persentase"
)
# Cek tipe data (ihni untuk memunculkan dropdown jenis kategori, kalau var nya kategori)
is_numeric = pd.api.types.is_numeric_dtype(df_filter[persen_col])
if not is_numeric:
    kategori_opsi = df_filter[persen_col].dropna().unique().tolist()
    
    persen_kategori = st.sidebar.selectbox(
        "Pilih Kategori sebagai Pembilang",
        kategori_opsi,
        key="kategori_persen"
    )
#nah ini kalau numerik
else:
    operator = st.sidebar.selectbox(
        "Pilih Operator",
        [">", "<", "=", ">=", "<="],
        key="operator_persen"
    )
    
    angka_persen = st.sidebar.number_input(
        "Masukkan Nilai",
        value=0.0,
        key="angka_persen"
    )


#KPI 4
st.sidebar.markdown("## Metric 4 (Rasio)")

rasio_var1 = st.sidebar.selectbox(
    "Variabel Rasio 1 (Pembilang)",
    df_filter.select_dtypes(include="number").columns,
    key="rasio_1"
)

rasio_var2 = st.sidebar.selectbox(
    "Variabel Rasio 2 (Penyebut)",
    df_filter.select_dtypes(include="number").columns,
    key="rasio_2"
)

#pembatas rows didisplay dashboard
st.sidebar.markdown("------------------")

# --- Line Chart ---
st.sidebar.markdown("### Chart Line")

# Dropdown X (semua kolom)
x_line = st.sidebar.selectbox(
    "Pilih X (Time / Kategori)",
    options=all_cols,
    key="line_x"
)

# Multiselect Y (khusus numerik)
numeric_cols = df_filter.select_dtypes(include=np.number).columns.tolist()

options_y = ["Semua Variabel"] + numeric_cols

y_line = st.sidebar.multiselect(
    "Pilih Y (Numerik)",
    options=options_y,
    key="line_y"
)

# Kalau pilih semua variabel
if "Semua Variabel" in y_line:
    y_line = numeric_cols


# --- Scatterplot ---
st.sidebar.markdown("### Chart Scatter")
opsi_kolom = [col for col in kpi_opsi]
var1 = st.sidebar.selectbox("X Scatter", opsi_kolom, key="scatter1")
var2 = st.sidebar.selectbox("Y Scatter", opsi_kolom, key="scatter2")

# --- Pie Chart ---
st.sidebar.markdown("### Chart Pie")
# khusus pie chart
opsi_kolom_pie = df_filter.select_dtypes(
    include=["object", "category", "number"]
).columns.tolist()

X1 = st.sidebar.selectbox("Pilih Kategori", opsi_kolom_pie, key="pie1")
#X2 = st.sidebar.selectbox("label", opsi_kolom, key="pie2")

#pembatas rows didisplay dashboard
st.sidebar.markdown("------------------")
#statistika deskriptif

st.sidebar.markdown("### Statistika Deskriptif")
if "df" in locals():  # pastikan df sudah ada

    # 1️⃣ Ambil kolom numerik dulu
    numeric_cols = df_filter.select_dtypes(include=np.number).columns.tolist()

    if len(numeric_cols) == 0:
        st.warning("Tidak ada kolom numerik dalam dataset.")

    else:
        options1=["Semua Variabel"]+numeric_cols
        # 2️⃣ multi select (memilih beberapa variabel)
        selected_col = st.sidebar.multiselect(
            "Pilih Variabel",
            options=options1,
            key="statdes_select"
        )
        if "Semua Variabel" in selected_col:
            selected_col=numeric_cols
       
#BATAS SECTION STATDESK DAN KORELASI
st.sidebar.markdown("------------------")
#SIDEBARKORELASIPEARSON

st.sidebar.markdown("### Korelasi Variabel Numerik & Kategorik")
st.sidebar.markdown("*Korelasi Pearson (Numerik)*")
if "df" in locals():  # pastikan df sudah ada

    # 1️⃣ Ambil kolom numerik dulu
    numeric_cols = df_filter.select_dtypes(include=np.number).columns.tolist()

    if len(numeric_cols) == 0:
        st.warning("Tidak ada variabel numerik dalam dataset")
        
    else:
        options_corr=["Semua Variabel"]+numeric_cols
        # 2️⃣ multi select (memilih beberapa variabel)
        selected_num = st.sidebar.multiselect(
            "Pilih Variabel (Numerik )",
            options=options_corr,
            key="pearson_select"
        )
        if "Semua Variabel" in selected_num:
            selected_num=numeric_cols

#SIDEBAR KORELASI CRAMER'S V
st.sidebar.markdown("*Korelasi Cramer's V (kategori)*")
if "df" in locals():  # pastikan df sudah ada

    # 1️⃣ Ambil kolom kategorik dulu
    string_cols = df_filter.select_dtypes(include=["object","category"]).columns.tolist()

    if len(string_cols) > 0:
        selected_col_string = st.sidebar.multiselect(
            "Pilih Variabel (Kategori)",
            options=["Semua Variabel"]+string_cols,
            key="cramer_select"
        )
        if "Semua Variabel" in selected_col_string:
            selected_col_string=string_cols
            
    else:
        selected_col_string = []

st.sidebar.markdown("-------------------------------")    

#=================
#JUDUL DASHBOARD
#=================
st.subheader("Dashboard Interactive")

# =======================
# HITUNG KPI TAMBAHAN
# =======================
# KPI PERSENTASE DINAMIS (metric 3)
# =======================

total_data = len(df_filter)

if total_data > 0:

    # Kalau KATEGORI
    if not is_numeric:
        pembilang = df_filter[df_filter[persen_col] == persen_kategori].shape[0]

    # Kalau NUMERIK
    else:
        if operator == ">":
            pembilang = df_filter[df_filter[persen_col] > angka_persen].shape[0]
        elif operator == "<":
            pembilang = df_filter[df_filter[persen_col] < angka_persen].shape[0]
        elif operator == "=":
            pembilang = df_filter[df_filter[persen_col] == angka_persen].shape[0]
        elif operator == ">=":
            pembilang = df_filter[df_filter[persen_col] >= angka_persen].shape[0]
        elif operator == "<=":
            pembilang = df_filter[df_filter[persen_col] <= angka_persen].shape[0]

    persentase = (pembilang / total_data) * 100

else:
    pembilang = 0
    persentase = 0


# KPI Rasio (metric 4)
sum1 = df_filter[rasio_var1].sum()
sum2 = df_filter[rasio_var2].sum()

if sum2 != 0:
    rasio_value = sum1 / sum2
else:
    rasio_value = 0

# =======================
# TAMPILAN KPI CARD
# =======================
st.markdown("""
<style>
.kpi-card {background-color:#f6ffbc; padding:8px 14px; border-radius:8px; margin-bottom:10px; box-shadow: 0 8px 20px rgba(0,0,0,0.3);}
.kpi-title {font-size:12px; font-weight:600;}
.kpi-value {font-size:30px; font-weight:700; margin-top:4px;}
.kpi-card:hover {transform: translateY(-4px); /* efek hover naik sedikit */}
</style>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>{kpi_col1}</div><div class='kpi-value'>{df_filter[kpi_col1].sum():,.0f}</div></div>", unsafe_allow_html=True)

with k2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>{kpi_col2}</div><div class='kpi-value'>{df_filter[kpi_col2].sum():,.0f}</div></div>", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
                <div class='kpi-card'>
                <div class='kpi-title'>persentase {persen_col}</div>
                <div class='kpi-value'>{persentase:.2f}%</div>
                <div style='font-size:14px'>
                    ({pembilang} dari {total_data})
                </div>
                </div>
                """,
                unsafe_allow_html=True)

with k4:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Rasio {rasio_var1} / {rasio_var2}</div>
            <div class='kpi-value'>{rasio_value:.2f}</div>
            <div style='font-size:14px'>
                {sum1:,.0f} : {sum2:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("-------------------------------------------")

# =======================
# CHARTS
# =======================
#TITLE DINAMIS SESUAI DENGAN VARIABEL YANG DIPILIH
# =======================
#title dinamis linechart
y_vars = y_line
y_vars = [v for v in y_vars if v is not None]  # jaga-jaga kalau ada kosong

title_line_lc = "Line Chart of " + ", ".join(y_vars)

#title dinamis scatterplot
y_var = [var1, var2]
y_var = [v for v in y_var if v is not None]  # jaga-jaga kalau ada kosong

title_line_scp = "Scatterplot of " + ", ".join(y_var)

#mulai untuk meng-code charts
kol1, kol2, kol3 = st.columns(3, gap="small")

#linechart
with kol1:
    st.markdown("*Line Chart*")
    fig_left = px.line(df_filter, x=x_line, y=y_vars, markers=True,
                       color_discrete_sequence=["#066D6D", "#B37100", "#00d6d6"])
    fig_left.update_layout(height=500, plot_bgcolor="#f6ffbc", paper_bgcolor="#f6ffbc",
                           margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=1.02))
                           
    fig_left.update_layout(title=dict(text=title_line_lc,x=0.5,xanchor="center",font=dict(size=12, color="#242424")                                           ))
    
    fig_left.update_xaxes(
        showgrid=True, gridcolor="#9EB7E7",
        title_font=dict(color="#000000", size=13),
        tickfont=dict(color="#000000", size=11)
    )
    fig_left.update_yaxes(
        showgrid=True, gridcolor="#9EB7E7",
        title_font=dict(color="#000000", size=13),
        tickfont=dict(color="#000000", size=11)
    )
    st.plotly_chart(fig_left, use_container_width=True, config={"displayModeBar": False})

#scatterplot
with kol2:
    st.markdown("*Scatterplot*")
    fig_right = px.scatter(df_filter, x=var1, y=var2, size_max=10,
                           color_discrete_sequence=["#711bff", "#74e107", "#ffa600"])
    fig_right.update_layout(height=500, plot_bgcolor="#f6ffbc", paper_bgcolor="#f6ffbc",
                            margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=1.02))
    
    fig_right.update_layout(title=dict(text=title_line_scp,x=0.5,xanchor="center",font=dict(size=12, color="#242424")))
    
    fig_right.update_xaxes(
        showgrid=True, gridcolor="#9EB7E7",
        title_font=dict(color="#000000", size=13),
        tickfont=dict(color="#000000", size=11)
    )
    fig_right.update_yaxes(
        showgrid=True, gridcolor="#9EB7E7",
        title_font=dict(color="#000000", size=13),
        tickfont=dict(color="#000000", size=11)
    )
    st.plotly_chart(fig_right, use_container_width=True, config={"displayModeBar": False})

#piechart
with kol3:
    st.markdown("*Pie Chart*")

    # title dinamis
    title_pie = f"Pie Chart of {X1}"

    # hitung data pie
    pie_data = df_filter[X1].value_counts().reset_index()
    pie_data.columns = [X1, "JUMLAH"]

    fig_pie = px.pie(
        pie_data,
        names=X1,
        values="JUMLAH",
        hole=0,  # ubah ke 0.4 kalau mau donut 🍩
        color_discrete_sequence=[
           "#DE1A58","#FFD41D", "#45B8E6","#96FA68", "#74e107",
            "#F16D34", "#FF986A", "#B8DB80", "#85409D",
            "#00B7B5", "#FAB95B","#F075AE", "#A5C89E",'#FFFBB1',
            "#E4FF30", "#3BC1A8","#FF5FCF","#C8AAAA","#FDB5CE",
            "#FD7979","#A3D78A"
        ]
    )

    fig_pie.update_traces(
        textinfo="percent+label",
        textfont_size=12
    )

    fig_pie.update_layout(
        height=500,  # ⬅️ SAMA DENGAN LINE & SCATTER
        title=dict(
            text=title_pie,
            x=0.5,
            xanchor="center",
            font=dict(size=12, color="#242424")
        ),
        plot_bgcolor="#f6ffbc",
        paper_bgcolor="#f6ffbc",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            y=-0.15
        )
    )

    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
    
    #pembatas display dashboard hal 2 ke 3
st.markdown("*Statistika Deskriptif*")
        # ========================
        # HITUNG STATISTIK DESKRIPTIF
        # ========================
if "selected_col" in locals() and len(selected_col)>0:
    
        stat_desc=df_filter[selected_col].describe().T
        stat_desc["Varians"]=df_filter[selected_col].var()
        stat_desc=stat_desc.reset_index().rename(columns={'index':"Variabel"})
        # ========================
        # TAMPILKAN
        # ========================
        st.dataframe(stat_desc, use_container_width=True)
else:
        st.info("Pilih minimal 1 variabel untuk menampilkan statistika deskriptif.")

#TAMPILAN CORELASI
#KORELASI PEARSON
st.markdown("-------------------------------------------")

def check_same_rows(df, vars_list):
    
    # Ambil hanya kolom yang dipilih
    df_selected = df[vars_list]

    # Drop baris yang ada missing di salah satu variabel
    df_clean = df_selected.dropna()

    # Jika kosong
    if df_clean.shape[0] == 0:
        st.warning("⚠️ Tidak ada baris data lengkap (tanpa missing) untuk variabel yang dipilih.")
        return False

    # Jika jumlah baris setelah drop berbeda dengan awal
    if df_clean.shape[0] < df_selected.shape[0]:
        st.warning(
            "⚠️ Variabel yang dipilih memiliki jumlah observasi valid yang berbeda (terdapat missing value).\n\n"
            "Analisis korelasi hanya menggunakan baris data yang lengkap.\n"
            "Silakan pilih variabel lain atau tangani missing value terlebih dahulu."
        )

        st.write("Jumlah data awal:", df_selected.shape[0])
        st.write("Jumlah data valid (tanpa missing):", df_clean.shape[0])

        return False

    return True 

coll1, coll2 = st.columns(2, gap="small")

with coll1:
    st.markdown("*Korelasi Pearson (Numerik)*")
    heatmap_vars = selected_num if "selected_num" in locals() else []

    if len(heatmap_vars) >= 2:
         if check_same_rows(df_filter, heatmap_vars):

            # Title dinamis
            title_heatmap = "Pairwise pearson Heatmap"

            # Mapping X1, X2, X3
            short_labels = {
                var: f"X{i+1}" 
                for i, var in enumerate(heatmap_vars)
            }

            # Rename kolom sementara
            df_temp = df_filter[heatmap_vars].dropna().rename(columns=short_labels)

            # Hitung korelasi
            corr = df_temp.corr(method="pearson")

            # Plot heatmap
            fig_heat = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale="YlGnBu",
                aspect="equal"
            )

            fig_heat.update_layout(
                title=dict(
                    text=title_heatmap,
                    x=0.5,
                    xanchor="center",
                    font=dict(size=13, color="#000000")
                ),
                height=500,
                plot_bgcolor="#f6ffbc",
                paper_bgcolor="#f6ffbc",
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

            # Keterangan Variabel (font kecil & rapat)
            st.markdown(
                "<p style='font-size:11px; margin-bottom:3px'><b>Keterangan Variabel</b></p>",
                unsafe_allow_html=True
            )

            for original, short in short_labels.items():
                st.markdown(
                    f"<p style='font-size:10px; line-height:1.1; margin:0'>{short} = {original}</p>",
                    unsafe_allow_html=True
                )

    else:
        st.info("Pilih minimal 2 variabel numerik untuk menampilkan heatmap.")

with coll2:  
    # =====================
    # CRAMER'S V 
    # =====================
    st.markdown("*Cramer's V (Kategorik)*")
    
    heatmap_vars_string=selected_col_string if "selected_col_string" in locals() else[]
    if len(heatmap_vars_string) >= 2:
        if not check_same_rows(df_filter, heatmap_vars_string):
            pass #(krn func check_same_rows sdh ada di warning)
            #st.warning("variabel memiliki jumlah baris yang berbeda. Pilih variabel lain")
            #st.stop() klo stop aja nnti menghentikan seluruh halaman streamlit
        
        else:    
    # Title dinamis
            title_heatmap1 = "Pairwise Cramer's V Heatmap"
        
            # 🔹 Mapping X1, X2, X3
            short_labels = {
                var: f"X{i+1}"
                for i, var in enumerate(heatmap_vars_string)
            }

            #RENAME KOLOM SEMENTARA
            df_temp = df_filter[heatmap_vars_string].dropna().rename(columns=short_labels)
            n=len(short_labels)
            cramer_matrix=pd.DataFrame(
                np.zeros((n,n)),
                index=short_labels.values(),
                columns=short_labels.values()
            )
            
            #MENYIMPAN P-VALUE MATRIX
            pvalue_matrix = pd.DataFrame(
                np.ones((n,n)),
                index=short_labels.values(),
                columns=short_labels.values()
            )       
            
            #HITUNG CRAMER'S V
            for var1, var2 in combinations(short_labels.values(),2):
                contingency=pd.crosstab(df_temp[var1].fillna("Missing"), 
                                        df_temp[var2].fillna("Missing"))

                if contingency.shape[0]>1 and contingency.shape[1]>1:
                    chi2, p, dof, expected=chi2_contingency(contingency)
                    
                    n_obs=contingency.sum().sum()
                    k=min(contingency.shape)
                    
                    cramer_v=np.sqrt(chi2/(n_obs*(k-1)))
                    
                else:
                    cramer_v=0
                    p=1
                    
                cramer_matrix.loc[var1,var2]=cramer_v
                cramer_matrix.loc[var2,var1]=cramer_v
                
                #simpan p-value
                pvalue_matrix.loc[var1,var2]=p
                pvalue_matrix.loc[var2,var1]=p
            
            np.fill_diagonal(cramer_matrix.values,1)
            np.fill_diagonal(pvalue_matrix.values,0)
            
            #HEATMAP CRAMER'S V
            # Plot heatmap
            fig_heat = px.imshow(
                cramer_matrix,
                text_auto=".2f",
                color_continuous_scale="YlGnBu",
                aspect="equal"
            )

            fig_heat.update_layout(
                title=dict(
                    text=title_heatmap1,
                    x=0.5,
                    xanchor="center",
                    font=dict(size=13, color="#000000")
                ),
                height=500,
                plot_bgcolor="#f6ffbc",
                paper_bgcolor="#f6ffbc",
                margin=dict(l=20, r=20, t=40, b=20)
            )

            #MENAMPILKAN CRAMERS V
            st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
            
            #BUTTON CHI-SQUARE TEST
            if st.button("Tampilkan p-value Chi-Square Test"):
                
                signif_matrix = pvalue_matrix.applymap(
                    lambda x: 0 if x < 0.05 else 1
                )
            #HEATMAP P-VALUE CHI-SQUARE TEST
                fig_p = px.imshow(
                    pvalue_matrix,
                    text_auto=".3f",
                    color_continuous_scale="Purples_r",
                    zmin=0,
                    zmax=1,
                    aspect="equal"
                )

                #fig_p.update_traces(texttemplate="%{text}")
                
                fig_p.update_layout(
                    title=dict(
                        text="Chi-Square Test p-value",
                        x=0.5,
                        xanchor="center",
                        font=dict(size=13, color="#000000")
                    ),
                    height=500,
                    plot_bgcolor="#f6ffbc",
                    paper_bgcolor="#f6ffbc"
                )
                #MENAMPILKAN CHI-SQUARE TEST
                st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar": False})

                st.caption("Semakin gelap warna maka semakin signifikan (p-value<0.05)")
    #LEGEND
            # Keterangan Variabel (font kecil & rapat)
            st.markdown(
                "<p style='font-size:11px; margin-bottom:3px'><b>Keterangan Variabel</b></p>",
                unsafe_allow_html=True
            )

            for original, short in short_labels.items():
                st.markdown(
                    f"<p style='font-size:10px; line-height:1.1; margin:0'>{short} = {original}</p>",
                    unsafe_allow_html=True
                )
    else:
        st.info("Pilih minimal 2 variabel kategorik untuk menampilkan heatmap.")

st.markdown("-------------------------------------------")