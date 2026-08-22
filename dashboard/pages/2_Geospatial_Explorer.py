"""
Page 2: Geospatial GIS & Infrastructure Hotspot Explorer.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import HeatMap
import streamlit.components.v1 as components
from dashboard.utils import load_data, apply_custom_css, get_filtered_data, render_ai_copilot_sidebar
from src.models.cluster_analyzer import GeospatialClusterAnalyzer

st.set_page_config(page_title="Geospatial Explorer - Civic Analytics", page_icon="🗺️", layout="wide")
apply_custom_css()

st.title("🗺️ Geospatial GIS & Infrastructure Hotspot Explorer")
st.markdown("Discover geographic patterns, spatial density heatmaps, and ML-detected chronic failure zones.")

raw_df = load_data()
df = get_filtered_data(raw_df)

# Render AI Copilot in Sidebar
render_ai_copilot_sidebar("Geospatial Explorer")

# Clustering Settings in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📍 DBSCAN Hotspot Parameters")
eps_km = st.sidebar.slider("Neighborhood Radius (km)", 0.5, 5.0, 1.5, 0.5)
min_samples = st.sidebar.slider("Min Cluster Tickets", 3, 20, 8, 1)

# Run Clustering
cluster_analyzer = GeospatialClusterAnalyzer(df)
clustered_df = cluster_analyzer.find_hotspots(eps_km=eps_km, min_samples=min_samples)
cluster_summaries = cluster_analyzer.summarize_clusters(clustered_df)

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Mapped Incidents", f"{len(df):,}")
with m2:
    st.metric("Detected Hotspot Zones", f"{len(cluster_summaries)}")
with m3:
    hotspot_tickets = len(clustered_df[clustered_df["Hotspot_Cluster_ID"] != -1])
    st.metric("Tickets in Hotspots", f"{hotspot_tickets:,}", f"{(hotspot_tickets/len(df)*100 if len(df)>0 else 0):.1f}% of total")
with m4:
    st.metric("Top Incident Area", df["Area"].value_counts().index[0] if not df.empty else "N/A")

st.markdown("---")

# Map View Selection
tab_scatter, tab_heatmap, tab_clusters = st.tabs(["🌐 Scatter Incident Map", "🔥 Density HeatMap", "🎯 Hotspot Cluster Analytics"])

with tab_scatter:
    st.subheader("Interactive Civic Incident Map")
    valid_coords = df.dropna(subset=["Latitude", "Longitude"])
    
    if not valid_coords.empty:
        fig_map = px.scatter_mapbox(
            valid_coords,
            lat="Latitude",
            lon="Longitude",
            color="Priority",
            size="Complaint_Severity_Score",
            hover_name="Complaint_ID",
            hover_data=["Issue_Type", "Department", "Area", "Status", "SLA_Status"],
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
            zoom=10,
            mapbox_style="carto-positron",
            height=550,
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No geographic coordinate data available for selected filter.")

with tab_heatmap:
    st.subheader("Spatial Concentration HeatMap")
    valid_coords = df.dropna(subset=["Latitude", "Longitude"])
    
    if not valid_coords.empty:
        center_lat = valid_coords["Latitude"].mean()
        center_lon = valid_coords["Longitude"].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="CartoDB positron")
        heat_data = [[row["Latitude"], row["Longitude"], row["Complaint_Severity_Score"]] for _, row in valid_coords.iterrows()]
        HeatMap(heat_data, radius=15, blur=18, min_opacity=0.4).add_to(m)
        
        components.html(m._repr_html_(), height=550)
    else:
        st.warning("No coordinates to render heatmap.")

with tab_clusters:
    st.subheader("Persistent Infrastructure Hotspot Breakdown")
    if cluster_summaries:
        summary_df = pd.DataFrame(cluster_summaries)
        summary_df.columns = [
            "Cluster ID",
            "Total Complaints",
            "Center Lat",
            "Center Lon",
            "Primary Areas",
            "Primary Issues",
            "Avg Rating",
            "SLA Breach Rate %",
        ]
        st.dataframe(
            summary_df[["Cluster ID", "Total Complaints", "Primary Areas", "Avg Rating", "SLA Breach Rate %"]],
            use_container_width=True,
        )
        
        st.info("💡 **Civic Recommendation:** Prioritize proactive infrastructure overhaul and preventative maintenance contracts in these persistent hotspot corridors.")
    else:
        st.info("No dense clusters found with current parameter settings. Try reducing the neighborhood radius or minimum samples.")
