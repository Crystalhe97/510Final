# LinkedIn UX Job Finder
Team members: Yuwei He, Jiaqi Wang

## Impress Me Sentence
LinkedIn UX Job Finder transforms the complex job search landscape for UX professionals into a user-friendly platform, offering real-time insights, personalized resume advice, and interactive maps to navigate the competitive market with precision.

## Technologies Used
- **Backend**: Python 3, MySQL
- **Libraries/Frameworks**: Streamlit (for web app), SQLAlchemy (for ORM), mysql-connector-python (for MySQL interaction), openai (for AI-driven features), requests, python-dotenv (for environment variables management), nltk, pypdf, pdfminer.six (for PDF handling)
- **APIs**: LinkedIn (data source), OpenAI (optional, for data enhancement)

## Problem to Solve
The inspiration for this web project came from the website Top UX School. This website helped us understand school rankings and compare program information when applying for schools. Now, as we look for internships and jobs, we wanted to create a website that could help students in UX-related fields. We scraped information related to UX positions from LinkedIn and displayed all jobs in a list format. Users can filter and sort the list based on position, location, company, and posting time, among other criteria. We also created bar charts and heat maps to allow users to understand more clearly and intuitively where there are more job opportunities. The information from LinkedIn is updated to our database daily at 12 PM. Additionally, we provide a resume advice feature. Users can select a job ID from the list, view the job description, and then upload their resume to receive corresponding advice.

## How to Run
Open the terminal and run the following commands:

```
pip install -r requirements.txt
streamlit run app.py
```

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- An OpenAI API key (if using features related to AI)

## Reflections

### What You Learned
- The intricacies of connecting to and interacting with MySQL databases using Python.
- Handling geospatial data and integrating it into web applications.
- Developing and deploying a Streamlit application to visualize data on a map.

### Challenges Faced
- Extracting accurate geospatial data from LinkedIn profiles required precise and reliable scraping techniques.
- The biggest problem we encountered is connecting to MYSQL. Since we used PostgreSQL in previous classes, we tried using MYSQL this time. There are many settings that are different from PostgreSQL. The issue with the database connection took us three days to resolve. We encountered various problems, such as issues with SSL, username and password, and so on.
- We also encountered issues with data visualization. We wanted to show on the website's map where there are more job opportunities. After searching and trying many libraries, we ultimately chose folium.plugins' HeatMap.



