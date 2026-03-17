import streamlit as st
import pandas as pd
import numpy as np

class PrepData:
#-------------UTK PAGE VISUAL-----------
    @staticmethod
    def visual(df):
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace("-", 0)

        df = df.copy()

        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        if df.empty:
            st.error("Data kosong.")
            return None

        return df
#-------------UTK PAGE REGRESI-----------
    @staticmethod
    def linear(df):
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace("-", np.nan)

        if df.select_dtypes(include="number").shape[1] < 2:
            st.error("Regresi Linear butuh minimal 2 kolom numerik.")
            return None

        return df

    @staticmethod
    def logistic(df):
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace("-", 0)

        if df.select_dtypes(include="number").shape[1] < 1:
            st.error("Regresi Logistik butuh minimal 1 kolom numerik.")
            return None

        return df
    
#-------------UTK PAGE FORECAST-----------
    @staticmethod
    def forecast(df):
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace("-", 0)

        df = df.copy()

        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        if df.empty:
            st.error("Data kosong.")
            return None

        return df

#-------------UTK PAGE ANOVA-----------
    @staticmethod
    def anova(df, value_col, group_col):
        
        # Copy dataframe
        df = df.copy()

        # Cek kolom tersedia (validasi kolom)
        if value_col not in df.columns:
            return None,f"Kolom {value_col} tidak ditemukan."
            
        if group_col not in df.columns:
            return None,f"Kolom {group_col} tidak ditemukan."

        #tidak boleh mengambil data yang sama
        if value_col == group_col:
            return None, "Kolom Nilai dan Kolom Kelompok tidak boleh sama."

        # Ambil hanya 2 kolom penting
        df = df[[value_col, group_col]]

        # Bersihkan data
        df = df.replace("-", None)

        # Ubah value jadi numerik
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        # Drop missing
        df = df.dropna()
        
        #cek apakah value kosong atau tidak semua numerik
        if df.empty:
            return None,f"Data dikolom '{value_col}' harus numerik. Tidak ada data yang valid setelah preprocessing"

        # CEK KEANEHAN GROUP
        total_rows = len(df)
        unique_groups = df[group_col].nunique()

        if total_rows/unique_groups <= 0.9:  # threshold 1 bisa diubah
            return None, (
                f"Jumlah kategori di kolom '{group_col}' hampir sama dengan jumlah baris.\n"
                "Data tidak bisa dianalisis karena tiap group hanya memiliki 1 row ⚠"
            )
                # Pastikan group sebagai kategori
        df[group_col] = df[group_col].astype("category")

        return df, None