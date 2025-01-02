import streamlit as st
import requests
import time
from bs4 import BeautifulSoup
import google.generativeai as genai
import json

# Load configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

# Streamlit UI

# Create two columns with equal height and width
col1, col2 = st.columns([4, 1])  # Create two columns with a 3:1 ratio

with col1:
    st.title("Find the Jobs")

with col2:
    # Use st.image with the desired width for the image
    st.image("https://i.pinimg.com/originals/66/2c/da/662cda1ea6bdac6afb16973961c2c8d1.gif", width=100)

# Number of jobs to fetch (between 1 and 20)
num_jobs = st.sidebar.slider("Number of Jobs to Display", min_value=1, max_value=20, step=1, key="num_jobs")

# Place the "Start Scraping" button right below the slider
start_scraping = st.sidebar.button("Start Scraping")

# Add some spacing
st.divider()  # Optional: Adds a horizontal line for visual separation

# Load secrets from config
api_key = config["general"]["api_key"]
gemini_model = config["general"]["gemini_model"]
data_urls = config["data_urls"]["urls"]

if not api_key:
    st.error("API key is missing in config.json.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(gemini_model)

# Function to fetch jobs from a URL and process them
def fetch_jobs(url, num_jobs):
    max_retries = 3  # Maximum retries for 429 errors
    retry_delay = 2  # Initial delay in seconds

    try:
        for attempt in range(max_retries):
            response = requests.get(url)

            if response.status_code == 429:
                if attempt < max_retries - 1:
                    st.warning("API quota exhausted. Retrying...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    st.error("API quota exhausted. Please try again later.")
                    return

            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            posts = response.json()

            if not isinstance(posts, list):
                st.warning(f"Unexpected data format from {url}")
                return

            posts_to_display = posts[:num_jobs]

            for post in posts_to_display:
                try:
                    content = post.get('content', {}).get('rendered', '')
                    soup = BeautifulSoup(content, 'html.parser')
                    html_content = str(soup)

                    # Generate content using generative AI
                    data = model.generate_content(f'''
                        Given the following HTML content from two sources:
                        html_content = {html_content}
                        Extract and return the following details in a well-structured JSON format, ensuring no unknown ASCII values are present. Use html_content2 as a secondary source for any missing information in html_content. The JSON structure should be:
                            {{
                            "job_details": {{
                            "company_name": "string",  # Name of the company offering the job.
                            "role": "string",  # Job title or role being offered.
                            "apply_link": "string",  # URL link to apply for the job.
                            "salary_min": "string",  # Annual minimum salary (convert if monthly). Prioritize html_content; fall back to html_content2 if necessary.
                            "salary_max": "string",  # Annual maximum salary (convert if monthly). Prioritize html_content; fall back to html_content2 if necessary.
                            "education": "string",  # Education qualifications required for the job.
                            "location": "string",  # Job location.
                            "experience_min": "integer",  # Minimum years of experience required.
                            "experience_max": "integer",  # Maximum years of experience required.
                            "batch": "string" or ["list"],  # Eligible batches (if recent batch is mentioned, calculate using experience as of 2025).
                            "job_type": ["string"],  # List indicating job type, e.g., ["Fresher", "Experienced"]. Determine based on experience_min and experience_max:
                                                     # - If both are 0, classify as Fresher.
                                                     # - If experience_min > 0, classify as Experienced.
                                                     # - If experience_min = 0 and experience_max > 0, include both Fresher and Experienced.
                            "employment_type": "string",  # Nature of employment, e.g., Remote, Full-Time,
                            "skills": "string",  # Required skills for the job.
                            }}
                        }}
                        
                            Ensure that:
                            - All extracted values are accurate and consistent.
                            - Salary values are always converted to annual figures if given monthly.
                            - Job description content is rewritten to be concise, professional, and suitable for publication on a job portal aggregator.
                    ''')

                    candidates = data._result.candidates
                    text = candidates[0].content.parts[0].text
                    job_data = json.loads(text[8:-5])

                    # Safely handle batch field to convert all elements to strings
                    batch = job_data['job_details'].get('batch', [])
                    if isinstance(batch, list):
                        batch = ', '.join(map(str, batch))
                    else:
                        batch = str(batch)

                    # Create a card-like display for each job post
                    message = f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                        <h3 style="margin-top: 0; color: #007bff;">{job_data['job_details']['company_name']} is Hiring Interns! 🚀</h3>
                        <p><strong>Salary:</strong> ₹ {job_data['job_details']['salary_min']} - ₹ {job_data['job_details']['salary_max']} per year</p>
                        <p><strong>Role:</strong> {job_data['job_details']['role']}</p>
                        <p><strong>Location:</strong> {job_data['job_details']['location']}</p>
                        <p><strong>Eligibility:</strong> {job_data['job_details']['education']}</p>
                        <p><strong>Batch:</strong> {batch}</p>
                        <p><strong>Skills:</strong> {job_data['job_details']['skills']}</p>
                        <p><a href="{job_data['job_details']['apply_link']}" target="_blank" style="color: #007bff;">View Full Job Details & Apply</a></p>
                    </div>
                    """
                    st.markdown(message, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Failed to process a job post: {e}")
            break
    except requests.RequestException as e:
        st.error(f"Failed to fetch data from {url}: {e}")

# Split the jobs between the two URLs
num_jobs_url1 = num_jobs // 2
num_jobs_url2 = num_jobs - num_jobs_url1

# Check if the button is clicked
if start_scraping:
    if not data_urls:
        st.error("No data URLs found in config.json.")
    else:
        try:
            # Fetch jobs from both URLs
            if len(data_urls) > 0:
                fetch_jobs(data_urls[0], num_jobs_url1)
            if len(data_urls) > 1:
                fetch_jobs(data_urls[1], num_jobs_url2)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
