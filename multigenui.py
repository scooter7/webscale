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

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats, min_chars, max_chars, call_to_action):
    prompt = f"{user_prompt}\n\nKeywords: {keywords}\nAudience: {audience}\nFacts/Stats: {specific_facts_stats}\nCall to Action: {call_to_action}\nMinimum Characters: {min_chars}\nMaximum Characters: {max_chars}\nContent:\n{content}"
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        attributes = placeholders[style]
        verbs = ", ".join(attributes["verbs"][:3])
        adjectives = ", ".join(attributes["adjectives"][:3])
        beliefs = "; ".join(attributes["beliefs"][:1])
        prompt += f"\nStyle: {style} - Incorporate verbs ({verbs}), adjectives ({adjectives}), and beliefs ({beliefs}) in {weight}% of the content."
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message["content"].strip()

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
            generated_content = generate_article(
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
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Content": generated_content}
            )
        st.success("Content generation completed! Navigate to the 'Generated Content' tab to view and download your results.")

elif active_tab == "Generated Content":
    st.subheader("Generated Content")
    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            card(
                title=f"Generated Content {content_data['Request']}",
                content=f"""
                    <div>
                        <div style="font-weight: bold; margin-bottom: 10px;">{content_data['Content']}</div>
                        <div style="font-size: small; color: gray;">Generated based on user input.</div>
                    </div>
                """,
                description="",
                key=f"card_{idx}",
            )
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

elif active_tab == "Revisions":
    st.subheader("Make Revisions")
    revision_content = textarea(default_value="", placeholder="Paste the generated content to revise...", key="revision_content")
    revision_request = textarea(default_value="", placeholder="Describe your revision requests...", key="revision_request")
    if button(text="Revise Content", key="revise"):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": revision_content},
            {"role": "user", "content": revision_request},
        ]
        response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
        revised_content = response.choices[0].message["content"].strip()
        card(
            title="Revised Content",
            content=f"""
                <div>
                    <div style="font-weight: bold; margin-bottom: 10px;">{revised_content}</div>
                    <div style="font-size: small; color: gray;">Updated based on your revision request.</div>
                </div>
            """,
            description="",
            key="revised_card",
        )

st.markdown('</div>', unsafe_allow_html=True)
