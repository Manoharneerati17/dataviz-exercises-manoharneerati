import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Food Delivery Performance Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Decluttered / Publication-Ready Styling
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    h1, h2, h3 { color: #1E293B; font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# Data Loader
@st.cache_data
def load_data():
    # Primary & Fallback paths
    abs_path = Path(r"C:\Users\Manohar\Desktop\data-viz\dataviz-exercises\final_project\data\Food_Delivery_Times.csv")
    rel_path_1 = Path("data/Food_Delivery_Times.csv")
    rel_path_2 = Path("Food_Delivery_Times.csv")

    if abs_path.exists():
        file_path = abs_path
    elif rel_path_1.exists():
        file_path = rel_path_1
    elif rel_path_2.exists():
        file_path = rel_path_2
    else:
       import os
import pandas as pd

@st.cache_data # or @st.cache depending on your Streamlit version
def load_data():
    # Gets the exact directory path where app.py resides
    file_path = os.path.join(current_dir, "data", "Food_Delivery_Times.csv")
    
    # If Food_Delivery_Times.csv is in the SAME folder as app.py:
    file_path = os.path.join(current_dir, "Food_Delivery_Times.csv")
    
    # OR if it is in a subfolder named 'data' inside final_project:
    # file_path = os.path.join(current_dir, "data", "Food_Delivery_Times.csv")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find file at: {file_path}")
        
    return pd.read_csv(file_path)

    df = pd.read_csv(file_path)

    # Clean Missing Values
    df['Weather'] = df['Weather'].fillna(df['Weather'].mode()[0])
    df['Traffic_Level'] = df['Traffic_Level'].fillna(df['Traffic_Level'].mode()[0])
    df['Time_of_Day'] = df['Time_of_Day'].fillna(df['Time_of_Day'].mode()[0])
    df['Courier_Experience_yrs'] = df['Courier_Experience_yrs'].fillna(df['Courier_Experience_yrs'].median())
    
    # Feature Engineering
    df['Speed_kmh'] = df['Distance_km'] / ((df['Delivery_Time_min'] - df['Preparation_Time_min']) / 60)
    df['Distance_Category'] = pd.cut(df['Distance_km'], bins=[0, 5, 12, 25], labels=['Short (<5km)', 'Medium (5-12km)', 'Long (>12km)'])
    df['Exp_Group'] = pd.cut(df['Courier_Experience_yrs'], bins=[-1, 2, 5, 10], labels=['Novice (0-2y)', 'Mid (3-5y)', 'Senior (5y+)'])
    return df

df = load_data()

# Palette Definition (CVD Safe)
COLOR_MAP = {'Car': '#0072B2', 'Scooter': '#009E73', 'Bike': '#D55E00'}
LIGHT_GREY = "#E5E5E5"

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Data Filters")
st.sidebar.markdown("Filter options to explore delivery patterns.")

selected_vehicles = st.sidebar.multiselect(
    "Vehicle Type", options=df['Vehicle_Type'].unique(), default=df['Vehicle_Type'].unique()
)

selected_weather = st.sidebar.multiselect(
    "Weather Condition", options=df['Weather'].unique(), default=df['Weather'].unique()
)

selected_traffic = st.sidebar.multiselect(
    "Traffic Level", options=df['Traffic_Level'].unique(), default=df['Traffic_Level'].unique()
)

distance_range = st.sidebar.slider(
    "Distance Range (km)", 
    min_value=float(df['Distance_km'].min()), 
    max_value=float(df['Distance_km'].max()), 
    value=(float(df['Distance_km'].min()), float(df['Distance_km'].max()))
)

# Apply Filters
filtered_df = df[
    (df['Vehicle_Type'].isin(selected_vehicles)) &
    (df['Weather'].isin(selected_weather)) &
    (df['Traffic_Level'].isin(selected_traffic)) &
    (df['Distance_km'].between(distance_range[0], distance_range[1]))
]

# --- MAIN DASHBOARD HEADER ---
st.title("🚚 Food Delivery Performance & Friction Analysis")
st.markdown("An interactive operational dashboard exploring drivers of delivery duration, vehicle efficiency, and weather/traffic bottlenecks.")

# Key Summary Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Orders Evaluated", f"{len(filtered_df):,}")
m2.metric("Avg Delivery Time", f"{filtered_df['Delivery_Time_min'].mean():.1f} min")
m3.metric("Avg Distance", f"{filtered_df['Distance_km'].mean():.1f} km")
m4.metric("Avg Prep Time", f"{filtered_df['Preparation_Time_min'].mean():.1f} min")

st.markdown("---")

# --- MULTI-TAB STRUCTURE ---
tab1, tab2, tab3 = st.tabs(["🚀 Vehicle & Route Efficiency", "🌧️ Weather & Traffic Impact", "👨‍✈️ Courier & Kitchen Dynamics"])

# TAB 1: VEHICLE & ROUTE EFFICIENCY
with tab1:
    st.subheader("Vehicle Speed and Distance Scaling")
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.scatter(
            filtered_df, x='Distance_km', y='Delivery_Time_min', color='Vehicle_Type',
            trendline='ols', opacity=0.6, color_discrete_map=COLOR_MAP,
            title="<b>Distance vs. Delivery Time</b>",
            labels={'Distance_km': 'Distance (km)', 'Delivery_Time_min': 'Delivery Time (min)'}
        )
        fig1.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=LIGHT_GREY), template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        df_speed = filtered_df.groupby(['Distance_Category', 'Vehicle_Type'])['Speed_kmh'].mean().reset_index()
        fig2 = px.line(
            df_speed, x='Distance_Category', y='Speed_kmh', color='Vehicle_Type', markers=True,
            color_discrete_map=COLOR_MAP,
            title="<b>Effective Speed by Distance Category</b>",
            labels={'Speed_kmh': 'Avg Speed (km/h)', 'Distance_Category': 'Distance Category'}
        )
        fig2.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=LIGHT_GREY), template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

# TAB 2: WEATHER & TRAFFIC IMPACT
with tab2:
    st.subheader("Environmental Friction Factors")
    col3, col4 = st.columns(2)
    
    with col3:
        df_wt = filtered_df.groupby(['Weather', 'Traffic_Level'])['Delivery_Time_min'].mean().reset_index()
        fig3 = px.bar(
            df_wt, x='Weather', y='Delivery_Time_min', color='Traffic_Level', barmode='group',
            color_discrete_sequence=['#56B4E9', '#0072B2', '#D55E00'],
            title="<b>Delivery Duration by Weather & Traffic</b>",
            labels={'Delivery_Time_min': 'Avg Delivery Time (min)'}
        )
        fig3.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=LIGHT_GREY), template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)
        
    with col4:
        heatmap_data = filtered_df.pivot_table(index='Time_of_Day', columns='Traffic_Level', values='Delivery_Time_min', aggfunc='mean')
        fig4 = px.imshow(
            heatmap_data, text_auto=".1f", color_continuous_scale="Blues",
            title="<b>Time of Day x Traffic Matrix</b> (Avg Min)",
            labels=dict(x="Traffic Level", y="Time of Day", color="Avg Time")
        )
        st.plotly_chart(fig4, use_container_width=True)

# TAB 3: COURIER & KITCHEN DYNAMICS
with tab3:
    st.subheader("Courier Experience & Kitchen Prep Time Analysis")
    col5, col6 = st.columns(2)
    
    with col5:
        fig5 = px.box(
            filtered_df, x='Courier_Experience_yrs', y='Delivery_Time_min', color='Vehicle_Type',
            color_discrete_map=COLOR_MAP,
            title="<b>Courier Experience Impact on Delivery Duration</b>",
            labels={'Courier_Experience_yrs': 'Experience (Years)', 'Delivery_Time_min': 'Delivery Time (min)'}
        )
        fig5.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=LIGHT_GREY), template="plotly_white")
        st.plotly_chart(fig5, use_container_width=True)
        
    with col6:
        fig6 = px.scatter(
            filtered_df, x='Preparation_Time_min', y='Delivery_Time_min', size='Distance_km', color='Traffic_Level',
            color_discrete_map={'Low': '#009E73', 'E69F00': '#E69F00', 'High': '#D55E00'},
            title="<b>Preparation Time vs. Total Delivery Time</b>",
            labels={'Preparation_Time_min': 'Prep Time (min)', 'Delivery_Time_min': 'Total Delivery Time (min)'}
        )
        fig6.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=LIGHT_GREY), template="plotly_white")
        st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption("Food Delivery Performance Analysis Dashboard • Developed with Streamlit & Plotly")
