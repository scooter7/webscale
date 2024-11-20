import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import input, textarea, button, tabs, card
import openai

# Initialize OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

# Styling
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

# Color placeholders
placeholders = {
    "Purple - caring, encouraging": {
        "verbs": ["assist", "befriend", "care", "empower"],
        "adjectives": ["caring", "encouraging", "compassionate"],
        "beliefs": ["Believe people should be cared for and encouraged"]
    },
    "Green - adventurous, curious": {
        "verbs": ["explore", "discover", "venture"],
        "adjectives": ["adventurous", "curious", "inquisitive"],
        "beliefs": ["The noblest pursuit is the quest for new knowledge"]
    },
    "Maroon - gritty, determined": {
        "verbs": ["overcome", "achieve", "persist"],
        "adjectives": ["gritty", "determined", "resilient"],
        "beliefs": ["Value hard work and grit"]
    },
    "Orange - artistic, creative": {
        "verbs": ["create", "design", "imagine"],
        "adjectives": ["artistic", "creative", "expressive"],
        "beliefs": ["Manifesting new and creative concepts is their end goal"]
    },
    "Yellow - innovative, intelligent": {
        "verbs": ["invent", "innovate", "experiment"],
        "adjectives": ["innovative", "visionary", "analytical"],
        "beliefs": ["Thrive on new concepts and experimentation"]
    },
    "Red - entertaining, humorous": {
        "verbs": ["engage", "entertain", "inspire"],
        "adjectives": ["dynamic", "engaging", "entertaining"],
        "beliefs": ["Energetic and uplifting"]
    },
    "Blue - confident, influential": {
        "verbs": ["lead", "influence", "achieve"],
        "adjectives": ["confident", "influential", "strong"],
        "beliefs": ["Achievement is paramount"]
    },
    "Pink - charming, elegant": {
        "verbs": ["enchant", "refine", "uplift"],
        "adjectives": ["charming", "refined", "elegant"],
        "beliefs": ["Pursue refinement, beauty, and vitality"]
    },
    "Silver - rebellious, daring": {
        "verbs": ["challenge", "disrupt", "ignite"],
        "adjectives": ["rebellious", "bold", "daring"],
        "beliefs": ["Value freedom, boldness, and defiant ideas"]
    },
    "Beige - dedicated, humble": {
        "verbs": ["collaborate", "empower", "dedicate"],
        "adjectives": ["dedicated", "humble", "collaborative"],
        "beliefs": ["All perspectives are equally worth holding"]
    },
}

if "content_requests" not in st.session_state:
    st.session_state.content_requests = []
if "generated_contents" not in st.session_state:
    st.session_state.generated_contents = []

def generate_content(request):
    """
    Generate actual content using OpenAI based on the form inputs.
    """
    user_prompt = request.get("user_prompt", "")
    keywords = request.get("keywords", "")
    audience = request.get("audience", "")
    specific_facts_stats = request.get("specific_facts_stats", "")
    call_to_action = request.get("call_to_action", "")
    user_content = request.get("user_content", "")
    min_chars = request.get("min_chars", "")
    max_chars = request.get("max_chars", "")
    writing_styles = request.get("writing_styles", [])
    style_weights = request.get("style_weights", [])

    # Create a prompt for the OpenAI model
    styles_description = "\n".join(
        f"Style: {style} ({weight}% weight)"
        for style, weight in zip(writing_styles, style_weights)
    )

    prompt = f"""
    You are an expert content creator. Please generate content based on the following inputs:
    
    Prompt: {user_prompt}
    Keywords: {keywords}
    Audience: {audience}
    Specific Facts/Stats: {specific_facts_stats}
    Call to Action: {call_to_action}
    Minimum Characters: {min_chars}
    Maximum Characters: {max_chars}
    User Content: {user_content}
    
    Writing Styles and Weights:
    {styles_description}
    
    Ensure the content is engaging, concise, and tailored to the audience described.
    """

    # Call OpenAI to generate content
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"].strip()

def generate_revised_content(original_content, revision_request):
    """
    Generate revised content using OpenAI based on the provided revision instructions.
    """
    prompt = f"""
    Please revise the following content based on the described revision request:
    
    Original Content:
    {original_content}
    
    Revision Request:
    {revision_request}
    """

    # Call OpenAI to generate the revised content
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"].strip()

def download_content(content, filename):
    st.download_button(
        label="Download Content",
        data=content,
        file_name=filename,
        mime="text/plain",
    )

tabs_options = ["Create Content", "Generated Content", "Revisions"]
active_tab = tabs(options=tabs_options, default_value="Create Content", key="main_tabs")

if active_tab == "Create Content":
    st.subheader("Create Content Requests")
    num_requests = input(
        default_value="1",
        type="number",
        placeholder="How many pieces of content to create?",
        key="num_requests",
    )
    if button(text="Generate Form", key="generate_form"):
        st.session_state.content_requests = [{} for _ in range(int(num_requests))]
    if st.session_state.content_requests:
        for idx, _ in enumerate(st.session_state.content_requests):
            st.markdown(f"### Content Request {idx + 1}")
            user_prompt = textarea(default_value="", placeholder="Enter your prompt...", key=f"prompt_{idx}")
            keywords = textarea(default_value="", placeholder="Enter optional keywords...", key=f"keywords_{idx}")
            audience = input(default_value="", placeholder="Define the audience...", key=f"audience_{idx}")
            specific_facts_stats = textarea(default_value="", placeholder="Enter specific facts/stats...", key=f"facts_{idx}")
            call_to_action = input(default_value="", placeholder="Enter a call to action...", key=f"cta_{idx}")
            user_content = textarea(default_value="", placeholder="Paste existing content (if modifying)...", key=f"content_{idx}")
            min_chars = input(default_value="", placeholder="Enter minimum character count...", key=f"min_chars_{idx}")
            max_chars = input(default_value="", placeholder="Enter maximum character count...", key=f"max_chars_{idx}")
            writing_styles = st.multiselect(label=f"Select Writing Styles for Request {idx + 1}:", options=list(placeholders.keys()), default=[], key=f"styles_{idx}")
            style_weights = []
            if writing_styles:
                st.markdown("### Set Weights for Selected Writing Styles")
                for style in writing_styles:
                    weight = st.slider(label=f"Weight for {style}:", min_value=0, max_value=100, value=50, step=1, key=f"weight_{idx}_{style}")
                    style_weights.append(weight)
            st.session_state.content_requests[idx] = {
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
    if button(text="Generate All Content", key="generate_all"):
        st.session_state.generated_contents = []
        for idx, request in enumerate(st.session_state.content_requests):
            generated_content = generate_content(request)
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Content": generated_content}
            )
        st.success("Content generation completed! Navigate to the 'Generated Content' tab to view and download your results.")

elif active_tab == "Generated Content":
    st.subheader("Generated Content")
    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            content = content_data["Content"]
            ui.card(
                title=f"Generated Content {content_data['Request']}",
                content=f"<div>{content}</div>",
                description="Generated based on user input.",
                key=f"card_{idx}",
            ).render()
            download_content(content, f"content_{content_data['Request']}.txt")
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

elif active_tab == "Revisions":
    st.subheader("Make Revisions")
    original_content = textarea(default_value="", placeholder="Paste content to revise...", key="revision_content")
    revision_request = textarea(default_value="", placeholder="Describe the revisions needed...", key="revision_request")
    if button(text="Revise Content", key="revise"):
        revised_content = generate_revised_content(original_content, revision_request)
        ui.card(
            title="Revised Content",
            content=f"<div>{revised_content}</div>",
            description="Updated based on your revision input.",
            key="revised_card",
        ).render()
        download_content(revised_content, "revised_content.txt")

st.markdown('</div>', unsafe_allow_html=True)
