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
    .vis-network {{
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
    photo_url = get_google_drive_image_url(row.get("photo url", "").strip())

    if not is_valid_image(photo_url):
        photo_url = DEFAULT_PHOTO

    nodes.append(Node(id=name, label=name, size=10, color=NODE_NAME_COLOR, title=f"{name}\nTelegram: {telegram}\nEmail: {email}"))

    for label, color in [(city, NODE_CITY_COLOR), (country, NODE_CITY_COLOR)]:
        if label and label not in added:
            nodes.append(Node(id=label, label=label, size=5, color=color))
            added.add(label)

    if city:
        edges.append(Edge(source=name, target=city, color=EDGE_COLOR))
    if country:
        edges.append(Edge(source=name, target=country, color=EDGE_COLOR))
        if city:
            edges.append(Edge(source=country, target=city, color=EDGE_COLOR))

    for field in fields:
        if field not in added:
            nodes.append(Node(id=field, label=field, size=5, color=NODE_FIELD_COLOR))
            added.add(field)
        edges.append(Edge(source=name, target=field, color=EDGE_COLOR))

    for role in roles:
        if role not in added:
            nodes.append(Node(id=role, label=role, size=5, color=NODE_ROLE_COLOR))
            added.add(role)
        edges.append(Edge(source=name, target=role, color=EDGE_COLOR))

# === Конфигурация графа ===
config = Config(
    width=1100,
    height=700,
    directed=False,
    physics=True,
    hierarchical=False,
    nodeHighlightBehavior=True,
    highlightColor=HIGHLIGHT_EDGE_COLOR,
    collapsible=True,
    node={'labelProperty': 'label', 'font': {'color': GRAPH_LABEL_COLOR}},
    edge={'color': EDGE_COLOR},
    backgroundColor=GRAPH_BG_COLOR
)

# === Отображение графа ===
st.subheader("HOSQ Artist Graph")
return_value = agraph(nodes=nodes, edges=edges, config=config)

# === Инфо о выбранном художнике в сайдбаре ===
with st.sidebar:
    clicked_label = return_value.strip() if isinstance(return_value, str) else None
    if clicked_label:
        selected_artist = df[df["name"].str.strip() == clicked_label]
        if not selected_artist.empty:
            artist = selected_artist.iloc[0]
            photo_url = get_google_drive_image_url(artist.get("photo url", "").strip())
            if not is_valid_image(photo_url):
                photo_url = DEFAULT_PHOTO
            st.markdown("---")
            st.image(photo_url, width=200)
            st.markdown(f"**Name:** {artist['name']}")
            if artist["telegram nickname"]:
                st.markdown(f"**Telegram:** {artist['telegram nickname']}")
            if artist["email"]:
                st.markdown(f"**Email:** {artist['email']}")
    else:
        st.info("Click a node to view artist info")
