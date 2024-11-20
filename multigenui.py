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

def generate_email(subject, body, signature, writing_style, weight):
    style_data = placeholders.get(writing_style, {})
    verbs = ", ".join(style_data.get("verbs", [])[:3])
    adjectives = ", ".join(style_data.get("adjectives", [])[:3])
    beliefs = "; ".join(style_data.get("beliefs", [])[:1])

    email_content = f"""
    Subject: {subject}

    {body}

    Verbs ({verbs}), Adjectives ({adjectives}), Beliefs ({beliefs}) included in {weight}% of the content.

    {signature}
    """
    return {
        "subject": subject,
        "body": email_content,
        "signature": signature,
    }

def download_email(email_data, filename):
    email_text = f"Subject: {email_data['subject']}\n\n{email_data['body']}\n\n{email_data['signature']}"
    st.download_button(
        label="Download Email",
        data=email_text,
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
            subject = input(default_value="", placeholder="Enter email subject...", key=f"subject_{idx}")
            body = textarea(default_value="", placeholder="Enter email body content...", key=f"body_{idx}")
            signature = textarea(default_value="", placeholder="Enter email signature...", key=f"signature_{idx}")
            writing_style = st.selectbox("Choose a writing style", options=list(placeholders.keys()), key=f"style_{idx}")
            weight = st.slider("Style weight percentage", min_value=0, max_value=100, value=50, step=5, key=f"weight_{idx}")
            st.session_state.content_requests[idx] = {
                "subject": subject,
                "body": body,
                "signature": signature,
                "writing_style": writing_style,
                "weight": weight,
            }
    if button(text="Generate All Content", key="generate_all"):
        st.session_state.generated_contents = []
        for idx, request in enumerate(st.session_state.content_requests):
            generated_email = generate_email(
                request["subject"],
                request["body"],
                request["signature"],
                request["writing_style"],
                request["weight"],
            )
            st.session_state.generated_contents.append(
                {"Request": idx + 1, "Email": generated_email}
            )
        st.success("Content generation completed! Navigate to the 'Generated Content' tab to view and download your results.")

elif active_tab == "Generated Content":
    st.subheader("Generated Content")
    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            email_data = content_data["Email"]
            ui.card(
                title=f"Generated Email {content_data['Request']}",
                content=f"""
                    <div style="margin-bottom: 10px;"><strong>Subject:</strong> {email_data['subject']}</div>
                    <div style="margin-bottom: 10px;">{email_data['body']}</div>
                    <div><em>{email_data['signature']}</em></div>
                """,
                description="Generated based on user input.",
                key=f"card_{idx}",
            ).render()

            download_email(email_data, f"email_{content_data['Request']}.txt")
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

elif active_tab == "Revisions":
    st.subheader("Make Revisions")
    revision_subject = input(default_value="", placeholder="Enter revised subject...", key="revision_subject")
    revision_body = textarea(default_value="", placeholder="Enter revised body...", key="revision_body")
    revision_signature = textarea(default_value="", placeholder="Enter revised signature...", key="revision_signature")
    revision_style = st.selectbox("Choose a writing style for revision", options=list(placeholders.keys()), key="revision_style")
    revision_weight = st.slider("Style weight percentage for revision", min_value=0, max_value=100, value=50, step=5, key="revision_weight")
    if button(text="Revise Content", key="revise"):
        revised_email = generate_email(
            revision_subject,
            revision_body,
            revision_signature,
            revision_style,
            revision_weight,
        )
        ui.card(
            title="Revised Email",
            content=f"""
                <div style="margin-bottom: 10px;"><strong>Subject:</strong> {revised_email['subject']}</div>
                <div style="margin-bottom: 10px;">{revised_email['body']}</div>
                <div><em>{revised_email['signature']}</em></div>
            """,
            description="Updated based on your revision input.",
            key="revised_card",
        ).render()

        download_email(revised_email, "revised_email.txt")

st.markdown('</div>', unsafe_allow_html=True)
