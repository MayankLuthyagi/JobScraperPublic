import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json

# Streamlit UI
st.title("Find the Jobs")

# Number of jobs to fetch (between 1 and 10)
num_jobs = st.slider("Select number of jobs to fetch (1-10):", 1, 10, 5)

# Load the API key from the config file
with open('config.json', 'r') as file:
    config = json.load(file)

api_key = config.get("API_KEY")
url = config.get("URL")

if not api_key:
    raise ValueError("API_KEY not found in config.json.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if st.button("Start Scraping"):
    if not api_key:
        st.error("Please provide the API key.")
    else:
        try:
            # Send a GET request to the website
            response = requests.get(url)

            if response.status_code == 200:
                # Parse the JSON response
                posts = response.json()

                # Limit the number of jobs to fetch based on user input
                posts_to_display = posts[:num_jobs]

                # Collect and process each post
                for post in posts_to_display:
                    content = post['content']['rendered']
                    soup = BeautifulSoup(content, 'html.parser')

                    # Get the raw HTML content of the post
                    html_content = str(soup)

                    # Generate content using generative AI
                    data = model.generate_content(f'''
                        Extract the following details from the provided HTML content: {html_content}
                        Return Data like this:
                          job_details:
                            company_name: "string",
                            role: "string",
                            apply_link: "string",
                            salary_min: "string" (calculate the salary for per annum if monthly given then convert that),
                            salary_max: "string" (calculate the salary for per annum if monthly given then convert that),
                            education: "string",
                            location: "string",
                            batch: "string" or if multiple batch put that in list,
                            experience_min: "integer",
                            experience_max: "integer",
                            job_type: "string" ((eg ["Fresher", "Experienced"]) this is a list calculate from experience_min and experience_max if (Both are 0) then fresher or if (experience_min>0) then Experienced or if (min is 0 and max>0) then put both),
                            employment_type: "string" (eg Remote or Full Time),
                            job_id: "string" (Extract it from apply_link there is always a unique id accosiate with it),
                            skills: "string"
                    ''')
                    candidates = data._result.candidates
                    text = data._result.candidates[0].content.parts[0].text
                    data = json.loads(text[8:-5])

                    # Create a card-like display for each job post
                    message = f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                        <h3 style="margin-top: 0; color: #007bff;">{data['job_details']['company_name']} is Hiring Interns! 🚀</h3>
                        <p><strong>Salary:</strong> ₹ {data['job_details']['salary_min']} /month - ₹ {data['job_details']['salary_max']} /month</p>
                        <p><strong>Role:</strong> {data['job_details']['role']}</p>
                        <p><strong>Location:</strong> {data['job_details']['location']}</p>
                        <p><strong>Eligibility:</strong> {data['job_details']['education']}</p>
                        <p><strong>Batch:</strong> {', '.join(data['job_details']['batch'])}</p>
                        <p><strong>Skills:</strong> {data['job_details']['skills']}</p>
                        <p><a href="{data['job_details']['apply_link']}" target="_blank" style="color: #007bff;">View Full Job Details & Apply</a></p>
                    </div>
                    """
                    st.markdown(message, unsafe_allow_html=True)

            else:
                st.error(f"Failed to retrieve data, status code: {response.status_code}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
