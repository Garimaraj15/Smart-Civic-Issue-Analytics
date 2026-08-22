"""
Page 5: Citizen Sentiment, Satisfaction Drivers & Feedback Analytics.
"""

import sys
from pathlib import Path

FILE_DIR = Path(__file__).resolve().parent
ROOT_DIR = FILE_DIR.parent.parent
for path in [ROOT_DIR, FILE_DIR.parent, FILE_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dashboard.utils import load_data, apply_custom_css, get_filtered_data, render_ai_copilot_sidebar

st.set_page_config(page_title="Citizen Sentiment - Civic Analytics", page_icon="⭐", layout="wide")
apply_custom_css()

st.title("⭐ Citizen Satisfaction & Feedback Sentiment Intelligence")
st.markdown("Quantify citizen trust, explore rating drivers, and analyze turnaround impact on public sentiment.")

raw_df = load_data()
df = get_filtered_data(raw_df)

# Render AI Copilot in Sidebar
render_ai_copilot_sidebar("Citizen Sentiment")

rated_df = df[df["Citizen_Rating"].notna()].copy()

# Summary Metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Citizen Ratings", f"{len(rated_df):,}", f"{(len(rated_df)/len(df)*100 if len(df)>0 else 0):.1f}% Response Rate")
with c2:
    st.metric("Average Citizen Rating", f"⭐ {rated_df['Citizen_Rating'].mean():.2f} / 5.0")
with c3:
    satisfied_pct = (rated_df["Citizen_Rating"] >= 4.0).sum() / len(rated_df) * 100 if len(rated_df) > 0 else 0
    st.metric("Satisfied Citizens (4-5 ★)", f"{satisfied_pct:.1f}%")
with c4:
    dissatisfied_pct = (rated_df["Citizen_Rating"] <= 2.0).sum() / len(rated_df) * 100 if len(rated_df) > 0 else 0
    st.metric("Critical Dissatisfaction (1-2 ★)", f"{dissatisfied_pct:.1f}%")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Rating Distribution (1 to 5 Stars)")
    rating_counts = rated_df["Citizen_Rating"].value_counts().sort_index().reset_index()
    rating_counts.columns = ["Rating", "Count"]
    rating_counts["Rating_Label"] = rating_counts["Rating"].astype(int).astype(str) + " Stars"

    fig_ratings = px.bar(
        rating_counts,
        x="Rating_Label",
        y="Count",
        color="Rating",
        color_continuous_scale="RdYlGn",
        text="Count",
    )
    fig_ratings.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig_ratings, use_container_width=True)

with col2:
    st.subheader("📉 Turnaround Time vs Citizen Rating")
    fig_scatter = px.scatter(
        rated_df,
        x="Resolution_Time_Days",
        y="Citizen_Rating",
        color="Priority",
        labels={"Resolution_Time_Days": "Resolution Turnaround (Days)", "Citizen_Rating": "Rating (1-5)"},
        color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
    )
    trendline_df = rated_df[["Resolution_Time_Days", "Citizen_Rating"]].dropna()
    if len(trendline_df) >= 2 and trendline_df["Resolution_Time_Days"].nunique() > 1:
        coefficients = np.polyfit(
            trendline_df["Resolution_Time_Days"], trendline_df["Citizen_Rating"], 1
        )
        x_line = np.linspace(
            trendline_df["Resolution_Time_Days"].min(),
            trendline_df["Resolution_Time_Days"].max(),
            100,
        )
        fig_scatter.add_trace(
            go.Scatter(
                x=x_line,
                y=np.polyval(coefficients, x_line),
                mode="lines",
                name="Trendline",
                line={"color": "#334155", "dash": "dash"},
            )
        )
    fig_scatter.update_layout(height=380)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# Department Rating Comparison
st.subheader("🏢 Department Satisfaction Benchmarks")
dept_ratings = rated_df.groupby("Department")["Citizen_Rating"].agg(["mean", "count", "median"]).reset_index()
dept_ratings.columns = ["Department", "Average Rating", "Rated Tickets", "Median Rating"]
dept_ratings["Average Rating"] = dept_ratings["Average Rating"].round(2)

fig_dept_ratings = px.bar(
    dept_ratings.sort_values("Average Rating", ascending=False),
    x="Department",
    y="Average Rating",
    color="Average Rating",
    color_continuous_scale="Blues",
    text="Average Rating",
)
fig_dept_ratings.update_layout(height=350, yaxis=dict(range=[1, 5]))
st.plotly_chart(fig_dept_ratings, use_container_width=True)
