import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as alt
from db import get_db_conn

import os
from io import BytesIO
from pdfminer.high_level import extract_text
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PDFReader
from dotenv import load_dotenv
from streamlit import session_state

load_dotenv()

if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()

# Initialize the sidebar navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to', ['LinkedIn Job Listings', 'Resume Suggestion'])

if page == 'LinkedIn Job Listings':
    st.title('LinkedIn Job Listings')

    # Function to execute read query and return result as DataFrame
    def execute_read_query(connection, query):
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        return pd.DataFrame(result, columns=columns)

    # SQL query to select data from the table
    select_jobs_query = """
    SELECT * FROM newtable;
    """

    # Create the database connection
    conn = get_db_conn()

    # Execute the query and convert to DataFrame
    df = execute_read_query(conn, select_jobs_query)
    st.session_state.df = df
    
    # Rename columns for compatibility with st.map()
    df['Job_location'] = df['Job_location'].fillna('Unknown').astype(str)  
    df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)  
    df['Job_description_display'] = df['Job_description'].apply(lambda x: (x[:50] + '...' if len(x) > 50 else x) if isinstance(x, str) else x)

    # Getting unique values for filtering
    seniority_levels = df['Seniority_level'].unique().tolist()
    job_locations = sorted(list(set(df['Job_location']) - {'Unknown', 'United States'}))

    # Filters
    selected_seniority_levels = st.multiselect("Seniority Level", options=seniority_levels, default=seniority_levels)
    selected_job_location = st.selectbox("Job Location", ['All'] + job_locations)

    # Search bar for company search
    company_search_query = st.text_input("Search for a company")

    # Apply filters sequentially
    df_filtered = df[df['Seniority_level'].isin(selected_seniority_levels)]
    if selected_job_location != 'All':
        df_filtered = df_filtered[df_filtered['Job_location'] == selected_job_location]

    # Filter based on search query
    if company_search_query:
        df_filtered = df_filtered[df_filtered['Company'].str.contains(company_search_query, case=False, na=False)]

    # Filter for map data to include only rows with latitude and longitude
    df_filtered = df_filtered.drop(columns=['Location'], errors='ignore')

    # DataFrame
    if not df_filtered.empty:
        columns_to_hide = ['Keyword', 'Person_hiring','Job_link']
        df_display = df_filtered.drop(columns=columns_to_hide, errors='ignore')
        st.dataframe(df_display)

        # Chart
        category = st.selectbox("Select a category", seniority_levels)  
        chart_data = df_filtered[(df_filtered['Seniority_level'] == category) & (df_filtered['Job_location'] != 'United States')]
        bar_chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X("count()", title="Number of Listings"),
            y=alt.Y("Job_location", sort='-x', title="Job Location"),
            color=alt.Color('Job_location', legend=alt.Legend(title="Locations"))
        ).properties(
            title=f"Distribution of Job Listings in {category}"
        ).interactive()
        st.altair_chart(bar_chart, use_container_width=True)

        # Folium Heat Map
        df_map_data = df_filtered.dropna(subset=['lat', 'lon'])  
        if not df_map_data.empty:
            show_markers = st.checkbox("Click Here to Show Companies Details", value=False)
            m = folium.Map(location=[df_map_data['lat'].mean(), df_map_data['lon'].mean()], zoom_start=4)
            heat_data = [[row['lat'], row['lon']] for index, row in df_map_data.iterrows()]
            HeatMap(heat_data).add_to(m)

            if show_markers:
                for index, row in df_map_data.iterrows():
                    popup_content = f"{row['Company']}<br>{row['Job_location']}"
                    folium.Marker(
                        [row['lat'], row['lon']],
                        popup=folium.Popup(popup_content, max_width=300),
                ).add_to(m)
            st_folium(m, width=1800, height=600)
                    
    else:
        st.write("No job listings match your filters.")



elif page == 'Resume Suggestion':
    st.title('Resume Analysis and Suggestions')
    
    if not st.session_state.df.empty:
        job_id = st.number_input("Enter the job ID for which you want suggestions",
                                 min_value=0, 
                                 max_value=len(st.session_state.df)-1, 
                                 key="job_id")
        job_description = st.session_state.df.iloc[job_id]['Job_description'] if 0 <= job_id < len(st.session_state.df) else "No job description available"
        st.text_area("Job Description", job_description, height=150)
    else:
        st.error("Please load the job listings from the 'LinkedIn Job Listings' page first.")
        job_description = "No job description available"
    
    
    def analyze_resume(text):
        feedback = ["Resume Feedback:"]
        essential_sections = ["experience", "education", "skills"]
        has_essential_sections = any(section in text.lower() for section in essential_sections)

        if not has_essential_sections:
            feedback.append("Your resume should include essential sections such as Experience, Education, and Skills.")
        if "managed" in text.lower() or "led" in text.lower():
            feedback.append("Good use of action verbs to describe your roles and achievements.")
        else:
            feedback.append("Consider using action verbs to describe your roles and achievements.")
        if len(text.split()) > 500:
            feedback.append("Your resume may be too long. Consider making it more concise.")
        else:
            feedback.append("The length of your resume is appropriate.")

        return "\n".join(feedback)
    
    # Function to classify and analyze the document
    def classify_and_analyze_document(text):
        if "experience" in text.lower() and "education" in text.lower():
            return analyze_resume(text)
        else:
            return "It's challenging to determine the type of document. Please ensure the document is a resume."
        
    def generate_suggestions_based_on_job_description(existing_feedback, job_description):
        suggestions = existing_feedback
        keywords_to_suggestions = {
            "communication skills": "Emphasize your communication skills, such as public speaking or writing experience.",
            "problem-solving": "Detail instances where you successfully solved problems, especially complex or unexpected ones.",
            "analytical skills": "Mention any experience with data analysis, research projects, or any technical skills relevant to data processing.",
            "creative thinking": "If the job requires innovation, provide examples where you demonstrated creativity.",
            "customer service": "If the job involves customer interaction, highlight any past customer service experiences.",
            "technical skills": "List specific technical skills or tools you are proficient with that match the job requirements.",
            "project management": "Include any project management experience, certifications, or relevant methodologies like Agile or SCRUM.",
            "team": "Include experiences where you worked in or led a team."
        }
            
        job_description_lower = job_description.lower()

        for keyword, suggestion in keywords_to_suggestions.items():
            if keyword in job_description_lower:
                suggestions += "\n" + suggestion
            
        return suggestions

    # Streamlit UI for uploading a document
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type="pdf")
    if uploaded_file:
        bytes_data = uploaded_file.read()
        text = extract_text(BytesIO(bytes_data))
        feedback = classify_and_analyze_document(text)
        suggestions = generate_suggestions_based_on_job_description("", job_description)
        st.text_area("Analysis Feedback", feedback + suggestions, height=300)