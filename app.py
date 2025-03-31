import streamlit as st
import pandas as pd
import requests
from streamlit_agraph import agraph, Node, Edge, Config

# === Цветовая схема и параметры ===
PAGE_BG_COLOR = "#262123"
PAGE_TEXT_COLOR = "#E8DED3"
SIDEBAR_BG_COLOR = "#262123"
SIDEBAR_LABEL_COLOR = "#E8DED3"
SIDEBAR_TAG_TEXT_COLOR = "#E8DED3"
SIDEBAR_TAG_BG_COLOR = "#6A50FF"
BUTTON_BG_COLOR = "#262123"
BUTTON_TEXT_COLOR = "#4C4646"
BUTTON_CLEAN_TEXT_COLOR = "#E8DED3"
SIDEBAR_HEADER_COLOR = "#E8DED3"
SIDEBAR_TOGGLE_ARROW_COLOR = "#E8DED3"
HEADER_MENU_COLOR = "#262123"
GRAPH_BG_COLOR = "#262123"
GRAPH_LABEL_COLOR = "#E8DED3"
NODE_NAME_COLOR = "#4C4646"
NODE_CITY_COLOR = "#D3DAE8"
NODE_FIELD_COLOR = "#EEC0E7"
NODE_ROLE_COLOR = "#F4C07C"
EDGE_COLOR = "#4C4646"
HIGHLIGHT_EDGE_COLOR = "#6A50FF"
DEFAULT_PHOTO = "https://static.tildacdn.com/tild3532-6664-4163-b538-663866613835/hosq-design-NEW.png"

# === Настройки страницы ===
st.set_page_config(page_title="HOSQ Artists Mapping (Agraph)", layout="wide")

# === CSS стилизация ===
st.markdown(f"""
    <style>
    body, .stApp {{
        background-color: {PAGE_BG_COLOR};
        color: {PAGE_TEXT_COLOR};
    }}
    .stSidebar {{
        background-color: {SIDEBAR_BG_COLOR} !important;
    }}
    .stSidebar label, .stSidebar .css-1n76uvr {{
        color: {SIDEBAR_LABEL_COLOR} !important;
    }}
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {{
        color: {SIDEBAR_HEADER_COLOR} !important;
    }}
    .stSidebar .css-ewr7em svg {{
        stroke: {SIDEBAR_TOGGLE_ARROW_COLOR} !important;
    }}
    .stMultiSelect>div>div {{
        background-color: {PAGE_BG_COLOR} !important;
        color: {PAGE_TEXT_COLOR} !important;
    }}
    .stMultiSelect [data-baseweb="tag"] {{
        background-color: {SIDEBAR_TAG_BG_COLOR} !important;
        color: {SIDEBAR_TAG_TEXT_COLOR} !important;
    }}
    .stButton > button {{
        background-color: {BUTTON_BG_COLOR} !important;
        color: {BUTTON_CLEAN_TEXT_COLOR} !important;
        border: none;
    }}
    .artist-card * {{
        color: {PAGE_TEXT_COLOR} !important;
    }}
    header {{
        background-color: {HEADER_MENU_COLOR} !important;
    }}
    iframe[src*="agraph"] {{
        background-color: {GRAPH_BG_COLOR} !important;
    }}
    .element-container iframe {{
        background-color: {GRAPH_BG_COLOR} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# === Загрузка данных ===
df = pd.read_csv("Etudes Lab 1 artistis.csv").fillna("")
df["professional field"] = df["professional field"].astype(str)
df["role"] = df["role"].astype(str)
df["country"] = df["country and city"].apply(lambda x: x.split(",")[0].strip() if "," in x else x.strip())
df["city"] = df["country and city"].apply(lambda x: x.split(",")[1].strip() if "," in x else "")

def get_google_drive_image_url(url):
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/thumbnail?id={file_id}"
    return url

def is_valid_image(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=3)
        return r.status_code == 200 and 'image' in r.headers.get('Content-Type', '')
    except:
        return False

# === Распарсить поля для фильтров ===
df_fields = sorted(set(field.strip() for sublist in df["professional field"].str.split(",") for field in sublist if field.strip()))
df_roles = sorted(set(role.strip() for sublist in df["role"].str.split(",") for role in sublist if role.strip()))

# === Фильтры ===
st.sidebar.header("Filters")
field_filter = st.sidebar.multiselect("Professional Field", df_fields)
role_filter = st.sidebar.multiselect("Role", df_roles)
country_filter = st.sidebar.multiselect("Country", sorted([x for x in df["country"].unique() if x]))
city_filter = st.sidebar.multiselect("City", sorted([x for x in df["city"].unique() if x]))

filtered_df = df.copy()
if field_filter:
    filtered_df = filtered_df[filtered_df["professional field"].apply(lambda x: any(f.strip() in field_filter for f in x.split(",")))]
if role_filter:
    filtered_df = filtered_df[filtered_df["role"].apply(lambda x: any(r.strip() in role_filter for r in x.split(",")))]
if country_filter:
    filtered_df = filtered_df[filtered_df["country"].isin(country_filter)]
if city_filter:
    filtered_df = filtered_df[filtered_df["city"].isin(city_filter)]
