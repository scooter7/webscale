import streamlit as st
import pandas as pd
import openai
import requests
from serpapi import GoogleSearch

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
        width: 300px;
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
        <img src="https://seeklogo.com/images/E/east-carolina-university-logo-D87F964E5D-seeklogo.com.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="app-container">', unsafe_allow_html=True)

openai.api_key = st.secrets["openai_api_key"]
serpapi_key = st.secrets["serpapi_api_key"]
github_token = st.secrets["github_token"]

placeholders = {
    # placeholders dictionary from the previous code...
}

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
        return []

def read_github_files(file_urls):
    examples = []
    headers = {"Authorization": f"token {github_token}"}
    for url in file_urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            examples.append(response.text)
        else:
            st.error(f"Failed to retrieve file: {url}")
    return examples

def fetch_social_media_posts(institution_name, channel):
    search_query = f"{institution_name} {channel}"
    params = {
        "engine": "google",
        "q": search_query,
        "api_key": serpapi_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    posts = []
    if 'organic_results' in results:
        for result in results['organic_results'][:5]:  # Limit to top 5 results
            posts.append(result['snippet'])

    return " ".join(posts)

def generate_content_with_examples(institution, page_type, channel, examples, facts, writing_styles, style_weights, keywords, audience, specific_facts_stats, min_chars, max_chars):
    examples_text = "\n\n".join(examples)

    if channel == "email":
        prompt = (
            "The following are examples of well-written and structured emails:\n\n"
            f"{examples_text}\n\n"
            "Based on the above examples, create a new email with the following details:\n"
        )
    else:
        social_posts = fetch_social_media_posts(institution, channel)
        prompt = (
            "The following are recent posts from the institution's social media page:\n\n"
            f"{social_posts}\n\n"
            f"Based on these posts, create a {channel} post with the following details:\n"
        )

    prompt += f"Institution: {institution}\n"
    prompt += f"Type of page: {page_type}\n"
    prompt += f"Include the following facts about the institution: {facts}\n"

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

    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        if weight > 0:
            style_name = style.split(' - ')[1]
            prompt += f"\nModify {weight}% of the content in a {style_name} manner."

    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message["content"].strip()

def main():
    if 'generated_pages' not in st.session_state:
        st.session_state.generated_pages = []
        st.session_state.revised_pages = []  # For revisions

    uploaded_file = st.file_uploader("Upload CSV", type="csv")

    if uploaded_file and st.button("Generate Content"):
        csv_data = pd.read_csv(uploaded_file)

        file_urls = get_github_files()

        if file_urls:
            examples = read_github_files(file_urls)

            generated_pages = []
            for _, row in csv_data.iterrows():
                institution = row["Institution"]
                page_type = row["Type"]
                channel = row["Channel"]  # New column for content channel
                keywords = row["Keywords"]
                audience = row["Audience"]
                specific_facts_stats = row["Facts"]
                min_chars = row["Minimum"]
                max_chars = row["Maximum"]
                style_weights = [
                    row["Purple"], row["Green"], row["Maroon"], row["Orange"],
                    row["Yellow"], row["Red"], row["Blue"], row["Pink"],
                    row["Silver"], row["Beige"]
                ]
                writing_styles = list(placeholders.keys())

                generated_content = generate_content_with_examples(
                    institution, page_type, channel, examples, specific_facts_stats, writing_styles, style_weights, keywords, audience, specific_facts_stats, min_chars, max_chars
                )
                generated_pages.append((institution, page_type, channel, generated_content))

            st.session_state.generated_pages = generated_pages
        else:
            st.error("Failed to retrieve example files from GitHub.")

    if st.session_state.generated_pages:
        for idx, (institution, page_type, channel, content) in enumerate(st.session_state.generated_pages):
            st.subheader(f"{institution} - {page_type} ({channel})")
            generated_content = st.text_area("Generated Content", content, height=300, key=f"generated_content_{idx}")

            # Revision prompt and button
            revision_prompt = st.text_input(f"Provide revisions for {institution} - {page_type} ({channel})", key=f"revision_prompt_{idx}")
            if st.button(f"Revise Content {idx}", key=f"revise_button_{idx}"):
                if revision_prompt:
                    # Generate revised content based on user input
                    revision_response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"Revise the following content based on the user's feedback:\n\n{generated_content}"},
                            {"role": "user", "content": revision_prompt}
                        ]
                    )
                    revised_content = revision_response.choices[0].message["content"].strip()
                    st.session_state.revised_pages.append((institution, page_type, channel, revised_content))
                    st.write("Revision Complete!")
            
            # Show revisions if they exist
            if st.session_state.revised_pages:
                for ridx, (inst, pg_type, chn, revised) in enumerate(st.session_state.revised_pages):
                    if institution == inst and page_type == pg_type and channel == chn:
                        st.text_area(f"Revised Content for {inst} - {pg_type} ({chn})", revised, height=300, key=f"revised_content_{ridx}")

            content_text = f"{institution} - {page_type}\n\n{content}"
            st.download_button(
                label="Download as Text",
                data=content_text,
                file_name=f"{institution}_{page_type}_{channel}.txt",
                mime="text/plain",
                key=f"download_button_{idx}"
            )

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
