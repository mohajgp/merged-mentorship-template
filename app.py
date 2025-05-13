import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pyperclip

# -------------------- PAGE CONFIGURATION --------------------
st.set_page_config(
    page_title="KNCCI Mentorship Dashboard",
    page_icon="\ud83d\udcda",
    layout="wide"
)

st.title("\ud83d\udcda KNCCI Jiinue Mentorship Dashboard")
st.caption("Tracking Mentorship Sessions by Field Officers")

# -------------------- SETTINGS --------------------
OLD_FORM_URL = "https://docs.google.com/spreadsheets/d/107tWhbwBgF89VGCRnNSL4-_WrCIa68NGSPA4GkwVjDE/export?format=csv"
NEW_FORM_URL = "https://docs.google.com/spreadsheets/d/1CA7WvTkEUfeMyLuxhP91BgSWbkhV_S8V94kACj5LUMM/export?format=csv"

# -------------------- FUNCTION TO LOAD AND MERGE DATA --------------------
@st.cache_data(ttl=300)
def load_and_merge_data():
    df_old = pd.read_csv(OLD_FORM_URL)
    df_new = pd.read_csv(NEW_FORM_URL)

    df_old.columns = df_old.columns.str.strip()
    df_new.columns = df_new.columns.str.strip()

    df_old['Form Version'] = 'Original'
    df_new['Form Version'] = 'New'

    df_old.rename(columns={
        'Timestamp': 'Timestamp',
        'County': 'County',
        'Gender': 'Gender',
        'Age': 'Age',
    }, inplace=True)

    df_new.rename(columns={
        'Timestamp': 'Timestamp',
        '14. County of Business Location': 'County',
        '12. Gender of mentee (participant)': 'Gender',
        '11. Age of mentee (full years)': 'Age',
    }, inplace=True)

    df_old['Timestamp'] = pd.to_datetime(df_old['Timestamp'], errors='coerce')
    df_new['Timestamp'] = pd.to_datetime(df_new['Timestamp'], errors='coerce')

    df_old['County'] = df_old['County'].astype(str).str.strip().str.title()
    df_new['County'] = df_new['County'].astype(str).str.strip().str.title()

    df_old['Gender'] = df_old['Gender'].astype(str).str.strip().str.title()
    df_new['Gender'] = df_new['Gender'].astype(str).str.strip().str.title()

    df_old['Age'] = pd.to_numeric(df_old['Age'], errors='coerce')
    df_new['Age'] = pd.to_numeric(df_new['Age'], errors='coerce')

    return pd.concat([df_old, df_new], ignore_index=True)

# -------------------- LOAD DATA --------------------
df = load_and_merge_data()

if df.empty:
    st.error("\u274c No data available! Please check both spreadsheets.")
    st.stop()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("\ud83d\uddd3\ufe0f Filter Sessions")

min_date = df['Timestamp'].min().date()
max_date = df['Timestamp'].max().date()

st.sidebar.markdown(f"\ud83d\uddd3\ufe0f **Earliest Submission**: `{min_date}`")
st.sidebar.markdown(f"\ud83d\uddd3\ufe0f **Latest Submission**: `{max_date}`")

# Date Range Filter
date_range = st.sidebar.date_input("Select Date Range:", value=(min_date, max_date), min_value=min_date, max_value=max_date)
start_date, end_date = date_range if isinstance(date_range, tuple) else (date_range, date_range)

# Form Version Filter
form_versions = df['Form Version'].unique().tolist()
selected_versions = st.sidebar.multiselect("Select Form Version:", options=form_versions, default=form_versions)

# County Filter
counties = df['County'].dropna().unique()
selected_counties = st.sidebar.multiselect("Select Counties:", options=sorted(counties), default=sorted(counties))

# Gender Filter
genders = df['Gender'].dropna().unique()
selected_genders = st.sidebar.multiselect("Select Gender:", options=sorted(genders), default=sorted(genders))

# Apply Filters
filtered_df = df[
    (df['Timestamp'].dt.date >= start_date) &
    (df['Timestamp'].dt.date <= end_date) &
    (df['Form Version'].isin(selected_versions)) &
    (df['County'].isin(selected_counties)) &
    (df['Gender'].isin(selected_genders))
]

# -------------------- METRICS --------------------
st.subheader("\ud83d\udcc8 Summary Metrics")

total_sessions = df.shape[0]
filtered_sessions = filtered_df.shape[0]
unique_counties = filtered_df['County'].nunique()
total_participants = filtered_df.drop_duplicates(subset=['County', 'Gender']).shape[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("\u2705 Total Sessions", f"{total_sessions:,}")
col2.metric("\ud83d\udcca Filtered Sessions", f"{filtered_sessions:,}")
col3.metric("\ud83d\udccd Counties Covered", unique_counties)
col4.metric("\ud83d\udc65 Unique Participants", total_participants)

# -------------------- COUNTY SUBMISSION BAR CHART --------------------
st.subheader("\ud83d\udccd Submissions by County")
county_counts = filtered_df.groupby('County').size().reset_index(name='Submissions')
fig_bar = px.bar(county_counts, x='County', y='Submissions', color='County', title='Number of Submissions by County')
st.plotly_chart(fig_bar, use_container_width=True)

# -------------------- NON-SUBMISSIONS --------------------
st.subheader("\u274c Counties with No Submissions")
all_counties_47 = [...]
submitted_counties = filtered_df['County'].unique().tolist()
no_submission_counties = [c for c in all_counties_47 if c not in submitted_counties]

if no_submission_counties:
    st.error(f"\u274c Counties with **NO** Submissions: {', '.join(no_submission_counties)}")
else:
    st.success("\u2705 All counties have submissions in selected date range.")

# -------------------- DATA TABLE & DOWNLOAD --------------------
st.subheader("\ud83d\udcc4 Filtered Data Table")
if not filtered_df.empty:
    st.dataframe(filtered_df)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="\ud83d\udcc5 Download CSV",
        data=csv_data,
        file_name=f"Mentorship_Submissions_{datetime.now().date()}.csv",
        mime='text/csv'
    )
else:
    st.info("\u2139\ufe0f No submissions match current filters.")
