import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO

# ---------- Page Setup ----------
st.set_page_config(layout="wide", page_title="Thematic India Map", page_icon="🗺️")

# ---------- Global Styles ----------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding: 2rem 3rem;
        }

        .stSidebar {
            background-color: #1F2937 !important;  /* Dark gray background */
        }

        .stSidebar label,
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4,
        .stSidebar div, .stSidebar p {
            color: #F3F4F6 !important;  /* Light text for contrast */
        }

        .stNumberInput input,
        .stTextInput > div > input,
        .stSelectbox > div {
            background-color: #111827 !important;  /* Darker input fields */
            color: #F9FAFB !important;  /* Light text inside inputs */
            border-radius: 8px;
            border: 1px solid #374151;
        }

        .stButton > button {
            background-color: #4F46E5;
            color: white;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            border: none;
        }

        .stDownloadButton > button {
            background-color: #22C55E;
            color: white;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            border: none;
        }

        h1 {
            font-size: 2.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Top Header ----------
st.markdown("""
<div style="width: 100%; background-color: #111827; padding: 1rem 2rem; border-radius: 0.5rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
    <div style="font-size: 1.5rem; font-weight: 600; color: #F9FAFB;">🗺️ Thematic India Map</div>
    <div style="font-size: 0.9rem; font-weight: 400; color: #9CA3AF;">made by Ruhaan</div>
</div>
""", unsafe_allow_html=True)




# ---------- Load GeoJSON ----------
@st.cache_data
def load_geojson():
    return gpd.read_file("india_states.geojson")

gdf = load_geojson()
STATE_KEY = "st_nm"
state_names = gdf[STATE_KEY].tolist()

# ---------- Sidebar Data Inputs ----------
st.sidebar.header("📊 State Data Input")
state_values = {}
for state in state_names:
    state_values[state] = st.sidebar.number_input(state, min_value=0, value=0)

st.sidebar.markdown("---")
map_title = st.sidebar.text_input("📝 Map Title", "India Thematic Map")
map_unit = st.sidebar.text_input("📏 Data Unit", "e.g., Literacy Rate (%)")
color_scheme = st.sidebar.selectbox("🌈 Color Scheme", ["Blues", "Greens", "Oranges", "Purples", "Reds"])

# ---------- Plot Map ----------
st.markdown("### 🧭 Map Preview")
df = pd.DataFrame(list(state_values.items()), columns=[STATE_KEY, "value"])
merged = gdf.merge(df, on=STATE_KEY)

fig, ax = plt.subplots(1, 1, figsize=(10, 11))
merged.plot(
    column="value",
    cmap=color_scheme,
    linewidth=0.8,
    ax=ax,
    edgecolor="0.8",
    legend=True,
)

ax.set_title(map_title, fontsize=18, fontweight="bold", pad=20)
ax.text(
    0.5, -0.1,
    f"Unit: {map_unit}\nColor scale: Light ➝ Dark = Low ➝ High",
    transform=ax.transAxes,
    ha='center',
    fontsize=10,
    bbox=dict(facecolor='white', alpha=0.7, boxstyle="round,pad=0.3")
)
ax.axis("off")
st.pyplot(fig)

# ---------- Export Map ----------
buffer = BytesIO()
fig.savefig(buffer, format="png", bbox_inches="tight")
buffer.seek(0)
st.download_button(
    label="⬇️ Download Map as PNG",
    data=buffer,
    file_name=f"{map_title.replace(' ', '_')}.png",
    mime="image/png"
)

# ---------- Save Map ----------
if "saved_maps" not in st.session_state:
    st.session_state.saved_maps = []

if st.button("💾 Save this map"):
    st.session_state.saved_maps.append({
        "title": map_title,
        "unit": map_unit,
        "colors": color_scheme,
        "values": state_values.copy()
    })
    st.success("✅ Map saved to session memory!")

# ---------- Show Saved Maps ----------
st.markdown("### 📁 Saved Maps This Session")
if st.session_state.saved_maps:
    for i, m in enumerate(st.session_state.saved_maps):
        with st.expander(f"{i+1}. {m['title']} ({m['unit']})"):
            st.json(m["values"])
else:
    st.info("You haven’t saved any maps yet.")
