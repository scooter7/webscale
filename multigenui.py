import streamlit as st
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

placeholders = {
    "Purple - caring, encouraging": {"verbs": ["assist", "befriend", "care"], "adjectives": ["caring", "encouraging"], "beliefs": ["Believe people should be cared for and encouraged"]},
    "Green - adventurous, curious": {"verbs": ["analyze", "discover", "examine"], "adjectives": ["adventurous", "curious"], "beliefs": ["The noblest pursuit is the quest for new knowledge"]},
    "Maroon - gritty, determined": {"verbs": ["accomplish", "achieve", "build"], "adjectives": ["competitive", "determined"], "beliefs": ["Value extreme and hard work"]},
    "Orange - artistic, creative": {"verbs": ["compose", "conceptualize", "create"], "adjectives": ["artistic", "creative"], "beliefs": ["Intensely expressive"]},
    "Yellow - innovative, intelligent": {"verbs": ["accelerate", "advance", "change"], "adjectives": ["innovative", "intelligent"], "beliefs": ["Thrive on new concepts and experimentation"]},
    "Red - entertaining, humorous": {"verbs": ["animate", "amuse", "captivate"], "adjectives": ["dynamic", "entertaining"], "beliefs": ["Energetic and uplifting"]},
    "Blue - confident, influential": {"verbs": ["accomplish", "achieve", "affect"], "adjectives": ["confident", "influential"], "beliefs": ["Achievement is paramount"]},
    "Pink - charming, elegant": {"verbs": ["arise", "aspire", "detail"], "adjectives": ["charming", "elegant"], "beliefs": ["Hold high regard for tradition and excellence"]},
    "Silver - rebellious, daring": {"verbs": ["activate", "campaign", "challenge"], "adjectives": ["bold", "daring"], "beliefs": ["Rule breakers and establishment challengers"]},
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble", "collaborate"], "adjectives": ["dedicated", "humble"], "beliefs": ["There’s no need to differentiate from others"]},
}

if "content_requests" not in st.session_state:
    st.session_state.content_requests = []
if "generated_contents" not in st.session_state:
    st.session_state.generated_contents = []

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats, min_chars, max_chars, call_to_action):
    full_prompt = user_prompt
    if keywords:
        full_prompt += f"\nKeywords: {keywords}"
    if audience:
        full_prompt += f"\nAudience: {audience}"
    if specific_facts_stats:
        full_prompt += f"\nFacts/Stats: {specific_facts_stats}"
    if call_to_action:
        full_prompt += f"\nCall to Action: {call_to_action}"
    if min_chars:
        full_prompt += f"\nMinimum Character Count: {min_chars}"
    if max_chars:
        full_prompt += f"\nMaximum Character Count: {max_chars}"
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        attributes = placeholders[style]
        verbs = ", ".join(attributes["verbs"][:3])
        adjectives = ", ".join(attributes["adjectives"][:3])
        beliefs = "; ".join(attributes["beliefs"][:1])
        full_prompt += f"\nStyle: {style} - Incorporate verbs ({verbs}), adjectives ({adjectives}), and beliefs ({beliefs}) in {weight}% of the content."
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": content})
    messages.append({"role": "user", "content": full_prompt})
    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message["content"].strip()

def content_request_form(index):
    st.markdown(f"### Content Request {index + 1}")
    user_prompt = st.text_area(f"Specify a prompt for Request {index + 1}:", key=f"prompt_{index}")
    keywords = st.text_area(f"Optional Keywords for Request {index + 1}:", key=f"keywords_{index}")
    audience = st.text_input(f"Define Audience for Request {index + 1}:", key=f"audience_{index}")
    specific_facts_stats = st.text_area(f"Specific Facts/Stats for Request {index + 1}:", key=f"facts_{index}")
    call_to_action = st.text_input(f"Optional Call to Action for Request {index + 1}:", key=f"cta_{index}")
    user_content = st.text_area(f"Paste Existing Content (if modifying) for Request {index + 1}:", key=f"content_{index}")
    min_chars = st.text_input(f"Minimum Character Count for Request {index + 1}:", key=f"min_chars_{index}")
    max_chars = st.text_input(f"Maximum Character Count for Request {index + 1}:", key=f"max_chars_{index}")
    writing_styles = st.multiselect(f"Select Writing Styles for Request {index + 1}:", list(placeholders.keys()), key=f"styles_{index}")
    style_weights = [st.slider(f"Weight for {style} (Request {index + 1}):", 0, 100, 50, key=f"weight_{index}_{style}") for style in writing_styles]
    return {
        "user_prompt": user_prompt,
        "keywords": keywords,
        "audience": audience,
        "specific_facts_stats": specific_facts_stats,
        "call_to_action": call_to_action,
        "user_content": user_content,
        "min_chars": min_chars,
        "max_chars": max_chars,
        "writing_styles": writing_styles,
        "style_weights": style_weights,
    }

def main():
    st.title("AI Content Generator with Multiple Requests")
    st.markdown("---")

    num_requests = st.number_input("How many pieces of content do you want to create?", min_value=1, max_value=20, step=1)
    if len(st.session_state.content_requests) != num_requests:
        st.session_state.content_requests = [{} for _ in range(num_requests)]

    st.markdown("---")
    st.header("Step 2: Enter Content Details")
    for i in range(num_requests):
        st.session_state.content_requests[i] = content_request_form(i)

    if st.button("Generate All Content"):
        st.session_state.generated_contents = []
        for i, request in enumerate(st.session_state.content_requests):
            content = generate_article(
                request["user_content"],
                request["writing_styles"],
                request["style_weights"],
                request["user_prompt"],
                request["keywords"],
                request["audience"],
                request["specific_facts_stats"],
                request["min_chars"],
                request["max_chars"],
                request["call_to_action"],
            )
            st.session_state.generated_contents.append((i + 1, content))

    if st.session_state.generated_contents:
        st.markdown("---")
        st.header("Generated Content")
        for idx, content in st.session_state.generated_contents:
            st.subheader(f"Content Request {idx}")
            st.text_area(f"Generated Content for Request {idx}", content, height=300, key=f"generated_{idx}")
            st.download_button(
                label=f"Download Content for Request {idx}",
                data=content,
                file_name=f"generated_content_request_{idx}.txt",
                mime="text/plain",
                key=f"download_{idx}"
            )

    st.markdown("---")
    st.header("Revision Section")
    with st.expander("Revision Fields"):
        pasted_content = st.text_area("Paste Generated Content Here (for further revisions):", key="pasted_revision")
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
