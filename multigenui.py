import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import input, textarea, slider, button, tabs, table, card
import openai

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

def generate_article(content, user_prompt, call_to_action):
    prompt = f"{user_prompt}\n\nCall to Action: {call_to_action}\n\nContent:\n{content}"
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message["content"].strip()

# Tabs for layout
tabs_options = ["Create Content", "Generated Content", "Revisions"]
active_tab = tabs(options=tabs_options, default_value="Create Content", key="main_tabs")

if active_tab == "Create Content":
    st.subheader("Create Content Requests")

    num_requests = input(
        default_value="1",
        type="number",
        placeholder="How many pieces of content to create?",
        label="Number of Requests",
        key="num_requests",
    )
    if button(text="Generate Form", key="generate_form"):
        st.session_state.content_requests = [{} for _ in range(int(num_requests))]

    if st.session_state.content_requests:
        for idx, _ in enumerate(st.session_state.content_requests):
            st.markdown(f"### Content Request {idx + 1}")

            # Input fields using Shadcn components
            prompt = textarea(
                default_value="",
                placeholder="Enter your prompt...",
                label=f"Prompt for Request {idx + 1}",
                key=f"prompt_{idx}",
            )
            call_to_action = input(
                default_value="",
                placeholder="Enter call to action...",
                label=f"Call to Action for Request {idx + 1}",
                key=f"cta_{idx}",
            )
            content = textarea(
                default_value="",
                placeholder="Paste any existing content (if modifying)...",
                label=f"Existing Content for Request {idx + 1}",
                key=f"content_{idx}",
            )

            # Save request data
            st.session_state.content_requests[idx] = {
                "prompt": prompt,
                "call_to_action": call_to_action,
                "content": content,
            }

    if button(text="Generate All Content", key="generate_all"):
        st.session_state.generated_contents = []
        for idx, request in enumerate(st.session_state.content_requests):
            generated_content = generate_article(
                request["content"], request["prompt"], request["call_to_action"]
            )
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Content": generated_content}
            )

elif active_tab == "Generated Content":
    st.subheader("Generated Content")

    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            card(
                title=f"Generated Content {content_data['Request']}",
                content=content_data["Content"],
                description="Generated based on user input.",
                key=f"card_{idx}",
            )

elif active_tab == "Revisions":
    st.subheader("Make Revisions")

    revision_content = textarea(
        default_value="",
        placeholder="Paste the generated content to revise...",
        label="Generated Content",
        key="revision_content",
    )
    revision_request = textarea(
        default_value="",
        placeholder="Describe your revision requests...",
        label="Revision Request",
        key="revision_request",
    )

    if button(text="Revise Content", key="revise"):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": revision_content},
            {"role": "user", "content": revision_request},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", messages=messages
        )
        revised_content = response.choices[0].message["content"].strip()
        card(
            title="Revised Content",
            content=revised_content,
            description="Updated based on your revision request.",
            key="revised_card",
        )

st.markdown('</div>', unsafe_allow_html=True)
