import streamlit as st
import pandas as pd
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt

from utils.data_source import get_data_source
from utils.prep_data import PrepData
from utils.stats_test import StatsTest
from utils.layout import load_layout
load_layout()

# ==============================
# NAVIGASI
# ==============================
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
if st.button("🏠︎ HOME"):
    st.switch_page("HOME.py")

reglinear1, reglog2 = st.columns(2, gap="small")

with reglinear1:
    with st.container(border=True):
        st.subheader("Analisis Regresi Linear")

        #CONTOH FORMAT DATA REGRESI LINEAR
        with st.expander("Klik untuk melihat contoh format data REGRESI LINEAR"):
            st.image("assets/contoh_data_reglinear.png",caption="Contoh Data Regresi Linear",width=350)

        # ==============================
        # LOAD DATA (SAMA SEPERTI ANOVA)
        # ==============================
        df_raw = get_data_source("reg_linear")

        if df_raw is not None:
            new_signature = (df_raw.shape, tuple(df_raw.columns))

            if "df_regresi" not in st.session_state:
                st.session_state["df_regresi"] = df_raw.copy()
                st.session_state["data_signature_regresi"] = new_signature

            else:
                old_signature = st.session_state.get("data_signature_regresi")

                if new_signature != old_signature:
                    keys_to_reset = [
                        "linear_results",
                        "linear_assumption",
                        "linear_final"
                    ]

                    for key in keys_to_reset:
                        if key in st.session_state:
                            del st.session_state[key]

                    st.session_state["df_regresi"] = df_raw.copy()
                    st.session_state["data_signature_regresi"] = new_signature
                    st.success("Sumber data berubah → hasil regresi direset ✅")

        if "df_regresi" not in st.session_state:
            st.info("Silakan upload data terlebih dahulu.")
        else:

            df = st.session_state["df_regresi"]

            df.columns = df.columns.str.strip().str.replace(" ", "_")

            with st.expander("Preview Data"):
                st.dataframe(df.head())

            # ==============================
            # PILIH VARIABEL
            # ==============================

            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

            if len(numeric_cols) < 2:
                st.error("Minimal butuh 2 kolom numerik untuk regresi ❌")
                st.stop()

            y_var = st.selectbox("Pilih Variabel Y (Dependen)", numeric_cols)
            x_var = st.multiselect("Pilih Variabel X (Independen)", 
                                [col for col in numeric_cols if col != y_var])

            # ==============================
            # VALIDASI
            # ==============================

            if y_var and len(x_var) >= 1:

                if st.button("Jalankan Regresi Linear"):
                    results = StatsTest.run_linear_regres(df, y_var, x_var)
                    st.session_state["linear_results"] = results
                    st.session_state["linear_final"] = True

            # ==============================
            # TAMPILKAN HASIL
            # ==============================

            if st.session_state.get("linear_final", False):
                results = st.session_state["linear_results"]
                st.markdown("**Uji Asumsi Regresi**")
                st.dataframe(results["assumption_table"])
                st.markdown("**Hasil Multiple Linear Regression**")
                st.dataframe(results["summary_table"])

                # ===============================
                # VISUALISASI REGRESI LINEAR
                # ===============================
            if st.session_state.get("linear_final",False):     

                results = st.session_state["linear_results"]

                model = results["model"]

                y_actual = model.model.endog
                y_pred = model.fittedvalues
                residuals = model.resid

                params=model.params

                #menampilkan hasil persamaan regresi
                equation="Y="
                for i, (var,coef) in enumerate(params.items()):
                    if i==0:
                        equation += f"{coef:.4f}"
                    else:
                        equation += f" + ({coef:.4f} x {var})"
                
                st.markdown("**Persamaan Model**")
                
                with st.container(border=True):
                    st.latex(equation.replace("x", r"\times"))
                    #st.write(equation)
                            
                st.markdown("**Visualisasi Model**")

                # =====================================
                # 1️⃣ Predicted vs Actual
                # =====================================
                st.markdown("*Predicted vs Actual*")

                fig1, ax1 = plt.subplots(figsize=(6,4), dpi=150)  # dpi ditambah
                ax1.scatter(y_actual, y_pred)
                ax1.plot([min(y_actual), max(y_actual)], [min(y_actual), max(y_actual)])
                ax1.set_xlabel("Actual Y")
                ax1.set_ylabel("Predicted Y")
                ax1.set_title("Predicted vs Actual")

                st.pyplot(fig1)

                # =====================================
                # 2️⃣ Residual Plot
                # =====================================
                st.markdown("*Residual Plot*")

                fig2, ax2 = plt.subplots(figsize=(6,4), dpi=150)
                ax2. scatter(y_pred, residuals)
                ax2.axhline(0)
                ax2.set_xlabel("Predicted Y")
                ax2.set_ylabel("Residuals")
                ax2.set_title("Residual Plot")

                st.pyplot(fig2)

with reglog2:
#LOAD DATA REGRESI LOGISTIK DULUUU, ADA DI GPT KOLOY

    with st.container(border=True):
        st.subheader("Analisis Regresi Logistik Multinomial")
        
        #CONTOH FORMAT DATA REGRESI LOGISTIK
        with st.expander("Klik untuk melihat contoh format data REGRESI LOGISTIK"):
            st.image("assets/contoh_data_reglog.png",caption="Contoh Data Regresi Linear",width=350)
        
        # ==============================
        # LOAD DATA (SAMA SEPERTI ANOVA)
        # ==============================
        df_raw_log = get_data_source("reg_log")

        if df_raw_log is not None:
            new_signature_log = (df_raw_log.shape, tuple(df_raw_log.columns))

            if "df_reglog" not in st.session_state:
                st.session_state                 ["df_reglog"] = df_raw_log.copy()
                st.session_state["data_signature_reglog"] = new_signature_log

            else:
                old_signature_log = st.session_state.get("data_signature_reglog")

                if new_signature_log != old_signature_log:
                    keys_to_reset = [
                        "logistic_results",
                        "logistic_final"
                    ]

                    for key in keys_to_reset:
                        if key in st.session_state:
                            del st.session_state[key]

                    st.session_state["df_reglog"] = df_raw_log.copy()
                    st.session_state["data_signature_reglog"] = new_signature_log
                    st.success("Sumber data berubah → hasil regresi direset ✅")

        if "df_reglog" not in st.session_state:
            st.info("Silakan upload data terlebih dahulu.")
            st.stop()

        df1 = st.session_state["df_reglog"]

        df1.columns = df1.columns.str.strip().str.replace(" ", "_")

        with st.expander("Preview Data"):
            st.dataframe(df1.head())
        
        #vvvLANJUT KE PILIH DATAvvv
        #identifikasi tipe data
        numeric_cols = df1.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df1.select_dtypes(exclude=np.number).columns.tolist()

    #Jika ada kolom numerik tapi kategorikal (misl=a 0/1)
        low_unique_numeric=[
            col for col in numeric_cols if df1[col].nunique() < 10
        ] 
        
        categorical_cols=list(set(categorical_cols +low_unique_numeric))

        #PILIH VARIABEL
        y_var = st.selectbox("Pilih Variabel Y (Kategorikal)", categorical_cols, key="log_y")
        #validasi & section pilih referensi Y 
        if y_var:
            y_categories=df1[y_var].astype("category").cat.categories.tolist()
            if len(y_categories)<2:
                st.warning(f"⚠ Variabel {y_var} hanya memiliki {len(y_categories)} kategori.")
                st.stop()
            else:
                y_reference=st.selectbox(
                    "pilih referensi pembanding variabel Y",
                    y_categories,
                    key="ref_y"
                )
        
        x_numeric=st.multiselect("Pilih variabel X numerik (opsional)", [col for col in numeric_cols if col !=y_var], key="log_x_num")
        x_categorical=st.multiselect("Pilih variabel x kategorikal", [col for col in categorical_cols if col !=y_var], key="log_x_cat")        
        
        #SECTION REFERENSI X
        x_reference={}
        if x_categorical:
            st.markdown("Pilih referensi variabel X")
            for col in x_categorical:
                categories=df1[col].astype("category").cat.categories.tolist()
                ref= st.selectbox(
                    f"referensi untuk {col}",
                    categories,
                    key=f"ref{col}"
                )
                
                x_reference[col]=ref
        x_var = x_numeric + x_categorical

        # ==============================
        # CEK MISSING VALUE
        # ==============================
        if y_var and x_var:
            cols_check = [y_var] + x_var
            df_check = df1[cols_check]

            nan_summary = df_check.isna().sum()
            total_nan = nan_summary.sum()

            if total_nan > 0:
                st.warning("⚠ Ditemukan missing values (NaN) pada data")

                nan_df = pd.DataFrame({
                    "Variabel": nan_summary.index,
                    "Jumlah NaN": nan_summary.values
                })

                nan_df = nan_df[nan_df["Jumlah NaN"] > 0]

                st.dataframe(nan_df)

        #VALIDASI
        if y_var and len(x_var) >= 1 and y_reference:
            if st.button("Jalankan Regresi Logistik Multinomial", key="run_logistic"):
                
                df_model = df1[[y_var] + x_var].copy()

                # ============================
                # HANDLE INF DAN NAN
                # ============================
                df_model = df_model.replace([np.inf, -np.inf], np.nan)

                before = len(df_model)
                df_model = df_model.dropna()
                after = len(df_model)

                if before != after:
                    st.info(f"ℹ {before-after} baris dengan NaN/INF dihapus otomatis")

                # ============================
                # JALANKAN MODEL
                # ============================
                results = StatsTest.run_multinomial_logistic(
                    df_model, y_var, x_var, x_reference, y_reference
                )

                st.session_state["logistic_results"] = results
                st.session_state["logistic_final"] = True

        #TAMPILKAN HASIL REGRESINYA
        if st.session_state.get("logistic_final", False):

            results = st.session_state["logistic_results"]

            st.markdown("### Ringkasan Model")
            st.dataframe(results["summary_table"])

            st.metric("Pseudo R-Square (McFadden)", f"{results['pseudo_r2']:.4f}")
            st.metric("Accuracy", f"{results['accuracy']:.4f}")

            st.markdown("### Confusion Matrix")
            cm=pd.DataFrame(
                results["confusion_matrix"],
                index=results["labels"],
                columns=results["labels"]
            )
            st.dataframe(cm)
            # st.dataframe(pd.DataFrame(results["confusion_matrix"]))