import streamlit as st
import pandas as pd
import openai
import requests
from io import StringIO

# Load Streamlit secrets for OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

# Function to read text files from the Examples folder in the GitHub repository
def read_github_files():
    base_url = "https://raw.githubusercontent.com/scooter7/webscale/main/Examples/"
    file_names = ["example1.txt", "example2.txt", "example3.txt"]  # Add the actual file names from your repo
    examples = []
    for file_name in file_names:
        response = requests.get(base_url + file_name)
        if response.status_code == 200:
            examples.append(response.text)
    return examples

# Function to analyze examples and generate new content using OpenAI
def generate_content(institution, page_type, examples):
    examples_text = "\n".join(examples)
    prompt = f"Use the following examples of well-written and structured webpages:\n\n{examples_text}\n\n"
    prompt += f"Create a new {page_type} page for {institution} using the same structure and style."

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=1500
    )
    return response.choices[0].text.strip()

# Streamlit app
st.title("Web Page Content Generator")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    # Read the uploaded CSV file
    csv_data = pd.read_csv(uploaded_file)

    # Read examples from GitHub repository
    examples = read_github_files()

    # Generate content for each row in the CSV
    generated_pages = []
    for _, row in csv_data.iterrows():
        institution = row["Institution"]
        page_type = row["Type"]
        generated_content = generate_content(institution, page_type, examples)
        generated_pages.append((institution, page_type, generated_content))

    # Display and download generated content
    for institution, page_type, content in generated_pages:
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
