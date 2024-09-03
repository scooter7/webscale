import streamlit as st
import pandas as pd
import openai
import requests
from serpapi import GoogleSearch

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

openai.api_key = st.secrets["openai_api_key"]
serpapi_key = st.secrets["serpapi_api_key"]
github_token = st.secrets["github_token"]

def get_github_files():
    repo_url = "https://api.github.com/repos/scooter7/webscale/contents/Examples"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(repo_url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        return [file['download_url'] for file in files if file['name'].endswith('.txt')]
    else:
        st.error("Failed to retrieve files from GitHub")
        return []

def read_github_files(file_urls):
    examples = []
    headers = {"Authorization": f"token {github_token}"}
    for url in file_urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            examples.append(response.text)
        else:
            st.error("Failed to retrieve file from GitHub")
    return examples

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
        for result in results['organic_results'][:3]:
            facts.append(result['snippet'])
    return " ".join(facts)

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
        messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"].strip()

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats, min_chars, max_chars):
    full_prompt = user_prompt
    if keywords:
        full_prompt += f"\nKeywords: {keywords}"
    if audience:
        full_prompt += f"\nAudience: {audience}"
    if specific_facts_stats:
        full_prompt += f"\nFacts/Stats: {specific_facts_stats}"
    if min_chars:
        full_prompt += f"\nMinimum Character Count: {min_chars}"
    if max_chars:
        full_prompt += f"\nMaximum Character Count: {max_chars}"

    messages = [{"role": "system", "content": full_prompt}]
    messages.append({"role": "user", "content": content})
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"].strip()

def main():
    st.title("AI Content Generator")
    st.markdown("---")
    use_examples = st.checkbox("Use examples?")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")

    user_prompt = ""
    if not use_examples:
        user_prompt = st.text_area("Specify a prompt about the type of content you want produced:", "")

    keywords = st.text_area("Optional: Specify specific keywords to be used:", "")
    audience = st.text_input("Optional: Define the audience for the generated content:", "")
    specific_facts_stats = st.text_area("Optional: Add specific facts or stats to be included:", "")
    user_content = st.text_area("Paste your content here (ONLY IF MODIFYING EXISTING CONTENT):")
    min_chars = st.text_input("Optional: Specify a minimum character count:", "")
    max_chars = st.text_input("Optional: Specify a maximum character count:", "")
    writing_styles = st.multiselect("Select Writing Styles:", ["Purple", "Green", "Maroon", "Orange", "Yellow", "Red", "Blue", "Pink", "Silver", "Beige"])

    style_weights = []
    for style in writing_styles:
        weight = st.slider(f"Weight for {style}:", 0, 100, 50)
        style_weights.append(weight)

    if st.button("Generate Content"):
        if uploaded_file:
            csv_data = pd.read_csv(uploaded_file)
            if use_examples:
                file_urls = get_github_files()
                if file_urls:
                    examples = read_github_files(file_urls)
                    generated_pages = []
                    for _, row in csv_data.iterrows():
                        institution = row["Institution"]
                        page_type = row["Type"]
                        facts = fetch_university_facts(institution)
                        generated_content = generate_content_with_examples(
                            institution, page_type, examples, facts, writing_styles, 
                            style_weights, keywords, audience, specific_facts_stats, min_chars, max_chars
                        )
                        generated_pages.append((institution, page_type, generated_content))
                    st.session_state.generated_pages = generated_pages
                else:
                    st.error("Failed to retrieve example files from GitHub.")
            else:
                generated_pages = []
                for _, row in csv_data.iterrows():
                    institution = row["Institution"]
                    page_type = row["Type"]
                    revised_content = generate_article(
                        user_content, writing_styles, style_weights, user_prompt, 
                        keywords, audience, specific_facts_stats, min_chars, max_chars
                    )
                    generated_pages.append((institution, page_type, revised_content))
                st.session_state.generated_pages = generated_pages

    if "generated_pages" in st.session_state:
        for idx, (institution, page_type, content) in enumerate(st.session_state.generated_pages):
            st.subheader(f"{institution} - {page_type}")
            st.text_area("Generated Content", content, height=300)
            st.download_button(
                label="Download as Text",
                data=f"{institution} - {page_type}\n\n{content}",
                file_name=f"{institution}_{page_type}.txt",
                mime="text/plain",
                key=f"download_button_{idx}"
            )

    st.markdown("---")
    st.header("Revision Section")

    with st.expander("Revision Fields"):
        pasted_content = st.text_area("Paste Generated Content Here (for further revisions):")
        revision_requests = st.text_area("Specify Revisions Here:")

    if st.button("Revise Further"):
        revision_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": pasted_content},
            {"role": "user", "content": revision_requests}
        ]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=revision_messages)
        revised_content = response.choices[0].message["content"].strip()
        st.text(revised_content)
        st.download_button("Download Revised Content", revised_content, "revised_content_revision.txt", key="download_revised_content")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
