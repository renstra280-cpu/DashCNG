import streamlit as st
import pandas as pd
import os
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
import seaborn as sns
from scipy.stats import chi2_contingency
from itertools import combinations
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from scipy.stats import shapiro
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import pandas as pd


#manggil style dr file utils/layout.py
from utils.layout import load_layout
load_layout()

#mulai dashboard
st.subheader("Dashboard Interaktif")
st.markdown("**Selamat Datang!**")
st.markdown("Silakan pilih menu di bawah ini")

# Tombol visualisasi dasar
if st.button("GRAFIK VISUALISASI", use_container_width=True):
    st.switch_page("pages/Visualisasi_Data.py")

# Tombol Regresi
if st.button("ANALISIS REGRESI", use_container_width=True):
    st.switch_page("pages/Analisis_Regresi.py")

# Tombol Forecasting
if st.button("ANALISIS ANOVA", use_container_width=True):
    st.switch_page("pages/Analisis_Anova.py")

# Tombol Forecasting
if st.button("FORECASTING", use_container_width=True):
    st.switch_page("pages/Analisis_Forecast.py")

