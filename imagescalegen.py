import streamlit as st
import pandas as pd
import openai
import requests
import replicate

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
        <img src="https://wfin.com/wp-content/uploads/2018/08/UF-Academic-Logo-1.jpg" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="app-container">', unsafe_allow_html=True)

# Load Streamlit secrets for API keys
openai.api_key = st.secrets["openai_api_key"]
serpapi_key = st.secrets["serpapi_api_key"]
github_token = st.secrets["github_token"]
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINTSTABILITY = st.secrets["REPLICATE_MODEL_ENDPOINTSTABILITY"]

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

# Function to split text into chunks
def chunk_text(text, chunk_size=2000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Function to analyze examples and generate new content using GPT-4o-mini with chunking
def generate_content_with_examples(institution, page_type, examples, facts, writing_styles, style_weights, keywords, audience, specific_facts_stats, min_chars, max_chars, image_description):
    examples_text = "\n\n".join(examples)
    prompt_base = (
        "The following are examples of well-written and structured webpages:\n\n"
        f"{examples_text}\n\n"
        "Based on the above examples, create a new webpage with the following details:\n"
        f"Institution: {institution}\n"
        f"Type of page: {page_type}\n"
    )

    if facts:
        prompt_base += f"Include the following facts about the institution: {facts}\n"
    if keywords:
        prompt_base += f"Keywords: {keywords}\n"
    if audience:
        prompt_base += f"Audience: {audience}\n"
    if specific_facts_stats:
        prompt_base += f"Facts/Stats: {specific_facts_stats}\n"
    if min_chars:
        prompt_base += f"Minimum Character Count: {min_chars}\n"
    if max_chars:
        prompt_base += f"Maximum Character Count: {max_chars}\n"

    # Handling chunking for large prompts
    text_chunks = chunk_text(prompt_base)

    detailed_responses = []
    for chunk in text_chunks:
        prompt_text = chunk
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        detailed_responses.append(response.choices[0].message['content'])

    generated_text = "\n".join(detailed_responses)

    # Generate image using the image_description
    output = replicate.run(
        REPLICATE_MODEL_ENDPOINTSTABILITY,
        input={
            "prompt": image_description,
            "width": 1024,
            "height": 1024,
            "num_outputs": 1,
            "scheduler": "DDIM",
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        }
    )
    image_url = output[0] if output else None

    return generated_text, image_url

# Main function
def main():
    st.title("AI Content Generator")
    st.markdown("---")

    if 'generated_pages' not in st.session_state:
        st.session_state.generated_pages = []

    uploaded_file = st.file_uploader("Upload CSV", type="csv")

    if uploaded_file and st.button("Generate Content"):
        csv_data = pd.read_csv(uploaded_file)

        file_urls = get_github_files()

        if file_urls:
            examples = read_github_files(file_urls)

            generated_pages = []
            for _, row in csv_data.iterrows():
                institution = row.get("Institution", "Unknown Institution")
                page_type = row.get("Type", "General")
                keywords = row.get("Keywords", "")
                audience = row.get("Audience", "")
                specific_facts_stats = row.get("Facts", "")
                min_chars = row.get("Minimum", "")
                max_chars = row.get("Maximum", "")
                style_weights = [
                    row.get("Purple", 0), row.get("Green", 0), row.get("Maroon", 0), row.get("Orange", 0),
                    row.get("Yellow", 0), row.get("Red", 0), row.get("Blue", 0), row.get("Pink", 0),
                    row.get("Silver", 0), row.get("Beige", 0)
                ]
                writing_styles = list(placeholders.keys())
                image_description = row.get("Image", "")
                
                generated_content, image_url = generate_content_with_examples(
                    institution, page_type, examples, specific_facts_stats, writing_styles, style_weights, keywords, audience, specific_facts_stats, min_chars, max_chars, image_description
                )
                generated_pages.append((institution, page_type, generated_content, image_url))

            st.session_state.generated_pages = generated_pages
        else:
            st.error("Failed to retrieve example files from GitHub.")

    if st.session_state.generated_pages:
        for idx, (institution, page_type, content, image_url) in enumerate(st.session_state.generated_pages):
            st.subheader(f"{institution} - {page_type}")
            st.text_area("Generated Content", content, height=300)
            if image_url:
                st.image(image_url, caption="Generated Image", use_column_width=True)

            content_text = f"{institution} - {page_type}\n\n{content}"
            st.download_button(
                label="Download as Text",
                data=content_text,
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
        response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=revision_messages, max_tokens=500)
        revised_content = response.choices[0].message["content"].strip()
        st.text(revised_content)
        st.download_button("Download Revised Content", revised_content, "revised_content_revision.txt", key="download_revised_content")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
