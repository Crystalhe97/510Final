import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as alt

# 调整页面布局为宽屏模式
st.set_page_config(layout="wide")

# 设置页面标题
st.title('LinkedIn Job Listings')

# 读取CSV文件
df = pd.read_csv('Enhanced_LinkedIn_Job_Listings.csv')

# 数据预处理
df['Job_location'] = df['Job_location'].fillna('Unknown').astype(str)  # 处理NaN值
df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)  # 重命名列以适配地图
df['Job_description_display'] = df['Job_description'].apply(lambda x: (x[:50] + '...' if len(x) > 50 else x) if isinstance(x, str) else x)

# 过滤器准备
seniority_levels = df['Seniority_level'].unique().tolist()
# 排除'Unknown'和'United States'
job_locations = sorted(list(set(df['Job_location']) - {'Unknown', 'United States'}))

# 过滤器用户界面
selected_seniority_levels = st.multiselect("Filter by Seniority Level", options=seniority_levels, default=seniority_levels)
selected_job_location = st.selectbox("Filter by Job Location", ['All'] + job_locations)

# 应用过滤器
df_filtered = df[df['Seniority_level'].isin(selected_seniority_levels)]
if selected_job_location != 'All':
    df_filtered = df_filtered[df_filtered['Job_location'] == selected_job_location]

# 在显示之前从df_filtered中删除'Job_location'列
df_filtered = df_filtered.drop(columns=['Location'], errors='ignore')

# 显示过滤后的DataFrame
if not df_filtered.empty:
    # 隐藏不需要的列
    columns_to_hide = ['Keyword', 'Person_hiring']
    df_display = df_filtered.drop(columns=columns_to_hide, errors='ignore')
    st.dataframe(df_display)

    # 交互式条形图
    category = st.selectbox("Select a category", seniority_levels)  # 使用已过滤的seniority_levels
    chart_data = df_filtered[(df_filtered['Seniority_level'] == category) & (df_filtered['Job_location'] != 'United States')]
    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("count()", title="Number of Listings"),
        y=alt.Y("Job_location", sort='-x', title="Job Location"),
        color=alt.Color('Job_location', legend=alt.Legend(title="Locations"))
    ).properties(
        title=f"Distribution of Job Listings in {category}"
    ).interactive()
    st.altair_chart(bar_chart, use_container_width=True)

    # 使用Folium的热力图显示地图
    df_map_data = df_filtered.dropna(subset=['lat', 'lon'])  # 确保仅对有地理信息的行进行处理
    if not df_map_data.empty:
        m = folium.Map(location=[df_map_data['lat'].mean(), df_map_data['lon'].mean()], zoom_start=4)
        heat_data = [[row['lat'], row['lon']] for index, row in df_map_data.iterrows()]
        HeatMap(heat_data).add_to(m)
        st_folium(m, width=1800, height=600)
else:
    st.write("No job listings match your filters.")
