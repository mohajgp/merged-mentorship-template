import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pyperclip
from io import BytesIO
from docx import Document

# -------------------- PAGE CONFIGURATION --------------------
st.set_page_config(page_title="KNCCI Mentorship Dashboard", layout="wide")
st.title("KNCCI Jiinue Mentorship Dashboard")
st.caption("Tracking Mentorship Sessions by Field Officers")

# -------------------- SETTINGS --------------------
OLD_FORM_URL = "https://docs.google.com/spreadsheets/d/107tWhbwBgF89VGCRnNSL4-_WrCIa68NGSPA4GkwVjDE/export?format=csv"
NEW_FORM_URL = "https://docs.google.com/spreadsheets/d/1CA7WvTkEUfeMyLuxhP91BgSWbkhV_S8V94kACj5LUMM/export?format=csv"

@st.cache_data(ttl=300)
def load_and_merge_data():
    df_old = pd.read_csv(OLD_FORM_URL)
    df_new = pd.read_csv(NEW_FORM_URL)

    df_old['Form Version'] = 'Original'
    df_new['Form Version'] = 'New'

    df_old.rename(columns={'Timestamp': 'Timestamp','County': 'County','Gender': 'Gender','Age': 'Age'}, inplace=True)
    df_new.rename(columns={'Timestamp': 'Timestamp','14. County of Business Location': 'County','12. Gender of mentee (participant)': 'Gender','11. Age of mentee (full years)': 'Age'}, inplace=True)

    df_old['Timestamp'] = pd.to_datetime(df_old['Timestamp'], errors='coerce')
    df_new['Timestamp'] = pd.to_datetime(df_new['Timestamp'], errors='coerce')

    return pd.concat([df_old, df_new], ignore_index=True)

# -------------------- LOAD DATA --------------------
df = load_and_merge_data()

if df.empty:
    st.error("❌ No data available! Please check both spreadsheets.")
    st.stop()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🗓️ Filter Sessions")
min_date, max_date = df['Timestamp'].min().date(), df['Timestamp'].max().date()
date_range = st.sidebar.date_input("Select Date Range:",(min_date, max_date),min_value=min_date, max_value=max_date)

selected_counties = st.sidebar.multiselect("Select Counties:", options=sorted(df['County'].unique()))

filtered_df = df[(df['Timestamp'].dt.date >= date_range[0]) & (df['Timestamp'].dt.date <= date_range[1])]

if selected_counties:
    filtered_df = filtered_df[filtered_df['County'].isin(selected_counties)]

st.subheader("📄 Filtered Data Table")
st.dataframe(filtered_df)

csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", data=csv_data, file_name="Filtered_Mentorship_Data.csv", mime='text/csv')
