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

def generate_content(request, content_type):
    """
    Generate content based on request details and type.
    """
    subject = request.get("subject", "")
    body = request.get("body", "")
    signature = request.get("signature", "")
    writing_style = request.get("writing_style", "General")
    weight = request.get("weight", 0)
    
    style_data = placeholders.get(writing_style, {})
    verbs = ", ".join(style_data.get("verbs", [])[:3])
    adjectives = ", ".join(style_data.get("adjectives", [])[:3])
    beliefs = "; ".join(style_data.get("beliefs", [])[:1])

    if content_type == "Email":
        return {
            "type": "Email",
            "content": {
                "subject": subject,
                "body": f"{body}\n\nVerbs: {verbs}, Adjectives: {adjectives}, Beliefs: {beliefs} ({weight}%).",
                "signature": signature,
            },
        }
    else:
        return {
            "type": "General",
            "content": f"Subject: {subject}\n\n{body}\n\nSignature: {signature}\n\nStyle: {writing_style} with {weight}% emphasis.\nVerbs: {verbs}, Adjectives: {adjectives}, Beliefs: {beliefs}.",
        }

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
            subject = input(default_value="", placeholder="Enter subject (if applicable)...", key=f"subject_{idx}")
            body = textarea(default_value="", placeholder="Enter content body...", key=f"body_{idx}")
            signature = textarea(default_value="", placeholder="Enter signature (if applicable)...", key=f"signature_{idx}")
            content_type = st.selectbox("Select content type", ["Email", "General"], key=f"type_{idx}")
            writing_style = st.selectbox("Choose a writing style", options=list(placeholders.keys()), key=f"style_{idx}")
            weight = st.slider("Style weight percentage", min_value=0, max_value=100, value=50, step=5, key=f"weight_{idx}")
            st.session_state.content_requests[idx] = {
                "subject": subject,
                "body": body,
                "signature": signature,
                "content_type": content_type,
                "writing_style": writing_style,
                "weight": weight,
            }
    if button(text="Generate All Content", key="generate_all"):
        st.session_state.generated_contents = []
        for idx, request in enumerate(st.session_state.content_requests):
            content_type = request.get("content_type", "General")
            generated_content = generate_content(request, content_type)
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Content": generated_content}
            )
        st.success("Content generation completed! Navigate to the 'Generated Content' tab to view and download your results.")

elif active_tab == "Generated Content":
    st.subheader("Generated Content")
    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            content = content_data.get("Content", {})
            if isinstance(content, dict) and "type" in content:
                content_type = content["type"]
                if content_type == "Email":
                    email_content = content["content"]
                    ui.card(
                        title=f"Generated Email {content_data['Request']}",
                        content=f"""
                            <div><strong>Subject:</strong> {email_content['subject']}</div>
                            <div>{email_content['body']}</div>
                            <div><em>{email_content['signature']}</em></div>
                        """,
                        description="Generated email content",
                        key=f"card_email_{idx}",
                    ).render()
                    download_content(
                        f"Subject: {email_content['subject']}\n\n{email_content['body']}\n\n{email_content['signature']}",
                        f"email_{content_data['Request']}.txt",
                    )
                elif content_type == "General":
                    general_content = content["content"]
                    ui.card(
                        title=f"Generated Content {content_data['Request']}",
                        content=f"<div>{general_content}</div>",
                        description="General content generated",
                        key=f"card_general_{idx}",
                    ).render()
                    download_content(
                        general_content,
                        f"content_{content_data['Request']}.txt",
                    )
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

elif active_tab == "Revisions":
    st.subheader("Make Revisions")
    revision_body = textarea(default_value="", placeholder="Enter revised body...", key="revision_body")
    revision_type = st.selectbox("Select content type for revision", ["Email", "General"], key="revision_type")
    if button(text="Revise Content", key="revise"):
        revised_content = generate_content({"body": revision_body}, revision_type)
        content_text = revised_content["content"] if revision_type == "General" else f"Subject: {revised_content['content']['subject']}\n\n{revised_content['content']['body']}\n\n{revised_content['content']['signature']}"
        ui.card(
            title="Revised Content",
            content=f"<div>{content_text}</div>",
            description="Revised content based on input",
            key="revised_card",
        ).render()
        download_content(content_text, "revised_content.txt")

st.markdown('</div>', unsafe_allow_html=True)
