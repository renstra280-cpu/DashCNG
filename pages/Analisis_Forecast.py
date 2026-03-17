# ==========================================
# ARIMA & MOVING AVERAGE - CLEAN VERSION
# ==========================================

import streamlit as st
import plotly.express as px
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from utils.data_source import get_data_source
from utils.prep_data import PrepData
from utils.layout import load_layout
load_layout()

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
if st.button("🏠︎ HOME"):
    st.switch_page("HOME.py")

st.subheader("ANALISIS FORECASTING")

#CONTOH FORMAT DATA ANOVA
with st.expander("Klik untuk melihat contoh format data FORECASTING"):
        st.image("assets/format_data_forecasting.png",caption="Contoh Format Data Forecasting",width=200)

# ==========================================
# LOAD DATA
# ==========================================

df = None
df_raw = get_data_source("forecast")

if df_raw is not None:
    df = PrepData.forecast(df_raw)

if df is None:
    st.warning("Silakan upload data terlebih dahulu.")
    st.stop()

# Pastikan kolom unik
df = df.loc[:, ~df.columns.duplicated()].copy()

st.success("Data berhasil dimuat")
with st.expander("Klik untuk melihat preview data upload"):
    st.dataframe(df.head(20))

# ==========================================
# IDENTIFIKASI TIPE DATA
# ==========================================

datetime_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

timeline_options = ["Tanpa Rentang Waktu"] + datetime_cols + numeric_cols
forecast_options = numeric_cols.copy()

# ==========================================
# PILIH KOLOM
# ==========================================

col1, col2 = st.columns(2)

with col1:
    time_col = st.selectbox(
        "Pilih Kolom Base Time-Line",
        timeline_options
    )

with col2:
    target_col = st.selectbox(
        "Pilih Variabel yang Diforecast",
        forecast_options
    )

# ==========================================
# BENTUK DATA FINAL (DINAMIS & AMAN)
# ==========================================
if time_col != "Tanpa Rentang Waktu":

    # Buat dataframe awal
    df_filter = pd.DataFrame({
        time_col: df[time_col],
        target_col: df[target_col]
    }).dropna()

    # Sort dulu
    df_filter = df_filter.sort_values(by=time_col)

    # ==========================
    # FILTER RENTANG WAKTU
    # ==========================

    st.subheader("Filter Rentang Waktu")

    # Jika datetime
    if pd.api.types.is_datetime64_any_dtype(df_filter[time_col]):

        min_date = df_filter[time_col].min()
        max_date = df_filter[time_col].max()

        start_date = st.date_input(
            "Pilih Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

        end_date = st.date_input(
            "Pilih End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        df_filter = df_filter[
            (df_filter[time_col] >= pd.to_datetime(start_date)) &
            (df_filter[time_col] <= pd.to_datetime(end_date))
        ]

    # Jika numerik
    else:

        min_val = df_filter[time_col].min()
        max_val = df_filter[time_col].max()

        start_val = st.number_input(
            "Start Value",
            value=float(min_val)
        )

        end_val = st.number_input(
            "End Value",
            value=float(max_val)
        )

        df_filter = df_filter[
            (df_filter[time_col] >= start_val) &
            (df_filter[time_col] <= end_val)
        ]

else:

    df_filter = pd.DataFrame({
        "Index": range(1, len(df) + 1),
        target_col: df[target_col]
    }).dropna()

    time_col = "Index"
# ==========================================
# SIDEBAR SETTING
# ==========================================

st.sidebar.header("Pengaturan Model")

p = st.sidebar.number_input("ARIMA p", 0, 5, 1)
d = st.sidebar.number_input("ARIMA d", 0, 2, 1)
q = st.sidebar.number_input("ARIMA q", 0, 5, 1)


forecast_steps_arima = st.sidebar.number_input(
    "Jumlah Periode Forecast (ARIMA)",
    min_value=1,
    max_value=100,
    value=10
)

st.sidebar.divider()

st.sidebar.subheader("Moving Average Setting")

window_size = st.sidebar.slider("Window Moving Average", 2, 30, 5)

forecast_steps_ma = st.sidebar.number_input(
    "Jumlah Periode Forecast (MA)",
    min_value=1,
    max_value=100,
    value=5
)
# ==========================================
# VISUALISASI
# ==========================================

colA, colB = st.columns(2)

# ==========================================
# ARIMA
# ==========================================

with colA:
    st.subheader("ARIMA Forecasting")

    df_arima = df_filter.copy()

    if len(df_arima) > 10:

        model = ARIMA(df_arima[target_col], order=(p, d, q))
        model_fit = model.fit()

        forecast = model_fit.get_forecast(steps=forecast_steps_arima)

        last_x = df_arima[time_col].iloc[-1]

        if pd.api.types.is_datetime64_any_dtype(df_arima[time_col]):
            future_index = future_index = pd.date_range(start=last_x,periods=forecast_steps_arima + 1,freq="D")[1:]

        else:
            future_index = future_index = range(
                            int(last_x) + 1,
                            int(last_x) + 1 + forecast_steps_arima
                        )

        forecast_df = pd.DataFrame({
            time_col: future_index,
            f"{target_col}_Forecast": forecast.predicted_mean.values
        })

        actual_df = df_arima.rename(
            columns={target_col: f"{target_col}_Actual"}
        )

        plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)

        fig_arima = px.line(
            plot_df,
            x=time_col,
            y=[f"{target_col}_Actual", f"{target_col}_Forecast"],
            markers=True
        )

        st.plotly_chart(fig_arima, use_container_width=True)

    else:
        st.warning("Data terlalu sedikit untuk ARIMA (minimal >10 baris)")

# ==========================================
# MOVING AVERAGE
# ==========================================

with colB:
    st.subheader("Moving Average")

    df_ma = df_filter.copy()

    df_ma[f"{target_col}_MA"] = df_ma[target_col].rolling(
        window=window_size
    ).mean()

        # Forecast MA sederhana (pakai rata-rata terakhir)
    last_ma = df_ma[f"{target_col}_MA"].iloc[-1]

    last_x = df_ma[time_col].iloc[-1]

    if pd.api.types.is_datetime64_any_dtype(df_ma[time_col]):
        future_index_ma = pd.date_range(
            start=last_x,
            periods=forecast_steps_ma + 1,
            freq="D"
        )[1:]
    else:
        future_index_ma = range(
            int(last_x) + 1,
            int(last_x) + 1 + forecast_steps_ma
        )

    forecast_ma_df = pd.DataFrame({
        time_col: future_index_ma,
        f"{target_col}_MA_Forecast": [last_ma] * forecast_steps_ma
    })

    df_ma_plot = pd.concat([df_ma, forecast_ma_df], ignore_index=True)

    fig_ma = px.line(
    df_ma_plot,
    x=time_col,
    y=[target_col, f"{target_col}_MA", f"{target_col}_MA_Forecast"],
    markers=True
)

    st.plotly_chart(fig_ma, use_container_width=True)