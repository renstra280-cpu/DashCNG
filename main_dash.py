import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# =======================
# PAGE CONFIG
# =======================
st.set_page_config(
    page_title="PT Cipta Nirmala",
    layout="wide"
)

# =======================
# BACKGROUND
# =======================
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: transparent;
}
.block-container {
    background-color: #eeff7b;
}
section.main {
    background-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# =======================
# HEADER
# =======================
col1, col2 = st.columns([1, 25])
with col1:
    st.markdown(
        """
        <div style="margin-top:-3px;">
            <img src="data:image/png;base64,{}" width="30">
        </div>
        """.format(
            __import__("base64").b64encode(
                open("assets/logo_cn.png", "rb").read()
            ).decode()
        ),
        unsafe_allow_html=True
    )
with col2:
    st.markdown("""
    <div style="font-family:Arial;">
        <div style="font-size:18px; font-weight:600; color:#000000;">
            PT CIPTA NIRMALA GROUP
        </div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("Dashboard Interactive")

# =======================
# UPLOAD DATA
# =======================
uploaded_file = st.file_uploader(
    "Upload data (CSV / Excel)",
    type=["csv", "xlsx"]
)

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if uploaded_file:
    df = load_data(uploaded_file)
    st.session_state["df"] = df
    st.success("Data berhasil diupload & disimpan")
    st.dataframe(df, use_container_width=True)

# =======================
# CEK DATA
# =======================
if "df" not in st.session_state:
    st.warning("Silakan upload data terlebih dahulu.")
    st.stop()

df = st.session_state["df"].copy()
df.columns = df.columns.str.strip().str.upper()
df = df.replace("-", 0)

all_cols = df.columns.tolist()
time_col = st.selectbox(
    "Pilih Kolom Time-Line (Sumbu X)",
    options=[None] + all_cols,
    index=0,
    help="Kolom waktu / periode / urutan"
)
if not time_col:
    st.stop()

# =======================
# FILTER DATA (FLEKSIBEL)
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
        start_val = st.selectbox("Mulai", unique_vals, index=0)

    with col_end:
        end_val = st.selectbox("Selesai", unique_vals, index=len(unique_vals) - 1)

    # Ambil posisi index
    start_idx = unique_vals.index(start_val)
    end_idx = unique_vals.index(end_val)

    # Pastikan urutan benar
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx

    # Filter berdasarkan posisi
    allowed_vals = unique_vals[start_idx:end_idx + 1]

    df_filter = df[df[time_col].astype(str).isin(allowed_vals)].copy()

# =======================
# SIDEBAR: PILIH VARIABEL
# =======================
kpi_opsi = df_filter.select_dtypes(include="number").columns.tolist()

st.sidebar.header("Pilih Variabel KPI & Chart")

# --- KPI ---
kpi_col1 = st.sidebar.selectbox("KPI 1", kpi_opsi, index=0, key="kpi_1")
kpi_col2 = st.sidebar.selectbox("KPI 2", kpi_opsi, index=1 if len(kpi_opsi) > 1 else 0, key="kpi_2")
kpi_col3 = st.sidebar.selectbox("KPI 3", kpi_opsi, index=2 if len(kpi_opsi) > 2 else 0, key="kpi_3")
kpi_col4 = st.sidebar.selectbox("KPI 4", kpi_opsi, index=3 if len(kpi_opsi) > 3 else 0, key="kpi_4")

# --- Korelasi ---
st.sidebar.markdown("### Korelasi")
var_corr1 = st.sidebar.selectbox("Variabel 1", kpi_opsi, index=0, key="corr_1")
var_corr2 = st.sidebar.selectbox("Variabel 2", kpi_opsi, index=1 if len(kpi_opsi) > 1 else 0, key="corr_2")
corr_value = df_filter[[var_corr1, var_corr2]].corr().iloc[0,1]

# --- Line Chart ---
st.sidebar.markdown("### Chart Line")
opsi_kolom = [col for col in kpi_opsi]
var_y1 = st.sidebar.selectbox("Indikator 1", opsi_kolom, key="ind_1")
var_y2 = st.sidebar.selectbox("Indikator 2", opsi_kolom, index=1 if len(opsi_kolom)>1 else 0, key="ind_2")
var_y3 = st.sidebar.selectbox("Indikator 3", opsi_kolom, index=2 if len(opsi_kolom)>2 else 0, key="ind_3")

# --- Scatterplot ---
st.sidebar.markdown("### Chart Scatter")
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

#=================
#JUDUL DASHBOARD
#=================
st.subheader("Dashboard Interactive")

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

k1, k2, k3, k4 = st.columns(4, gap="xsmall")

with k1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>{kpi_col1}</div><div class='kpi-value'>{df_filter[kpi_col1].sum():,.0f}</div></div>", unsafe_allow_html=True)

with k2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>{kpi_col2}</div><div class='kpi-value'>{df_filter[kpi_col2].sum():,.0f}</div></div>", unsafe_allow_html=True)

with k3:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>{kpi_col3}</div><div class='kpi-value'>{df_filter[kpi_col3].sum():,.0f}</div></div>", unsafe_allow_html=True)

with k4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Korelasi {var_corr1} & {var_corr2}</div><div class='kpi-value'>{corr_value:.2f}</div></div>", unsafe_allow_html=True)

# =======================
# CHARTS
# =======================
#TITLE DINAMIS SESUAI DENGAN VARIABEL YANG DIPILIH
# =======================
#title dinamis linechart
y_vars = [var_y1, var_y2, var_y3]
y_vars = [v for v in y_vars if v is not None]  # jaga-jaga kalau ada kosong

title_line_lc = "Line Chart of " + ", ".join(y_vars)

#title dinamis scatterplot
y_var = [var1, var2]
y_var = [v for v in y_var if v is not None]  # jaga-jaga kalau ada kosong

title_line_scp = "Scatterplot of " + ", ".join(y_var)

kol1, kol2, kol3 = st.columns(3, gap="small")

with kol1:
    st.markdown("**Line Chart**")
    fig_left = px.line(df_filter, x=time_col, y=y_vars, markers=True,
                       color_discrete_sequence=["#066D6D", "#B37100", "#00d6d6"])
    fig_left.update_layout(height=340, plot_bgcolor="#f6ffbc", paper_bgcolor="#f6ffbc",
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
    st.plotly_chart(fig_left, use_container_width=True)

with kol2:
    st.markdown("**Scatterplot**")
    fig_right = px.scatter(df_filter, x=var1, y=var2, size_max=10,
                           color_discrete_sequence=["#711bff", "#74e107", "#ffa600"])
    fig_right.update_layout(height=340, plot_bgcolor="#f6ffbc", paper_bgcolor="#f6ffbc",
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
    st.plotly_chart(fig_right, use_container_width=True)

with kol3:
    st.markdown("**Pie Chart**")

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
        height=340,  # ⬅️ SAMA DENGAN LINE & SCATTER
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

    st.plotly_chart(fig_pie, use_container_width=True)
