import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import input, textarea, button, tabs, card
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

# Tabs for layout
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

            # Input fields using Shadcn components
            prompt = textarea(
                default_value="",
                placeholder="Enter your prompt...",
                key=f"prompt_{idx}",
            )
            keywords = textarea(
                default_value="",
                placeholder="Enter optional keywords...",
                key=f"keywords_{idx}",
            )
            audience = input(
                default_value="",
                placeholder="Define the audience...",
                key=f"audience_{idx}",
            )
            specific_facts_stats = textarea(
                default_value="",
                placeholder="Enter specific facts/stats...",
                key=f"facts_{idx}",
            )
            call_to_action = input(
                default_value="",
                placeholder="Enter a call to action...",
                key=f"cta_{idx}",
            )
            user_content = textarea(
                default_value="",
                placeholder="Paste existing content (if modifying)...",
                key=f"content_{idx}",
            )
            min_chars = input(
                default_value="",
                placeholder="Enter minimum character count...",
                key=f"min_chars_{idx}",
            )
            max_chars = input(
                default_value="",
                placeholder="Enter maximum character count...",
                key=f"max_chars_{idx}",
            )

            # Writing styles and sliders
            writing_styles = st.multiselect(
                label=f"Select Writing Styles for Request {idx + 1}:",
                options=list(placeholders.keys()),
                default=[],
                key=f"styles_{idx}",
            )
            style_weights = []
            if writing_styles:
                st.markdown("### Set Weights for Selected Writing Styles")
                for style in writing_styles:
                    weight = st.slider(
                        label=f"Weight for {style} (Request {idx + 1})",
                        min_value=0,
                        max_value=100,
                        value=50,
                        key=f"weight_{idx}_{style}",
                    )
                    style_weights.append(weight)

            # Save request data
            st.session_state.content_requests[idx] = {
                "prompt": prompt,
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
                request["prompt"],
                request["keywords"],
                request["audience"],
                request["specific_facts_stats"],
                request["min_chars"],
                request["max_chars"],
                request["call_to_action"],
            )
            # Append generated content to session state
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Content": generated_content}
            )
            # Debug log for generated content
            st.write(f"Debug: Content for Request {idx + 1} generated successfully.")

        # Show success notification and feedback
        st.success("Content generation completed! Navigate to the 'Generated Content' tab to view and download your results.")
        st.info("Click on the 'Generated Content' tab at the top to access your generated content.")

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
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

elif active_tab == "Revisions":
    st.subheader("Make Revisions")

    revision_content = textarea(
        default_value="",
        placeholder="Paste the generated content to revise...",
        key="revision_content",
    )
    revision_request = textarea(
        default_value="",
        placeholder="Describe your revision requests...",
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
