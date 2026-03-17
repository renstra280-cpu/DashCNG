import streamlit as st
import pandas as pd
import re
import requests
from io import BytesIO


def get_data_source(key_name):
    source = st.radio(
        "Pilih Sumber Data",
        ["Upload File", "Input URL Spreadsheet"],
        key=f"source_{key_name}"
    )

    df = None
    selected_sheet= None

    #=====UPLOAD FILE==========
    if source == "Upload File":
        file = st.file_uploader("Upload CSV / Excel",type=["csv", "xlsx"],key=f"upload_{key_name}")
        if file:
            #file csv, (hnya ada 1 sheet saja)
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            #file excel terdiri beberapa sheets
            else:
                #ambil daftar sheet dulu
                excel_file=pd.ExcelFile(file)
                sheet_list=excel_file.sheet_names
                selected_sheet=st.selectbox(
                    "Pilih Sheet",
                    options=sheet_list,
                    key=f"sheet_{key_name}"
                )
                df = pd.read_excel(
                    excel_file,
                    sheet_name=selected_sheet,
                    engine="openpyxl"
                )
                #berishkan data
                if df is not None:
                    df = df.dropna(axis=1, how="all")
                    df = df.dropna(axis=0, how="all")

#===========GOOGLE SHEET==========
#===========GOOGLE SHEET==========
    else:
        url = st.text_input(
            "Masukkan URL Google Sheets (link harus public/viewer)",
            key=f"url_{key_name}"
        )

        if url:
            if not url.startswith("http"):
                url = "https://" + url

            try:
                import re
                import requests
                from io import BytesIO

                # ambil file_id dari url
                match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                if not match:
                    raise ValueError("URL Google Sheets tidak valid")

                file_id = match.group(1)

                # download excel dari google sheets
                excel_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
                response = requests.get(excel_url)

                if response.status_code != 200:
                    raise ValueError("File tidak bisa diakses (pastikan public)")

                # baca excel dari memory
                xls = pd.ExcelFile(BytesIO(response.content))

                sheet_list = xls.sheet_names

                selected_sheet = st.selectbox(
                    "Pilih Sheet",
                    options=sheet_list,
                    key=f"gsheet_{key_name}"
                )

                df = pd.read_excel(
                    xls,
                    sheet_name=selected_sheet,
                    engine="openpyxl"
                )

                # bersihkan data
                df = df.dropna(axis=1, how="all")
                df = df.dropna(axis=0, how="all")

            except Exception as e:
                st.error(f"Gagal membaca Google Sheets: {e}")

    return df