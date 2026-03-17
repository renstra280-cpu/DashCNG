import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import shapiro
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from sklearn.metrics import confusion_matrix, accuracy_score
import numpy as np
import streamlit as st

class StatsTest:
#-------------UTK PAGE REGRESI MULTIPLE LINEAR-----------
    @staticmethod
    def run_linear_regres(df, y_var, x_var):

        Y = df[y_var]
        X = df[x_var]
        

        st.write("X types:", X.dtypes)
        st.write("Jumlah NaN:", X.isna().sum())

        # gabungkan dulu supaya baris sinkron
        data = pd.concat([Y, X], axis=1)

        # ubah semua jadi numerik
        data = data.apply(pd.to_numeric, errors="coerce")

        # hilangkan inf dan nan
        data = data.replace([np.inf, -np.inf], np.nan).dropna()
        
        # pisahkan lagi
        Y = data[y_var]
        X = data[x_var]
        
        X = sm.add_constant(X)
        
        model = sm.OLS(Y, X).fit()
        residuals = model.resid

        # ===== UJI ASUMSI =====
        shapiro_stat, shapiro_p = shapiro(residuals)
        bp_test = het_breuschpagan(residuals, X)
        dw_stat = durbin_watson(residuals)

        assumption_table = pd.DataFrame({
            "Uji": [
                "Normalitas (Shapiro-Wilk)",
                "Homoskedastisitas (Breusch-Pagan)",
                "Independensi (Durbin-Watson)"
            ],
            "Statistik": [
                round(shapiro_stat, 4),
                "-",
                round(dw_stat, 4)
            ],
            "P-Value": [
                round(shapiro_p, 4),
                round(bp_test[1], 4),
                "-"
            ]
        })

        summary_table = pd.DataFrame({
            "Coef": model.params,
            "Std Err": model.bse,
            "t": model.tvalues,
            "P>|t|": model.pvalues,
            "Lower 95%": model.conf_int()[0],
            "Upper 95%": model.conf_int()[1]
        }).round(4)

        return {
            "model": model,
            "assumption_table": assumption_table,
            "summary_table": summary_table
        }
#-------------UTK PAGE REGRESI LOGISTIK MULTINOMIAL-----------
    @staticmethod
    def run_multinomial_logistic(df, y_var, x_var, x_reference, y_reference):

        df=df.copy()

        #pastikan Y kategorik
        df[y_var]=df[y_var].astype("category")
        labels=df[y_var].cat.categories
        #encode Y ke angka
        y=df[y_var].cat.codes

        #encode X ke angka
        X = df[x_var]
        # encode variabel kategorikal
        X = pd.get_dummies(X, drop_first=True)
        #Pastikan semua numeric
        X=X.astype(float)
        X = sm.add_constant(X)

        #model MNLogit
        model=sm.MNLogit(y,X)
        result=model.fit(disp=False)

        #prediksi probs
        pred_prob=result.predict(X)

        #ambil kelas dengan probabilitas tertinggi 
        y_pred=np.argmax(pred_prob.values, axis=1)

        #confusion matrix
        cm=confusion_matrix(y,y_pred)
        acc=accuracy_score(y,y_pred)

        #ringkasan koefisien
        summary_table=result.summary2().tables[1]
        
        coef_col="Coef." if "Coef." in summary_table.columns else "Coef"
        summary_table["Odds_Ratio"]=np.exp(summary_table[coef_col])

        return{
            "model": result,
            "summary_table": summary_table,
            "confusion_matrix": cm,
            "accuracy": acc,
            "pseudo_r2": result.prsquared,
            "labels": labels
        }

#-------------UTK PAGE ANOVA-----------
    @staticmethod
    def run_anova(df, value_col, group_col):

        # Model
        model = ols(f'{value_col} ~ C({group_col})', data=df).fit()
        residuals = model.resid

        # Uji Normalitas
        stat_norm, p_norm = stats.shapiro(residuals)

        # Uji Homogenitas
        groups = df[group_col].unique()
        group_data = [
            df[df[group_col] == g][value_col]
            for g in groups
        ]

        stat_lev, p_lev = stats.levene(*group_data)

        # ANOVA table
        anova_table = sm.stats.anova_lm(model, typ=2)

        return {
            "stat_norm": stat_norm,
            "p_norm": p_norm,
            "stat_lev": stat_lev,
            "p_lev": p_lev,
            "anova_table": anova_table
        }
    
    #tambahan jika data user tidak memenuhi asumsi dan pilih lanjut kruskal 
    @staticmethod
    def run_kruskal(df, value_col, group_col):
        groups=df[group_col].unique()
        groups_data=[
            df[df[group_col]==g][value_col]
            for g in groups
        ]
        stat_krus, p_krus=stats.kruskal(*groups_data)

        return {
            "stat_krus": stat_krus,
            "p_krus": p_krus,
        }
    

