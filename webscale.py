import streamlit as st
import pandas as pd
import openai
import requests
from serpapi import GoogleSearch

# Load Streamlit secrets for API keys
openai.api_key = st.secrets["openai_api_key"]
serpapi_key = st.secrets["serpapi_api_key"]
github_token = st.secrets["github_token"]

# Function to get a list of all text files in the Examples folder from the GitHub repository
def get_github_files():
    repo_url = "https://api.github.com/repos/scooter7/webscale/contents/Examples"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(repo_url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        text_files = [file['download_url'] for file in files if file['name'].endswith('.txt')]
        return text_files
    else:
        st.error(f"Failed to retrieve files from GitHub: {response.status_code}")
        st.error(f"Response content: {response.text}")
        return []

# Function to read text files from the Examples folder in the GitHub repository
def read_github_files(file_urls):
    examples = []
    headers = {"Authorization": f"token {github_token}"}
    for url in file_urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            examples.append(response.text)
        else:
            st.error(f"Failed to retrieve file: {url}")
            st.error(f"Response content: {response.text}")
    return examples

# Function to fetch facts about a university using SerpAPI
def fetch_university_facts(university_name):
    params = {
        "engine": "google",
        "q": university_name,
        "api_key": serpapi_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    facts = []
    
    if 'organic_results' in results:
        for result in results['organic_results'][:3]:  # Limit to top 3 results
            facts.append(result['snippet'])
    
    return " ".join(facts)

# Function to analyze examples and generate new content using OpenAI
def generate_content(institution, page_type, examples, facts):
    examples_text = "\n\n".join(examples)
    prompt = (
        "The following are examples of well-written and structured webpages:\n\n"
        f"{examples_text}\n\n"
        "Based on the above examples, create a new webpage with the following details:\n"
        f"Institution: {institution}\n"
        f"Type of page: {page_type}\n"
        f"Include the following facts about the institution: {facts}\n"
        "The new page should follow the same structure and writing style as the examples provided. "
        "Please avoid using markdown characters in the output."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

# Streamlit app
st.title("Web Page Content Generator")

if 'generated_pages' not in st.session_state:
    st.session_state.generated_pages = []

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file and st.button("Generate Content"):
    # Read the uploaded CSV file
    csv_data = pd.read_csv(uploaded_file)

    # Get the list of text files from GitHub repository
    file_urls = get_github_files()

    if file_urls:
        # Read examples from GitHub repository
        examples = read_github_files(file_urls)

        # Generate content for each row in the CSV
        generated_pages = []
        for _, row in csv_data.iterrows():
            institution = row["Institution"]
            page_type = row["Type"]
            facts = fetch_university_facts(institution)
            generated_content = generate_content(institution, page_type, examples, facts)
            generated_pages.append((institution, page_type, generated_content))
        
        st.session_state.generated_pages = generated_pages
    else:
        st.error("Failed to retrieve example files from GitHub.")

if st.session_state.generated_pages:
    # Display and download generated content
    for institution, page_type, content in st.session_state.generated_pages:
        st.subheader(f"{institution} - {page_type}")
        st.text_area("Generated Content", content, height=300)

        # Create a download button for the generated content
        content_text = f"{institution} - {page_type}\n\n{content}"
        st.download_button(
            label="Download as Text",
            data=content_text,
            file_name=f"{institution}_{page_type}.txt",
            mime="text/plain"
        )
