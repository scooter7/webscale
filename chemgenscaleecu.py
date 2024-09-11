import streamlit as st
import pandas as pd
import openai
import requests
from serpapi import GoogleSearch

# Add custom CSS to hide the header and toolbar
st.markdown(
    """
    <style>
    .st-emotion-cache-12fmjuu.ezrtsby2 {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add logo
st.markdown(
    """
    <style>
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    .logo-container img {
        width: 600px;
    }
    .app-container {
        border-left: 5px solid #58258b;
        border-right: 5px solid #58258b;
        padding-left: 15px;
        padding-right: 15px;
    }
    .stTextArea, .stTextInput, .stMultiSelect, .stSlider {
        color: #42145f;
    }
    .stButton button {
        background-color: #fec923;
        color: #42145f;
    }
    .stButton button:hover {
        background-color: #42145f;
        color: #fec923;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="logo-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/East_Carolina_University.svg/1280px-East_Carolina_University.svg.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="app-container">', unsafe_allow_html=True)

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
def generate_content_with_examples(institution, page_type, examples, facts, writing_styles, style_weights, keywords, audience, specific_facts_stats, min_chars, max_chars):
    examples_text = "\n\n".join(examples)
    prompt = (
        "The following are examples of well-written and structured webpages:\n\n"
        f"{examples_text}\n\n"
        "Based on the above examples, create a new webpage with the following details:\n"
        f"Institution: {institution}\n"
        f"Type of page: {page_type}\n"
        f"Include the following facts about the institution: {facts}\n"
    )

    if keywords:
        prompt += f"\nKeywords: {keywords}"
    if audience:
        prompt += f"\nAudience: {audience}"
    if specific_facts_stats:
        prompt += f"\nFacts/Stats: {specific_facts_stats}"
    if min_chars:
        prompt += f"\nMinimum Character Count: {min_chars}"
    if max_chars:
        prompt += f"\nMaximum Character Count: {max_chars}"

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": prompt})
    
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        if weight > 0:  # Only include non-zero weights
            style_name = style.split(' - ')[1]  # Extract the style name
            messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style_name} manner."})

    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
    generated_text = response.choices[0].message["content"].strip()

placeholders = {
    # Placeholder dictionary remains unchanged
}

def main():
    st.title("AI Content Generator")
    st.markdown("---")

    # Initialize the session state for generated pages
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
            for idx, row in csv_data.iterrows():
                institution = row["Institution"]
                page_type = row["Type"]
                keywords = row["Keywords"]
                audience = row["Audience"]
                specific_facts_stats = row["Facts"]  # Use the specific facts verbatim
                min_chars = row["Minimum"]
                max_chars = row["Maximum"]
                style_weights = [
                    row["Purple"], row["Green"], row["Maroon"], row["Orange"],
                    row["Yellow"], row["Red"], row["Blue"], row["Pink"],
                    row["Silver"], row["Beige"]
                ]
                writing_styles = list(placeholders.keys())
                
                generated_content = generate_content_with_examples(
                    institution, page_type, examples, specific_facts_stats, writing_styles, style_weights, keywords, audience, specific_facts_stats, min_chars, max_chars
                )
                generated_pages.append((institution, page_type, generated_content))

            st.session_state.generated_pages = generated_pages
        else:
            st.error("Failed to retrieve example files from GitHub.")

    if st.session_state.generated_pages:
        # Display and download generated content
        for idx, (institution, page_type, content) in enumerate(st.session_state.generated_pages):
            st.subheader(f"{institution} - {page_type}")
            st.text_area("Generated Content", content, height=300, key=f"text_area_{idx}")  # Ensure unique key

            # Create a download button for the generated content
            content_text = f"{institution} - {page_type}\n\n{content}"
            st.download_button(
                label="Download as Text",
                data=content_text,
                file_name=f"{institution}_{page_type}.txt",
                mime="text/plain",
                key=f"download_button_{idx}"  # Ensure unique key for download button
            )

    st.markdown("---")
    st.header("Revision Section")

    with st.expander("Revision Fields"):
        pasted_content = st.text_area("Paste Generated Content Here (for further revisions):", key="pasted_content")
        revision_requests = st.text_area("Specify Revisions Here:", key="revision_requests")

    if st.button("Revise Further"):
        revision_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": pasted_content},
            {"role": "user", "content": revision_requests}
        ]
        response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=revision_messages)
        revised_content = response.choices[0].message["content"].strip()
        st.text(revised_content)
        st.download_button("Download Revised Content", revised_content, "revised_content_revision.txt", key="download_revised_content")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
