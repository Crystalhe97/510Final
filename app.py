import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
import altair as alt

# Set the page title
st.title('LinkedIn Job Listings')

# Read the CSV file
df = pd.read_csv('Enhanced_LinkedIn_Job_Listings.csv')

# Ensure that Job_location is a string, and handle NaN values
df['Job_location'] = df['Job_location'].fillna('Unknown').astype(str)

# Rename columns for compatibility with st.map()
df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)

# Preparing the DataFrame for display
df['Job_description_display'] = df['Job_description'].apply(lambda x: (x[:50] + '...' if len(x) > 50 else x) if isinstance(x, str) else x)

# Getting unique values for filtering
seniority_levels = df['Seniority_level'].unique().tolist()
job_locations = sorted(list(set(df['Job_location']) - {'Unknown'}))

# Filters
selected_seniority_levels = st.multiselect("Filter by Seniority Level", options=seniority_levels, default=seniority_levels)
selected_job_location = st.selectbox("Filter by Job Location", ['All'] + job_locations)

# Apply filters sequentially
df_filtered = df[df['Seniority_level'].isin(selected_seniority_levels)]
if selected_job_location != 'All':
    df_filtered = df_filtered[df_filtered['Job_location'] == selected_job_location]

# Filter for map data to include only rows with latitude and longitude
df_map_data = df_filtered.dropna(subset=['lat', 'lon'])

# Display filtered DataFrame
if not df_filtered.empty:
    columns_to_hide = ['Keyword', 'Person_hiring']
    df_display = df_filtered.drop(columns=columns_to_hide, errors='ignore')
    st.dataframe(df_display)

    # Display full Job Description
    job_descriptions = df_filtered['Job_description'].tolist()
    selected_description = st.selectbox("View Full Job Description", job_descriptions)
    st.text_area("Full Job Description", selected_description, height=300)

    # Interactive bar chart
    category = st.selectbox("Select a category", df['Seniority_level'].unique())
    chart_data = df[df['Seniority_level'] == category]
    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("count()", title="Number of Listings"),
        y=alt.Y("Job_location", sort='-x', title="Job Location")
    ).properties(
        title=f"Distribution of Job Listings in {category}"
    ).interactive()
    st.altair_chart(bar_chart, use_container_width=True)

    # Map visualization using Folium
    # Display the map if we have map data
    if not df_map_data.empty:
        m = folium.Map(location=[df_map_data['lat'].mean(), df_map_data['lon'].mean()], zoom_start=4)
        for idx, row in df_map_data.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=row['Job_location']
            ).add_to(m)
        st_folium(m, width=725, height=500)

else:
    st.write("No job listings match your filters.")
