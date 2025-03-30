import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

# === Настройки страницы ===
st.set_page_config(page_title="HOSQ Artists Mapping (Agraph)", layout="wide")

# === Цвета ===
PAGE_BG_COLOR = "#262123"
PAGE_TEXT_COLOR = "#E8DED3"
NODE_NAME_COLOR = "#4C4646"
NODE_CITY_COLOR = "#D3DAE8"
NODE_FIELD_COLOR = "#EEC0E7"
NODE_ROLE_COLOR = "#F4C07C"
DEFAULT_PHOTO = "https://static.tildacdn.com/tild3532-6664-4163-b538-663866613835/hosq-design-NEW.png"

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
    </style>
""", unsafe_allow_html=True)

# === Загрузка данных ===
df = pd.read_csv("Etudes Lab 1 artistis.csv").fillna("")
df["professional field"] = df["professional field"].astype(str)
df["role"] = df["role"].astype(str)
df["country"] = df["country and city"].apply(lambda x: x.split(",")[0].strip() if "," in x else x.strip())
df["city"] = df["country and city"].apply(lambda x: x.split(",")[1].strip() if "," in x else "")

# === Построение узлов и рёбер ===
nodes = []
edges = []
added = set()

for _, row in df.iterrows():
    name = row["name"].strip()
    city = row["city"].strip()
    country = row["country"].strip()
    location = f"{country}, {city}" if city else country
    fields = [f.strip() for f in row["professional field"].split(",") if f.strip()]
    roles = [r.strip() for r in row["role"].split(",") if r.strip()]
    telegram = row["telegram nickname"].strip()
    email = row["email"].strip()
    photo = row["photo url"].strip() or DEFAULT_PHOTO

    label = name
    tooltip = f"{name}\nTelegram: {telegram}\nEmail: {email}"
    nodes.append(Node(id=name, label=label, size=400, color=NODE_NAME_COLOR, title=tooltip))

    if location and location not in added:
        nodes.append(Node(id=location, label=location, size=200, color=NODE_CITY_COLOR))
        added.add(location)
    edges.append(Edge(source=name, target=location))

    for field in fields:
        if field not in added:
            nodes.append(Node(id=field, label=field, size=200, color=NODE_FIELD_COLOR))
            added.add(field)
        edges.append(Edge(source=name, target=field))

    for role in roles:
        if role not in added:
            nodes.append(Node(id=role, label=role, size=200, color=NODE_ROLE_COLOR))
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

# === Инфо о выбранном художнике ===
if return_value and return_value.get("label") in df["name"].values:
    selected_artist = df[df["name"] == return_value.get("label")].iloc[0]
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"<div class='node-card'><h4>🎨 {selected_artist['name']}</h4>", unsafe_allow_html=True)
        st.image(selected_artist['photo url'] or DEFAULT_PHOTO, width=200)
        if selected_artist['telegram nickname']:
            st.markdown(f"**Telegram:** {selected_artist['telegram nickname']}")
        if selected_artist['email']:
            st.markdown(f"**Email:** {selected_artist['email']}")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.sidebar.info("Click a node to view artist info")
