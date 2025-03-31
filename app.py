import streamlit as st
import pandas as pd
import requests
from streamlit_agraph import agraph, Node, Edge, Config

# === Цветовая схема и параметры ===
PAGE_BG_COLOR = "#262123"               # Цвет фона страницы
PAGE_TEXT_COLOR = "#E8DED3"             # Основной цвет текста
SIDEBAR_BG_COLOR = "#262123"            # Цвет фона сайдбара
SIDEBAR_LABEL_COLOR = "#E8DED3"         # Цвет текста лейблов фильтров
SIDEBAR_TAG_TEXT_COLOR = "#E8DED3"      # Цвет текста выбранных тэгов
SIDEBAR_TAG_BG_COLOR = "#6A50FF"        # Фон выбранных тэгов
BUTTON_BG_COLOR = "#262123"             # Фон кнопок
BUTTON_TEXT_COLOR = "#4C4646"           # Цвет текста кнопок
BUTTON_CLEAN_TEXT_COLOR = "#E8DED3"     # Цвет текста кнопки очистки
SIDEBAR_HEADER_COLOR = "#E8DED3"        # Цвет заголовка Filters
SIDEBAR_TOGGLE_ARROW_COLOR = "#E8DED3"  # Цвет стрелки бокового меню
HEADER_MENU_COLOR = "#262123"           # Цвет шапки
GRAPH_LABEL_COLOR = "#E8DED3"           # Цвет подписей графа
NODE_NAME_COLOR = "#4C4646"             # Цвет узлов-художников
NODE_CITY_COLOR = "#D3DAE8"             # Цвет узлов-городов
NODE_FIELD_COLOR = "#EEC0E7"            # Цвет узлов-проф. полей
NODE_ROLE_COLOR = "#F4C07C"             # Цвет узлов-ролей
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
    .node-card * {{
        color: {PAGE_TEXT_COLOR} !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: {SIDEBAR_BG_COLOR};
        color: {SIDEBAR_LABEL_COLOR};
    }}
    .stMultiSelect, .stSelectbox, .stTextInput {{
        background-color: {SIDEBAR_BG_COLOR} !important;
        color: {SIDEBAR_LABEL_COLOR} !important;
    }}
    .stButton>button {{
        background-color: {BUTTON_BG_COLOR};
        color: {BUTTON_TEXT_COLOR};
    }}
    </style>
""", unsafe_allow_html=True)

# === Загрузка данных ===
df = pd.read_csv("Etudes Lab 1 artistis.csv").fillna("")
df["professional field"] = df["professional field"].astype(str)
df["role"] = df["role"].astype(str)
df["country"] = df["country and city"].apply(lambda x: x.split(",")[0].strip() if "," in x else x.strip())
df["city"] = df["country and city"].apply(lambda x: x.split(",")[1].strip() if "," in x else "")

# === Фильтры ===
st.sidebar.header("Filters")
field_filter = st.sidebar.multiselect("Professional Field", sorted(df["professional field"].unique()))
role_filter = st.sidebar.multiselect("Role", sorted(df["role"].unique()))
country_filter = st.sidebar.multiselect("Country", sorted(df["country"].unique()))
city_filter = st.sidebar.multiselect("City", sorted(df["city"].unique()))

filtered_df = df.copy()
if field_filter:
    filtered_df = filtered_df[filtered_df["professional field"].isin(field_filter)]
if role_filter:
    filtered_df = filtered_df[filtered_df["role"].isin(role_filter)]
if country_filter:
    filtered_df = filtered_df[filtered_df["country"].isin(country_filter)]
if city_filter:
    filtered_df = filtered_df[filtered_df["city"].isin(city_filter)]

def get_google_drive_image_url(url):
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?id={file_id}"
    return url

def is_valid_image(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=3)
        return r.status_code == 200 and 'image' in r.headers.get('Content-Type', '')
    except:
        return False

# === Построение узлов и рёбер ===
nodes = []
edges = []
added = set()

for _, row in filtered_df.iterrows():
    name = row["name"].strip()
    city = row["city"].strip()
    country = row["country"].strip()
    fields = [f.strip() for f in row["professional field"].split(",") if f.strip()]
    roles = [r.strip() for r in row["role"].split(",") if r.strip()]
    telegram = row["telegram nickname"].strip()
    email = row["email"].strip()
    photo_drive = row.get("photo google drive", "").strip()
    photo_direct = row.get("photo url", "").strip()

    photo = get_google_drive_image_url(photo_drive) if photo_drive else photo_direct
    if not is_valid_image(photo):
        photo = DEFAULT_PHOTO

    label = name
    tooltip = f"{name}\nTelegram: {telegram}\nEmail: {email}"
    nodes.append(Node(id=name, label=label, size=25, color=NODE_NAME_COLOR, title=tooltip))

    if city:
        if city not in added:
            nodes.append(Node(id=city, label=city, size=15, color=NODE_CITY_COLOR))
            added.add(city)
        edges.append(Edge(source=name, target=city))

    if country:
        if country not in added:
            nodes.append(Node(id=country, label=country, size=15, color=NODE_CITY_COLOR))
            added.add(country)
        edges.append(Edge(source=name, target=country))
        if city:
            edges.append(Edge(source=country, target=city))

    for field in fields:
        if field not in added:
            nodes.append(Node(id=field, label=field, size=15, color=NODE_FIELD_COLOR))
            added.add(field)
        edges.append(Edge(source=name, target=field))

    for role in roles:
        if role not in added:
            nodes.append(Node(id=role, label=role, size=15, color=NODE_ROLE_COLOR))
            added.add(role)
        edges.append(Edge(source=name, target=role))

# === Конфигурация графа ===
config = Config(
    width=1100,
    height=700,
    directed=False,
    physics=True,
    hierarchical=False,
    nodeHighlightBehavior=True,
    highlightColor="#6A50FF",
    collapsible=True
)

# === Отображение графа ===
st.subheader("HOSQ Artist Graph")
return_value = agraph(nodes=nodes, edges=edges, config=config)
st.write("Selected node:", return_value)

# === Инфо о выбранном художнике в popup сбоку ===
clicked_label = return_value.strip() if isinstance(return_value, str) else None
if clicked_label:
    selected_artist = df[df["name"].str.strip() == clicked_label]
    if not selected_artist.empty:
        artist = selected_artist.iloc[0]
        photo_drive = artist.get("photo google drive", "").strip()
        photo_direct = artist.get("photo url", "").strip()
        photo = get_google_drive_image_url(photo_drive) if photo_drive else photo_direct
        if not is_valid_image(photo):
            photo = DEFAULT_PHOTO

        with st.expander("🎨 Artist Info", expanded=True):
            st.image(photo, width=200)
            st.markdown(f"**Name:** {artist['name']}")
            if artist['telegram nickname']:
                st.markdown(f"**Telegram:** {artist['telegram nickname']}")
            if artist['email']:
                st.markdown(f"**Email:** {artist['email']}")
    else:
        st.info("Selected node does not match any artist")
else:
    st.info("Click a node to view artist info")
