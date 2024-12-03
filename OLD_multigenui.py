import re
import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import input, textarea, button, tabs
import openai
import textwrap
from pathlib import Path
import os
from datetime import datetime
from github import Github

# GitHub credentials
GITHUB_TOKEN = st.secrets["github_token"]  # Store your token securely in Streamlit secrets
REPO_NAME = "scooter7/webscale"
SAVE_FOLDER = "ECU"

# Initialize GitHub
github = Github(GITHUB_TOKEN)
repo = github.get_repo(REPO_NAME)

def save_to_github(file_name, content):
    try:
        file_path = f"{SAVE_FOLDER}/{file_name}"
        repo.create_file(
            path=file_path,
            message=f"Add {file_name}",
            content=content,
            branch="main"
        )
        st.success(f"Saved {file_name} to GitHub.")
    except Exception as e:
        st.error(f"Error saving {file_name} to GitHub: {e}")

def save_user_data_and_content(requests, generated_contents):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = "user_requests_and_content"
    os.makedirs(folder_name, exist_ok=True)

    # Save user requests
    request_file_name = f"{folder_name}/user_requests_{timestamp}.txt"
    with open(request_file_name, "w") as f:
        for idx, request in enumerate(requests):
            f.write(f"Request {idx + 1}:\n")
            for key, value in request.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

    # Save generated content
    content_file_name = f"{folder_name}/generated_content_{timestamp}.txt"
    with open(content_file_name, "w") as f:
        for idx, content in enumerate(generated_contents):
            f.write(f"Generated Content {idx + 1}:\n")
            f.write(content["Content"] + "\n")
            f.write("\n")

    # Upload to GitHub
    with open(request_file_name, "r") as f:
        save_to_github(f"user_requests_{timestamp}.txt", f.read())

    with open(content_file_name, "r") as f:
        save_to_github(f"generated_content_{timestamp}.txt", f.read())

openai.api_key = st.secrets["openai_api_key"]

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
    .tabs-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
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

# Placeholder data
placeholders = {
    "Purple - caring, encouraging": {
        "verbs": [
            "assist", "befriend", "care", "collaborate", "connect", "embrace", 
            "empower", "encourage", "foster", "give", "help", "nourish", 
            "nurture", "promote", "protect", "provide", "serve", "share", 
            "shepherd", "steward", "tend", "uplift", "value", "welcome"
        ],
        "adjectives": [
            "caring", "encouraging", "attentive", "compassionate", 
            "empathetic", "generous", "hospitable", "nurturing", 
            "protective", "selfless", "supportive", "welcoming"
        ],
        "beliefs": [
            "Believe people should be cared for and encouraged",
            "Desire to make others feel safe and supported",
            "Have a strong desire to mend and heal",
            "Become loyal teammates and trusted allies",
            "Are put off by aggression and selfish motivations"
        ]
    },
    "Green - adventurous, curious": {
        "verbs": [
            "analyze", "discover", "examine", "expand", "explore", "extend", 
            "inquire", "journey", "launch", "move", "pioneer", "pursue", 
            "question", "reach", "search", "uncover", "venture", "wonder"
        ],
        "adjectives": [
            "adventurous", "curious", "discerning", "examining", "experiential", 
            "exploratory", "inquisitive", "investigative", "intrepid", 
            "philosophical"
        ],
        "beliefs": [
            "The noblest pursuit is the quest for new knowledge",
            "Continually inquiring and examining everything",
            "Have an insatiable thirst for progress and discovery",
            "Cannot sit still or accept present realities",
            "Curiosity and possibility underpin their actions"
        ]
    },
    "Maroon - gritty, determined": {
        "verbs": [
            "accomplish", "achieve", "build", "challenge", "commit", 
            "compete", "contend", "dedicate", "defend", "devote", "drive", 
            "endeavor", "entrust", "endure", "fight", "grapple", "grow", 
            "improve", "increase", "overcome", "persevere", "persist", 
            "press on", "pursue", "resolve"
        ],
        "adjectives": [
            "competitive", "determined", "gritty", "industrious", 
            "persevering", "relentless", "resilient", "tenacious", "tough", 
            "unwavering"
        ],
        "beliefs": [
            "Value extreme and hard work",
            "Gritty and strong, they’re determined to overcome",
            "Have no tolerance for laziness or inability",
            "Highly competitive and intent on proving prowess",
            "Will not be outpaced or outworked"
        ]
    },
    "Orange - artistic, creative": {
        "verbs": [
            "compose", "conceptualize", "conceive", "craft", "create", 
            "design", "dream", "envision", "express", "fashion", "form", 
            "imagine", "interpret", "make", "originate", "paint", "perform", 
            "portray", "realize", "shape"
        ],
        "adjectives": [
            "artistic", "conceptual", "creative", "eclectic", "expressive", 
            "imaginative", "interpretive", "novel", "original", "whimsical"
        ],
        "beliefs": [
            "Intensely expressive",
            "Communicate in diverse ways",
            "A lack of imagination and rigidity may feel oppressive",
            "Constructive, conceptual, and adept storytellers",
            "Manifesting new and creative concepts is their end goal"
        ]
    },
    "Yellow - innovative, intelligent": {
        "verbs": [
            "accelerate", "advance", "change", "conceive", "create", 
            "engineer", "envision", "experiment", "dream", "ignite", 
            "illuminate", "imagine", "innovate", "inspire", "invent", 
            "pioneer", "progress", "shape", "spark", "solve", "transform", 
            "unleash", "unlock"
        ],
        "adjectives": [
            "advanced", "analytical", "brilliant", "experimental", 
            "forward-thinking", "innovative", "intelligent", "inventive", 
            "leading-edge", "visionary"
        ],
        "beliefs": [
            "Thrive on new concepts and experimentation",
            "Live to make things newer and better",
            "Work well in ambiguity or unknowns",
            "Feel stifled by established processes and the status quo",
            "See endless possibilities and opportunities to invent"
        ]
    },
    "Red - entertaining, humorous": {
        "verbs": [
            "animate", "amuse", "captivate", "cheer", "delight", "encourage", 
            "energize", "engage", "enjoy", "enliven", "entertain", "excite", 
            "express", "inspire", "joke", "motivate", "play", "stir", "uplift"
        ],
        "adjectives": [
            "dynamic", "energetic", "engaging", "entertaining", 
            "enthusiastic", "exciting", "fun", "lively", "magnetic", 
            "playful", "humorous"
        ],
        "beliefs": [
            "Energetic and uplifting",
            "Motivated to entertain and create excitement",
            "Magnetic and able to rally support for new concepts",
            "Often naturally talented presenters and speakers",
            "Sensitive to the mood and condition of others"
        ]
    },
    "Blue - confident, influential": {
        "verbs": [
            "accomplish", "achieve", "affect", "assert", "cause", "command", 
            "determine", "direct", "dominate", "drive", "empower", 
            "establish", "guide", "impact", "impress", "influence", "inspire", 
            "lead", "outpace", "outshine", "realize", "shape", "succeed", 
            "transform", "win"
        ],
        "adjectives": [
            "accomplished", "assertive", "confident", "decisive", "elite", 
            "influential", "powerful", "prominent", "proven", "strong"
        ],
        "beliefs": [
            "Achievement is paramount",
            "Highly tolerant of risk and stress",
            "Seeks influence and accomplishments",
            "Comfortable making decisions with incomplete information",
            "Set strategic visions and lead the way"
        ]
    },
    "Pink - charming, elegant": {
        "verbs": [
            "arise", "aspire", "detail", "dream", "elevate", "enchant", 
            "enrich", "envision", "exceed", "excel", "experience", "improve", 
            "idealize", "imagine", "inspire", "perfect", "poise", "polish", 
            "prepare", "refine", "uplift"
        ],
        "adjectives": [
            "aesthetic", "charming", "classic", "dignified", "idealistic", 
            "meticulous", "poised", "polished", "refined", "sophisticated", 
            "elegant"
        ],
        "beliefs": [
            "Hold high regard for tradition and excellence",
            "Dream up and pursue refinement, beauty, and vitality",
            "Typically highly detailed and very observant",
            "Mess and disorder only deflates their enthusiasm"
        ]
    },
    "Silver - rebellious, daring": {
        "verbs": [
            "activate", "campaign", "challenge", "commit", "confront", "dare", 
            "defy", "disrupting", "drive", "excite", "face", "ignite", "incite", 
            "influence", "inspire", "inspirit", "motivate", "move", "push", 
            "rebel", "reimagine", "revolutionize", "rise", "spark", "stir", 
            "fight", "free"
        ],
        "adjectives": [
            "bold", "daring", "fearless", "independent", "non-conformist", 
            "radical", "rebellious", "resolute", "unconventional", "valiant"
        ],
        "beliefs": [
            "Rule breakers and establishment challengers",
            "Have a low need to fit in with the pack",
            "Value unconventional and independent thinking",
            "Value freedom, boldness, and defiant ideas",
            "Feel stifled by red tape and bureaucratic systems"
        ]
    },
    "Beige - dedicated, humble": {
        "verbs": [
            "dedicate", "humble", "collaborate", "empower", "inspire", 
            "empassion", "transform"
        ],
        "adjectives": [
            "dedicated", "collaborative", "consistent", "empowering", 
            "enterprising", "humble", "inspiring", "passionate", "proud", 
            "traditional", "transformative"
        ],
        "beliefs": [
            "There’s no need to differentiate from others",
            "All perspectives are equally worth holding",
            "Will not risk offending anyone",
            "Light opinions are held quite loosely",
            "Information tells enough of a story"
        ]
    }
}

def load_templates():
    templates = {}
    base_path = Path("https://raw.githubusercontent.com/scooter7/webscale/main/Examples")
    for template_path in base_path.glob("*.txt"):
        with template_path.open("r") as f:
            templates[template_path.stem] = f.read()
    return templates

templates = load_templates()

if "content_requests" not in st.session_state:
    st.session_state.content_requests = []
if "generated_contents" not in st.session_state:
    st.session_state.generated_contents = []

def clean_content(content):
    cleaned_content = re.sub(r"\*", "", content)  # Remove all asterisks
    cleaned_content = re.sub(r"[^\w\s,.\'\"!?-]", "", cleaned_content)  # Remove emojis and non-alphanumeric characters
    return cleaned_content.strip()

def generate_revised_content(original_content, revision_request):
    prompt = f"""
    Revise the following content based on the described revision request:

    Original Content:
    {original_content}

    Revision Request:
    {revision_request}

    Ensure the revised content aligns with the requested changes, maintains high quality, and adheres to the original structure.
    Do not use asterisks (*) or emojis in the response.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message["content"]
    return clean_content(content)

def generate_content(request):
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

    styles_description = "\n".join(
        f"Style: {style} ({weight}% weight). Verbs: {', '.join(placeholders.get(style, {}).get('verbs', [])[:3])}, "
        f"Adjectives: {', '.join(placeholders.get(style, {}).get('adjectives', [])[:3])}, "
        f"Beliefs: {', '.join(placeholders.get(style, {}).get('beliefs', [])[:1])}"
        for style, weight in zip(writing_styles, style_weights)
    )

    template_descriptions = "\n".join(
        f"{name}: {content[:200]}..."
        for name, content in templates.items()
    )

    prompt = f"""
    You are an expert content creator. Use the following inputs and templates to guide the content creation:

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

    Templates for Guidance:
    {template_descriptions}

    Ensure the content is engaging, concise, and tailored to the audience described.
    Ensure the call to action (CTA) always appears at the bottom of the email, just above the signature section. This is critical - use the CTA verbatim as the user has entered it.
    Do not include paragraph numbering in the output. Ensure the content aligns with the tone, structure, and length suggested by the templates.
    Use the verbs and adjectives for each color placeholder sparingly.
    Do not use asterisks (*) or emojis in the response.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message["content"]
    return clean_content(content)

tabs_options = ["Create Content", "Generated Content", "Revisions"]
active_tab = tabs(options=tabs_options, default_value="Create Content", key="main_tabs", container_class="tabs-container")

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
                        label=f"Weight for {style}:",
                        min_value=0,
                        max_value=100,
                        value=50,
                        step=1,
                        key=f"weight_{idx}_{style}",
                    )
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
        save_user_data_and_content(st.session_state.content_requests, st.session_state.generated_contents)

elif active_tab == "Generated Content":
    st.subheader("Generated Content")
    if st.session_state.generated_contents:
        for idx, content_data in enumerate(st.session_state.generated_contents):
            content = content_data["Content"]
            st.text_area(
                label=f"Content {idx + 1}",
                value=content,
                height=300,
                key=f"generated_content_{idx}",
            )
            st.download_button(
                label="Download Content",
                data=content,
                file_name=f"content_{content_data['Request']}.txt",
                mime="text/plain",
            )
    else:
        st.info("No content generated yet. Go to 'Create Content' to generate content.")

elif active_tab == "Revisions":
    st.subheader("Revise Content")
    original_content = textarea(
        default_value="", 
        placeholder="Paste content to revise...", 
        key="revision_content"
    )
    revision_request = textarea(
        default_value="", 
        placeholder="Describe the revisions needed...", 
        key="revision_request"
    )
    if button(text="Revise Content", key="revise"):
        # Ensure both fields are filled before generating revisions
        if original_content.strip() and revision_request.strip():
            revised_content = generate_revised_content(original_content, revision_request)

            # Display the revised content
            st.text_area(
                label="Revised Content",
                value=revised_content,
                height=300,
                key="revised_content",
            )

            # Save to GitHub
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            revision_file_name = f"revised_content_{timestamp}.txt"
            revision_content = f"Original Content:\n{original_content}\n\nRevision Request:\n{revision_request}\n\nRevised Content:\n{revised_content}\n"
            save_to_github(revision_file_name, revision_content)

            # Allow download
            st.download_button(
                label="Download Revised Content",
                data=revised_content,
                file_name="revised_content.txt",
                mime="text/plain",
            )
            st.success(f"Revised content saved to GitHub as {revision_file_name}.")
        else:
            st.error("Please provide both the original content and the revision request.")
